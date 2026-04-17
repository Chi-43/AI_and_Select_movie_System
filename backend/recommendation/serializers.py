from rest_framework import serializers
from .models import (
    Movie,
    User,
    Rating,
    VideoPlatform,
    UserProfile,
    RecommendationLog,
    MovieFeedback,
    MovieComment,
)


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "genre",
            "year",
            "description",
            "country",
            "rating",
            "rating_count",
            "douban_url",
            "quote",
            "director",
            "actors",
            "created_at",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "favorite_genres",
            "favorite_countries",
            "favorite_years",
            "favorite_keywords",
            "onboarding_completed",
            "profile_summary",
            "updated_at",
        ]


class OnboardingPreferenceSerializer(serializers.Serializer):
    favorite_genres = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    favorite_countries = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    favorite_keywords = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    favorite_years = serializers.DictField(
        child=serializers.IntegerField(),
        required=False,
        default=dict
    )


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "avatar",
            "avatar_url",
            "date_joined",
            "profile",
        ]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and hasattr(obj.avatar, "url"):
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True
    )
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source="movie",
        write_only=True
    )

    class Meta:
        model = Rating
        fields = [
            "id",
            "user",
            "movie",
            "user_id",
            "movie_id",
            "rating",
            "timestamp",
        ]
        read_only_fields = ["timestamp"]


class RecommendationLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = RecommendationLog
        fields = [
            "id",
            "user",
            "movie",
            "algorithm",
            "score",
            "reason",
            "query_text",
            "clicked",
            "liked",
            "created_at",
        ]


class RecommendationResultSerializer(serializers.Serializer):
    movie = MovieSerializer()
    score = serializers.FloatField()
    algorithm = serializers.CharField()
    reason = serializers.CharField(allow_blank=True, required=False)


class VideoPlatformSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source="get_platform_display", read_only=True)
    vip_status_display = serializers.CharField(source="get_vip_status_display", read_only=True)

    class Meta:
        model = VideoPlatform
        fields = [
            "id",
            "movie_title",
            "douban_url",
            "platform",
            "platform_display",
            "platform_url",
            "vip_status",
            "vip_status_display",
            "price",
            "quality",
            "available",
            "last_checked",
        ]
        read_only_fields = ["last_checked"]


class MovieFeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        required=False,
    )
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source="movie",
        write_only=True,
    )

    class Meta:
        model = MovieFeedback
        fields = [
            "id",
            "user",
            "movie",
            "user_id",
            "movie_id",
            "feedback_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class MovieCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        required=False,
    )
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source="movie",
        write_only=True,
    )

    class Meta:
        model = MovieComment
        fields = [
            "id",
            "user",
            "movie",
            "user_id",
            "movie_id",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class MovieFeedbackSummarySerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    like_count = serializers.IntegerField()
    dislike_count = serializers.IntegerField()
    current_user_feedback = serializers.CharField(allow_null=True)