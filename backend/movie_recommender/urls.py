from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from recommendation.views import MovieViewSet, UserViewSet, RatingViewSet, RecommendationView, TopMoviesView, SimilarMoviesView
from recommendation.auth_views import (
    UserRegistrationView, UserLoginView, UserLogoutView,
    UserProfileView, ChangePasswordView, CheckAuthView, TokenLoginView
)

# 创建路由器并注册视图集
router = routers.DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'users', UserViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),
    
    # 认证相关路由
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', UserLoginView.as_view(), name='login'),
    path('api/auth/logout/', UserLogoutView.as_view(), name='logout'),
    path('api/auth/profile/', UserProfileView.as_view(), name='profile'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/auth/check/', CheckAuthView.as_view(), name='check_auth'),
    path('api/auth/token-login/', TokenLoginView.as_view(), name='token_login'),
    
    # 推荐相关路由
    path('api/recommendations/', RecommendationView.as_view(), name='recommendations'),
    path('api/top-movies/', TopMoviesView.as_view(), name='top_movies'),
    path('api/similar-movies/<int:movie_id>/', SimilarMoviesView.as_view(), name='similar_movies'),
]
