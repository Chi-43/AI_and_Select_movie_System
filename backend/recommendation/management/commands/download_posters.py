"""批量下载电影海报到本地缓存"""
import os, hashlib, json, time
import requests as req
from django.core.management.base import BaseCommand

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "media", "posters")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://movie.douban.com/",
}


class Command(BaseCommand):
    help = "批量下载电影海报到本地缓存"

    def handle(self, *args, **options):
        os.makedirs(CACHE_DIR, exist_ok=True)

        # 读取 detail cache
        from recommendation.movie_detail_cache import load_movie_detail_cache
        cache = load_movie_detail_cache()

        total = len(cache)
        downloaded = 0
        skipped = 0
        failed = 0

        self.stdout.write(f"共 {total} 条缓存，开始检查海报...\n")

        for i, (douban_url, detail) in enumerate(cache.items()):
            poster = detail.get("poster", "")
            # 过滤相册链接
            if not poster or "photos?type=" in poster or "/subject/" in poster:
                skipped += 1
                continue

            if not poster.startswith("http"):
                poster = "https:" + poster

            cache_name = hashlib.md5(poster.encode()).hexdigest() + ".jpg"
            cache_path = os.path.join(CACHE_DIR, cache_name)

            if os.path.exists(cache_path):
                skipped += 1
                continue

            try:
                resp = req.get(poster, headers=HEADERS, timeout=15)
                with open(cache_path, "wb") as f:
                    f.write(resp.content)
                downloaded += 1
                if (i + 1) % 20 == 0:
                    self.stdout.write(f"  进度: {i+1}/{total}")
            except Exception:
                failed += 1

            time.sleep(0.3)  # 防止请求太快

        self.stdout.write(f"\n完成: 下载 {downloaded} 张，跳过 {skipped} 张，失败 {failed} 张")
