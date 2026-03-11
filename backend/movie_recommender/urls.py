from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from recommendation.views import (
    MovieViewSet, UserViewSet, RatingViewSet, VideoPlatformViewSet,
    RecommendationView, TopMoviesView, SimilarMoviesView,
    VideoPlatformLinksView, MovieDetailView
)
from recommendation.auth_views import (
    UserRegistrationView, UserLoginView, UserLogoutView,
    UserProfileView, ChangePasswordView, CheckAuthView, TokenLoginView
)
from recommendation.ai_views import AIChatView, MovieRecommendationView, MovieAnalysisView, AIConfigView

# 创建路由器并注册视图集
router = routers.DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'users', UserViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'video-platforms', VideoPlatformViewSet)

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
    
    # 视频平台链接相关路由
    path('api/video-platform-links/', VideoPlatformLinksView.as_view(), name='video_platform_links'),
    path('api/movie-detail/', MovieDetailView.as_view(), name='movie_detail'),
    # AI相关路由
    path('api/ai/chat/', AIChatView.as_view(), name='ai_chat'),
    path('api/ai/recommendations/', MovieRecommendationView.as_view(), name='ai_recommendations'),
    path('api/ai/analysis/', MovieAnalysisView.as_view(), name='ai_analysis'),
    path('api/ai/config/', AIConfigView.as_view(), name='ai_config'),
]

# 在开发环境中提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)