from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete, post_save


class Movie(models.Model):
    """电影模型"""
    title = models.CharField(max_length=200, verbose_name="电影名称")
    genre = models.CharField(max_length=200, blank=True, default="", verbose_name="类型")
    year = models.IntegerField(null=True, blank=True, verbose_name="年份")
    description = models.TextField(blank=True, default="", verbose_name="简介")

    country = models.CharField(max_length=200, blank=True, default="", verbose_name="国家/地区")
    rating = models.FloatField(null=True, blank=True, verbose_name="豆瓣评分")
    rating_count = models.IntegerField(null=True, blank=True, verbose_name="评分人数")
    douban_url = models.URLField(blank=True, null=True, verbose_name="豆瓣链接")
    quote = models.CharField(max_length=300, blank=True, default="", verbose_name="一句话评价")
    director = models.CharField(max_length=200, blank=True, default="", verbose_name="导演")
    actors = models.TextField(blank=True, default="", verbose_name="主演")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "电影"
        verbose_name_plural = "电影"
        ordering = ["-rating", "title"]

    def __str__(self):
        year_text = self.year if self.year else "未知年份"
        return f"{self.title} ({year_text})"


class VideoPlatform(models.Model):
    """视频平台模型"""
    PLATFORM_CHOICES = [
        ("iqiyi", "爱奇艺"),
        ("tencent", "腾讯视频"),
        ("youku", "优酷"),
        ("bilibili", "哔哩哔哩"),
        ("migu", "咪咕视频"),
        ("mango", "芒果TV"),
        ("netflix", "Netflix"),
        ("disney", "Disney+"),
        ("amazon", "Amazon Prime"),
        ("other", "其他平台"),
    ]

    VIP_CHOICES = [
        ("free", "免费观看"),
        ("vip", "VIP可看"),
        ("pay", "付费观看"),
        ("rent", "租赁观看"),
        ("unknown", "未知"),
    ]

    movie_title = models.CharField(max_length=200, verbose_name="电影名称")
    douban_url = models.URLField(max_length=500, verbose_name="豆瓣链接")
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, verbose_name="视频平台")
    platform_url = models.URLField(max_length=500, verbose_name="平台链接")
    vip_status = models.CharField(
        max_length=20,
        choices=VIP_CHOICES,
        default="unknown",
        verbose_name="观看权限",
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="价格(元)",
    )
    quality = models.CharField(max_length=50, null=True, blank=True, verbose_name="画质")
    available = models.BooleanField(default=True, verbose_name="是否可用")
    last_checked = models.DateTimeField(auto_now=True, verbose_name="最后检查时间")

    class Meta:
        verbose_name = "视频平台链接"
        verbose_name_plural = "视频平台链接"
        unique_together = ["douban_url", "platform"]

    def __str__(self):
        return f"{self.movie_title} - {self.get_platform_display()} ({self.get_vip_status_display()})"


class User(AbstractUser):
    """扩展的用户模型"""
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_instance = User.objects.get(pk=self.pk)
                if old_instance.avatar and old_instance.avatar != self.avatar:
                    if os.path.isfile(old_instance.avatar.path):
                        os.remove(old_instance.avatar.path)
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """用户画像模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    favorite_genres = models.JSONField(default=list, blank=True, verbose_name="偏好类型")
    favorite_countries = models.JSONField(default=list, blank=True, verbose_name="偏好国家")
    favorite_years = models.JSONField(default=dict, blank=True, verbose_name="偏好年份范围")
    favorite_keywords = models.JSONField(default=list, blank=True, verbose_name="偏好关键词")

    onboarding_completed = models.BooleanField(default=False, verbose_name="是否完成冷启动选择")
    profile_summary = models.TextField(blank=True, null=True, verbose_name="画像总结")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "用户画像"
        verbose_name_plural = "用户画像"

    def __str__(self):
        return f"{self.user.username} 的画像"


class Rating(models.Model):
    """评分模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    rating = models.FloatField(verbose_name="评分")  # 1-5 分
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "movie"]
        verbose_name = "评分"
        verbose_name_plural = "评分"

    def __str__(self):
        return f"{self.user.username} -> {self.movie.title}: {self.rating}"


class RecommendationLog(models.Model):
    """推荐日志模型"""
    ALGORITHM_CHOICES = [
        ("user_based", "基于用户协同过滤"),
        ("item_based", "基于物品协同过滤"),
        ("top", "热门推荐"),
        ("cold_start", "冷启动推荐"),
        ("hybrid", "混合推荐"),
        ("nl_query", "自然语言推荐"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recommendation_logs")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="recommendation_logs")
    algorithm = models.CharField(max_length=50, choices=ALGORITHM_CHOICES, verbose_name="推荐算法")
    score = models.FloatField(default=0, verbose_name="推荐分数")
    reason = models.TextField(blank=True, null=True, verbose_name="推荐理由")
    query_text = models.TextField(blank=True, null=True, verbose_name="查询文本")
    clicked = models.BooleanField(default=False, verbose_name="是否点击")
    liked = models.BooleanField(default=False, verbose_name="是否喜欢")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "推荐日志"
        verbose_name_plural = "推荐日志"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} <- {self.movie.title} ({self.algorithm})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """创建用户时自动创建画像"""
    if created:
        UserProfile.objects.create(user=instance)


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