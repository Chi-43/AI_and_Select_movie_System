from rest_framework import serializers
from .models import Movie, User, Rating, VideoPlatform

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'genre', 'year', 'description']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all(), source='movie', write_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'user', 'movie', 'user_id', 'movie_id', 'rating', 'timestamp']

class VideoPlatformSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    vip_status_display = serializers.CharField(source='get_vip_status_display', read_only=True)
    
    class Meta:
        model = VideoPlatform
        fields = [
            'id', 'movie_title', 'douban_url', 'platform', 'platform_display',
            'platform_url', 'vip_status', 'vip_status_display', 'price',
            'quality', 'available', 'last_checked'
        ]
        read_only_fields = ['last_checked']