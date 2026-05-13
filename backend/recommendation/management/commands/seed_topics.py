from django.core.management.base import BaseCommand
from recommendation.models import DiscussionTopic, User


class Command(BaseCommand):
    help = "初始化社区讨论话题"

    def handle(self, *args, **options):
        admin = User.objects.filter(is_staff=True).first()
        if not admin:
            self.stderr.write("需要先创建一个管理员用户 (python manage.py createsuperuser)")
            return

        topics = [
            {"name": "电影推荐", "description": "求推荐、安利好片，分享你的观影清单", "icon": "🎯"},
            {"name": "观影讨论", "description": "聊聊你最近看的电影，交流观后感和影评", "icon": "🎬"},
            {"name": "导演与演员", "description": "讨论你喜欢的导演风格和演员作品", "icon": "🌟"},
            {"name": "影视杂谈", "description": "影视资讯、幕后故事、行业动态", "icon": "📺"},
            {"name": "经典老片", "description": "回顾那些被时间检验过的经典电影", "icon": "📽️"},
        ]

        for t in topics:
            obj, created = DiscussionTopic.objects.get_or_create(
                name=t["name"],
                defaults={
                    "description": t["description"],
                    "icon": t["icon"],
                    "created_by": admin,
                },
            )
            if created:
                self.stdout.write(f"创建话题: {obj.name}")

        self.stdout.write("话题初始化完成")
