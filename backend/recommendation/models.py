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
    public_favorites = models.BooleanField(default=False, verbose_name="是否公开收藏夹")
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

"""推荐日志模型"""
class RecommendationLog(models.Model):
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


# =========================
# 电影点赞 / 拉踩
# =========================
class MovieFeedback(models.Model):
    FEEDBACK_CHOICES = [
        ("like", "点赞"),
        ("dislike", "拉踩"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="movie_feedbacks")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="feedbacks")
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_CHOICES, verbose_name="反馈类型")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "电影反馈"
        verbose_name_plural = "电影反馈"
        unique_together = ["user", "movie"]

    def __str__(self):
        return f"{self.user.username} -> {self.movie.title} ({self.feedback_type})"


# =========================
# 电影评论
# =========================
class MovieComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="movie_comments")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name="父评论",
    )
    content = models.TextField(verbose_name="评论内容")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "电影评论"
        verbose_name_plural = "电影评论"
        ordering = ["created_at"]

    def __str__(self):
        prefix = "回复" if self.parent_id else "评论"
        return f"{self.user.username} {prefix}了 {self.movie.title}"


# =========================
# 社区讨论区
# =========================
class DiscussionTopic(models.Model):
    """讨论话题/小组"""
    name = models.CharField(max_length=100, verbose_name="话题名称")
    description = models.TextField(blank=True, default="", verbose_name="话题描述")
    icon = models.CharField(max_length=10, blank=True, default="💬", verbose_name="图标")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_topics")
    created_at = models.DateTimeField(auto_now_add=True)
    post_count = models.IntegerField(default=0, verbose_name="帖子数")

    class Meta:
        verbose_name = "讨论话题"
        verbose_name_plural = "讨论话题"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class DiscussionPost(models.Model):
    """讨论帖子"""
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    image = models.ImageField(upload_to="community/", blank=True, null=True, verbose_name="配图")
    topic = models.ForeignKey(DiscussionTopic, on_delete=models.CASCADE, related_name="posts")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    view_count = models.IntegerField(default=0, verbose_name="浏览数")
    reply_count = models.IntegerField(default=0, verbose_name="回复数")
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "讨论帖子"
        verbose_name_plural = "讨论帖子"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class DiscussionReply(models.Model):
    """帖子回复（支持嵌套）"""
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name="replies")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discussion_replies")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "帖子回复"
        verbose_name_plural = "帖子回复"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.created_by.username} 回复了 {self.post.title}"


class PostLike(models.Model):
    """帖子点赞"""
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "帖子点赞"
        verbose_name_plural = "帖子点赞"
        unique_together = ["post", "user"]

    def __str__(self):
        return f"{self.user.username} 赞了 {self.post.title}"


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