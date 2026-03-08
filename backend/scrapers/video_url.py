import time
from urllib.parse import urlparse, parse_qs, unquote

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def unwrap_douban_link(url: str) -> str:
    """
    将豆瓣中转链接解码成真实平台链接
    例如：
    https://www.douban.com/link2/?url=https%3A%2F%2Fv.qq.com...
    ->
    https://v.qq.com/...
    """
    if not url:
        return url

    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        real_url = query.get("url", [None])[0]
        return unquote(real_url) if real_url else url
    except Exception:
        return url


def fetch_douban_watch_links(douban_url: str):
    if not douban_url:
        return []

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

        # 等页面主标题出现
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[property="v:itemreviewed"]'))
        )

        # 滚动触发右侧区域懒加载
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.4);")
        time.sleep(1.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
        time.sleep(1.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.select_one('span[property="v:itemreviewed"]')
        movie_title = title_tag.get_text(strip=True) if title_tag else ""

        selector_groups = [
            "div.gray-ad ul.bs li",
            "div.gray-ad li",
            "ul.bs li",
            "a.playBtn",
            "a[class*='playBtn']",
            "[data-cn]",
        ]

        items = []
        matched_selector = None

        for selector in selector_groups:
            found = soup.select(selector)
            if found:
                items = found
                matched_selector = selector
                break

        result = []
        seen = set()

        # 模式1：直接匹配到 a.playBtn / [data-cn]
        if matched_selector in ["a.playBtn", "a[class*='playBtn']", "[data-cn]"]:
            for a_tag in items:
                if a_tag.name != "a":
                    continue

                platform_name = (a_tag.get("data-cn") or a_tag.get_text(strip=True) or "").strip()
                raw_url = a_tag.get("href", "").strip()
                platform_url = unwrap_douban_link(raw_url)

                if platform_url.startswith("//"):
                    platform_url = "https:" + platform_url

                if platform_name and platform_url:
                    key = (platform_name, platform_url)
                    if key in seen:
                        continue
                    seen.add(key)

                    result.append({
                        "movie_title": movie_title,
                        "platform": platform_name,
                        "platform_url": platform_url,
                        "icon": "",
                        "price_info": "",
                    })

            print(f"[DoubanSpider] 抓取成功: {movie_title}, 共 {len(result)} 条")
            return result

        # 模式2：li 容器模式
        for li in items:
            a_tag = li.select_one("a.playBtn") or li.select_one("a[data-cn]") or li.select_one("a")
            if not a_tag:
                continue

            platform_name = (a_tag.get("data-cn") or a_tag.get_text(strip=True) or "").strip()
            raw_url = a_tag.get("href", "").strip()
            platform_url = unwrap_douban_link(raw_url)

            img_tag = li.select_one("img.vendor-icon") or li.select_one("img")
            icon_url = img_tag.get("src", "").strip() if img_tag else ""

            price_tag = li.select_one("span.buylink-price") or li.select_one("span")
            price_info = price_tag.get_text(" ", strip=True) if price_tag else ""

            if platform_url.startswith("//"):
                platform_url = "https:" + platform_url

            if icon_url.startswith("//"):
                icon_url = "https:" + icon_url

            if platform_name and platform_url:
                key = (platform_name, platform_url)
                if key in seen:
                    continue
                seen.add(key)

                result.append({
                    "movie_title": movie_title,
                    "platform": platform_name,
                    "platform_url": platform_url,
                    "icon": icon_url,
                    "price_info": price_info,
                })

        print(f"[DoubanSpider] 抓取成功: {movie_title}, 共 {len(result)} 条")
        return result

    except Exception as e:
        print(f"[DoubanSpider] 抓取失败: {douban_url}, 错误: {str(e)}")
        return []

    finally:
        driver.quit()