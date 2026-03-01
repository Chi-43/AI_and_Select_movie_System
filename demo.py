#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
豆瓣电影TOP250爬虫
支持命令行参数，输出CSV或JSON格式

✅ 修复“评分人数一直为0”的根因：
你拿到的 li 节点里，“xxx人评价”不一定稳定地落在 div.star/span 结构上（不同返回内容/结构会变）。
最稳的做法：直接把“该电影条目 li 内所有文本拼起来”，用正则抓 “(\d+)人评价”。

另外：
- 兼容 12,345 人评价（带逗号）
- --debug 会额外打印第一条电影的提取文本片段，方便你确认“人评价”到底在不在你拿到的 HTML 里
"""

import random
import re
import argparse
import time
import csv
import json
from urllib.parse import urljoin

import requests
from lxml import etree
import pandas as pd


# ==================== 配置区域 ====================
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
]

BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://movie.douban.com/top250",
}

START_URL = "https://movie.douban.com/top250"


# ==================== 全局数据列表 ====================
movie_names = []
urls = []
scores = []
star_people_nums = []
directors = []
actors = []
years = []
countrys = []
types = []
one_evaluates = []


# ==================== 辅助函数 ====================
def get_headers():
    h = dict(BASE_HEADERS)
    h["User-Agent"] = random.choice(USER_AGENTS)
    return h


def extract_first(trees, default=""):
    return trees[0] if trees else default


def clean_text(text):
    if not isinstance(text, str):
        return text
    cleaned = ' '.join(text.strip().splitlines())
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def parse_rating_people(li, debug=False):
    """
    ✅ 最稳的“人评价”提取方式：拼接该 li 内所有文本，再正则抓取。
    这样不依赖 div.star/span 的具体结构。
    """
    li_all_text = "".join(li.xpath(".//text()"))
    li_all_text = clean_text(li_all_text)

    if debug:
        # 只打印一小段，避免刷屏
        print("DEBUG li_all_text snippet:", li_all_text[:200])

    m = re.search(r'(\d[\d,]*)\s*人评价', li_all_text)
    return m.group(1).replace(',', '') if m else "0"


# ==================== 核心爬取函数 ====================
def parse(page_url, remaining_pages=None, delay_range=(3, 8), debug=False):
    if remaining_pages is not None and remaining_pages <= 0:
        print("已达到指定页数，停止爬取")
        return

    print(f"----------开始爬取：{page_url}-------------")
    try:
        resp = requests.get(page_url, headers=get_headers(), timeout=15)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
    except Exception as e:
        print(f"请求失败：{e}")
        return

    tree = etree.HTML(resp.text)

    if debug:
        title = extract_first(tree.xpath("//title/text()")).strip()
        print("DEBUG page title:", title)

    lis = tree.xpath("//ol[@class='grid_view']/li")
    if not lis:
        print("未找到电影列表，可能页面结构已变或请求被风控/验证码拦截")
        if debug:
            snippet = resp.text[:500].replace("\n", " ")
            print("DEBUG html snippet:", snippet)
        return

    for idx, li in enumerate(lis):
        try:
            # ---------- 电影详情页链接 ----------
            url = extract_first(li.xpath(".//div[@class='hd']/a/@href")).strip()

            # ---------- 电影名称 ----------
            movie_name = "".join(li.xpath(".//div[@class='hd']/a//text()"))
            movie_name = clean_text(movie_name)

            # ---------- 评分 ----------
            score = extract_first(li.xpath(".//span[@class='rating_num']/text()")).strip()

            # ---------- 评价人数（✅修复：不依赖结构） ----------
            star_people_num = parse_rating_people(li, debug=debug and idx == 0)

            # ---------- 一句话评价 ----------
            one_evaluate = extract_first(li.xpath(".//p[@class='quote']/span/text()")).strip()
            one_evaluate = clean_text(one_evaluate)

            # ---------- 导演、主演、年份、国家、类型 ----------
            bd_parts = li.xpath(".//div[@class='bd']/p//text()")
            bd_text = "".join(bd_parts).strip()

            director = ""
            actor = ""
            year = ""
            country = ""
            genre = ""

            director_match = re.search(r'导演:\s*([^\n]+?)(?:\s*主演:|$)', bd_text)
            if director_match:
                director = director_match.group(1).strip()

            actor_match = re.search(r'主演:\s*([^\n]+?)(?:\s*\d{4}|$)', bd_text)
            if actor_match:
                actor = actor_match.group(1).strip()

            info_match = re.search(r'(\d{4})\s*/\s*([^/]+?)\s*/\s*([^\n]+)', bd_text)
            if info_match:
                year = info_match.group(1).strip()
                country = info_match.group(2).strip()
                genre = info_match.group(3).strip()

            # 兜底：按行拆分
            if not year or not country or not genre:
                lines = [line.strip() for line in bd_text.split('\n') if line.strip()]
                if len(lines) >= 1:
                    first_line = lines[0]
                    if '导演:' in first_line:
                        director_part = first_line.split('导演:')[1]
                        if '主演:' in director_part:
                            parts = director_part.split('主演:')
                            director = parts[0].strip()
                            actor = parts[1].strip() if len(parts) > 1 else ""
                        else:
                            director = director_part.strip()

                if len(lines) >= 2:
                    second_line = lines[1]
                    parts = [p.strip() for p in second_line.split('/')]
                    if len(parts) >= 3:
                        year = parts[0]
                        country = parts[1]
                        genre = '/'.join(parts[2:]).strip()

            director = clean_text(director)
            actor = clean_text(actor)
            year = clean_text(year)
            country = clean_text(country)
            genre = clean_text(genre)

            # 如果主演混入年份等，再清理
            if actor and re.search(r'\d{4}\s*/\s*[^/]+\s*/\s*[^/]+', actor):
                actor_info_match = re.search(r'(.+?)(?:\s+\d{4}\s*/\s*[^/]+\s*/\s*[^/]+)', actor)
                if actor_info_match:
                    actor = actor_info_match.group(1).strip()
                else:
                    if re.match(r'\d{4}\s*/\s*[^/]+\s*/\s*[^/]+', actor):
                        actor = ""

            # ---------- 存入列表 ----------
            urls.append(url)
            movie_names.append(movie_name)
            scores.append(score)
            star_people_nums.append(star_people_num)
            one_evaluates.append(one_evaluate)
            directors.append(director)
            actors.append(actor)
            years.append(year)
            countrys.append(country)
            types.append(genre)

            print(f"{movie_name} | {score} | {star_people_num}人评价 | {director} | {actor} | {year} | {country} | {genre}")

        except Exception as e:
            print(f"解析电影条目时出错：{e}，跳过该条目")
            continue

    # ---------- 下一页 ----------
    next_span = tree.xpath("//div[@class='paginator']/span[@class='next']")
    if next_span:
        a = next_span[0].xpath("./a")
        if a:
            next_href = a[0].xpath("./@href")[0]
            next_url = urljoin(page_url, next_href)

            if delay_range:
                sleep_time = random.uniform(*delay_range)
                print(f"休眠 {sleep_time:.2f} 秒，继续爬取下一页")
                time.sleep(sleep_time)

            parse(next_url, remaining_pages - 1 if remaining_pages else None, delay_range, debug=debug)
        else:
            print("已到达最后一页")
    else:
        print("未找到下一页链接")


# ==================== 保存函数 ====================
def save_to_csv(csv_name):
    def clean_field(val):
        if isinstance(val, str):
            return ' '.join(val.strip().splitlines())
        return val

    cleaned_data = {
        '电影名字': [clean_field(x) for x in movie_names],
        '电影链接': [clean_field(x) for x in urls],
        '评分': [clean_field(x) for x in scores],
        '评分人数': [clean_field(x) for x in star_people_nums],
        '导演': [clean_field(x) for x in directors],
        '主演': [clean_field(x) for x in actors],
        '年份': [clean_field(x) for x in years],
        '国家': [clean_field(x) for x in countrys],
        '类型': [clean_field(x) for x in types],
        '一句话评价': [clean_field(x) for x in one_evaluates],
    }

    df = pd.DataFrame(cleaned_data)
    df.to_csv(csv_name, encoding='utf-8-sig', index=False, quoting=csv.QUOTE_ALL)
    print(f"CSV文件保存成功：{csv_name}")


def save_to_json(json_name):
    data = []
    for i in range(len(movie_names)):
        item = {
            '电影名字': clean_text(movie_names[i]) if i < len(movie_names) else '',
            '电影链接': clean_text(urls[i]) if i < len(urls) else '',
            '评分': clean_text(scores[i]) if i < len(scores) else '',
            '评分人数': clean_text(star_people_nums[i]) if i < len(star_people_nums) else '',
            '导演': clean_text(directors[i]) if i < len(directors) else '',
            '主演': clean_text(actors[i]) if i < len(actors) else '',
            '年份': clean_text(years[i]) if i < len(years) else '',
            '国家': clean_text(countrys[i]) if i < len(countrys) else '',
            '类型': clean_text(types[i]) if i < len(types) else '',
            '一句话评价': clean_text(one_evaluates[i]) if i < len(one_evaluates) else '',
        }
        data.append(item)

    with open(json_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, separators=(',', ': '))
    print(f"JSON文件保存成功：{json_name}")


def ensure_extension(filename, ext):
    if not filename.lower().endswith(ext):
        return filename + ext
    return filename


# ==================== 主程序入口 ====================
def main():
    parser = argparse.ArgumentParser(description="豆瓣电影TOP250爬虫")
    parser.add_argument('--pages', type=int, default=10, help='要爬取的页数，每页25部，默认为10（全部）')
    parser.add_argument('--output', type=str, default='豆瓣电影TOP250', help='输出文件名（不包含扩展名），默认为"豆瓣电影TOP250"')
    parser.add_argument('--format', type=str, choices=['csv', 'json'], default='csv', help='输出格式，可选csv或json，默认为csv')
    parser.add_argument('--delay', type=float, nargs=2, default=[3, 8], metavar=('MIN', 'MAX'),
                        help='请求延时范围（秒），默认为3 8')
    parser.add_argument('--no-delay', action='store_true', help='禁用延时（不推荐）')
    parser.add_argument('--debug', action='store_true', help='打印调试信息（title + 第一条li文本片段）')
    args = parser.parse_args()

    delay_range = None if args.no_delay else (args.delay[0], args.delay[1])

    parse(START_URL, remaining_pages=args.pages, delay_range=delay_range, debug=args.debug)

    if not movie_names:
        print("未获取到任何电影数据，请检查网络或页面结构")
        return

    if args.format == 'csv':
        filename = ensure_extension(args.output, '.csv')
        save_to_csv(filename)
    else:
        filename = ensure_extension(args.output, '.json')
        save_to_json(filename)


if __name__ == '__main__':
    main()