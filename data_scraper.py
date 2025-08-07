import os
import json
import time
from typing import List

# Google Trends
from pytrends.request import TrendReq
# Twitter
import tweepy
# LINE NEWS/Creators
import requests
from bs4 import BeautifulSoup

CACHE_FILE = os.path.join(os.path.dirname(__file__), 'hot_topics_cache.json')
CACHE_TTL = 60 * 60  # 1小时

# 读取环境变量
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')


def get_google_trends() -> List[str]:
    try:
        pytrend = TrendReq(hl="ja-JP", tz=540)
        kw_df = pytrend.trending_searches(pn="japan").head(20)
        return kw_df[0].tolist()
    except Exception as e:
        print(f"[GoogleTrends] 抓取失败: {e}")
        return []


def get_twitter_trends() -> List[str]:
    if not TWITTER_BEARER_TOKEN:
        print("[Twitter] 未配置 TWITTER_BEARER_TOKEN，跳过 Twitter 热词抓取。")
        return []
    try:
        client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        # 日本 WOEID: 23424856
        trends = client.get_place_trends(id=23424856)
        return [t['name'] for t in trends[0]['trends'][:20]]
    except Exception as e:
        print(f"[Twitter] 抓取失败: {e}")
        return []


def get_line_news_trends() -> List[str]:
    url = "https://news.line.me/issue/topstories"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        # 解析新闻标题
        titles = [t.get_text(strip=True) for t in soup.find_all('span', class_='mdMN05Ttl')]
        return titles[:20]
    except Exception as e:
        print(f"[LINE NEWS] 抓取失败: {e}")
        return []


def load_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if time.time() - data.get('ts', 0) < CACHE_TTL:
            return data
    except Exception:
        pass
    return {}


def save_cache(topics: List[str]):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'ts': time.time(), 'topics': topics}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Cache] 保存失败: {e}")


def get_hot_topics(force_refresh=False) -> List[str]:
    topics = set()
    if not force_refresh:
        cache = load_cache()
        if cache.get('topics'):
            return cache['topics']
    try:
        topics.update(get_google_trends())
    except Exception as e:
        pass  # 或 print(f"get_google_trends error: {e}")
    try:
        topics.update(get_twitter_trends())
    except Exception as e:
        pass
    try:
        topics.update(get_line_news_trends())
    except Exception as e:
        pass
    
    # 如果没有获取到任何热词，使用默认热词
    if not topics:
        topics = {"春天", "樱花", "猫咪", "工作", "周末", "咖啡", "雨天", "晴天"}
        print("🔄 使用默认热词作为 fallback")
    
    topics = [t for t in topics if t and len(t) <= 20]
    save_cache(topics)
    return topics


if __name__ == "__main__":
    print("今日热词：")
    for i, t in enumerate(get_hot_topics(), 1):
        print(f"{i}. {t}")