from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete


class Movie(models.Model):
    """电影模型"""
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    year = models.IntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.year})"


class VideoPlatform(models.Model):
    """视频平台模型"""
    PLATFORM_CHOICES = [
        ('iqiyi', '爱奇艺'),
        ('tencent', '腾讯视频'),
        ('youku', '优酷'),
        ('bilibili', '哔哩哔哩'),
        ('migu', '咪咕视频'),
        ('mango', '芒果TV'),
        ('netflix', 'Netflix'),
        ('disney', 'Disney+'),
        ('amazon', 'Amazon Prime'),
        ('other', '其他平台'),
    ]

    VIP_CHOICES = [
        ('free', '免费观看'),
        ('vip', 'VIP可看'),
        ('pay', '付费观看'),
        ('rent', '租赁观看'),
        ('unknown', '未知'),
    ]

    movie_title = models.CharField(max_length=200, verbose_name="电影名称")
    douban_url = models.URLField(max_length=500, verbose_name="豆瓣链接")
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, verbose_name="视频平台")
    platform_url = models.URLField(max_length=500, verbose_name="平台链接")
    vip_status = models.CharField(
        max_length=20,
        choices=VIP_CHOICES,
        default='unknown',
        verbose_name="观看权限"
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="价格(元)"
    )
    quality = models.CharField(max_length=50, null=True, blank=True, verbose_name="画质")
    available = models.BooleanField(default=True, verbose_name="是否可用")
    last_checked = models.DateTimeField(auto_now=True, verbose_name="最后检查时间")

    class Meta:
        verbose_name = "视频平台链接"
        verbose_name_plural = "视频平台链接"
        # 推荐你用 douban_url + platform，更稳
        unique_together = ['douban_url', 'platform']

    def __str__(self):
        return f"{self.movie_title} - {self.get_platform_display()} ({self.get_vip_status_display()})"


class User(AbstractUser):
    """扩展的用户模型"""
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # 重写 email 字段使其可为空
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # 如果更新时 avatar 改了，删除旧头像文件
        if self.pk:
            try:
                old_instance = User.objects.get(pk=self.pk)
                if old_instance.avatar and old_instance.avatar != self.avatar:
                    if os.path.isfile(old_instance.avatar.path):
                        os.remove(old_instance.avatar.path)
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)


@receiver(post_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    """删除用户时删除头像文件"""
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)


@receiver(pre_save, sender=User)
def delete_old_avatar_on_update(sender, instance, **kwargs):
    """更新头像前删除旧文件"""
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