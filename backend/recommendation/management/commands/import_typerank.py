"""导入 typerank 爬取的电影详情缓存到数据库"""
import json
from django.core.management.base import BaseCommand
from recommendation.models import Movie


class Command(BaseCommand):
    help = "从 typerank JSON（cache 格式）导入电影到 Movie 表"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str)

    def handle(self, *args, **options):
        with open(options["json_file"], encoding="utf-8") as f:
            data = json.load(f)

        created = 0
        skipped = 0
        for douban_url, detail in data.items():
            title = detail.get("movie_title", "").strip()
            if not title or not douban_url:
                continue

            if Movie.objects.filter(douban_url=douban_url).exists():
                skipped += 1
                continue

            year = detail.get("year", "")
            if not year:
                # 从上映日期中提取年份
                for rd in detail.get("release_dates", []):
                    if len(rd) >= 4 and rd[:4].isdigit():
                        year = rd[:4]
                        break

            Movie.objects.create(
                title=title,
                douban_url=douban_url,
                genre=" / ".join(detail.get("genres", [])),
                year=int(year) if str(year).isdigit() else None,
                country=" / ".join(detail.get("countries", [])),
                rating=float(detail["rating"]) if detail.get("rating") else None,
                rating_count=int(detail["rating_count"]) if detail.get("rating_count", "").isdigit() else None,
                director=" / ".join(detail.get("director", [])),
                actors=" / ".join(detail.get("actors", [])[:8]),
                description=detail.get("summary", ""),
            )
            created += 1

        self.stdout.write(f"导入完成：新增 {created} 部，跳过 {skipped} 部（已存在）")
