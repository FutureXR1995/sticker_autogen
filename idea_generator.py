import os
from openai import OpenAI
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def make_idea(topic, mock=False):
    """
    输入一个热词，返回一组创意信息（角色、短语、风格、色板等）
    """
    if mock or not OPENAI_API_KEY:
        # 本地 mock，便于测试
        return {
            "character": f"可爱{topic}君",
            "phrases": ["你好", "加油", "哈哈"],
            "style": "flat pastel, bold outline",
            "palette": ["#FCE99B", "#FFC1C1", "#334D5C"]
        }

    prompt = f"""
你是一个LINE贴图策划师。请根据今日热词"{topic}"，输出一组原创角色创意，要求：
1. 角色原创且可爱，适合LINE贴图；
2. 输出JSON，字段包括 character（角色名）、phrases（短语列表）、style（风格描述）、palette（主色板，HEX数组）。
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,
            max_tokens=512
        )
        idea = json.loads(resp.choices[0].message.content)
        return idea
    except Exception as e:
        print(f"openai api error: {e}")
        # 失败时可返回 mock
        return {
            "character": f"可爱{topic}君",
            "phrases": ["你好", "加油", "哈哈"],
            "style": "flat pastel, bold outline",
            "palette": ["#FCE99B", "#FFC1C1", "#334D5C"]
        }

def make_ideas(topics, mock=False):
    """
    批量生成创意信息
    """
    return [make_idea(topic, mock=mock) for topic in topics]