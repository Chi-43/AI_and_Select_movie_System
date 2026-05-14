from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import login
from django.middleware.csrf import get_token

from .auth_serializers import UserLoginSerializer
from .serializers import UserSerializer, MovieSerializer, MovieCommentSerializer
from .models import User, Movie, MovieComment, DiscussionTopic, DiscussionPost, DiscussionReply, MovieCollection


class AdminPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class AdminLoginView(APIView):
    """
    管理员登录接口
    只有 is_staff=True 的用户才能登录管理员后台
    """
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            if not user.is_staff:
                return Response(
                    {"error": "当前账号不是管理员账号"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            token, _ = Token.objects.get_or_create(user=user)
            login(request, user)
            csrf_token = get_token(request)

            return Response(
                {
                    "message": "管理员登录成功",
                    "token": token.key,
                    "csrf_token": csrf_token,
                    "user": UserSerializer(user, context={"request": request}).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProfileView(APIView):
    """
    管理员个人信息接口
    GET: 获取管理员信息
    PUT: 修改管理员信息
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "管理员信息更新成功",
                    "admin": serializer.data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUserListView(APIView):
    """
    管理员查看用户列表
    GET: 获取所有普通用户
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_staff=False).order_by("-date_joined")
        paginator = AdminPagination()
        page = paginator.paginate_queryset(users, request)
        if page is not None:
            serializer = UserSerializer(page, many=True, context={"request": request})
            return paginator.get_paginated_response(serializer.data)
        serializer = UserSerializer(users, many=True, context={"request": request})
        return Response({"count": users.count(), "users": serializer.data})


class AdminUserDetailView(APIView):
    """
    管理员管理单个用户
    GET: 查看单个用户
    PUT: 修改用户信息
    DELETE: 删除用户
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, user_id):
        try:
            return User.objects.get(id=user_id, is_staff=False)
        except User.DoesNotExist:
            return None

    def get(self, request, user_id):
        user = self.get_object(user_id)
        if not user:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, context={"request": request})
        return Response(serializer.data)

    def put(self, request, user_id):
        user = self.get_object(user_id)
        if not user:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(
            user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "用户信息更新成功",
                    "user": serializer.data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = self.get_object(user_id)
        if not user:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({"message": "用户删除成功"}, status=status.HTTP_200_OK)


class AdminMovieListView(APIView):
    """
    管理员查看 / 新增电影
    GET: 获取所有电影
    POST: 新增电影
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        movies = Movie.objects.all().order_by("-created_at")
        paginator = AdminPagination()
        page = paginator.paginate_queryset(movies, request)
        if page is not None:
            serializer = MovieSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = MovieSerializer(movies, many=True)
        return Response({"count": movies.count(), "movies": serializer.data})

    def post(self, request):
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            movie = serializer.save()
            return Response(
                {
                    "message": "电影新增成功",
                    "movie": MovieSerializer(movie).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminMovieDetailView(APIView):
    """
    管理员管理单个电影
    GET: 查看单个电影
    PUT: 修改电影信息
    DELETE: 删除电影
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, movie_id):
        try:
            return Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return None

    def get(self, request, movie_id):
        movie = self.get_object(movie_id)
        if not movie:
            return Response({"error": "电影不存在"}, status=status.HTTP_404_NOT_FOUND)

        return Response(MovieSerializer(movie).data)

    def put(self, request, movie_id):
        movie = self.get_object(movie_id)
        if not movie:
            return Response({"error": "电影不存在"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MovieSerializer(movie, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "电影信息更新成功",
                    "movie": serializer.data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, movie_id):
        movie = self.get_object(movie_id)
        if not movie:
            return Response({"error": "电影不存在"}, status=status.HTTP_404_NOT_FOUND)

        movie.delete()
        return Response({"message": "电影删除成功"}, status=status.HTTP_200_OK)


class AdminCommentListView(APIView):
    """
    管理员查看评论列表
    GET: 获取所有评论
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        comments = MovieComment.objects.select_related("user", "movie").order_by("-created_at")
        paginator = AdminPagination()
        page = paginator.paginate_queryset(comments, request)
        if page is not None:
            serializer = MovieCommentSerializer(page, many=True, context={"request": request})
            return paginator.get_paginated_response(serializer.data)
        serializer = MovieCommentSerializer(comments, many=True, context={"request": request})
        return Response({"count": comments.count(), "comments": serializer.data})


class AdminCommentDetailView(APIView):
    """
    管理员管理单条评论
    GET: 查看单条评论
    DELETE: 删除评论
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, comment_id):
        try:
            return MovieComment.objects.select_related("user", "movie").get(id=comment_id)
        except MovieComment.DoesNotExist:
            return None

    def get(self, request, comment_id):
        comment = self.get_object(comment_id)
        if not comment:
            return Response({"error": "评论不存在"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MovieCommentSerializer(comment, context={"request": request})
        return Response(serializer.data)

    def delete(self, request, comment_id):
        comment = self.get_object(comment_id)
        if not comment:
            return Response({"error": "评论不存在"}, status=status.HTTP_404_NOT_FOUND)

        comment.delete()
        return Response({"message": "评论删除成功"}, status=status.HTTP_200_OK)


# ==================== 社区管理 ====================

class AdminTopicView(APIView):
    """管理员管理话题：增删改查"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        topics = DiscussionTopic.objects.all().order_by("-created_at")
        data = [
            {"id": t.id, "name": t.name, "description": t.description,
             "icon": t.icon, "post_count": t.post_count, "created_at": t.created_at}
            for t in topics
        ]
        return Response({"topics": data})

    def post(self, request):
        name = (request.data.get("name") or "").strip()
        if not name:
            return Response({"error": "话题名称不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        topic = DiscussionTopic.objects.create(
            name=name,
            description=(request.data.get("description") or "").strip(),
            icon=request.data.get("icon", "💬"),
            created_by=request.user,
        )
        return Response({"message": "话题创建成功", "id": topic.id}, status=status.HTTP_201_CREATED)

    def put(self, request):
        topic_id = request.data.get("topic_id")
        try:
            topic = DiscussionTopic.objects.get(id=topic_id)
        except DiscussionTopic.DoesNotExist:
            return Response({"error": "话题不存在"}, status=status.HTTP_404_NOT_FOUND)
        if request.data.get("name"):
            topic.name = request.data["name"].strip()
        if "description" in request.data:
            topic.description = request.data["description"].strip()
        if request.data.get("icon"):
            topic.icon = request.data["icon"]
        topic.save()
        return Response({"message": "话题更新成功"})

    def delete(self, request):
        topic_id = request.data.get("topic_id") or request.query_params.get("topic_id")
        DiscussionTopic.objects.filter(id=topic_id).delete()
        return Response({"message": "话题删除成功"})


class AdminPostManageView(APIView):
    """管理员管理帖子：列表和删除"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        posts = DiscussionPost.objects.select_related("created_by", "topic").order_by("-created_at")
        data = [
            {"id": p.id, "title": p.title, "content": p.content[:150],
             "created_by": p.created_by.username, "topic": p.topic.name,
             "view_count": p.view_count, "reply_count": p.reply_count,
             "like_count": p.like_count, "created_at": p.created_at}
            for p in posts
        ]
        return Response({"posts": data})

    def delete(self, request):
        post_id = request.data.get("post_id") or request.query_params.get("post_id")
        DiscussionPost.objects.filter(id=post_id).delete()
        return Response({"message": "帖子删除成功"})


class AdminReplyManageView(APIView):
    """管理员管理回复：列表和删除"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        replies = DiscussionReply.objects.select_related("created_by", "post").order_by("-created_at")
        data = [
            {"id": r.id, "content": r.content, "created_by": r.created_by.username,
             "post_title": r.post.title, "created_at": r.created_at}
            for r in replies
        ]
        return Response({"replies": data})

    def delete(self, request):
        reply_id = request.data.get("reply_id") or request.query_params.get("reply_id")
        DiscussionReply.objects.filter(id=reply_id).delete()
        return Response({"message": "回复删除成功"})


class AdminCollectionView(APIView):
    """管理员管理片单：列表和删除"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        collections = MovieCollection.objects.select_related("created_by").order_by("-created_at")
        data = [
            {
                "id": c.id, "title": c.title, "description": c.description[:80],
                "created_by": c.created_by.username,
                "is_public": c.is_public,
                "movie_count": c.movie_count, "like_count": c.like_count,
                "created_at": c.created_at,
            }
            for c in collections
        ]
        return Response({"collections": data})

    def delete(self, request):
        coll_id = request.data.get("collection_id") or request.query_params.get("collection_id")
        MovieCollection.objects.filter(id=coll_id).delete()
        return Response({"message": "片单删除成功"})