from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Movie, User, Rating
from .serializers import MovieSerializer, UserSerializer, RatingSerializer
from .collaborative_filtering import CollaborativeFiltering

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class RecommendationView(APIView):
    """推荐API"""
    
    def get(self, request):
        user_id = request.query_params.get('user_id')
        algorithm = request.query_params.get('algorithm', 'user_based')  # user_based 或 item_based
        top_n = int(request.query_params.get('top_n', 10))
        
        if not user_id:
            return Response({'error': 'user_id参数是必需的'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        cf = CollaborativeFiltering()
        
        if algorithm == 'user_based':
            movie_ids = cf.user_based_recommendations(user.id, top_n)
        elif algorithm == 'item_based':
            movie_ids = cf.item_based_recommendations(user.id, top_n)
        else:
            return Response({'error': '算法参数必须是user_based或item_based'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取电影详情
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
        
        # 获取电影详情
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
            return Response({'error': '电影不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        cf = CollaborativeFiltering()
        cf.calculate_movie_similarity()
        
        if cf.movie_similarity is None:
            return Response({'error': '无法计算电影相似度'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 找到电影索引
        if movie.id not in cf.movie_ids:
            return Response({'error': '电影不在矩阵中'}, status=status.HTTP_404_NOT_FOUND)
        
        movie_idx = cf.movie_ids.index(movie.id)
        
        # 获取相似电影
        similarities = cf.movie_similarity[movie_idx]
        
        # 排除自己
        similar_movies = []
        for idx, similarity in enumerate(similarities):
            if idx != movie_idx and similarity > 0:
                similar_movies.append((cf.movie_ids[idx], similarity))
        
        # 按相似度排序
        similar_movies.sort(key=lambda x: x[1], reverse=True)
        
        # 获取前top_n个相似电影
        top_movie_ids = [movie_id for movie_id, _ in similar_movies[:top_n]]
        
        # 获取电影详情
        movies = Movie.objects.filter(id__in=top_movie_ids)
        serializer = MovieSerializer(movies, many=True)
        
        return Response({
            'movie_id': movie.id,
            'movie_title': movie.title,
            'similar_movies': serializer.data
        })