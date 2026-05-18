"""
从豆瓣类型排行榜爬取电影数据（解析HTML页面）
输出格式与 movie_detail_cache.json 一致（key=douban_url）
"""
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup

# 复用已有详情爬虫
import sys
sys.path.append(os.path.dirname(__file__))
from movie_detail import fetch_douban_movie_detail

FETCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

GENRE_MAP = {
    "剧情": 11, "喜剧": 24, "动作": 5, "爱情": 13, "科幻": 17,
    "悬疑": 10, "犯罪": 3, "动画": 25, "奇幻": 16, "冒险": 15,
    "战争": 22, "恐怖": 20, "惊悚": 19, "历史": 4, "纪录片": 1,
    "家庭": 18, "音乐": 14, "传记": 2, "武侠": 7, "灾难": 12,
}

RATING_INTERVALS = [("100:90", "9-10分"), ("90:80", "8-9分"), ("80:70", "7-8分")]


def fetch_typerank_urls(genre_name, genre_id, interval="100:90", pages=2):
    """从 typerank HTML 页面解析电影链接"""
    urls = []
    for page in range(pages):
        start = page * 20
        url = (
            f"https://movie.douban.com/typerank"
            f"?type_name={genre_name}&type={genre_id}"
            f"&interval_id={interval}&action=&start={start}&limit=20"
        )
        try:
            resp = requests.get(url, headers=FETCH_HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            print(f"  请求失败: {e}")
            break

        # 从 HTML 中提取电影链接
        links = []
        for a_tag in soup.select('a[href*="/subject/"]'):
            href = a_tag.get("href", "")
            match = re.search(r"/subject/(\d+)/", href)
            if match:
                links.append(f"https://movie.douban.com/subject/{match.group(1)}/")

        # 去重
        links = list(dict.fromkeys(links))
        urls.extend(links)

        print(f"  [{genre_name}] {interval} 第{page+1}页: {len(links)} 个链接")
        if len(links) < 5:
            break
        time.sleep(1)
    return urls


def scrape(genres=None, pages=2, existing_cache_path=None):
    """
    主函数：爬取类型排行 → 逐个抓详情 → 返回 cache 格式的 dict
    如果传 existing_cache_path，会加载已有缓存并只补充新的
    """
    # 加载已有缓存
    cache = {}
    if existing_cache_path and os.path.exists(existing_cache_path):
        with open(existing_cache_path, encoding="utf-8") as f:
            cache = json.load(f)
        print(f"已加载 {len(cache)} 条已有缓存")

    if genres is None:
        genres = list(GENRE_MAP.keys())

    all_urls = set()
    for genre_name in genres:
        genre_id = GENRE_MAP[genre_name]
        print(f"\n=== {genre_name} (type={genre_id}) ===")
        for interval, label in RATING_INTERVALS:
            urls = fetch_typerank_urls(genre_name, genre_id, interval, pages=pages)
            for u in urls:
                all_urls.add(u)
            time.sleep(0.5)

    new_urls = [u for u in all_urls if u not in cache]
    print(f"\n共 {len(all_urls)} 个链接（去重），其中 {len(new_urls)} 个需要抓取")

    for i, douban_url in enumerate(new_urls):
        print(f"[{i+1}/{len(new_urls)}] {douban_url}")
        try:
            detail = fetch_douban_movie_detail(douban_url)
            if detail and detail.get("movie_title"):
                cache[douban_url] = detail
                print(f"  ✓ {detail['movie_title']}")
            else:
                print(f"  ✗ 抓取失败")
        except Exception as e:
            print(f"  ✗ 异常: {e}")
        time.sleep(1.5 if i % 3 == 2 else 1)

    print(f"\n完成：缓存共 {len(cache)} 条（新增 {len(new_urls)} 条）")
    return cache


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=1, help="每种每段爬几页（每页20条）")
    parser.add_argument("--cache", type=str, default="", help="已有缓存文件路径")
    parser.add_argument("--output", type=str, default="douban_typerank.json", help="输出文件")
    parser.add_argument("--genres", type=str, default="", help="只爬指定类型（逗号分隔，默认全部）")
    args = parser.parse_args()

    genres = [g.strip() for g in args.genres.split(",") if g.strip()] if args.genres else None

    result = scrape(
        genres=genres,
        pages=args.pages,
        existing_cache_path=args.cache or None,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"已保存到 {args.output}（{len(result)} 条）")
