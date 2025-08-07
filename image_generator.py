import os
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import base64
import io
from rembg import remove

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def get_emotion_context(phrase):
    """根据短语推断情感上下文，用于优化图像生成"""
    emotion_map = {
        # 问候类
        "你好": "friendly waving gesture, cheerful expression",
        "晚安": "sleepy, yawning, peaceful expression",
        "早上好": "energetic, bright smile, morning mood",
        
        # 情感类  
        "开心": "very happy, big smile, joyful expression",
        "生气": "angry expression, puffed cheeks, frustrated",
        "难过": "sad expression, teary eyes, downcast",
        "爱你": "heart eyes, loving expression, affectionate",
        "想你": "longing expression, missing someone",
        
        # 鼓励类
        "加油": "cheering pose, fist pump, encouraging gesture",
        "棒棒": "thumbs up, proud expression, approval",
        "努力": "determined expression, working hard",
        
        # 礼貌类
        "谢谢": "grateful expression, bowing slightly, thankful",
        "对不起": "apologetic expression, sorry gesture",
        "请": "polite gesture, requesting something nicely",
        
        # 反应类
        "哈哈": "laughing hard, funny expression, entertained",
        "呵呵": "gentle smile, mild amusement",
        "哇": "surprised expression, amazed, shocked",
        "嗯": "thinking expression, contemplative, nodding"
    }
    
    # 匹配最相关的情感
    for key, context in emotion_map.items():
        if key in phrase:
            return context
    
    # 默认表情
    return "cute expression, friendly demeanor"


def dalle_generate(prompt, quality="standard"):
    # 优化的DALL-E提示词，确保适合贴图
    enhanced_prompt = f"""
LINE sticker style illustration: {prompt}
Requirements: simple cartoon style, clean lines, cute kawaii aesthetic, solid colors, minimal details, white or transparent background, centered composition, expressive character suitable for messaging app stickers.
Art style: vector-like illustration, flat design, bold outlines, emoji-like simplicity.
"""
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=enhanced_prompt,
        n=1,
        size="1024x1024",
        quality=quality,
        response_format="b64_json"
    )
    b64_img = response.data[0].b64_json
    img_bytes = base64.b64decode(b64_img)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    return img


def postprocess_image(img, phrase=None, font_path=None):
    try:
        # 先调整尺寸减少内存占用
        img = img.resize((370, 320))
        # 去背景（添加错误处理）
        img = remove(img)
    except Exception as e:
        print(f"⚠️ 背景移除失败，使用原图: {e}")
        # 如果背景移除失败，至少确保尺寸正确
        img = img.resize((370, 320))
    
    # 加短语文字
    if phrase and font_path:
        try:
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(font_path, 42)
            draw.text((10, 260), phrase, font=font, fill="#333")
        except Exception as e:
            print(f"⚠️ 文字添加失败: {e}")
    
    return img


def create_stickers(idea, mock=False, font_path=None, out_dir="output"):
    os.makedirs(out_dir, exist_ok=True)
    stickers = []
    if mock or not OPENAI_API_KEY:
        # 生成 mock 图片（匹配新的8张格式）
        img = Image.new("RGBA", (370, 320), (255, 230, 200, 255))
        stickers = [img.copy() for _ in idea["phrases"][:8]]  # 最多8张
    else:
        # 限制为前8张贴图，符合LINE贴图套装标准
        phrases_to_generate = idea["phrases"][:8]
        for i, phrase in enumerate(phrases_to_generate):
            try:
                print(f"    正在生成第 {i+1}/{len(phrases_to_generate)} 张贴图: {phrase}")
                # 构建详细的提示词
                char_desc = idea.get('character_description', idea['character'])
                emotion_context = get_emotion_context(phrase)
                
                prompt = f"{idea['character']} ({char_desc}), {emotion_context}, {idea['style']}, color palette: {', '.join(idea['palette'])}"
                
                img = dalle_generate(prompt, quality="standard")
                img = postprocess_image(img, phrase=phrase, font_path=font_path)
                stickers.append(img)
                # 释放内存
                del img
            except Exception as e:
                print(f"    ❌ 第 {i+1} 张贴图生成失败: {e}")
                print(f"    🔄 尝试重新生成...")
                # 简化版提示词重试一次
                simple_prompt = f"{idea['character']}, {phrase}, cute sticker style"
                try:
                    img = dalle_generate(simple_prompt, quality="standard")
                    img = postprocess_image(img, phrase=phrase, font_path=font_path)
                    stickers.append(img)
                    del img
                    print(f"    ✅ 重试成功！")
                except:
                    # 最终备用图片
                    backup_img = Image.new("RGBA", (370, 320), (255, 230, 200, 255))
                    stickers.append(backup_img)
                    print(f"    ⚠️ 使用备用图片")
    
    # 保存贴图
    paths = []
    for idx, img in enumerate(stickers, 1):
        path = os.path.join(out_dir, f"{idx:02d}.png")
        img.save(path)
        paths.append(path)
    
    # 生成主图 main.png（缩略第一张）
    main_path = os.path.join(out_dir, "main.png")
    stickers[0].resize((240, 240)).save(main_path)
    
    # 生成 tab.png（头像裁剪）
    tab_path = os.path.join(out_dir, "tab.png")
    stickers[0].crop((0, 0, 96, 74)).save(tab_path)
    
    return paths + [main_path, tab_path]