import os
import json
from zipfile import ZipFile
from PIL import Image
from datetime import datetime
from line_compliance import LineComplianceChecker

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

def package_line_stickers(image_paths, idea, out_dir="output", sticker_type="static"):
    """
    专门为LINE贴图打包的函数，完全符合LINE Creators Market要求
    
    Args:
        image_paths: 贴图文件路径列表 
        idea: 创意信息字典
        out_dir: 输出目录
        sticker_type: 贴图类型 ("static", "animated", "popup", "effect")
    
    Returns:
        tuple: (zip_path, package_info)
    """
    os.makedirs(out_dir, exist_ok=True)
    
    # 初始化合规检查器
    checker = LineComplianceChecker()
    
    # 验证文件完整性
    required_files = []
    sticker_files = []
    main_file = None
    tab_file = None
    
    print("🔍 开始LINE贴图打包验证...")
    
    for path in image_paths:
        filename = os.path.basename(path)
        
        if filename == "main.png":
            main_file = path
            # 验证main.png规格 (240x240)
            validation = checker.validate_image_specs(path, "main")
            if not validation['valid']:
                print(f"❌ main.png 规格问题: {', '.join(validation['issues'])}")
                return None, {"error": f"main.png规格不符合要求: {validation['issues']}"}
                
        elif filename == "tab.png":
            tab_file = path
            # 验证tab.png规格 (96x74)
            validation = checker.validate_image_specs(path, "tab")
            if not validation['valid']:
                print(f"❌ tab.png 规格问题: {', '.join(validation['issues'])}")
                return None, {"error": f"tab.png规格不符合要求: {validation['issues']}"}
                
        elif filename.endswith('.png') and filename[:-4].isdigit():
            sticker_files.append(path)
            # 验证贴图规格
            validation = checker.validate_image_specs(path, sticker_type)
            if not validation['valid']:
                print(f"❌ {filename} 规格问题: {', '.join(validation['issues'])}")
                return None, {"error": f"{filename}规格不符合要求: {validation['issues']}"}
            
            if validation['suggestions']:
                print(f"💡 {filename} 建议: {', '.join(validation['suggestions'])}")
    
    # 检查必需文件
    if not main_file:
        return None, {"error": "缺少必需的 main.png 文件"}
    if not tab_file:
        return None, {"error": "缺少必需的 tab.png 文件"}
    
    # 检查贴图数量
    sticker_count = len(sticker_files)
    if sticker_count not in [8, 16, 24]:
        return None, {"error": f"贴图数量 {sticker_count} 不符合LINE要求（8/16/24张）"}
    
    print(f"✅ 文件验证通过: {sticker_count}张贴图 + main.png + tab.png")
    
    # 生成ZIP文件名（加入时间戳避免重复）
    character_name = idea.get("character", "sticker_set").replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"LINE_{character_name}_{sticker_count}stickers_{timestamp}.zip"
    zip_path = os.path.join(out_dir, zip_name)
    
    # 创建LINE标准包结构
    print("📦 创建LINE标准ZIP包...")
    
    # 生成元数据
    metadata = {
        "package_info": {
            "creator": "AI Sticker Generator",
            "character": idea.get("character", ""),
            "character_description": idea.get("character_description", ""),
            "style": idea.get("style", "kawaii"),
            "phrases": idea.get("phrases", [])[:sticker_count],
            "palette": idea.get("palette", []),
            "sticker_count": sticker_count,
            "sticker_type": sticker_type,
            "ai_generated": True,
            "created_at": datetime.now().isoformat(),
            "line_specs": {
                "static_size": "370x320",
                "main_size": "240x240", 
                "tab_size": "96x74",
                "format": "PNG",
                "background": "transparent"
            }
        }
    }
    
    # 创建临时元数据文件
    metadata_path = os.path.join(out_dir, "metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    try:
        with ZipFile(zip_path, 'w') as z:
            # 添加贴图文件（按标准顺序）
            sticker_files.sort(key=lambda x: int(os.path.basename(x)[:-4]))
            for path in sticker_files:
                z.write(path, os.path.basename(path))
            
            # 添加必需文件
            z.write(main_file, "main.png")
            z.write(tab_file, "tab.png")
            
            # 添加元数据（可选，便于管理）
            z.write(metadata_path, "metadata.json")
        
        # 清理临时文件
        os.remove(metadata_path)
        
        # 验证ZIP包大小
        zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        if zip_size_mb > 60:
            os.remove(zip_path)
            return None, {"error": f"ZIP包过大: {zip_size_mb:.2f}MB，最大限制60MB"}
        
        print(f"✅ ZIP包创建成功!")
        print(f"📁 文件: {zip_name}")
        print(f"📊 大小: {zip_size_mb:.2f}MB")
        
        package_info = {
            "zip_path": zip_path,
            "zip_name": zip_name,
            "size_mb": zip_size_mb,
            "sticker_count": sticker_count,
            "sticker_type": sticker_type,
            "character": idea.get("character", ""),
            "created_at": datetime.now().isoformat(),
            "line_ready": True
        }
        
        return zip_path, package_info
        
    except Exception as e:
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        return None, {"error": f"打包失败: {str(e)}"}

def package_set(image_paths, idea, out_dir="output"):
    """保留原有函数以兼容性"""
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

def validate_line_package(zip_path):
    """验证ZIP包是否符合LINE要求"""
    
    checker = LineComplianceChecker()
    validation_result = {
        "valid": True,
        "issues": [],
        "suggestions": [],
        "file_count": 0,
        "package_size_mb": 0
    }
    
    try:
        # 检查ZIP包大小
        size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        validation_result["package_size_mb"] = size_mb
        
        if size_mb > 60:
            validation_result["valid"] = False
            validation_result["issues"].append(f"ZIP包过大: {size_mb:.2f}MB（最大60MB）")
        
        # 检查ZIP包内容
        with ZipFile(zip_path, 'r') as z:
            file_list = z.namelist()
            validation_result["file_count"] = len(file_list)
            
            # 检查必需文件
            if "main.png" not in file_list:
                validation_result["valid"] = False
                validation_result["issues"].append("缺少 main.png")
                
            if "tab.png" not in file_list:
                validation_result["valid"] = False
                validation_result["issues"].append("缺少 tab.png")
            
            # 统计贴图文件
            sticker_files = [f for f in file_list if f.endswith('.png') and f not in ['main.png', 'tab.png']]
            sticker_count = len(sticker_files)
            
            if sticker_count not in [8, 16, 24]:
                validation_result["valid"] = False
                validation_result["issues"].append(f"贴图数量错误: {sticker_count}（应为8/16/24）")
            
            # 检查文件命名规范
            expected_names = [f"{i:02d}.png" for i in range(1, sticker_count + 1)]
            for expected in expected_names:
                if expected not in file_list:
                    validation_result["issues"].append(f"缺少文件: {expected}")
    
    except Exception as e:
        validation_result["valid"] = False
        validation_result["issues"].append(f"ZIP文件读取错误: {str(e)}")
    
    return validation_result