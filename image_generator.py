import os
import openai
from PIL import Image, ImageDraw, ImageFont
import base64
import io
from rembg import remove

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def dalle_generate(prompt, size="512x512"):
    openai.api_key = OPENAI_API_KEY
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size=size,
        response_format="b64_json"
    )
    b64_img = response['data'][0]['b64_json']
    img_bytes = base64.b64decode(b64_img)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    return img


def postprocess_image(img, phrase=None, font_path=None):
    # 去背景
    img = remove(img)
    # 调整尺寸
    img = img.resize((370, 320))
    # 加短语文字
    if phrase and font_path:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, 42)
        draw.text((10, 260), phrase, font=font, fill="#333")
    return img


def create_stickers(idea, mock=False, font_path=None, out_dir="output"):
    os.makedirs(out_dir, exist_ok=True)
    stickers = []
    if mock or not OPENAI_API_KEY:
        # 生成 mock 图片
        img = Image.new("RGBA", (370, 320), (255, 230, 200, 255))
        stickers = [img.copy() for _ in idea["phrases"]]
    else:
        for phrase in idea["phrases"]:
            prompt = f"{idea['character']}, {idea['style']}, palette: {', '.join(idea['palette'])}"
            img = dalle_generate(prompt)
            img = postprocess_image(img, phrase=phrase, font_path=font_path)
            stickers.append(img)
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