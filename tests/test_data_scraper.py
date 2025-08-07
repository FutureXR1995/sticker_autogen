import os
import pytest
import json
from unittest import mock
from data_scraper import get_hot_topics, CACHE_FILE


def test_get_hot_topics_cache(tmp_path, monkeypatch):
    # 模拟缓存命中
    cache_file = tmp_path / "hot_topics_cache.json"
    monkeypatch.setattr("data_scraper.CACHE_FILE", str(cache_file))
    topics = ["测试热词1", "测试热词2"]
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump({'ts': 9999999999, 'topics': topics}, f)
    result = get_hot_topics()
    assert result == topics


def test_get_hot_topics_refresh(monkeypatch):
    # 模拟无缓存，mock 各数据源
    monkeypatch.setattr("data_scraper.get_google_trends", lambda: ["A"])
    monkeypatch.setattr("data_scraper.get_twitter_trends", lambda: ["B"])
    monkeypatch.setattr("data_scraper.get_line_news_trends", lambda: ["C"])
    monkeypatch.setattr("data_scraper.CACHE_FILE", "/tmp/hot_topics_cache.json")
    result = get_hot_topics(force_refresh=True)
    assert set(result) == {"A", "B", "C"}


def test_get_hot_topics_all_empty(monkeypatch):
    # 所有数据源都返回空
    monkeypatch.setattr("data_scraper.get_google_trends", lambda: [])
    monkeypatch.setattr("data_scraper.get_twitter_trends", lambda: [])
    monkeypatch.setattr("data_scraper.get_line_news_trends", lambda: [])
    monkeypatch.setattr("data_scraper.CACHE_FILE", "/tmp/hot_topics_cache2.json")
    result = get_hot_topics(force_refresh=True)
    assert result == []


def test_get_hot_topics_exception(monkeypatch):
    # 某数据源抛异常
    monkeypatch.setattr("data_scraper.get_google_trends", lambda: 1/0)
    monkeypatch.setattr("data_scraper.get_twitter_trends", lambda: ["B"])
    monkeypatch.setattr("data_scraper.get_line_news_trends", lambda: ["C"])
    monkeypatch.setattr("data_scraper.CACHE_FILE", "/tmp/hot_topics_cache3.json")
    result = get_hot_topics(force_refresh=True)
    assert set(result) == {"B", "C"}