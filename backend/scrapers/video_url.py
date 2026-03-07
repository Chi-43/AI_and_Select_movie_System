import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://movie.douban.com/",
}

def fetch_douban_watch_links(douban_url: str):
    """
    抓取豆瓣电影详情页中的观看链接
    返回示例：
    [
        {
            "platform": "咪咕视频",
            "platform_url": "...",
            "icon": "...",
            "price_info": "VIP免费观看"
        }
    ]
    """
    if not douban_url:
        return []

    resp = requests.get(douban_url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    result = []

    # 右侧观看区
    gray_ad = soup.select_one("div.gray-ad")
    if not gray_ad:
        return result

    items = gray_ad.select("ul.bs li")
    for li in items:
        a_tag = li.select_one("a.playBtn")
        if not a_tag:
            continue

        platform_name = a_tag.get("data-cn") or a_tag.get_text(strip=True)
        platform_url = a_tag.get("href", "").strip()

        img_tag = li.select_one("img.vendor-icon")
        icon_url = img_tag.get("src", "").strip() if img_tag else ""

        price_tag = li.select_one("span.buylink-price")
        price_info = price_tag.get_text(" ", strip=True) if price_tag else ""

        if platform_url and platform_url.startswith("//"):
            platform_url = "https:" + platform_url

        result.append({
            "platform": platform_name,
            "platform_url": platform_url,
            "icon": icon_url,
            "price_info": price_info,
        })

    return result