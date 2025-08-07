import os
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import base64
import io
from rembg import remove
from line_compliance import LineComplianceChecker, create_line_sticker_prompt

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


def dalle_generate_line_sticker(character, character_desc, phrase, style="kawaii", 
                               palette=None, quality="standard"):
    """专门为LINE贴图优化的DALL-E生成函数"""
    
    # 使用LINE合规的提示词生成器
    optimized_prompt = create_line_sticker_prompt(
        character=character,
        character_desc=character_desc, 
        phrase=phrase,
        style=style,
        palette=palette or []
    )
    
    print(f"🎨 优化后的提示词: {optimized_prompt[:100]}...")
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=optimized_prompt,
        n=1,
        size="1024x1024",
        quality=quality,
        response_format="b64_json"
    )
    b64_img = response.data[0].b64_json
    img_bytes = base64.b64decode(b64_img)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    return img

def dalle_generate(prompt, quality="standard"):
    """保留原有函数以兼容性"""
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


def postprocess_line_sticker(img, phrase=None, font_path=None, sticker_type="static"):
    """专门为LINE贴图进行后处理优化"""
    
    # 初始化合规检查器
    checker = LineComplianceChecker()
    
    try:
        # 调整到LINE标准尺寸
        if sticker_type == "static":
            target_size = (370, 320)
        elif sticker_type == "animated": 
            target_size = (320, 270)
        else:
            target_size = (370, 320)
        
        # 保持宽高比调整尺寸
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # 确保尺寸为偶数像素（LINE要求）
        width, height = img.size
        if width % 2 != 0:
            width += 1
        if height % 2 != 0:
            height += 1
        
        if (width, height) != img.size:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # 背景移除（添加错误处理）
        try:
            img = remove(img)
            print("✅ 背景移除成功")
        except Exception as e:
            print(f"⚠️ 背景移除失败，保持原图: {e}")
        
        # 确保透明背景格式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # LINE贴图不建议添加文字（会影响审核）
        # 如果需要文字，应该在图像生成时包含
        
    except Exception as e:
        print(f"❌ 后处理失败: {e}")
        # 降级处理：至少确保基本格式正确
        img = img.resize((370, 320), Image.Resampling.LANCZOS).convert('RGBA')
    
    return img

def postprocess_image(img, phrase=None, font_path=None):
    """保留原有函数以兼容性"""
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


def create_line_stickers(idea, mock=False, style="kawaii", sticker_count=8, out_dir="output"):
    """专门为LINE贴图生成的优化函数"""
    
    os.makedirs(out_dir, exist_ok=True)
    
    # 初始化合规检查器
    checker = LineComplianceChecker()
    
    # 预先检查内容合规性
    compliance_result = checker.validate_content_compliance(
        prompt=f"{idea['character']} {idea.get('character_description', '')}",
        character_name=idea['character'],
        description=idea.get('character_description', '')
    )
    
    if not compliance_result['valid']:
        print("❌ 内容不符合LINE审核标准:")
        for issue in compliance_result['issues']:
            print(f"  - {issue}")
        return []
    
    print(f"✅ 内容合规检查通过 (风险等级: {compliance_result['risk_level']})")
    
    stickers = []
    generated_images = []
    
    if mock or not OPENAI_API_KEY:
        # 生成 mock 图片
        for i in range(sticker_count):
            img = Image.new("RGBA", (370, 320), (255, 230, 200, 255))
            stickers.append(img)
        print(f"🎭 生成了 {sticker_count} 张mock贴图")
    else:
        # 限制贴图数量为LINE标准
        if sticker_count not in [8, 16, 24]:
            print(f"⚠️ 调整贴图数量从 {sticker_count} 到 8 张（LINE标准）")
            sticker_count = 8
        
        phrases_to_generate = idea["phrases"][:sticker_count]
        
        for i, phrase in enumerate(phrases_to_generate):
            try:
                print(f"🎨 正在生成第 {i+1}/{len(phrases_to_generate)} 张贴图: {phrase}")
                
                # 使用LINE优化的生成函数
                img = dalle_generate_line_sticker(
                    character=idea['character'],
                    character_desc=idea.get('character_description', ''),
                    phrase=phrase,
                    style=style,
                    palette=idea.get('palette', []),
                    quality="standard"
                )
                
                # 使用LINE优化的后处理
                processed_img = postprocess_line_sticker(img, phrase=phrase, sticker_type="static")
                stickers.append(processed_img)
                generated_images.append(processed_img.copy())
                
                # 释放内存
                del img
                
                print(f"    ✅ 第 {i+1} 张贴图生成成功")
                
            except Exception as e:
                print(f"    ❌ 第 {i+1} 张贴图生成失败: {e}")
                print(f"    🔄 尝试重新生成...")
                
                # 简化版重试
                try:
                    simple_img = dalle_generate(f"{idea['character']}, {phrase}, cute LINE sticker style")
                    processed_img = postprocess_line_sticker(simple_img, phrase=phrase)
                    stickers.append(processed_img)
                    generated_images.append(processed_img.copy())
                    del simple_img
                    print(f"    ✅ 重试成功！")
                except:
                    # 最终备用图片
                    backup_img = Image.new("RGBA", (370, 320), (255, 200, 200, 255))
                    stickers.append(backup_img)
                    print(f"    ⚠️ 使用备用图片")
    
    # 保存贴图文件（LINE标准命名）
    paths = []
    for idx, img in enumerate(stickers, 1):
        filename = f"{idx:02d}.png"
        path = os.path.join(out_dir, filename)
        img.save(path, 'PNG', optimize=True)
        paths.append(path)
        
        # 验证生成的文件是否符合LINE规格
        if not mock:
            validation = checker.validate_image_specs(path, "static")
            if not validation['valid']:
                print(f"⚠️ {filename} 规格问题: {', '.join(validation['issues'])}")
            if validation['suggestions']:
                print(f"💡 {filename} 建议: {', '.join(validation['suggestions'])}")
    
    # 生成main.png（LINE要求：240×240）
    main_path = os.path.join(out_dir, "main.png")
    main_img = stickers[0].copy()
    main_img = main_img.resize((240, 240), Image.Resampling.LANCZOS)
    main_img.save(main_path, 'PNG', optimize=True)
    
    # 生成tab.png（LINE要求：96×74）
    tab_path = os.path.join(out_dir, "tab.png")
    tab_img = stickers[0].copy()
    # 智能裁剪：从中心区域提取最具代表性的部分
    width, height = tab_img.size
    # 计算居中裁剪区域
    crop_width = min(width, int(height * 96/74))
    crop_height = min(height, int(width * 74/96))
    left = (width - crop_width) // 2
    top = (height - crop_height) // 2
    tab_img = tab_img.crop((left, top, left + crop_width, top + crop_height))
    tab_img = tab_img.resize((96, 74), Image.Resampling.LANCZOS)
    tab_img.save(tab_path, 'PNG', optimize=True)
    
    # 返回完整的文件列表
    all_paths = paths + [main_path, tab_path]
    
    print(f"🎉 LINE贴图生成完成！")
    print(f"📁 输出目录: {out_dir}")
    print(f"📊 生成文件: {len(all_paths)} 个")
    print(f"   - 贴图: {len(paths)} 张")
    print(f"   - 主图: main.png")
    print(f"   - 标签: tab.png")
    
    return all_paths

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