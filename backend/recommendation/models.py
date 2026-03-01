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

import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete

class User(AbstractUser):
    """扩展的用户模型"""
    # 添加额外的字段
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # 重写email字段使其可以为空
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        # 如果是更新操作且avatar字段有变化，删除旧的头像文件
        if self.pk:
            try:
                old_instance = User.objects.get(pk=self.pk)
                if old_instance.avatar and old_instance.avatar != self.avatar:
                    if os.path.isfile(old_instance.avatar.path):
                        os.remove(old_instance.avatar.path)
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)

# 信号：删除用户时删除头像文件
@receiver(post_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)

# 信号：更新头像前删除旧文件
@receiver(pre_save, sender=User)
def delete_old_avatar_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return False
    
    try:
        old_instance = User.objects.get(pk=instance.pk)
        if old_instance.avatar and old_instance.avatar != instance.avatar:
            if os.path.isfile(old_instance.avatar.path):
                os.remove(old_instance.avatar.path)
    except User.DoesNotExist:
        return False

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