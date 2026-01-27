from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Movie(models.Model):
    """电影模型"""
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.year})"

class User(AbstractUser):
    """扩展的用户模型"""
    # 添加额外的字段
    bio = models.TextField(blank=True, null=True)
    
    # 重写email字段使其可以为空
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.username

class Rating(models.Model):
    """评分模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    rating = models.FloatField()  # 评分，1-5分
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie']
    
    def __str__(self):
        return f"{self.user.username} -> {self.movie.title}: {self.rating}"