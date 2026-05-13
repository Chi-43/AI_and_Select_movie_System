from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination

from .models import (
    DiscussionTopic, DiscussionPost, DiscussionReply, PostLike,
    User,
)
from .serializers import UserSerializer

POST_PAGE_SIZE = 15
REPLY_PAGE_SIZE = 20


class CommunityPagination(PageNumberPagination):
    page_size = POST_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = 50


# ==================== 话题 ====================

class TopicListView(APIView):
    """话题列表 / 管理员创建话题"""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        topics = DiscussionTopic.objects.all().order_by("-created_at")
        data = [
            {
                "id": t.id, "name": t.name, "description": t.description,
                "icon": t.icon, "post_count": t.post_count,
                "created_at": t.created_at,
            }
            for t in topics
        ]
        return Response({"topics": data})

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({"error": "需要管理员权限"}, status=status.HTTP_403_FORBIDDEN)
        topic = DiscussionTopic.objects.create(
            name=request.data.get("name", "").strip(),
            description=request.data.get("description", "").strip(),
            icon=request.data.get("icon", "💬"),
            created_by=request.user,
        )
        return Response({
            "id": topic.id, "name": topic.name, "description": topic.description,
            "icon": topic.icon, "post_count": 0,
        }, status=status.HTTP_201_CREATED)


# ==================== 帖子 ====================

class PostListView(APIView):
    """帖子列表 / 发帖"""
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        topic_id = request.query_params.get("topic_id")
        queryset = DiscussionPost.objects.filter(topic_id=topic_id).select_related("created_by").order_by("-created_at")
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)

        paginator = CommunityPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            data = [
                {
                    "id": p.id, "title": p.title, "content": p.content[:200],
                    "created_by": UserSerializer(p.created_by).data,
                    "view_count": p.view_count, "reply_count": p.reply_count,
                    "like_count": p.like_count, "created_at": p.created_at,
                    "topic_id": p.topic_id,
                }
                for p in page
            ]
            return paginator.get_paginated_response(data)

        data = [
            {
                "id": p.id, "title": p.title, "content": p.content[:200],
                "created_by": UserSerializer(p.created_by).data,
                "view_count": p.view_count, "reply_count": p.reply_count,
                "like_count": p.like_count, "created_at": p.created_at,
                "topic_id": p.topic_id,
            }
            for p in queryset
        ]
        return Response({"results": data, "count": queryset.count()})

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "请先登录"}, status=status.HTTP_401_UNAUTHORIZED)
        title = (request.data.get("title") or "").strip()
        content = (request.data.get("content") or "").strip()
        topic_id = request.data.get("topic_id")
        if not title or not content or not topic_id:
            return Response({"error": "标题、内容和话题不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            topic = DiscussionTopic.objects.get(id=topic_id)
        except DiscussionTopic.DoesNotExist:
            return Response({"error": "话题不存在"}, status=status.HTTP_404_NOT_FOUND)
        post = DiscussionPost.objects.create(
            title=title, content=content, topic=topic, created_by=request.user,
        )
        topic.post_count = topic.posts.count()
        topic.save()
        return Response({
            "id": post.id, "title": post.title, "content": post.content,
            "created_by": UserSerializer(post.created_by).data,
            "view_count": 0, "reply_count": 0, "like_count": 0,
            "created_at": post.created_at, "topic_id": post.topic_id,
        }, status=status.HTTP_201_CREATED)


class PostDetailView(APIView):
    """帖子详情 / 编辑 / 删除"""
    authentication_classes = [TokenAuthentication]

    def get(self, request, post_id):
        try:
            post = DiscussionPost.objects.select_related("created_by", "topic").get(id=post_id)
        except DiscussionPost.DoesNotExist:
            return Response({"error": "帖子不存在"}, status=status.HTTP_404_NOT_FOUND)
        post.view_count += 1
        post.save(update_fields=["view_count"])

        replies = DiscussionReply.objects.filter(post=post).select_related("created_by", "parent").order_by("created_at")
        reply_data = []
        for r in replies:
            reply_data.append({
                "id": r.id, "content": r.content,
                "created_by": UserSerializer(r.created_by).data,
                "parent_id": r.parent_id,
                "created_at": r.created_at,
            })

        liked = False
        if request.user.is_authenticated:
            liked = PostLike.objects.filter(post=post, user=request.user).exists()

        return Response({
            "id": post.id, "title": post.title, "content": post.content,
            "created_by": UserSerializer(post.created_by).data,
            "topic": {"id": post.topic.id, "name": post.topic.name, "icon": post.topic.icon},
            "view_count": post.view_count, "reply_count": post.reply_count,
            "like_count": post.like_count, "liked": liked,
            "created_at": post.created_at, "updated_at": post.updated_at,
            "replies": reply_data,
        })

    def delete(self, request, post_id):
        try:
            post = DiscussionPost.objects.get(id=post_id, created_by=request.user)
        except DiscussionPost.DoesNotExist:
            return Response({"error": "帖子不存在或无权限"}, status=status.HTTP_404_NOT_FOUND)
        topic = post.topic
        post.delete()
        topic.post_count = topic.posts.count()
        topic.save()
        return Response({"message": "删除成功"})


# ==================== 回复 ====================

class ReplyView(APIView):
    """发表 / 删除回复"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        post_id = request.data.get("post_id")
        content = (request.data.get("content") or "").strip()
        parent_id = request.data.get("parent_id")
        if not post_id or not content:
            return Response({"error": "参数不完整"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = DiscussionPost.objects.get(id=post_id)
        except DiscussionPost.DoesNotExist:
            return Response({"error": "帖子不存在"}, status=status.HTTP_404_NOT_FOUND)

        parent = None
        if parent_id:
            try:
                parent = DiscussionReply.objects.get(id=parent_id, post=post)
            except DiscussionReply.DoesNotExist:
                return Response({"error": "父回复不存在"}, status=status.HTTP_404_NOT_FOUND)

        reply = DiscussionReply.objects.create(
            post=post, created_by=request.user, parent=parent, content=content,
        )
        post.reply_count = post.replies.count()
        post.save()
        return Response({
            "id": reply.id, "content": reply.content,
            "created_by": UserSerializer(reply.created_by).data,
            "parent_id": reply.parent_id, "created_at": reply.created_at,
        }, status=status.HTTP_201_CREATED)

    def delete(self, request):
        reply_id = request.data.get("reply_id") or request.query_params.get("reply_id")
        try:
            reply = DiscussionReply.objects.get(id=reply_id, created_by=request.user)
        except DiscussionReply.DoesNotExist:
            return Response({"error": "回复不存在或无权限"}, status=status.HTTP_404_NOT_FOUND)
        post = reply.post
        reply.delete()
        post.reply_count = post.replies.count()
        post.save()
        return Response({"message": "删除成功"})


# ==================== 点赞 ====================

class PostLikeView(APIView):
    """点赞 / 取消点赞"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        post_id = request.data.get("post_id")
        if not post_id:
            return Response({"error": "post_id 必填"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = DiscussionPost.objects.get(id=post_id)
        except DiscussionPost.DoesNotExist:
            return Response({"error": "帖子不存在"}, status=status.HTTP_404_NOT_FOUND)

        _, created = PostLike.objects.get_or_create(post=post, user=request.user)
        if created:
            post.like_count = post.likes.count()
            post.save()
            return Response({"message": "点赞成功", "like_count": post.like_count, "liked": True})
        return Response({"message": "已点赞过了", "like_count": post.like_count, "liked": True})

    def delete(self, request):
        post_id = request.data.get("post_id") or request.query_params.get("post_id")
        deleted, _ = PostLike.objects.filter(post_id=post_id, user=request.user).delete()
        if deleted:
            post = DiscussionPost.objects.get(id=post_id)
            post.like_count = post.likes.count()
            post.save()
            return Response({"message": "取消点赞", "like_count": post.like_count, "liked": False})
        return Response({"error": "未点赞过"}, status=status.HTTP_404_NOT_FOUND)
