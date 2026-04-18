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


def join_list(value):
    if isinstance(value, list):
        return " / ".join([str(v).strip() for v in value if str(v).strip()])
    if isinstance(value, str):
        return value.strip()
    return ""


def extract_year_from_text(raw_year):
    if raw_year is None:
        return None

    raw_year = str(raw_year).strip()
    match = re.search(r"(\d{4})", raw_year)
    if match:
        return int(match.group(1))
    return None


class Command(BaseCommand):
    help = "导入豆瓣电影数据到 Movie 表，支持 movie_detail_cache.json 和 豆瓣电影TOP250.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="",
            help="自定义 JSON 文件路径",
        )

    def handle(self, *args, **kwargs):
        custom_file = kwargs.get("file", "").strip()

        if custom_file:
            file_path = custom_file
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            file_path = os.path.join(base_dir, "datasets", "douban", "豆瓣电影TOP250.json")

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"找不到数据文件: {file_path}"))
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"读取 JSON 失败: {str(e)}"))
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        # =========================
        # 1. 兼容 movie_detail_cache.json（dict）
        # =========================
        if isinstance(data, dict):
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
                year_value = extract_year_from_text(item.get("year", ""))
                rating_value = safe_float(item.get("rating"))
                rating_count_value = safe_int(item.get("rating_count"))

                _, created = Movie.objects.update_or_create(
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

        # =========================
        # 2. 兼容 豆瓣电影TOP250.json（list）
        # =========================
        elif isinstance(data, list):
            for item in data:
                title = str(item.get("电影名字", "")).strip()
                douban_url = str(item.get("电影链接", "")).strip()

                if not title or not douban_url:
                    skipped_count += 1
                    continue

                genre = str(item.get("类型", "")).replace(" ", " / ").strip()
                year_value = extract_year_from_text(item.get("年份", ""))
                country = str(item.get("国家", "")).strip()
                director = str(item.get("导演", "")).strip()
                actors = str(item.get("主演", "")).strip()
                rating_value = safe_float(item.get("评分"))
                rating_count_value = safe_int(item.get("评分人数"))
                quote = str(item.get("一句话评价", "")).strip()

                _, created = Movie.objects.update_or_create(
                    douban_url=douban_url,
                    defaults={
                        "title": title,
                        "genre": genre,
                        "year": year_value,
                        "description": quote,
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

        else:
            self.stdout.write(self.style.ERROR("JSON 格式不支持，只支持 dict 或 list"))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"导入完成：新增 {created_count} 条，更新 {updated_count} 条，跳过 {skipped_count} 条"
            )
        )