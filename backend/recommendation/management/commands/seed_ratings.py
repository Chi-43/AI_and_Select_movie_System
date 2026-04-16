import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recommendation.models import Movie, Rating

User = get_user_model()


class Command(BaseCommand):
    help = "为现有用户生成测试评分数据"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=5,
            help="如果现有用户不足，则额外创建多少个测试用户"
        )
        parser.add_argument(
            "--ratings-per-user",
            type=int,
            default=12,
            help="每个用户生成多少条评分"
        )

    def handle(self, *args, **options):
        extra_users = options["users"]
        ratings_per_user = options["ratings_per_user"]

        movies = list(Movie.objects.all())
        if len(movies) == 0:
            self.stdout.write(self.style.ERROR("Movie 表为空，请先导入电影数据"))
            return

        users = list(User.objects.all())

        # 如果当前用户太少，就自动创建测试用户
        if len(users) < extra_users:
            need_create = extra_users - len(users)
            for i in range(need_create):
                username = f"test_user_{len(users) + i + 1}"
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        password="12345678"
                    )
                    users.append(user)

        created_count = 0
        updated_count = 0

        for user in users:
            sampled_movies = random.sample(movies, min(ratings_per_user, len(movies)))

            for movie in sampled_movies:
                # 更偏向高分，便于系统初期更容易推荐
                score = random.choice([3.0, 3.5, 4.0, 4.5, 5.0])

                rating_obj, created = Rating.objects.update_or_create(
                    user=user,
                    movie=movie,
                    defaults={"rating": score}
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"测试评分生成完成：新增 {created_count} 条，更新 {updated_count} 条"
            )
        )