import os
import django
import random

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommender.settings')
django.setup()

from recommendation.models import Movie, Rating, RecommendationLog, MovieComment, MovieFeedback


def create_sample_data():
    """创建示例数据"""
    
    # 清空现有数据
    Movie.objects.all().delete()
    Rating.objects.all().delete()
    RecommendationLog.objects.all().delete()
    MovieComment.objects.all().delete()
    MovieFeedback.objects.all().delete()
    
    print("数据删除完成！")

if __name__ == "__main__":
    create_sample_data()