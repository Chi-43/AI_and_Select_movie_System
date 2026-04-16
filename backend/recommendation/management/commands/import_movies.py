import json
import os
import re
from django.core.management.base import BaseCommand
from recommendation.models import Movie


def safe_float(value):
    try:
        return float(value) if value not in [None, ""] else None
    except Exception:
        return None


def safe_int(value):
    try:
        value = str(value).replace(",", "").strip()
        return int(value) if value else None
    except Exception:
        return None


def extract_year(raw_year, release_dates):
    # 先用 year 字段
    if raw_year:
        raw_year = str(raw_year).strip()
        if raw_year.isdigit():
            return int(raw_year)

    # 再从 release_dates 里提取第一个四位年份
    if release_dates:
        for item in release_dates:
            match = re.search(r"(\d{4})", str(item))
            if match:
                return int(match.group(1))

    return None


def join_list(value):
    if isinstance(value, list):
        return " / ".join([str(v).strip() for v in value if str(v).strip()])
    if isinstance(value, str):
        return value.strip()
    return ""


class Command(BaseCommand):
    help = "从 movie_detail_cache.json 导入电影数据到 Movie 表"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="",
            help="自定义 JSON 文件路径，不传则默认 recommendation/data/movie_detail_cache.json",
        )

    def handle(self, *args, **kwargs):
        custom_file = kwargs.get("file", "").strip()

        if custom_file:
            file_path = custom_file
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            file_path = os.path.join(base_dir, "data", "movie_detail_cache.json")

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"找不到数据文件: {file_path}"))
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"读取 JSON 失败: {str(e)}"))
            return

        if not isinstance(data, dict):
            self.stdout.write(self.style.ERROR("当前 JSON 结构不是 dict，不符合 movie_detail_cache.json 格式"))
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for douban_url, item in data.items():
            title = str(item.get("movie_title", "")).strip()
            if not title:
                skipped_count += 1
                continue

            genre = join_list(item.get("genres", []))
            country = join_list(item.get("countries", []))
            director = join_list(item.get("director", []))
            actors = join_list(item.get("actors", []))

            description = str(item.get("summary", "")).strip()
            quote = description[:120] if description else ""

            year_value = extract_year(
                item.get("year", ""),
                item.get("release_dates", []),
            )

            rating_value = safe_float(item.get("rating"))
            rating_count_value = safe_int(item.get("rating_count"))

            movie, created = Movie.objects.update_or_create(
                douban_url=douban_url,
                defaults={
                    "title": title,
                    "genre": genre,
                    "year": year_value,
                    "description": description,
                    "country": country,
                    "rating": rating_value,
                    "rating_count": rating_count_value,
                    "quote": quote,
                    "director": director,
                    "actors": actors,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"导入完成：新增 {created_count} 条，更新 {updated_count} 条，跳过 {skipped_count} 条"
            )
        )