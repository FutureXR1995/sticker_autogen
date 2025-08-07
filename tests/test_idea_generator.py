import pytest
from idea_generator import make_idea, make_ideas


def test_make_idea_mock():
    topic = "猫"
    result = make_idea(topic, mock=True)
    assert isinstance(result, dict)
    assert result["character"].startswith("可爱猫")
    assert isinstance(result["phrases"], list)
    assert isinstance(result["style"], str)
    assert isinstance(result["palette"], list)
    assert all(isinstance(c, str) for c in result["palette"])


def test_make_ideas_mock():
    topics = ["猫", "狗"]
    results = make_ideas(topics, mock=True)
    assert isinstance(results, list)
    assert len(results) == 2
    for res, topic in zip(results, topics):
        assert res["character"].startswith(f"可爱{topic}")


def test_make_idea_no_api_key(monkeypatch):
    # 模拟无 OPENAI_API_KEY 环境变量
    monkeypatch.setenv("OPENAI_API_KEY", "")
    topic = "熊猫"
    result = make_idea(topic)
    assert result["character"].startswith("可爱熊猫")
    assert isinstance(result["phrases"], list)
    assert isinstance(result["style"], str)
    assert isinstance(result["palette"], list)