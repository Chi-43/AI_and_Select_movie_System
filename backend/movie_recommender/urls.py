from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from recommendation.views import (
    MovieViewSet,
    UserViewSet,
    RatingViewSet,
    VideoPlatformViewSet,
    RecommendationView,
    TopMoviesView,
    SimilarMoviesView,
    VideoPlatformLinksView,
    MovieDetailView,
    OnboardingPreferenceView,
    UserProfileView as RecommendationUserProfileView,
    MovieFeedbackView,
    MovieCommentView,
    MovieCommentDetailView,
)
from recommendation.auth_views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    ChangePasswordView,
    CheckAuthView,
    TokenLoginView,
)
from recommendation.ai_views import (
    AIChatView,
    MovieRecommendationView,
    MovieAnalysisView,
    AIConfigView,
    NaturalLanguageRecommendationView,
)
from recommendation.admin_views import (
    AdminLoginView,
    AdminProfileView,
    AdminUserListView,
    AdminUserDetailView,
    AdminMovieListView,
    AdminMovieDetailView,
    AdminCommentListView,
    AdminCommentDetailView,
)

# 创建路由器并注册视图集
router = routers.DefaultRouter()
router.register(r"movies", MovieViewSet)
router.register(r"users", UserViewSet)
router.register(r"ratings", RatingViewSet)
router.register(r"video-platforms", VideoPlatformViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),

    # 认证相关路由
    path("api/auth/register/", UserRegistrationView.as_view(), name="register"),
    path("api/auth/login/", UserLoginView.as_view(), name="login"),
    path("api/auth/logout/", UserLogoutView.as_view(), name="logout"),
    path("api/auth/profile/", UserProfileView.as_view(), name="profile"),
    path("api/auth/change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("api/auth/check/", CheckAuthView.as_view(), name="check_auth"),
    path("api/auth/token-login/", TokenLoginView.as_view(), name="token_login"),

    # 推荐相关路由
    path("api/recommendations/", RecommendationView.as_view(), name="recommendations"),
    path("api/top-movies/", TopMoviesView.as_view(), name="top_movies"),
    path("api/similar-movies/<int:movie_id>/", SimilarMoviesView.as_view(), name="similar_movies"),

    # 新增：冷启动 & 用户画像
    path("api/onboarding-preferences/", OnboardingPreferenceView.as_view(), name="onboarding_preferences"),
    path("api/user-profile/", RecommendationUserProfileView.as_view(), name="recommendation_user_profile"),

    # 视频平台 / 电影详情
    path("api/video-platform-links/", VideoPlatformLinksView.as_view(), name="video_platform_links"),
    path("api/movie-detail/", MovieDetailView.as_view(), name="movie_detail"),

    # 电影互动：点赞/拉踩/评论
    path("api/movie-feedback/", MovieFeedbackView.as_view(), name="movie_feedback"),
    path("api/movie-comments/", MovieCommentView.as_view(), name="movie_comments"),
    path("api/movie-comments/<int:comment_id>/", MovieCommentDetailView.as_view(), name="movie_comment_detail"),

    # AI相关路由
    path("api/ai/chat/", AIChatView.as_view(), name="ai_chat"),
    path("api/ai/recommendations/", MovieRecommendationView.as_view(), name="ai_recommendations"),
    path("api/ai/analysis/", MovieAnalysisView.as_view(), name="ai_analysis"),
    path("api/ai/config/", AIConfigView.as_view(), name="ai_config"),
    path("api/ai/nl-recommend/", NaturalLanguageRecommendationView.as_view(), name="ai_nl_recommend"),

    # 管理员相关路由
    path("api/admin/login/", AdminLoginView.as_view(), name="admin_login"),
    path("api/admin/profile/", AdminProfileView.as_view(), name="admin_profile"),

    path("api/admin/users/", AdminUserListView.as_view(), name="admin_user_list"),
    path("api/admin/users/<int:user_id>/", AdminUserDetailView.as_view(), name="admin_user_detail"),

    path("api/admin/movies/", AdminMovieListView.as_view(), name="admin_movie_list"),
    path("api/admin/movies/<int:movie_id>/", AdminMovieDetailView.as_view(), name="admin_movie_detail"),

    path("api/admin/comments/", AdminCommentListView.as_view(), name="admin_comment_list"),
    path("api/admin/comments/<int:comment_id>/", AdminCommentDetailView.as_view(), name="admin_comment_detail"),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)