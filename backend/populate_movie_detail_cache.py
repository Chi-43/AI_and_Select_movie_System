import argparse
import json
import os
import re
import sys
import time
from typing import Dict, Any, List, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from recommendation.movie_detail_cache import load_movie_detail_cache  # noqa: E402

from selenium import webdriver  # noqa: E402
from selenium.webdriver.edge.options import Options  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.common.exceptions import TimeoutException  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402


JSON_SOURCE_FILE = os.path.join(
    PROJECT_ROOT,
    "frontend",
    "src",
    "data",
    "豆瓣电影TOP250.json"
)

CACHE_FILE = os.path.join(
    CURRENT_DIR,
    "recommendation",
    "data",
    "movie_detail_cache.json"
)


def ensure_cache_file() -> None:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def save_movie_detail_cache(cache_data: Dict[str, Any]) -> None:
    ensure_cache_file()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)


def load_source_movies() -> List[Dict[str, Any]]:
    if not os.path.exists(JSON_SOURCE_FILE):
        raise FileNotFoundError(f"未找到源数据文件: {JSON_SOURCE_FILE}")

    with open(JSON_SOURCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("电影源数据格式错误，应为列表")
    return data


def split_names(value: str) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in re.split(r"[ /]+", value) if item.strip()]


def build_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    return webdriver.Edge(options=options)


def fetch_douban_movie_detail(
    douban_url: str,
    fallback_title: str = "",
    wait_seconds: int = 15,
) -> Dict[str, Any]:
    driver = build_driver()

    try:
        driver.set_page_load_timeout(wait_seconds + 10)
        driver.get(douban_url)

        wait = WebDriverWait(driver, wait_seconds)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[property="v:itemreviewed"]'))
        )

        time.sleep(1.5)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.select_one('span[property="v:itemreviewed"]')
        movie_title = title_tag.get_text(strip=True) if title_tag else fallback_title

        title_text = soup.title.get_text(strip=True) if soup.title else ""
        english_title = ""
        if movie_title and movie_title in title_text:
            english_title = title_text.replace(movie_title, "").replace("(豆瓣)", "").strip()

        rating_tag = soup.select_one('strong[property="v:average"]')
        rating = rating_tag.get_text(strip=True) if rating_tag else ""

        rating_count_tag = soup.select_one('span[property="v:votes"]')
        rating_count = rating_count_tag.get_text(strip=True) if rating_count_tag else ""

        poster_tag = soup.select_one("#mainpic img")
        poster = poster_tag.get("src", "").strip() if poster_tag else ""

        summary_tag = soup.select_one('span[property="v:summary"]')
        summary = summary_tag.get_text("\n", strip=True) if summary_tag else ""

        year_match = re.search(r"\((\d{4})\)", title_text)
        year = year_match.group(1) if year_match else ""

        director = [a.get_text(strip=True) for a in soup.select('#info .attrs a[rel="v:directedBy"]')]
        actors = [a.get_text(strip=True) for a in soup.select('#info .attrs a[rel="v:starring"]')]
        genres = [span.get_text(strip=True) for span in soup.select('#info span[property="v:genre"]')]
        release_dates = [span.get_text(strip=True) for span in soup.select('#info span[property="v:initialReleaseDate"]')]
        runtime = [span.get_text(strip=True) for span in soup.select('#info span[property="v:runtime"]')]

        info_node = soup.select_one("#info")
        info_text = info_node.get_text("\n", strip=True) if info_node else ""

        writer = []
        countries = []
        languages = []
        aka = []
        imdb = ""

        lines = [line.strip() for line in info_text.split("\n") if line.strip()]
        for i, line in enumerate(lines):
            if "编剧" in line and i + 1 < len(lines):
                writer = split_names(lines[i + 1])
            elif "制片国家/地区" in line and i + 1 < len(lines):
                countries = split_names(lines[i + 1])
            elif "语言" in line and i + 1 < len(lines):
                languages = split_names(lines[i + 1])
            elif "又名" in line and i + 1 < len(lines):
                aka = split_names(lines[i + 1])
            elif "IMDb" in line and i + 1 < len(lines):
                imdb = lines[i + 1]

        return {
            "movie_title": movie_title,
            "english_title": english_title,
            "douban_url": douban_url,
            "poster": poster,
            "rating": rating,
            "rating_count": rating_count,
            "director": director,
            "writer": writer,
            "actors": actors,
            "genres": genres,
            "countries": countries,
            "languages": languages,
            "release_dates": release_dates,
            "runtime": runtime,
            "aka": aka,
            "imdb": imdb,
            "summary": summary,
            "year": year,
        }

    finally:
        driver.quit()


def select_movies(
    source_movies: List[Dict[str, Any]],
    limit: Optional[int],
    title_keyword: Optional[str],
) -> List[Dict[str, Any]]:
    movies = source_movies

    if title_keyword:
        keyword = title_keyword.strip().lower()
        movies = [
            movie for movie in movies
            if keyword in movie.get("电影名字", "").strip().lower()
        ]

    if limit is not None and limit > 0:
        movies = movies[:limit]

    return movies


def try_fetch_with_retry(
    movie_title: str,
    douban_url: str,
    retries: int,
    sleep_seconds: float,
    wait_seconds: int,
) -> Dict[str, Any]:
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            print(f"    第 {attempt}/{retries} 次尝试...")
            detail = fetch_douban_movie_detail(
                douban_url=douban_url,
                fallback_title=movie_title,
                wait_seconds=wait_seconds,
            )

            if detail:
                return detail

            last_error = RuntimeError("返回空数据")

        except TimeoutException as e:
            last_error = e
            print(f"    超时: {str(e)}")
        except Exception as e:
            last_error = e
            print(f"    错误: {str(e)}")

        if attempt < retries:
            time.sleep(sleep_seconds)

    raise RuntimeError(f"重试失败: {str(last_error)}")


def main():
    parser = argparse.ArgumentParser(description="离线批量抓取豆瓣电影详情缓存")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="只抓前 N 部电影，例如 --limit 5"
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="只抓标题包含关键字的电影，例如 --title 肖申克"
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="失败重试次数，默认 3"
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=2.0,
        help="每次抓取成功/失败后的等待秒数，默认 2"
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=15,
        help="单页等待秒数，默认 15"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新抓取，即使缓存已存在"
    )

    args = parser.parse_args()

    ensure_cache_file()
    source_movies = load_source_movies()
    cache = load_movie_detail_cache()

    target_movies = select_movies(
        source_movies=source_movies,
        limit=args.limit,
        title_keyword=args.title,
    )

    total = len(target_movies)
    success = 0
    skipped = 0
    failed = 0

    if total == 0:
        print("没有匹配到要抓取的电影。")
        return

    print(f"[Start] 本次计划处理 {total} 部电影")

    for index, movie in enumerate(target_movies, start=1):
        movie_title = movie.get("电影名字", "").strip()
        douban_url = movie.get("电影链接", "").strip()

        if not douban_url:
            print(f"[{index}/{total}] 跳过：{movie_title}，缺少豆瓣链接")
            skipped += 1
            continue

        if (not args.force) and douban_url in cache:
            print(f"[{index}/{total}] 已存在缓存，跳过：{movie_title}")
            skipped += 1
            continue

        print(f"[{index}/{total}] 开始抓取：{movie_title}")

        try:
            detail = try_fetch_with_retry(
                movie_title=movie_title,
                douban_url=douban_url,
                retries=args.retries,
                sleep_seconds=args.sleep,
                wait_seconds=args.wait,
            )

            cache[douban_url] = detail
            save_movie_detail_cache(cache)

            print(f"[{index}/{total}] 抓取成功：{movie_title}")
            success += 1

        except Exception as e:
            print(f"[{index}/{total}] 抓取失败：{movie_title}，错误：{str(e)}")
            failed += 1

        time.sleep(args.sleep)

    print("\n[Done]")
    print(f"成功：{success}")
    print(f"跳过：{skipped}")
    print(f"失败：{failed}")
    print(f"缓存文件：{CACHE_FILE}")


if __name__ == "__main__":
    main()