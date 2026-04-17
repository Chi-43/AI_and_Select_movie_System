from decimal import Decimal
import re
from collections import Counter

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .ai_views import generate_llm_recommend_reason

from .models import (
    Movie,
    User,
    Rating,
    VideoPlatform,
    UserProfile,
    RecommendationLog,
    MovieFeedback,
    MovieComment,
)
from .serializers import (
    MovieSerializer,
    UserSerializer,
    RatingSerializer,
    VideoPlatformSerializer,
    UserProfileSerializer,
    OnboardingPreferenceSerializer,
    MovieFeedbackSerializer,
    MovieCommentSerializer,
)
from .collaborative_filtering import CollaborativeFiltering
from .movie_detail_cache import get_movie_detail_from_cache
from scrapers.video_url import fetch_douban_watch_links


PLATFORM_MAP = {
    "爱奇艺": "iqiyi",
    "腾讯视频": "tencent",
    "优酷视频": "youku",
    "优酷": "youku",
    "哔哩哔哩": "bilibili",
    "咪咕视频": "migu",
    "芒果TV": "mango",
    "Netflix": "netflix",
    "Disney+": "disney",
    "Amazon Prime": "amazon",
}


def map_platform_name(platform_name):
    """将豆瓣页面的平台名映射为模型中的 platform code"""
    return PLATFORM_MAP.get((platform_name or "").strip(), "other")


def map_vip_status(price_info):
    """根据价格/文案推断观看权限"""
    text = (price_info or "").strip()

    if not text:
        return "unknown"
    if "免费" in text:
        return "free"
    if "VIP" in text or "会员" in text:
        return "vip"
    if "租" in text:
        return "rent"
    if "付费" in text or "购买" in text:
        return "pay"
    return "unknown"


def extract_price(price_info):
    """从文案中提取价格，例如：'6.0元购买' -> Decimal('6.0')"""
    if not price_info:
        return None

    match = re.search(r"(\d+(?:\.\d+)?)\s*元", price_info)
    if match:
        return Decimal(match.group(1))
    return None


def split_multi_value(text):
    """把 '剧情 / 犯罪' 或 '美国 英国' 这类字段拆成列表"""
    if not text:
        return []
    return [item.strip() for item in re.split(r"[ /、,，]+", text) if item.strip()]


def build_profile_summary(profile: UserProfile):
    """生成用户画像总结（当前为规则版，后续可替换成 LLM 版）"""
    genres = "、".join(profile.favorite_genres[:3]) if profile.favorite_genres else "暂无明显类型偏好"
    countries = "、".join(profile.favorite_countries[:3]) if profile.favorite_countries else "暂无明显国家偏好"

    year_text = "年份偏好暂不明显"
    if profile.favorite_years and profile.favorite_years.get("min") and profile.favorite_years.get("max"):
        year_text = f"更偏好 {profile.favorite_years['min']} - {profile.favorite_years['max']} 年间的电影"

    keywords = "、".join(profile.favorite_keywords[:5]) if profile.favorite_keywords else "暂无明显关键词"

    return (
        f"该用户偏好类型主要为：{genres}；"
        f"偏好国家/地区主要为：{countries}；"
        f"{year_text}；"
        f"兴趣关键词包括：{keywords}。"
    )


def update_user_profile_from_ratings(user: User):
    """
    根据用户评分记录自动更新画像
    这里只统计 rating >= 4 的电影
    """
    ratings = (
        Rating.objects.filter(user=user, rating__gte=4)
        .select_related("movie")
        .order_by("-timestamp")
    )

    profile, _ = UserProfile.objects.get_or_create(user=user)

    genre_counter = Counter()
    country_counter = Counter()
    keyword_counter = Counter()
    years = []

    for r in ratings:
        movie = r.movie

        for g in split_multi_value(movie.genre):
            genre_counter[g] += 1

        for c in split_multi_value(movie.country):
            country_counter[c] += 1

        for kw in split_multi_value(movie.genre):
            keyword_counter[kw] += 1

        for kw in split_multi_value(movie.country):
            keyword_counter[kw] += 1

        if movie.year:
            years.append(movie.year)

    # 如果用户已经有冷启动选择的偏好，就和评分统计合并
    existing_genres = profile.favorite_genres or []
    existing_countries = profile.favorite_countries or []
    existing_keywords = profile.favorite_keywords or []

    for g in existing_genres:
        genre_counter[g] += 2
    for c in existing_countries:
        country_counter[c] += 2
    for kw in existing_keywords:
        keyword_counter[kw] += 1

    profile.favorite_genres = [name for name, _ in genre_counter.most_common(5)]
    profile.favorite_countries = [name for name, _ in country_counter.most_common(5)]
    profile.favorite_keywords = [name for name, _ in keyword_counter.most_common(8)]

    if years:
        profile.favorite_years = {
            "min": min(years),
            "max": max(years),
        }

    profile.profile_summary = build_profile_summary(profile)
    profile.save()

    return profile


def generate_basic_reason(user: User, movie: Movie, algorithm: str, context=None):
    """
    规则版推荐理由生成
    后续你接 DeepSeek 时，可以直接替换这里
    """
    profile = getattr(user, "profile", None)
    reasons = []

    if profile:
        if profile.favorite_genres:
            matched_genres = [g for g in profile.favorite_genres if g in (movie.genre or "")]
            if matched_genres:
                reasons.append(f"你偏好{'、'.join(matched_genres[:2])}题材")

        if profile.favorite_countries:
            matched_countries = [c for c in profile.favorite_countries if c in (movie.country or "")]
            if matched_countries:
                reasons.append(f"你较关注{'、'.join(matched_countries[:2])}电影")

    if getattr(movie, "rating", None):
        if movie.rating and movie.rating >= 9:
            reasons.append("该片本身属于高分电影")

    if algorithm == "user_based":
        reasons.append("与您兴趣相似的用户也喜欢这部电影")
    elif algorithm == "item_based":
        reasons.append("它与您高评分过的电影较为相似")
    elif algorithm == "cold_start":
        reasons.append("这是根据您初始兴趣偏好筛选得到的结果")
    elif algorithm == "top":
        reasons.append("该片在整体用户中热度和评分都较高")

    if context and context.get("user_high_rating_movies"):
        high_rated_titles = [item["title"] for item in context["user_high_rating_movies"][:2]]
        if high_rated_titles:
            reasons.append(f"与你喜欢的《{'》《'.join(high_rated_titles)}》具有一定偏好关联")

    if not reasons:
        return "根据您的兴趣偏好，为您推荐这部电影。"

    return "；".join(reasons) + "。"


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


class VideoPlatformViewSet(viewsets.ModelViewSet):
    queryset = VideoPlatform.objects.all()
    serializer_class = VideoPlatformSerializer

    @action(detail=False, methods=["get"])
    def by_movie_title(self, request):
        """根据电影名称或豆瓣链接获取视频平台链接"""
        movie_title = request.query_params.get("movie_title", "").strip()
        douban_url = request.query_params.get("douban_url", "").strip()
        use_spider = request.query_params.get("use_spider", "false").lower() == "true"

        if not movie_title and not douban_url:
            return Response(
                {"error": "请提供movie_title或douban_url参数"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = VideoPlatform.objects.all()

        if movie_title:
            queryset = queryset.filter(movie_title__icontains=movie_title)

        if douban_url:
            queryset = queryset.filter(douban_url__icontains=douban_url)

        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        if use_spider and douban_url:
            try:
                spider_results = fetch_douban_watch_links(douban_url)
                return Response({
                    "source": "douban_spider",
                    "results": spider_results
                })
            except Exception as e:
                return Response(
                    {"error": f"抓取失败: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response([])

    @action(detail=False, methods=["get"])
    def by_platform(self, request):
        """根据视频平台获取电影链接"""
        platform = request.query_params.get("platform", "").strip()

        if not platform:
            return Response(
                {"error": "请提供platform参数"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = VideoPlatform.objects.filter(platform=platform, available=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class VideoPlatformLinksView(APIView):
    """获取电影的视频平台链接API"""

    def get(self, request):
        movie_title = request.query_params.get("movie_title", "").strip()
        douban_url = request.query_params.get("douban_url", "").strip()
        use_spider = request.query_params.get("use_spider", "true").lower() == "true"
        save_to_db = request.query_params.get("save_to_db", "true").lower() == "true"

        if not movie_title and not douban_url:
            return Response(
                {"error": "请提供movie_title或douban_url参数"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = VideoPlatform.objects.filter(available=True)

        if movie_title:
            queryset = queryset.filter(movie_title__icontains=movie_title)

        if douban_url:
            queryset = queryset.filter(douban_url__icontains=douban_url)

        if queryset.exists():
            platforms = {}
            for platform in queryset:
                platform_name = platform.get_platform_display()
                if platform_name not in platforms:
                    platforms[platform_name] = []

                platforms[platform_name].append({
                    "id": platform.id,
                    "movie_title": platform.movie_title,
                    "douban_url": platform.douban_url,
                    "platform": platform.platform,
                    "platform_display": platform.get_platform_display(),
                    "platform_url": platform.platform_url,
                    "vip_status": platform.vip_status,
                    "vip_status_display": platform.get_vip_status_display(),
                    "price": float(platform.price) if platform.price else None,
                    "quality": platform.quality,
                    "available": platform.available,
                    "last_checked": platform.last_checked,
                    "source": "database",
                })

            return Response({
                "movie_title": movie_title,
                "douban_url": douban_url,
                "source": "database",
                "total_platforms": len(platforms),
                "total_links": queryset.count(),
                "platforms": platforms,
            })

        if not use_spider:
            return Response({
                "movie_title": movie_title,
                "douban_url": douban_url,
                "source": "database",
                "total_platforms": 0,
                "total_links": 0,
                "platforms": {},
            })

        if not douban_url:
            return Response(
                {"error": "数据库中无数据，且未提供douban_url，无法抓取豆瓣页面"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            spider_results = fetch_douban_watch_links(douban_url)

            if not spider_results:
                return Response({
                    "movie_title": movie_title,
                    "douban_url": douban_url,
                    "source": "douban_spider",
                    "total_platforms": 0,
                    "total_links": 0,
                    "platforms": {},
                    "message": "未抓取到平台链接，可能该页面无“在哪里看这部电影”区域，或页面结构已变化",
                })

            grouped_platforms = {}

            for item in spider_results:
                platform_display_name = item.get("platform", "").strip()
                platform_code = map_platform_name(platform_display_name)
                vip_status = map_vip_status(item.get("price_info"))
                price = extract_price(item.get("price_info"))
                resolved_movie_title = movie_title or item.get("movie_title") or ""

                db_obj = None
                if save_to_db:
                    db_obj, _ = VideoPlatform.objects.update_or_create(
                        douban_url=douban_url,
                        platform=platform_code,
                        defaults={
                            "movie_title": resolved_movie_title,
                            "platform_url": item.get("platform_url", ""),
                            "vip_status": vip_status,
                            "price": price,
                            "quality": None,
                            "available": True,
                        },
                    )

                if platform_display_name not in grouped_platforms:
                    grouped_platforms[platform_display_name] = []

                grouped_platforms[platform_display_name].append({
                    "id": db_obj.id if db_obj else None,
                    "movie_title": resolved_movie_title,
                    "douban_url": douban_url,
                    "platform": platform_code,
                    "platform_display": platform_display_name,
                    "platform_url": item.get("platform_url"),
                    "icon": item.get("icon"),
                    "vip_status": vip_status,
                    "vip_status_display": dict(VideoPlatform.VIP_CHOICES).get(vip_status, "未知"),
                    "price": float(price) if price else None,
                    "quality": None,
                    "available": True,
                    "price_info": item.get("price_info"),
                    "source": "douban_spider",
                })

            final_movie_title = movie_title
            if not final_movie_title and spider_results:
                final_movie_title = spider_results[0].get("movie_title", "")

            return Response({
                "movie_title": final_movie_title,
                "douban_url": douban_url,
                "source": "douban_spider",
                "total_platforms": len(grouped_platforms),
                "total_links": sum(len(v) for v in grouped_platforms.values()),
                "platforms": grouped_platforms,
            })

        except Exception as e:
            return Response(
                {"error": f"抓取豆瓣失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MovieDetailView(APIView):
    """获取电影详情API（轻量快速版）"""

    def get(self, request):
        movie_title = request.query_params.get("movie_title", "").strip()
        douban_url = request.query_params.get("douban_url", "").strip()

        if not douban_url:
            return Response(
                {"error": "请提供 douban_url 参数"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cached_data = get_movie_detail_from_cache(douban_url)

        if cached_data:
            data = dict(cached_data)
            if movie_title and not data.get("movie_title"):
                data["movie_title"] = movie_title
            data["source"] = "cache"
            return Response(data)

        return Response({
            "movie_title": movie_title,
            "english_title": "",
            "douban_url": douban_url,
            "poster": "",
            "rating": "",
            "rating_count": "",
            "director": [],
            "writer": [],
            "actors": [],
            "genres": [],
            "countries": [],
            "languages": [],
            "release_dates": [],
            "runtime": [],
            "aka": [],
            "imdb": "",
            "summary": "",
            "year": "",
            "source": "empty",
            "message": "暂无扩展详情缓存，当前返回基础空结构",
        })


class OnboardingPreferenceView(APIView):
    """
    冷启动兴趣选择接口
    GET: 获取当前用户兴趣
    POST: 保存当前用户兴趣
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        serializer = OnboardingPreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile.favorite_genres = serializer.validated_data.get("favorite_genres", [])
        profile.favorite_countries = serializer.validated_data.get("favorite_countries", [])
        profile.favorite_keywords = serializer.validated_data.get("favorite_keywords", [])
        profile.favorite_years = serializer.validated_data.get("favorite_years", {})
        profile.onboarding_completed = True
        profile.profile_summary = build_profile_summary(profile)
        profile.save()

        return Response({
            "message": "冷启动兴趣已保存",
            "profile": UserProfileSerializer(profile).data,
        })


class UserProfileView(APIView):
    """
    用户画像接口
    GET: 获取画像
    POST: 根据评分重新计算画像
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        profile = update_user_profile_from_ratings(request.user)
        return Response({
            "message": "用户画像已更新",
            "profile": UserProfileSerializer(profile).data,
        })


class RecommendationView(APIView):
    """推荐API（升级版：返回 score + reason）"""

    def get(self, request):
        user_id = request.query_params.get("user_id")
        algorithm = request.query_params.get("algorithm", "user_based")
        top_n = int(request.query_params.get("top_n", 10))

        if not user_id:
            return Response(
                {"error": "user_id参数是必需的"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "用户不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        cf = CollaborativeFiltering()
        user_rating_count = Rating.objects.filter(user=user).count()

        if algorithm == "user_based":
            recs = cf.user_based_recommendations_with_scores(user.id, top_n)
        elif algorithm == "item_based":
            recs = cf.item_based_recommendations_with_scores(user.id, top_n)
        elif algorithm == "cold_start":
            profile, _ = UserProfile.objects.get_or_create(user=user)
            queryset = Movie.objects.all()

            # 类型过滤：逐步缩小范围
            for genre in profile.favorite_genres[:3]:
                queryset = queryset.filter(genre__icontains=genre)

            # 国家过滤
            if profile.favorite_countries:
                queryset = queryset.filter(country__icontains=profile.favorite_countries[0])

            # 年份过滤
            if profile.favorite_years:
                year_min = profile.favorite_years.get("min")
                year_max = profile.favorite_years.get("max")
                if year_min:
                    queryset = queryset.filter(year__gte=year_min)
                if year_max:
                    queryset = queryset.filter(year__lte=year_max)

            movies = queryset.order_by("-rating")[:top_n]

            recs = [
                {
                    "movie_id": movie.id,
                    "score": float(movie.rating or 0),
                    "algorithm": "cold_start",
                }
                for movie in movies
            ]
        else:
            return Response(
                {"error": "算法参数必须是user_based、item_based或cold_start"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 如果没推荐出来，自动降级
        if not recs:
            if user_rating_count == 0:
                profile, _ = UserProfile.objects.get_or_create(user=user)
                queryset = Movie.objects.all()

                if profile.favorite_genres:
                    queryset = queryset.filter(genre__icontains=profile.favorite_genres[0])

                movies = queryset.order_by("-rating")[:top_n]
                recs = [
                    {
                        "movie_id": movie.id,
                        "score": float(movie.rating or 0),
                        "algorithm": "cold_start",
                    }
                    for movie in movies
                ]
            else:
                recs = cf.get_top_movies_with_scores(top_n)

        movie_ids = [item["movie_id"] for item in recs]
        movie_map = {movie.id: movie for movie in Movie.objects.filter(id__in=movie_ids)}

        results = []
        for item in recs:
            movie = movie_map.get(item["movie_id"])
            if not movie:
                continue

            context = cf.build_reason_context(user.id, movie.id, item["algorithm"])

            try:
                reason = generate_llm_recommend_reason(
                    user=user,
                    movie=movie,
                    algorithm=item["algorithm"],
                    context=context,
                )
            except Exception:
                reason = generate_basic_reason(
                    user=user,
                    movie=movie,
                    algorithm=item["algorithm"],
                    context=context,
                )

            RecommendationLog.objects.create(
                user=user,
                movie=movie,
                algorithm=item["algorithm"],
                score=item["score"],
                reason=reason,
            )

            results.append({
                "movie": MovieSerializer(movie).data,
                "score": round(item["score"], 4),
                "algorithm": item["algorithm"],
                "reason": reason,
            })

        return Response({
            "user_id": user.id,
            "username": user.username,
            "algorithm": algorithm,
            "recommendations": results,
        })


class TopMoviesView(APIView):
    """热门电影API"""

    def get(self, request):
        top_n = int(request.query_params.get("top_n", 10))

        cf = CollaborativeFiltering()
        recs = cf.get_top_movies_with_scores(top_n)

        movie_ids = [item["movie_id"] for item in recs]
        movie_map = {movie.id: movie for movie in Movie.objects.filter(id__in=movie_ids)}

        results = []
        for item in recs:
            movie = movie_map.get(item["movie_id"])
            if not movie:
                continue

            results.append({
                "movie": MovieSerializer(movie).data,
                "score": round(item["score"], 4),
                "algorithm": item["algorithm"],
                "rating_count": item.get("rating_count", 0),
            })

        return Response({
            "top_movies": results
        })


class SimilarMoviesView(APIView):
    """相似电影API"""

    def get(self, request, movie_id):
        top_n = int(request.query_params.get("top_n", 5))

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {"error": "电影不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        cf = CollaborativeFiltering()
        cf.calculate_movie_similarity()

        if cf.movie_similarity is None:
            return Response(
                {"error": "无法计算电影相似度"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if movie.id not in cf.movie_ids:
            return Response(
                {"error": "电影不在矩阵中"},
                status=status.HTTP_404_NOT_FOUND,
            )

        movie_idx = cf.movie_ids.index(movie.id)
        similarities = cf.movie_similarity[movie_idx]

        similar_movies = []
        for idx, similarity in enumerate(similarities):
            if idx != movie_idx and similarity > 0:
                similar_movies.append((cf.movie_ids[idx], float(similarity)))

        similar_movies.sort(key=lambda x: x[1], reverse=True)
        top_movie_ids = [mid for mid, _ in similar_movies[:top_n]]

        movie_map = {m.id: m for m in Movie.objects.filter(id__in=top_movie_ids)}

        results = []
        for mid, sim in similar_movies[:top_n]:
            movie_obj = movie_map.get(mid)
            if movie_obj:
                results.append({
                    "movie": MovieSerializer(movie_obj).data,
                    "similarity": round(sim, 4),
                })

        return Response({
            "movie_id": movie.id,
            "movie_title": movie.title,
            "similar_movies": results,
        })
    

class MovieFeedbackView(APIView):
    """
    电影点赞 / 拉踩接口
    GET: 获取当前电影的点赞数、拉踩数、当前用户反馈状态
    POST: 点赞 / 拉踩（会自动覆盖旧状态）
    DELETE: 取消当前用户对该电影的反馈
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        movie_id = request.query_params.get("movie_id")

        if not movie_id:
            return Response(
                {"error": "movie_id参数是必需的"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {"error": "电影不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        like_count = MovieFeedback.objects.filter(movie=movie, feedback_type="like").count()
        dislike_count = MovieFeedback.objects.filter(movie=movie, feedback_type="dislike").count()

        current_feedback = MovieFeedback.objects.filter(
            movie=movie,
            user=request.user
        ).first()

        return Response({
            "movie_id": movie.id,
            "movie_title": movie.title,
            "like_count": like_count,
            "dislike_count": dislike_count,
            "current_user_feedback": current_feedback.feedback_type if current_feedback else None,
        })

    def post(self, request):
        movie_id = request.data.get("movie_id")
        feedback_type = request.data.get("feedback_type")

        if not movie_id:
            return Response(
                {"error": "movie_id参数是必需的"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if feedback_type not in ["like", "dislike"]:
            return Response(
                {"error": "feedback_type必须是 like 或 dislike"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {"error": "电影不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        feedback, created = MovieFeedback.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={"feedback_type": feedback_type},
        )

        return Response({
            "message": "反馈提交成功" if created else "反馈更新成功",
            "feedback": MovieFeedbackSerializer(feedback, context={"request": request}).data,
        })

    def delete(self, request):
        movie_id = request.data.get("movie_id") or request.query_params.get("movie_id")

        if not movie_id:
            return Response(
                {"error": "movie_id参数是必需的"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted_count, _ = MovieFeedback.objects.filter(
            user=request.user,
            movie_id=movie_id
        ).delete()

        if deleted_count == 0:
            return Response(
                {"error": "当前用户没有对这部电影做过反馈"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({"message": "反馈已取消"})
    
class MovieCommentView(APIView):
    """
    电影评论接口
    GET: 获取某部电影评论列表
    POST: 发表评论
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        movie_id = request.query_params.get("movie_id")

        if not movie_id:
            return Response(
                {"error": "movie_id参数是必需的"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {"error": "电影不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        comments = MovieComment.objects.filter(movie=movie).select_related("user", "movie")
        serializer = MovieCommentSerializer(
            comments,
            many=True,
            context={"request": request}
        )

        return Response({
            "movie_id": movie.id,
            "movie_title": movie.title,
            "count": comments.count(),
            "comments": serializer.data,
        })

    def post(self, request):
        movie_id = request.data.get("movie_id")
        content = (request.data.get("content") or "").strip()

        if not movie_id:
            return Response(
                {"error": "movie_id参数是必需的"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not content:
            return Response(
                {"error": "评论内容不能为空"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {"error": "电影不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        comment = MovieComment.objects.create(
            user=request.user,
            movie=movie,
            content=content,
        )

        return Response({
            "message": "评论发布成功",
            "comment": MovieCommentSerializer(comment, context={"request": request}).data,
        })
    
class MovieCommentDetailView(APIView):
    """
    单条评论接口
    DELETE: 删除当前用户自己的评论
    PUT: 修改当前用户自己的评论
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, comment_id):
        try:
            comment = MovieComment.objects.get(id=comment_id, user=request.user)
        except MovieComment.DoesNotExist:
            return Response(
                {"error": "评论不存在或无权限修改"},
                status=status.HTTP_404_NOT_FOUND,
            )

        content = (request.data.get("content") or "").strip()
        if not content:
            return Response(
                {"error": "评论内容不能为空"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment.content = content
        comment.save()

        return Response({
            "message": "评论修改成功",
            "comment": MovieCommentSerializer(comment, context={"request": request}).data,
        })

    def delete(self, request, comment_id):
        try:
            comment = MovieComment.objects.get(id=comment_id, user=request.user)
        except MovieComment.DoesNotExist:
            return Response(
                {"error": "评论不存在或无权限删除"},
                status=status.HTTP_404_NOT_FOUND,
            )

        comment.delete()
        return Response({"message": "评论删除成功"})