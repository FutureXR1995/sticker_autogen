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
            "character_description": f"一个与{topic}相关的可爱角色",
            "phrases": ["你好", "加油", "哈哈", "谢谢", "晚安", "开心", "生气", "爱你"],
            "style": "kawaii style, simple line art, soft colors",
            "palette": ["#FCE99B", "#FFC1C1", "#334D5C", "#E8F5E8"]
        }

    prompt = f"""
你是一个专业的LINE贴图策划师。请根据热词"{topic}"设计一套原创贴图角色。

要求：
1. 角色设计：创造一个与"{topic}"相关的可爱原创角色，有明确的性格特点
2. 短语选择：提供8个实用的日常短语，涵盖问候、情感、鼓励等场景
3. 视觉风格：简洁可爱，线条清晰，适合小尺寸显示
4. 色彩搭配：3-4个和谐的主色调，避免过于鲜艳

输出JSON格式：
{{
  "character": "角色名（简洁有趣）",
  "character_description": "角色设定和性格特点",
  "phrases": ["实用短语1", "实用短语2", "实用短语3", "实用短语4", "实用短语5", "实用短语6", "实用短语7", "实用短语8"],
  "style": "艺术风格描述（如：kawaii style, simple line art, soft colors）",
  "palette": ["#色码1", "#色码2", "#色码3", "#色码4"]
}}

请确保角色有趣且实用，短语覆盖日常交流场景。"""
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
            "character_description": f"一个与{topic}相关的可爱角色",
            "phrases": ["你好", "加油", "哈哈", "谢谢", "晚安", "开心", "生气", "爱你"],
            "style": "kawaii style, simple line art, soft colors",
            "palette": ["#FCE99B", "#FFC1C1", "#334D5C", "#E8F5E8"]
        }

def make_ideas(topics, mock=False):
    """
    批量生成创意信息
    """
    return [make_idea(topic, mock=mock) for topic in topics]