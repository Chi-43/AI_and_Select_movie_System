import time
import re
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _split_names(value: str):
    if not value:
        return []
    return [item.strip() for item in re.split(r"[ /]+", value) if item.strip()]


def fetch_douban_movie_detail(douban_url: str):
    if not douban_url:
        return {}

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

    driver = webdriver.Edge(options=options)

    try:
        driver.get(douban_url)
        wait = WebDriverWait(driver, 15)

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[property="v:itemreviewed"]'))
        )

        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.select_one('span[property="v:itemreviewed"]')
        movie_title_full = title_tag.get_text(strip=True) if title_tag else ""

        title_text = soup.title.get_text(strip=True) if soup.title else ""
        english_title = ""
        if movie_title_full and movie_title_full in title_text:
            english_title = title_text.replace(movie_title_full, "").replace("(豆瓣)", "").strip()
        else:
            english_title = ""

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

        info_text = soup.select_one("#info")
        info_text = info_text.get_text("\n", strip=True) if info_text else ""

        writer = []
        countries = []
        languages = []
        aka = []
        imdb = ""

        lines = [line.strip() for line in info_text.split("\n") if line.strip()]
        for i, line in enumerate(lines):
            if "编剧" in line:
                if i + 1 < len(lines):
                    writer = _split_names(lines[i + 1])
            elif "制片国家/地区" in line:
                if i + 1 < len(lines):
                    countries = _split_names(lines[i + 1])
            elif "语言" in line:
                if i + 1 < len(lines):
                    languages = _split_names(lines[i + 1])
            elif "又名" in line:
                if i + 1 < len(lines):
                    aka = _split_names(lines[i + 1])
            elif "IMDb" in line:
                if i + 1 < len(lines):
                    imdb = lines[i + 1]

        return {
            "movie_title": movie_title_full,
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
            "source": "douban_spider",
        }

    except Exception as e:
        print(f"[MovieDetailSpider] 抓取失败: {douban_url}, 错误: {str(e)}")
        return {}

    finally:
        driver.quit()