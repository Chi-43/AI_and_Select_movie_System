from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse
import requests
import json
import os
import re
from django.conf import settings

class AIChatView(APIView):
    """AI对话视图（支持流式输出）"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        处理AI对话请求（流式输出）
        请求参数:
        - message: 用户消息
        - model: AI模型 (deepseek-chat, deepseek-coder)
        - temperature: 温度参数 (0.1-1.0)
        - stream: 是否启用流式输出 (默认True)
        """
        # 获取请求参数
        user_message = request.data.get('message', '')
        model = request.data.get('model', 'deepseek-chat')
        temperature = float(request.data.get('temperature', 0.7))
        stream = request.data.get('stream', True)
        
        if not user_message:
            return Response(
                {'error': '消息不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 从环境变量获取DeepSeek API密钥
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            # 尝试从配置文件获取
            try:
                from django.conf import settings
                api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
            except:
                api_key = None
        
        if not api_key:
            return Response(
                {'error': 'DeepSeek API密钥未配置'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 构建系统提示词（针对电影推荐优化）
        system_prompt = """你是一个专业的电影推荐助手，专门帮助用户发现和了解电影。
        你的知识库包含豆瓣电影TOP250的数据，包括电影名称、评分、年份、国家、类型和一句话评价。
        
        请遵循以下规则：
        1. 回答要专业、友好、有帮助
        2. 如果用户询问电影推荐，请根据他们的偏好提供个性化建议
        3. 如果用户询问特定电影，请提供详细信息
        4. 如果用户询问电影相关的问题（导演、演员、剧情等），请提供准确信息
        5. 如果不知道某个信息，请诚实说明
        6. 回答要简洁明了，但信息要完整
        
        电影数据库信息：
        - 包含250部高分电影
        - 涵盖多种类型：剧情、喜剧、爱情、科幻、动作、悬疑、动画等
        - 评分范围：8.0-9.7分
        - 年份范围：1931年至今
        
        请用中文回答，保持专业和友好的语气。"""
        
        # 如果启用流式输出
        if stream:
            return self._stream_response(api_key, model, system_prompt, user_message, temperature)
        else:
            return self._normal_response(api_key, model, system_prompt, user_message, temperature)
    
    def _normal_response(self, api_key, model, system_prompt, user_message, temperature):
        """普通响应模式"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_message}
                ],
                'temperature': temperature,
                'max_tokens': 2000,
                'stream': False
            }
            
            response = requests.post(
                'https://api.deepseek.com/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                return Response({
                    'response': ai_response,
                    'model': model,
                    'tokens_used': result.get('usage', {}).get('total_tokens', 0)
                })
            else:
                error_msg = f"API调用失败: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('error', {}).get('message', '未知错误')}"
                except:
                    error_msg += f" - {response.text}"
                
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except requests.exceptions.Timeout:
            return Response(
                {'error': 'API请求超时，请稍后重试'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {'error': '网络连接错误，请检查网络'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': f'服务器内部错误: {str(e)}'},
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

                    # ✅ 关键：iter_lines 必须在 with 块内
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

                # ✅ 兜底：如果没收到 DONE，也发一次 done
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

        # ✅ CORS（开发环境先用 *）
        resp["Access-Control-Allow-Origin"] = "*"
        resp["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp["Access-Control-Allow-Methods"] = "POST, OPTIONS"

        return resp

class MovieRecommendationView(APIView):
    """电影推荐视图（基于AI）"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        基于用户偏好生成电影推荐
        请求参数:
        - preferences: 用户偏好（类型、年份、国家等）
        - count: 推荐数量(默认5)
        """
        preferences = request.data.get('preferences', {})
        count = int(request.data.get('count', 5))
        
        # 这里可以添加基于用户偏好的推荐逻辑
        # 暂时返回一个简单的推荐列表
        
        recommendations = [
            {
                'title': '肖申克的救赎',
                'rating': '9.7',
                'year': '1994',
                'genre': '剧情 犯罪',
                'country': '美国',
                'description': '希望让人自由。',
                'reason': '根据您的偏好，推荐这部经典高分电影'
            },
            {
                'title': '霸王别姬',
                'rating': '9.6',
                'year': '1993',
                'genre': '剧情 爱情 同性',
                'country': '中国大陆 香港',
                'description': '风华绝代。',
                'reason': '华语电影的巅峰之作'
            },
            {
                'title': '阿甘正传',
                'rating': '9.5',
                'year': '1994',
                'genre': '剧情 爱情',
                'country': '美国',
                'description': '一部美国近现代史。',
                'reason': '温暖人心的励志故事'
            },
            {
                'title': '这个杀手不太冷',
                'rating': '9.4',
                'year': '1994',
                'genre': '剧情 动作 犯罪',
                'country': '法国 美国',
                'description': '怪蜀黍和小萝莉不得不说的故事。',
                'reason': '动作与情感的完美结合'
            },
            {
                'title': '美丽人生',
                'rating': '9.5',
                'year': '1997',
                'genre': '剧情 喜剧 爱情 战争',
                'country': '意大利',
                'description': '最美的谎言。',
                'reason': '笑中带泪的感人故事'
            }
        ]
        
        return Response({
            'recommendations': recommendations[:count],
            'count': len(recommendations[:count]),
            'preferences': preferences
        })

class MovieAnalysisView(APIView):
    """电影分析视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        分析电影信息
        请求参数:
        - movie_title: 电影名称
        - analysis_type: 分析类型（剧情、角色、主题等）
        """
        movie_title = request.data.get('movie_title', '')
        analysis_type = request.data.get('analysis_type', '剧情')
        
        if not movie_title:
            return Response(
                {'error': '电影名称不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 这里可以添加电影分析逻辑
        # 暂时返回一个示例分析
        
        analysis_result = {
            'movie_title': movie_title,
            'analysis_type': analysis_type,
            'analysis': f"《{movie_title}》是一部优秀的电影作品。",
            'key_points': [
                '优秀的导演和演员表现',
                '深刻的主题和寓意',
                '精美的画面和音乐',
                '感人的故事情节'
            ],
            'rating': '9.0',
            'recommendation': '强烈推荐观看'
        }
        
        return Response(analysis_result)

class AIConfigView(APIView):
    """AI配置视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取AI配置信息"""
        config = {
            'available_models': ['deepseek-chat', 'deepseek-coder'],
            'default_temperature': 0.7,
            'max_tokens': 2000,
            'api_status': 'active' if os.environ.get('DEEPSEEK_API_KEY') else 'inactive',
            'features': ['对话', '推荐', '分析', '问答']
        }
        return Response(config)
    
    def post(self, request):
        """更新AI配置需要管理员权限"""
        if not request.user.is_staff:
            return Response(
                {'error': '需要管理员权限'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 这里可以添加配置更新逻辑
        return Response({'message': '配置更新功能待实现'})