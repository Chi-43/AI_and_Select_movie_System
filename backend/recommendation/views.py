from decimal import Decimal
import re

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie, User, Rating, VideoPlatform
from .serializers import (
    MovieSerializer,
    UserSerializer,
    RatingSerializer,
    VideoPlatformSerializer
)
from .collaborative_filtering import CollaborativeFiltering
from .movie_detail_cache import get_movie_detail_from_cache
from scrapers.video_url import fetch_douban_watch_links


PLATFORM_MAP = {
    '爱奇艺': 'iqiyi',
    '腾讯视频': 'tencent',
    '优酷视频': 'youku',
    '优酷': 'youku',
    '哔哩哔哩': 'bilibili',
    '咪咕视频': 'migu',
    '芒果TV': 'mango',
    'Netflix': 'netflix',
    'Disney+': 'disney',
    'Amazon Prime': 'amazon',
}


def map_platform_name(platform_name):
    """将豆瓣页面的平台名映射为模型中的 platform code"""
    return PLATFORM_MAP.get((platform_name or '').strip(), 'other')


def map_vip_status(price_info):
    """根据价格/文案推断观看权限"""
    text = (price_info or '').strip()

    if not text:
        return 'unknown'
    if '免费' in text:
        return 'free'
    if 'VIP' in text or '会员' in text:
        return 'vip'
    if '租' in text:
        return 'rent'
    if '付费' in text or '购买' in text:
        return 'pay'
    return 'unknown'


def extract_price(price_info):
    """从文案中提取价格，例如：'6.0元购买' -> Decimal('6.0')"""
    if not price_info:
        return None

    match = re.search(r'(\d+(?:\.\d+)?)\s*元', price_info)
    if match:
        return Decimal(match.group(1))
    return None


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

    @action(detail=False, methods=['get'])
    def by_movie_title(self, request):
        """根据电影名称或豆瓣链接获取视频平台链接"""
        movie_title = request.query_params.get('movie_title', '').strip()
        douban_url = request.query_params.get('douban_url', '').strip()
        use_spider = request.query_params.get('use_spider', 'false').lower() == 'true'

        if not movie_title and not douban_url:
            return Response(
                {'error': '请提供movie_title或douban_url参数'},
                status=status.HTTP_400_BAD_REQUEST
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
                    'source': 'douban_spider',
                    'results': spider_results
                })
            except Exception as e:
                return Response(
                    {'error': f'抓取失败: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response([])

    @action(detail=False, methods=['get'])
    def by_platform(self, request):
        """根据视频平台获取电影链接"""
        platform = request.query_params.get('platform', '').strip()

        if not platform:
            return Response(
                {'error': '请提供platform参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = VideoPlatform.objects.filter(platform=platform, available=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class VideoPlatformLinksView(APIView):
    """获取电影的视频平台链接API"""

    def get(self, request):
        movie_title = request.query_params.get('movie_title', '').strip()
        douban_url = request.query_params.get('douban_url', '').strip()
        use_spider = request.query_params.get('use_spider', 'true').lower() == 'true'
        save_to_db = request.query_params.get('save_to_db', 'true').lower() == 'true'

        if not movie_title and not douban_url:
            return Response(
                {'error': '请提供movie_title或douban_url参数'},
                status=status.HTTP_400_BAD_REQUEST
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
                    'id': platform.id,
                    'movie_title': platform.movie_title,
                    'douban_url': platform.douban_url,
                    'platform': platform.platform,
                    'platform_display': platform.get_platform_display(),
                    'platform_url': platform.platform_url,
                    'vip_status': platform.vip_status,
                    'vip_status_display': platform.get_vip_status_display(),
                    'price': float(platform.price) if platform.price else None,
                    'quality': platform.quality,
                    'available': platform.available,
                    'last_checked': platform.last_checked,
                    'source': 'database',
                })

            return Response({
                'movie_title': movie_title,
                'douban_url': douban_url,
                'source': 'database',
                'total_platforms': len(platforms),
                'total_links': queryset.count(),
                'platforms': platforms
            })

        if not use_spider:
            return Response({
                'movie_title': movie_title,
                'douban_url': douban_url,
                'source': 'database',
                'total_platforms': 0,
                'total_links': 0,
                'platforms': {}
            })

        if not douban_url:
            return Response(
                {'error': '数据库中无数据，且未提供douban_url，无法抓取豆瓣页面'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            spider_results = fetch_douban_watch_links(douban_url)

            if not spider_results:
                return Response({
                    'movie_title': movie_title,
                    'douban_url': douban_url,
                    'source': 'douban_spider',
                    'total_platforms': 0,
                    'total_links': 0,
                    'platforms': {},
                    'message': '未抓取到平台链接，可能该页面无“在哪里看这部电影”区域，或页面结构已变化'
                })

            grouped_platforms = {}

            for item in spider_results:
                platform_display_name = item.get('platform', '').strip()
                platform_code = map_platform_name(platform_display_name)
                vip_status = map_vip_status(item.get('price_info'))
                price = extract_price(item.get('price_info'))
                resolved_movie_title = movie_title or item.get('movie_title') or ''

                db_obj = None
                if save_to_db:
                    db_obj, _ = VideoPlatform.objects.update_or_create(
                        douban_url=douban_url,
                        platform=platform_code,
                        defaults={
                            'movie_title': resolved_movie_title,
                            'platform_url': item.get('platform_url', ''),
                            'vip_status': vip_status,
                            'price': price,
                            'quality': None,
                            'available': True,
                        }
                    )

                if platform_display_name not in grouped_platforms:
                    grouped_platforms[platform_display_name] = []

                grouped_platforms[platform_display_name].append({
                    'id': db_obj.id if db_obj else None,
                    'movie_title': resolved_movie_title,
                    'douban_url': douban_url,
                    'platform': platform_code,
                    'platform_display': platform_display_name,
                    'platform_url': item.get('platform_url'),
                    'icon': item.get('icon'),
                    'vip_status': vip_status,
                    'vip_status_display': dict(VideoPlatform.VIP_CHOICES).get(vip_status, '未知'),
                    'price': float(price) if price else None,
                    'quality': None,
                    'available': True,
                    'price_info': item.get('price_info'),
                    'source': 'douban_spider',
                })

            final_movie_title = movie_title
            if not final_movie_title and spider_results:
                final_movie_title = spider_results[0].get('movie_title', '')

            return Response({
                'movie_title': final_movie_title,
                'douban_url': douban_url,
                'source': 'douban_spider',
                'total_platforms': len(grouped_platforms),
                'total_links': sum(len(v) for v in grouped_platforms.values()),
                'platforms': grouped_platforms
            })

        except Exception as e:
            return Response(
                {'error': f'抓取豆瓣失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MovieDetailView(APIView):
    """获取电影详情API（轻量快速版）"""

    def get(self, request):
        movie_title = request.query_params.get('movie_title', '').strip()
        douban_url = request.query_params.get('douban_url', '').strip()

        if not douban_url:
            return Response(
                {'error': '请提供 douban_url 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. 优先查本地缓存
        cached_data = get_movie_detail_from_cache(douban_url)

        if cached_data:
            data = dict(cached_data)
            if movie_title and not data.get("movie_title"):
                data["movie_title"] = movie_title
            data["source"] = "cache"
            return Response(data)

        # 2. 没有缓存时，直接返回空扩展结构
        # 前端会继续显示 sessionStorage 里的基础信息，不会阻塞页面
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
            "message": "暂无扩展详情缓存，当前返回基础空结构"
        })


class RecommendationView(APIView):
    """推荐API"""

    def get(self, request):
        user_id = request.query_params.get('user_id')
        algorithm = request.query_params.get('algorithm', 'user_based')
        top_n = int(request.query_params.get('top_n', 10))

        if not user_id:
            return Response(
                {'error': 'user_id参数是必需的'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        cf = CollaborativeFiltering()

        if algorithm == 'user_based':
            movie_ids = cf.user_based_recommendations(user.id, top_n)
        elif algorithm == 'item_based':
            movie_ids = cf.item_based_recommendations(user.id, top_n)
        else:
            return Response(
                {'error': '算法参数必须是user_based或item_based'},
                status=status.HTTP_400_BAD_REQUEST
            )

        movies = Movie.objects.filter(id__in=movie_ids)
        serializer = MovieSerializer(movies, many=True)

        return Response({
            'user_id': user.id,
            'username': user.username,
            'algorithm': algorithm,
            'recommendations': serializer.data
        })


class TopMoviesView(APIView):
    """热门电影API"""

    def get(self, request):
        top_n = int(request.query_params.get('top_n', 10))

        cf = CollaborativeFiltering()
        movie_ids = cf.get_top_movies(top_n)

        movies = Movie.objects.filter(id__in=movie_ids)
        serializer = MovieSerializer(movies, many=True)

        return Response({
            'top_movies': serializer.data
        })


class SimilarMoviesView(APIView):
    """相似电影API"""

    def get(self, request, movie_id):
        top_n = int(request.query_params.get('top_n', 5))

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {'error': '电影不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        cf = CollaborativeFiltering()
        cf.calculate_movie_similarity()

        if cf.movie_similarity is None:
            return Response(
                {'error': '无法计算电影相似度'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if movie.id not in cf.movie_ids:
            return Response(
                {'error': '电影不在矩阵中'},
                status=status.HTTP_404_NOT_FOUND
            )

        movie_idx = cf.movie_ids.index(movie.id)
        similarities = cf.movie_similarity[movie_idx]

        similar_movies = []
        for idx, similarity in enumerate(similarities):
            if idx != movie_idx and similarity > 0:
                similar_movies.append((cf.movie_ids[idx], similarity))

        similar_movies.sort(key=lambda x: x[1], reverse=True)
        top_movie_ids = [mid for mid, _ in similar_movies[:top_n]]

        movies = Movie.objects.filter(id__in=top_movie_ids)
        serializer = MovieSerializer(movies, many=True)

        return Response({
            'movie_id': movie.id,
            'movie_title': movie.title,
            'similar_movies': serializer.data
        })