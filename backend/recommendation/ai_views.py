from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse
from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
import requests
import json
import os
import re
from django.conf import settings

from .models import Movie, User, Rating, UserProfile
from .serializers import MovieSerializer
from .collaborative_filtering import CollaborativeFiltering


def get_deepseek_api_key():
    """
    优先从环境变量取，其次从 Django settings 取
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        api_key = getattr(settings, "DEEPSEEK_API_KEY", None)
    return api_key


def call_deepseek_chat(
    system_prompt: str,
    user_prompt: str,
    model: str = "deepseek-chat",
    temperature: float = 0.3,
):
    """
    通用 DeepSeek 调用函数（非流式）
    """
    api_key = get_deepseek_api_key()
    if not api_key:
        raise ValueError("DeepSeek API密钥未配置")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": 500,
        "stream": False,
    }

    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise ValueError(f"DeepSeek 调用失败: {detail}")

    result = response.json()
    return result["choices"][0]["message"]["content"]


def extract_json_from_text(text: str):
    """
    从 LLM 返回文本中提取 JSON
    支持:
    - 纯 JSON
    - ```json ... ```
    - 普通文本中夹杂 JSON
    """
    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except Exception:
            pass

    brace = re.search(r"(\{.*\})", text, re.S)
    if brace:
        try:
            return json.loads(brace.group(1))
        except Exception:
            pass

    raise ValueError("无法从模型输出中解析 JSON")


def parse_recommendation_intent(query: str):
    """
    用 DeepSeek 把自然语言推荐需求解析为结构化条件
    """
    system_prompt = """
你是电影推荐系统中的“意图解析器”。
你的任务是把用户的自然语言电影需求解析成 JSON。
只能返回 JSON，不要返回解释，不要返回 Markdown。

JSON字段定义：
{
  "genres": ["类型1", "类型2"],
  "countries": ["国家1", "国家2"],
  "year_min": 1900,
  "year_max": 2026,
  "min_rating": 0,
  "keywords": ["关键词1", "关键词2"],
  "similar_movie": "",
  "mood": "",
  "scene": ""
}

规则：
1. 没有的信息用空数组、空字符串或 null
2. 不要编造电影名
3. 如果用户表达的是“像某部电影一样”，把电影名放到 similar_movie
4. scene / mood 这类场景语义可以保留，但不要乱放到 genres
5. 只输出 JSON
"""

    user_prompt = f"用户输入：{query}"

    raw = call_deepseek_chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model="deepseek-chat",
        temperature=0.1,
    )

    parsed = extract_json_from_text(raw)

    return {
        "genres": parsed.get("genres", []) or [],
        "countries": parsed.get("countries", []) or [],
        "year_min": parsed.get("year_min"),
        "year_max": parsed.get("year_max"),
        "min_rating": parsed.get("min_rating"),
        "keywords": parsed.get("keywords", []) or [],
        "similar_movie": parsed.get("similar_movie", "") or "",
        "mood": parsed.get("mood", "") or "",
        "scene": parsed.get("scene", "") or "",
    }


def generate_llm_recommend_reason(user, movie, algorithm: str, context=None):
    """
    用 DeepSeek 生成推荐理由
    """
    system_prompt = """
你是一个电影推荐系统中的“推荐理由生成器”。
你的任务是根据给定的用户画像、推荐电影信息和推荐依据，生成一段简洁、自然、可信的中文推荐理由。

要求：
1. 只依据提供的信息生成，不要编造
2. 语气自然、简洁
3. 控制在 40~80 字
4. 不要使用“根据系统分析”这种生硬措辞
5. 输出纯文本，不要加标题，不要加编号
"""

    profile = getattr(user, "profile", None)
    profile_summary = ""
    if profile and getattr(profile, "profile_summary", ""):
        profile_summary = profile.profile_summary

    high_rating_titles = []
    if context and context.get("user_high_rating_movies"):
        high_rating_titles = [
            item["title"] for item in context["user_high_rating_movies"][:3]
        ]

    similar_users = context.get("similar_users", []) if context else []

    user_prompt = f"""
用户信息：
- 用户名：{getattr(user, 'username', '访客')}
- 用户画像：{profile_summary}

推荐电影信息：
- 电影名称：{movie.title}
- 类型：{movie.genre}
- 年份：{movie.year}
- 国家/地区：{movie.country}
- 豆瓣评分：{movie.rating}
- 简介：{movie.description}

推荐依据：
- 推荐算法：{algorithm}
- 用户高评分电影：{high_rating_titles}
- 相似用户信息：{similar_users}

请生成一句推荐理由。
"""

    return call_deepseek_chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model="deepseek-chat",
        temperature=0.3,
    )


def generate_llm_recommend_reply(query: str, movies_data: list):
    """
    给推荐结果生成一句总的自然语言回复
    """
    system_prompt = """
你是电影推荐系统中的回复生成器。
你的任务是根据用户需求和推荐结果，生成一段简短中文回复。

要求：
1. 简洁自然
2. 不超过 80 字
3. 语气友好
4. 不要重复电影详细信息
"""

    titles = [item["movie"]["title"] for item in movies_data[:5]]

    user_prompt = f"""
用户需求：{query}
推荐电影：{titles}

请生成一句回复，告诉用户你已经为他筛选了几部合适的电影。
"""

    return call_deepseek_chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model="deepseek-chat",
        temperature=0.3,
    )


def filter_movies_by_intent(queryset, intent: dict):
    """
    根据解析后的意图过滤 Movie queryset
    这里只做硬过滤：
    - genres
    - countries
    - year_min
    - year_max
    - min_rating

    不再把 keywords / mood / scene 当硬过滤条件。
    """
    genres = intent.get("genres", [])
    countries = intent.get("countries", [])
    year_min = intent.get("year_min")
    year_max = intent.get("year_max")
    min_rating = intent.get("min_rating")
    similar_movie = intent.get("similar_movie", "")

    # 类型过滤：至少命中一个
    if genres:
        genre_q = Q()
        for genre in genres[:3]:
            genre_q |= Q(genre__icontains=genre)
        queryset = queryset.filter(genre_q)

    # 国家过滤
    if countries:
        country_q = Q()
        for country in countries[:3]:
            country_q |= Q(country__icontains=country)
        queryset = queryset.filter(country_q)

    # 年份过滤
    if year_min:
        queryset = queryset.filter(year__gte=year_min)
    if year_max:
        queryset = queryset.filter(year__lte=year_max)

    # 评分过滤
    if min_rating:
        queryset = queryset.filter(rating__gte=min_rating)

    # “像某部电影一样”时，用那部电影的类型做补充过滤
    if similar_movie:
        base_movie = Movie.objects.filter(title__icontains=similar_movie).first()
        if base_movie and base_movie.genre:
            genre_q = Q()
            for genre in re.split(r"[ /、,，]+", base_movie.genre):
                genre = genre.strip()
                if genre:
                    genre_q |= Q(genre__icontains=genre)
            if genre_q:
                queryset = queryset.filter(genre_q)

    return queryset


def build_reason_context_from_profile(user, movie, algorithm):
    """
    给自然语言推荐结果构造上下文
    """
    profile = getattr(user, "profile", None) if user else None

    return {
        "user_high_rating_movies": [],
        "similar_users": [],
        "profile_summary": profile.profile_summary if profile and profile.profile_summary else "",
        "algorithm": algorithm,
        "movie_title": movie.title,
        "movie_genre": movie.genre,
        "movie_year": movie.year,
        "movie_country": movie.country,
        "movie_rating": movie.rating,
    }


class AIChatView(APIView):
    """AI对话视图（支持流式输出）"""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_message = request.data.get("message", "")
        model = request.data.get("model", "deepseek-chat")
        temperature = float(request.data.get("temperature", 0.7))
        stream = request.data.get("stream", True)

        if not user_message:
            return Response(
                {"error": "消息不能为空"},
                status=status.HTTP_400_BAD_REQUEST
            )

        api_key = get_deepseek_api_key()
        if not api_key:
            return Response(
                {"error": "DeepSeek API密钥未配置"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        system_prompt = """你是一个专业的电影推荐助手，专门帮助用户发现和了解电影。
你的知识库包含电影推荐系统中的高分电影数据、评分信息和推荐逻辑。

请遵循以下规则：
1. 回答要专业、友好、有帮助
2. 如果用户询问电影推荐，请给出自然建议
3. 如果用户询问特定电影，请提供详细信息
4. 如果用户询问电影相关问题（导演、演员、剧情等），请提供准确信息
5. 不知道的信息要诚实说明
6. 请用中文回答
"""

        if stream:
            return self._stream_response(api_key, model, system_prompt, user_message, temperature)
        else:
            return self._normal_response(api_key, model, system_prompt, user_message, temperature)

    def _normal_response(self, api_key, model, system_prompt, user_message, temperature):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": temperature,
                "max_tokens": 2000,
                "stream": False
            }

            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]

                return Response({
                    "response": ai_response,
                    "model": model,
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                })
            else:
                error_msg = f"API调用失败: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('error', {}).get('message', '未知错误')}"
                except Exception:
                    error_msg += f" - {response.text}"

                return Response(
                    {"error": error_msg},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except requests.exceptions.Timeout:
            return Response(
                {"error": "API请求超时，请稍后重试"},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {"error": "网络连接错误，请检查网络"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": f"服务器内部错误: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _stream_response(self, api_key, model, system_prompt, user_message, temperature):
        def generate():
            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }

                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "temperature": temperature,
                    "max_tokens": 2000,
                    "stream": True,
                }

                full_response = ""
                done_sent = False

                with requests.post(
                    "https://api.deepseek.com/chat/completions",
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=60,
                ) as r:

                    if r.status_code != 200:
                        error_msg = f"API调用失败: {r.status_code}"
                        try:
                            error_detail = r.json()
                            error_msg += f" - {error_detail.get('error', {}).get('message', '未知错误')}"
                        except Exception:
                            error_msg += f" - {r.text}"

                        yield f"data: {json.dumps({'error': error_msg, 'done': True}, ensure_ascii=False)}\n\n"
                        return

                    for line in r.iter_lines(decode_unicode=True):
                        if not line:
                            continue
                        if not line.startswith("data: "):
                            continue

                        data_str = line[6:].strip()

                        if data_str == "[DONE]":
                            yield f"data: {json.dumps({'done': True, 'full_response': full_response}, ensure_ascii=False)}\n\n"
                            done_sent = True
                            break

                        try:
                            data = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

                        choices = data.get("choices") or []
                        if not choices:
                            continue

                        delta = choices[0].get("delta") or {}
                        content = delta.get("content") or ""
                        if not content:
                            continue

                        full_response += content
                        yield f"data: {json.dumps({'content': content, 'full_response': full_response, 'done': False}, ensure_ascii=False)}\n\n"

                if not done_sent:
                    yield f"data: {json.dumps({'done': True, 'full_response': full_response}, ensure_ascii=False)}\n\n"

            except requests.exceptions.Timeout:
                yield f"data: {json.dumps({'error': 'API请求超时，请稍后重试', 'done': True}, ensure_ascii=False)}\n\n"
            except requests.exceptions.ConnectionError:
                yield f"data: {json.dumps({'error': '网络连接错误，请检查网络', 'done': True}, ensure_ascii=False)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': f'服务器内部错误: {str(e)}', 'done': True}, ensure_ascii=False)}\n\n"

        resp = StreamingHttpResponse(generate(), content_type="text/event-stream; charset=utf-8")
        resp["Cache-Control"] = "no-cache"
        resp["X-Accel-Buffering"] = "no"
        resp["Access-Control-Allow-Origin"] = "*"
        resp["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return resp


class NaturalLanguageRecommendationView(APIView):
    """
    自然语言推荐检索接口
    前端推荐模式直接调这个接口
    """
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        query = request.data.get("query", "").strip()
        user_id = request.data.get("user_id")
        top_n = int(request.data.get("top_n", 5))

        if not query:
            return Response(
                {"error": "query不能为空"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. 解析自然语言意图
        try:
            intent = parse_recommendation_intent(query)
        except Exception as e:
            return Response(
                {"error": f"意图解析失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        user = None
        if user_id:
            user = User.objects.filter(id=user_id).first()

        cf = CollaborativeFiltering()

        # 2. 先从数据库按硬条件筛出候选池
        base_queryset = Movie.objects.all()
        filtered_queryset = filter_movies_by_intent(base_queryset, intent)

        if filtered_queryset.exists():
            filtered_queryset = filtered_queryset.order_by("-rating")
        else:
            filtered_queryset = Movie.objects.all().order_by("-rating")

        qualified_movies = list(filtered_queryset[: top_n * 8])

        # 3. 如果用户有评分记录，优先结合协同过滤做排序
        results = []

        if user and Rating.objects.filter(user=user).exists():
            recs = cf.user_based_recommendations_with_scores(user.id, top_n * 10)
            rec_map = {item["movie_id"]: item for item in recs}

            # 先取同时满足：在候选池里 + 在 CF 结果里
            for movie in qualified_movies:
                if movie.id in rec_map:
                    results.append({
                        "movie": movie,
                        "score": float(rec_map[movie.id]["score"]),
                        "algorithm": "user_based",
                    })

            # 如果不够，再补候选池中的高分电影
            if len(results) < top_n:
                existing_ids = {item["movie"].id for item in results}
                for movie in qualified_movies:
                    if movie.id not in existing_ids:
                        results.append({
                            "movie": movie,
                            "score": float(movie.rating or 0),
                            "algorithm": "cold_start",
                        })
                        if len(results) >= top_n:
                            break

        else:
            # 4. 没有用户评分时，直接用候选池
            for movie in qualified_movies[:top_n]:
                results.append({
                    "movie": movie,
                    "score": float(movie.rating or 0),
                    "algorithm": "cold_start",
                })

        # 5. 如果还没有结果，最后兜底到高分电影
        if not results:
            fallback_movies = list(Movie.objects.all().order_by("-rating")[:top_n])
            for movie in fallback_movies:
                results.append({
                    "movie": movie,
                    "score": float(movie.rating or 0),
                    "algorithm": "top",
                })

        results = results[:top_n]

        # 6. 生成推荐理由
        recommendations = []
        for item in results:
            movie = item["movie"]

            if user and Rating.objects.filter(user=user).exists():
                context = cf.build_reason_context(user.id, movie.id, item["algorithm"])
            else:
                context = build_reason_context_from_profile(user, movie, item["algorithm"])

            temp_user = user if user else type("TempUser", (), {"username": "访客", "profile": None})()

            try:
                reason = generate_llm_recommend_reason(
                    user=temp_user,
                    movie=movie,
                    algorithm=item["algorithm"],
                    context=context,
                )
            except Exception:
                reason = f"《{movie.title}》在类型、评分和题材上与您的需求较为匹配。"

            recommendations.append({
                "movie": MovieSerializer(movie).data,
                "score": round(float(item["score"]), 4),
                "algorithm": item["algorithm"],
                "reason": reason,
            })

        # 7. 生成总回复
        try:
            reply = generate_llm_recommend_reply(query, recommendations)
        except Exception:
            reply = "我为你筛选了几部较符合你需求的电影，可以先看看这些推荐。"

        return Response({
            "query": query,
            "intent": intent,
            "reply": reply,
            "recommendations": recommendations,
        })


class MovieRecommendationView(APIView):
    """电影推荐视图（基于AI，保留旧接口）"""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        preferences = request.data.get("preferences", {})
        count = int(request.data.get("count", 5))

        recommendations = [
            {
                "title": "肖申克的救赎",
                "rating": "9.7",
                "year": "1994",
                "genre": "剧情 犯罪",
                "country": "美国",
                "description": "希望让人自由。",
                "reason": "根据您的偏好，推荐这部经典高分电影"
            },
            {
                "title": "霸王别姬",
                "rating": "9.6",
                "year": "1993",
                "genre": "剧情 爱情 同性",
                "country": "中国大陆 香港",
                "description": "风华绝代。",
                "reason": "华语电影的巅峰之作"
            },
            {
                "title": "阿甘正传",
                "rating": "9.5",
                "year": "1994",
                "genre": "剧情 爱情",
                "country": "美国",
                "description": "一部美国近现代史。",
                "reason": "温暖人心的励志故事"
            },
            {
                "title": "这个杀手不太冷",
                "rating": "9.4",
                "year": "1994",
                "genre": "剧情 动作 犯罪",
                "country": "法国 美国",
                "description": "怪蜀黍和小萝莉不得不说的故事。",
                "reason": "动作与情感的完美结合"
            },
            {
                "title": "美丽人生",
                "rating": "9.5",
                "year": "1997",
                "genre": "剧情 喜剧 爱情 战争",
                "country": "意大利",
                "description": "最美的谎言。",
                "reason": "笑中带泪的感人故事"
            }
        ]

        return Response({
            "recommendations": recommendations[:count],
            "count": len(recommendations[:count]),
            "preferences": preferences
        })


class MovieAnalysisView(APIView):
    """电影分析视图"""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        movie_title = request.data.get("movie_title", "")
        analysis_type = request.data.get("analysis_type", "剧情")

        if not movie_title:
            return Response(
                {"error": "电影名称不能为空"},
                status=status.HTTP_400_BAD_REQUEST
            )

        analysis_result = {
            "movie_title": movie_title,
            "analysis_type": analysis_type,
            "analysis": f"《{movie_title}》是一部优秀的电影作品。",
            "key_points": [
                "优秀的导演和演员表现",
                "深刻的主题和寓意",
                "精美的画面和音乐",
                "感人的故事情节"
            ],
            "rating": "9.0",
            "recommendation": "强烈推荐观看"
        }

        return Response(analysis_result)


class AIConfigView(APIView):
    """AI配置视图"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        config = {
            "available_models": ["deepseek-chat", "deepseek-coder"],
            "default_temperature": 0.7,
            "max_tokens": 2000,
            "api_status": "active" if get_deepseek_api_key() else "inactive",
            "features": ["对话", "推荐", "分析", "问答", "推荐理由生成", "自然语言推荐检索"]
        }
        return Response(config)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"error": "需要管理员权限"},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response({"message": "配置更新功能待实现"})