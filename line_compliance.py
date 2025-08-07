"""
LINE贴图合规性检查和规格优化模块
确保生成的贴图符合LINE Creators Market的所有要求
"""
import os
from PIL import Image, ImageOps
import re
from typing import Dict, List, Tuple, Optional

class LineComplianceChecker:
    """LINE贴图合规性检查器"""
    
    # LINE贴图规格常量
    STATIC_SIZE = (370, 320)  # 静态贴图最大尺寸
    MAIN_SIZE = (240, 240)    # 主图尺寸
    TAB_SIZE = (96, 74)       # 标签图尺寸
    
    ANIMATED_SIZE = (320, 270)  # 动态贴图最大尺寸
    POPUP_SIZE = (480, 480)     # 弹出贴图最大尺寸
    
    MAX_FILE_SIZE_MB = 1        # 单个文件最大1MB
    MAX_ZIP_SIZE_MB = 60        # ZIP包最大60MB
    
    # 禁止的内容关键词（版权风险）
    FORBIDDEN_KEYWORDS = [
        'mickey', 'disney', 'pokemon', 'pikachu', 'mario', 'sonic', 
        'hello kitty', 'doraemon', 'naruto', 'dragon ball', 'one piece',
        'marvel', 'batman', 'superman', 'spiderman', 'frozen', 'elsa',
        'minions', 'totoro', 'princess', 'coca-cola', 'pepsi', 'nike',
        'adidas', 'apple', 'google', 'facebook', 'instagram', 'tiktok'
    ]
    
    def __init__(self):
        self.check_results = {}
    
    def validate_image_specs(self, image_path: str, sticker_type: str = "static") -> Dict:
        """验证图片规格是否符合LINE要求"""
        result = {
            "valid": True,
            "issues": [],
            "suggestions": []
        }
        
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
                
                # 检查格式
                if img.format != 'PNG':
                    result["valid"] = False
                    result["issues"].append(f"格式错误: {img.format}，应为PNG")
                
                # 检查尺寸
                max_size = self._get_max_size(sticker_type)
                if width > max_size[0] or height > max_size[1]:
                    result["valid"] = False
                    result["issues"].append(f"尺寸超限: {width}×{height}，最大{max_size[0]}×{max_size[1]}")
                
                # 检查像素是否为偶数（LINE要求）
                if width % 2 != 0 or height % 2 != 0:
                    result["suggestions"].append("建议调整尺寸为偶数像素以保证缩放质量")
                
                # 检查文件大小
                if file_size_mb > self.MAX_FILE_SIZE_MB:
                    result["valid"] = False
                    result["issues"].append(f"文件过大: {file_size_mb:.2f}MB，最大{self.MAX_FILE_SIZE_MB}MB")
                
                # 检查透明背景
                if img.mode != 'RGBA':
                    result["suggestions"].append("建议使用RGBA模式以支持透明背景")
                
                # 检查是否有透明通道
                if img.mode == 'RGBA':
                    alpha = img.split()[-1]
                    if alpha.getextrema()[0] == 255:  # 没有透明区域
                        result["suggestions"].append("建议添加透明背景以符合LINE贴图标准")
                
                # 检查图片是否过于简单（纯色或文字）
                if self._is_too_simple(img):
                    result["issues"].append("图片过于简单，可能不符合LINE审核标准")
                
        except Exception as e:
            result["valid"] = False
            result["issues"].append(f"文件读取错误: {str(e)}")
        
        return result
    
    def validate_content_compliance(self, prompt: str, character_name: str = "", description: str = "") -> Dict:
        """验证内容是否符合LINE审核标准"""
        result = {
            "valid": True,
            "issues": [],
            "risk_level": "low"  # low, medium, high
        }
        
        # 检查版权风险关键词
        text_to_check = f"{prompt} {character_name} {description}".lower()
        found_keywords = []
        
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in text_to_check:
                found_keywords.append(keyword)
        
        if found_keywords:
            result["valid"] = False
            result["risk_level"] = "high"
            result["issues"].append(f"包含版权风险关键词: {', '.join(found_keywords)}")
        
        # 检查不当内容
        inappropriate_patterns = [
            r'(naked|nude|sex|porn)',  # 成人内容
            r'(kill|murder|blood)',  # 暴力内容
            r'(nazi|hitler|terrorist)',  # 极端内容
            r'(drug|cocaine|marijuana)',  # 毒品内容
            r'(violent|fighting)',  # 暴力相关
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                result["valid"] = False
                result["risk_level"] = "high"
                result["issues"].append(f"包含不当内容: {pattern}")
        
        # 检查是否适合日常对话使用
        if len(character_name) > 20:
            result["issues"].append("角色名过长，建议简化")
        
        return result
    
    def optimize_for_line(self, image_path: str, sticker_type: str = "static") -> str:
        """优化图片以符合LINE规格"""
        optimized_path = image_path.replace('.png', '_line_optimized.png')
        
        with Image.open(image_path) as img:
            # 确保是RGBA模式
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 调整尺寸
            max_size = self._get_max_size(sticker_type)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 确保尺寸为偶数
            width, height = img.size
            if width % 2 != 0:
                width += 1
            if height % 2 != 0:
                height += 1
            
            if (width, height) != img.size:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # 优化透明背景
            img = self._enhance_transparency(img)
            
            # 保存优化后的图片
            img.save(optimized_path, 'PNG', optimize=True)
        
        return optimized_path
    
    def generate_line_package_structure(self, images: List[str], main_image: str, 
                                      tab_image: str, sticker_count: int = 8) -> Dict:
        """生成符合LINE要求的包结构"""
        if sticker_count not in [8, 16, 24]:
            raise ValueError("贴图数量必须是8、16或24张")
        
        package_structure = {
            "stickers": {},
            "main.png": main_image,
            "tab.png": tab_image,
            "metadata": {
                "sticker_count": sticker_count,
                "type": "static",
                "ai_generated": True
            }
        }
        
        # 按01.png, 02.png...格式命名
        for i, image_path in enumerate(images[:sticker_count], 1):
            filename = f"{i:02d}.png"
            package_structure["stickers"][filename] = image_path
        
        return package_structure
    
    def _get_max_size(self, sticker_type: str) -> Tuple[int, int]:
        """获取指定类型贴图的最大尺寸"""
        size_map = {
            "static": self.STATIC_SIZE,
            "animated": self.ANIMATED_SIZE,
            "popup": self.POPUP_SIZE,
            "main": self.MAIN_SIZE,
            "tab": self.TAB_SIZE
        }
        return size_map.get(sticker_type, self.STATIC_SIZE)
    
    def _is_too_simple(self, img: Image.Image) -> bool:
        """检查图片是否过于简单"""
        # 转换为灰度检查颜色数量
        gray = img.convert('L')
        colors = len(gray.getcolors(maxcolors=256) or [])
        
        # 如果颜色数量太少，可能过于简单
        return colors < 5
    
    def _enhance_transparency(self, img: Image.Image) -> Image.Image:
        """增强透明背景效果"""
        if img.mode != 'RGBA':
            return img
        
        # 简单的边缘透明化处理
        # 这里可以添加更复杂的背景移除逻辑
        return img


class LinePromptOptimizer:
    """LINE贴图AI提示词优化器"""
    
    def __init__(self):
        self.style_templates = {
            "kawaii": "cute kawaii style, soft pastel colors, rounded features, big eyes, simple design",
            "minimal": "minimalist design, clean lines, simple shapes, solid colors, modern aesthetic",
            "chibi": "chibi style, super deformed, oversized head, small body, adorable proportions",
            "mascot": "mascot character style, friendly appearance, corporate-safe, approachable design",
            "emoji": "emoji-like style, clear emotion, simple expression, universal understanding"
        }
    
    def optimize_prompt_for_line(self, base_prompt: str, emotion: str, style: str = "kawaii") -> str:
        """优化AI提示词以符合LINE审核标准"""
        
        # 基础LINE贴图要求
        line_requirements = [
            "LINE sticker style",
            "transparent background",
            "clear emotion expression",
            "suitable for daily conversation",
            "no text overlay",
            "family-friendly content",
            "vector-like illustration",
            "centered composition"
        ]
        
        # 获取风格模板
        style_desc = self.style_templates.get(style, self.style_templates["kawaii"])
        
        # 构建优化后的提示词
        optimized_prompt = f"""
        {base_prompt}, expressing {emotion}
        Style: {style_desc}
        Requirements: {', '.join(line_requirements)}
        Technical: 370x320 pixels max, PNG format, high contrast for small size display
        Avoid: copyrighted characters, text, complex details, inappropriate content
        """
        
        return optimized_prompt.strip()
    
    def suggest_emotion_context(self, phrase: str) -> Dict:
        """根据短语建议情感上下文"""
        emotion_mapping = {
            # 问候类
            "你好": {"emotion": "friendly greeting", "gesture": "waving hand", "expression": "bright smile"},
            "早上好": {"emotion": "energetic morning", "gesture": "stretching arms", "expression": "refreshed"},
            "晚安": {"emotion": "sleepy goodnight", "gesture": "yawning", "expression": "peaceful drowsy"},
            
            # 情感类
            "开心": {"emotion": "very happy", "gesture": "jumping with joy", "expression": "big smile with sparkles"},
            "难过": {"emotion": "sad disappointed", "gesture": "hands to face", "expression": "teary eyes"},
            "生气": {"emotion": "angry frustrated", "gesture": "puffed cheeks", "expression": "frowning eyebrows"},
            "爱你": {"emotion": "loving affectionate", "gesture": "heart hands", "expression": "heart eyes"},
            
            # 鼓励类
            "加油": {"emotion": "encouraging cheering", "gesture": "fist pump", "expression": "determined confident"},
            "棒棒": {"emotion": "praising approval", "gesture": "thumbs up", "expression": "proud satisfied"},
            
            # 礼貌类
            "谢谢": {"emotion": "grateful thankful", "gesture": "bowing slightly", "expression": "warm appreciation"},
            "对不起": {"emotion": "apologetic sorry", "gesture": "hands together", "expression": "regretful sincere"},
            
            # 反应类
            "哈哈": {"emotion": "laughing amused", "gesture": "holding belly", "expression": "laughing hard"},
            "哇": {"emotion": "surprised amazed", "gesture": "hands to cheeks", "expression": "wide eyes shocked"},
            "嗯": {"emotion": "thinking contemplative", "gesture": "finger to chin", "expression": "thoughtful"}
        }
        
        # 查找最匹配的情感
        for key, context in emotion_mapping.items():
            if key in phrase:
                return context
        
        # 默认情感
        return {"emotion": "friendly cheerful", "gesture": "natural pose", "expression": "pleasant smile"}


def create_line_sticker_prompt(character: str, character_desc: str, phrase: str, 
                              style: str = "kawaii", palette: List[str] = None) -> str:
    """创建专门用于LINE贴图的优化提示词"""
    
    optimizer = LinePromptOptimizer()
    emotion_context = optimizer.suggest_emotion_context(phrase)
    
    base_prompt = f"""
    {character} ({character_desc}), {emotion_context['emotion']}, 
    {emotion_context['gesture']}, {emotion_context['expression']}
    """
    
    if palette:
        base_prompt += f", color palette: {', '.join(palette)}"
    
    return optimizer.optimize_prompt_for_line(base_prompt, emotion_context['emotion'], style)


# 测试函数
def test_line_compliance():
    """测试合规性检查功能"""
    checker = LineComplianceChecker()
    
    # 测试内容合规性
    test_prompts = [
        ("cute cat expressing happiness", "小猫咪", "一只可爱的小猫"),  # 正常
        ("mickey mouse style character", "米老鼠", "迪士尼风格"),    # 版权风险
        ("violent fighting scene", "战斗", "暴力场面")              # 内容不当
    ]
    
    print("🔍 LINE合规性检查测试:")
    for prompt, name, desc in test_prompts:
        result = checker.validate_content_compliance(prompt, name, desc)
        print(f"提示词: {prompt}")
        print(f"结果: {'✅ 通过' if result['valid'] else '❌ 不通过'}")
        print(f"风险等级: {result['risk_level']}")
        if result['issues']:
            print(f"问题: {', '.join(result['issues'])}")
        print("-" * 50)


if __name__ == "__main__":
    test_line_compliance()
