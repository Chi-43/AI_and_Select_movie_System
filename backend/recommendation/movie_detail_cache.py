import json
import os
from typing import Dict, Any


CACHE_FILE = os.path.join(
    os.path.dirname(__file__),
    "data",
    "movie_detail_cache.json"
)


def load_movie_detail_cache() -> Dict[str, Any]:
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_movie_detail_from_cache(douban_url: str) -> Dict[str, Any]:
    cache = load_movie_detail_cache()
    return cache.get(douban_url, {})