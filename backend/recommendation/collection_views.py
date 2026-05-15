from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination

from .models import (
    MovieCollection, CollectionMovie, CollectionComment, CollectionCommentLike,
    CollectionLike, Movie, User,
)
from .movie_detail_cache import get_movie_detail_from_cache
from .serializers import MovieSerializer, UserSerializer


class CollectionPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 50


# ==================== 评论树构建 ====================

def _build_comment_data(comment, request):
    user_liked, user_disliked = False, False
    if request.user.is_authenticated:
        fb = CollectionCommentLike.objects.filter(comment=comment, user=request.user).first()
        if fb:
            user_liked = fb.feedback_type == "like"
            user_disliked = fb.feedback_type == "dislike"
    return {
        "id": comment.id, "content": comment.content,
        "user": UserSerializer(comment.user).data,
        "parent_id": comment.parent_id,
        "like_count": comment.like_count, "dislike_count": comment.dislike_count,
        "user_liked": user_liked, "user_disliked": user_disliked,
        "created_at": comment.created_at, "replies": [],
    }


def _build_tree(comments, request):
    result, reply_map = [], {}
    for c in comments:
        node = _build_comment_data(c, request)
        if c.parent_id is None:
            result.append(node)
        else:
            reply_map.setdefault(c.parent_id, []).append(node)
    for node in result:
        _fill_replies(node, reply_map)
    return result


def _fill_replies(node, reply_map):
    children = reply_map.get(node["id"], [])
    for child in children:
        _fill_replies(child, reply_map)
    node["replies"] = children


# ==================== 片单广场 ====================

class CollectionListView(APIView):
    """片单列表 / 创建片单"""
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        queryset = MovieCollection.objects.select_related("created_by").order_by("-created_at")
        user_id = request.query_params.get("user_id")
        if user_id and request.user.is_authenticated and str(request.user.id) == str(user_id):
            pass  # 自己的片单，公开私密都展示
        elif user_id:
            queryset = queryset.filter(is_public=True)
        elif request.user.is_authenticated:
            from django.db.models import Q
            queryset = queryset.filter(Q(is_public=True) | Q(created_by=request.user))
        else:
            queryset = queryset.filter(is_public=True)

        paginator = CollectionPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            data = [
                {
                    "id": c.id, "title": c.title, "description": c.description,
                    "cover": request.build_absolute_uri(c.cover.url) if c.cover else None,
                    "created_by": UserSerializer(c.created_by).data,
                    "is_public": c.is_public, "like_count": c.like_count,
                    "movie_count": c.movie_count, "created_at": c.created_at,
                }
                for c in page
            ]
            return paginator.get_paginated_response(data)

        data = [
            {
                "id": c.id, "title": c.title, "description": c.description,
                "cover": request.build_absolute_uri(c.cover.url) if c.cover else None,
                "created_by": UserSerializer(c.created_by).data,
                "is_public": c.is_public, "like_count": c.like_count,
                "movie_count": c.movie_count, "created_at": c.created_at,
            }
            for c in queryset
        ]
        return Response({"results": data, "count": len(data)})

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "请先登录"}, status=status.HTTP_401_UNAUTHORIZED)
        title = (request.data.get("title") or "").strip()
        if not title:
            return Response({"error": "片单标题不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        cover = request.FILES.get("cover") if hasattr(request, "FILES") else None
        coll = MovieCollection.objects.create(
            title=title,
            description=(request.data.get("description") or "").strip(),
            created_by=request.user,
            is_public=request.data.get("is_public", "true") == "true",
            cover=cover,
        )

        # 创建时顺带添加电影
        import json
        movie_ids_str = request.data.get("movie_ids", "[]")
        try:
            movie_ids = json.loads(movie_ids_str)
        except (json.JSONDecodeError, TypeError):
            movie_ids = []
        added = 0
        for mid in movie_ids:
            if Movie.objects.filter(id=mid).exists():
                CollectionMovie.objects.get_or_create(collection=coll, movie_id=mid)
                added += 1
        if added:
            coll.movie_count = added
            coll.save()

        return Response({
            "id": coll.id, "title": coll.title, "description": coll.description,
            "cover": request.build_absolute_uri(coll.cover.url) if coll.cover else None,
            "created_by": UserSerializer(coll.created_by).data,
            "is_public": coll.is_public, "like_count": 0, "movie_count": coll.movie_count,
            "created_at": coll.created_at,
        }, status=status.HTTP_201_CREATED)


class CollectionDetailView(APIView):
    """片单详情 / 编辑 / 删除"""
    authentication_classes = [TokenAuthentication]

    def get(self, request, collection_id):
        try:
            coll = MovieCollection.objects.select_related("created_by").get(id=collection_id)
        except MovieCollection.DoesNotExist:
            return Response({"error": "片单不存在"}, status=status.HTTP_404_NOT_FOUND)

        items = CollectionMovie.objects.filter(collection=coll).select_related("movie").order_by("order", "-added_at")
        movies_data = []
        for item in items:
            poster = ""
            if item.movie.douban_url:
                detail = get_movie_detail_from_cache(item.movie.douban_url)
                if detail:
                    poster = detail.get("poster", "")
                    if poster and poster.startswith("/"):
                        poster = "https:" + poster
            movies_data.append({
                "id": item.id,
                "movie": MovieSerializer(item.movie).data,
                "poster": poster,
                "note": item.note,
                "order": item.order,
                "added_at": item.added_at,
            })

        comment_list = list(
            CollectionComment.objects
            .filter(collection=coll)
            .select_related("user")
            .order_by("-like_count", "-created_at")
        )
        comments_data = _build_tree(comment_list, request)

        user_liked = False
        user_disliked = False
        if request.user.is_authenticated:
            fb = CollectionLike.objects.filter(collection=coll, user=request.user).first()
            if fb:
                user_liked = fb.feedback_type == "like"
                user_disliked = fb.feedback_type == "dislike"

        dislike_count = CollectionLike.objects.filter(collection=coll, feedback_type="dislike").count()

        return Response({
            "id": coll.id, "title": coll.title, "description": coll.description,
            "cover": request.build_absolute_uri(coll.cover.url) if coll.cover else None,
            "created_by": UserSerializer(coll.created_by).data,
            "is_public": coll.is_public, "like_count": coll.like_count,
            "dislike_count": dislike_count, "user_liked": user_liked, "user_disliked": user_disliked,
            "movie_count": coll.movie_count, "created_at": coll.created_at,
            "movies": movies_data,
            "comments": comments_data,
        })

    def put(self, request, collection_id):
        try:
            coll = MovieCollection.objects.get(id=collection_id, created_by=request.user)
        except MovieCollection.DoesNotExist:
            return Response({"error": "片单不存在或无权限"}, status=status.HTTP_404_NOT_FOUND)
        if request.data.get("title"):
            coll.title = request.data["title"].strip()
        if "description" in request.data:
            coll.description = request.data["description"].strip()
        if "is_public" in request.data:
            coll.is_public = request.data["is_public"] in [True, "true", "True", 1]
        if hasattr(request, "FILES") and request.FILES.get("cover"):
            coll.cover = request.FILES["cover"]
        coll.save()
        return Response({"message": "更新成功"})

    def delete(self, request, collection_id):
        try:
            coll = MovieCollection.objects.get(id=collection_id, created_by=request.user)
        except MovieCollection.DoesNotExist:
            return Response({"error": "片单不存在或无权限"}, status=status.HTTP_404_NOT_FOUND)
        coll.delete()
        return Response({"message": "删除成功"})


class CollectionMovieView(APIView):
    """片单中添加/移除电影"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        collection_id = request.data.get("collection_id")
        movie_id = request.data.get("movie_id")
        note = (request.data.get("note") or "").strip()
        if not collection_id or not movie_id:
            return Response({"error": "参数不完整"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            coll = MovieCollection.objects.get(id=collection_id, created_by=request.user)
        except MovieCollection.DoesNotExist:
            return Response({"error": "片单不存在或无权限"}, status=status.HTTP_404_NOT_FOUND)
        try:
            Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({"error": "电影不存在"}, status=status.HTTP_404_NOT_FOUND)

        _, created = CollectionMovie.objects.get_or_create(
            collection=coll, movie_id=movie_id,
            defaults={"note": note},
        )
        if not created and note:
            CollectionMovie.objects.filter(collection=coll, movie_id=movie_id).update(note=note)

        coll.movie_count = coll.movies.count()
        coll.save()
        return Response({"message": "已添加到片单" if created else "已在片单中"}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request):
        collection_id = request.data.get("collection_id") or request.query_params.get("collection_id")
        movie_id = request.data.get("movie_id") or request.query_params.get("movie_id")
        deleted, _ = CollectionMovie.objects.filter(collection_id=collection_id, collection__created_by=request.user, movie_id=movie_id).delete()
        if deleted:
            coll = MovieCollection.objects.get(id=collection_id)
            coll.movie_count = coll.movies.count()
            coll.save()
            return Response({"message": "已移除"})
        return Response({"error": "未找到"}, status=status.HTTP_404_NOT_FOUND)


class CollectionCommentView(APIView):
    """片单评论：列表（含二级回复+按赞排序）/ 发表评论（支持回复）"""
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        collection_id = request.query_params.get("collection_id")
        all_comments = list(
            CollectionComment.objects
            .filter(collection_id=collection_id)
            .select_related("user")
            .order_by("-like_count", "-created_at")
        )
        data = _build_tree(all_comments, request)
        return Response({"comments": data})

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "请先登录"}, status=status.HTTP_401_UNAUTHORIZED)
        collection_id = request.data.get("collection_id")
        content = (request.data.get("content") or "").strip()
        parent_id = request.data.get("parent_id")
        if not collection_id or not content:
            return Response({"error": "参数不完整"}, status=status.HTTP_400_BAD_REQUEST)

        parent = None
        if parent_id:
            try:
                parent = CollectionComment.objects.get(id=parent_id, collection_id=collection_id)
            except CollectionComment.DoesNotExist:
                return Response({"error": "父评论不存在"}, status=status.HTTP_404_NOT_FOUND)

        c = CollectionComment.objects.create(
            collection_id=collection_id, user=request.user, parent=parent, content=content,
        )
        return Response({
            "id": c.id, "content": c.content,
            "user": UserSerializer(c.user).data,
            "parent_id": c.parent_id,
            "like_count": 0, "dislike_count": 0,
            "user_liked": False, "user_disliked": False,
            "created_at": c.created_at,
        }, status=status.HTTP_201_CREATED)


class CollectionCommentLikeView(APIView):
    """片单评论点赞 / 拉踩"""
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "请先登录"}, status=status.HTTP_401_UNAUTHORIZED)
        comment_id = request.data.get("comment_id")
        fb_type = request.data.get("feedback_type", "like")
        if not comment_id or fb_type not in ["like", "dislike"]:
            return Response({"error": "参数无效"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            comment = CollectionComment.objects.get(id=comment_id)
        except CollectionComment.DoesNotExist:
            return Response({"error": "评论不存在"}, status=status.HTTP_404_NOT_FOUND)

        fb, created = CollectionCommentLike.objects.update_or_create(
            comment=comment, user=request.user,
            defaults={"feedback_type": fb_type},
        )
        comment.like_count = CollectionCommentLike.objects.filter(comment=comment, feedback_type="like").count()
        comment.dislike_count = CollectionCommentLike.objects.filter(comment=comment, feedback_type="dislike").count()
        comment.save(update_fields=["like_count", "dislike_count"])
        return Response({
            "message": "已反馈",
            "like_count": comment.like_count,
            "dislike_count": comment.dislike_count,
        })

    def delete(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "请先登录"}, status=status.HTTP_401_UNAUTHORIZED)
        comment_id = request.data.get("comment_id") or request.query_params.get("comment_id")
        deleted, _ = CollectionCommentLike.objects.filter(comment_id=comment_id, user=request.user).delete()
        if deleted:
            comment = CollectionComment.objects.get(id=comment_id)
            comment.like_count = CollectionCommentLike.objects.filter(comment=comment, feedback_type="like").count()
            comment.dislike_count = CollectionCommentLike.objects.filter(comment=comment, feedback_type="dislike").count()
            comment.save(update_fields=["like_count", "dislike_count"])
            return Response({"message": "已取消", "like_count": comment.like_count, "dislike_count": comment.dislike_count})
        return Response({"error": "未找到反馈"}, status=status.HTTP_404_NOT_FOUND)


class CollectionLikeView(APIView):
    """片单点赞 / 拉踩"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        collection_id = request.data.get("collection_id")
        feedback_type = request.data.get("feedback_type", "like")
        if not collection_id or feedback_type not in ["like", "dislike"]:
            return Response({"error": "参数无效"}, status=status.HTTP_400_BAD_REQUEST)
        fb, created = CollectionLike.objects.update_or_create(
            collection_id=collection_id, user=request.user,
            defaults={"feedback_type": feedback_type},
        )
        coll = MovieCollection.objects.get(id=collection_id)
        coll.like_count = CollectionLike.objects.filter(collection=coll, feedback_type="like").count()
        coll.save()
        return Response({"message": "已反馈", "like_count": coll.like_count})

    def delete(self, request):
        collection_id = request.data.get("collection_id") or request.query_params.get("collection_id")
        CollectionLike.objects.filter(collection_id=collection_id, user=request.user).delete()
        coll = MovieCollection.objects.get(id=collection_id)
        coll.like_count = CollectionLike.objects.filter(collection=coll, feedback_type="like").count()
        coll.save()
        return Response({"message": "已取消", "like_count": coll.like_count})
