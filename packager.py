import os
from zipfile import ZipFile
from PIL import Image

def check_image(path, max_size=(370, 320), max_bytes=1024*1024):
    img = Image.open(path)
    # 尺寸校验
    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        raise ValueError(f"{path} 尺寸超限: {img.size}")
    # 透明度校验
    if img.mode != "RGBA":
        raise ValueError(f"{path} 非 RGBA 模式")
    # 单文件大小校验
    if os.path.getsize(path) > max_bytes:
        raise ValueError(f"{path} 文件大于1MB")
    return True

def package_set(image_paths, idea, out_dir="output"):
    """
    image_paths: 贴图图片路径列表（如 01.png ~ 08.png, main.png, tab.png）
    idea: 创意信息（可用于命名）
    out_dir: 输出目录
    """
    os.makedirs(out_dir, exist_ok=True)
    # 校验所有图片
    for p in image_paths:
        check_image(p)
    # 生成 zip 文件名
    set_name = idea.get("character", "sticker_set")
    zip_name = f"{set_name}.zip"
    zip_path = os.path.join(out_dir, zip_name)
    # 打包
    with ZipFile(zip_path, 'w') as z:
        for p in image_paths:
            z.write(p, os.path.basename(p))
    # 整体 ZIP 大小校验
    if os.path.getsize(zip_path) > 60 * 1024 * 1024:
        raise ValueError("ZIP 文件大于 60MB")
    return zip_path