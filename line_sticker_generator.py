#!/usr/bin/env python3
"""
LINE贴图定制生成器 - 主程序
专门用于生成符合LINE Creators Market标准的贴图套装
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# 导入核心模块
from data_scraper import get_hot_topics
from idea_generator import make_ideas, make_idea
from image_generator import create_line_stickers
from packager import package_line_stickers, validate_line_package
from line_compliance import LineComplianceChecker, create_line_sticker_prompt
from notifier import send_line_messaging, send_discord_notify, send_telegram_notify, send_email_notify


class LineStickerGenerator:
    """LINE贴图生成器主类"""
    
    def __init__(self):
        self.checker = LineComplianceChecker()
        self.generated_packages = []
        
    def interactive_mode(self):
        """交互式模式：用户自定义贴图内容"""
        
        print("🎨 LINE贴图定制生成器")
        print("=" * 50)
        print("欢迎使用AI贴图定制服务！让我们一起创造专属于你的LINE贴图吧！")
        print()
        
        # 收集用户需求
        print("📝 第一步：告诉我你想要什么样的贴图角色")
        
        while True:
            character = input("🐱 角色名称 (例如：小猫咪、我家的狗狗): ").strip()
            if character:
                break
            print("请输入角色名称")
        
        while True:
            description = input("📖 角色描述 (例如：一只爱睡觉的橘猫): ").strip()
            if description:
                break
            print("请描述一下你的角色")
        
        # 预检查内容合规性
        compliance = self.checker.validate_content_compliance(
            prompt=f"{character} {description}",
            character_name=character,
            description=description
        )
        
        if not compliance['valid']:
            print("❌ 很抱歉，你的角色设定包含了一些不适合的内容：")
            for issue in compliance['issues']:
                print(f"  - {issue}")
            print("\n💡 建议修改后重新尝试，或者选择其他角色设定。")
            return None
        
        print(f"✅ 角色设定检查通过！(风险等级: {compliance['risk_level']})")
        
        # 选择风格
        print("\n🎭 第二步：选择贴图风格")
        styles = {
            "1": ("kawaii", "可爱萌系 - 大眼睛、圆润、色彩柔和"),
            "2": ("minimal", "简约现代 - 线条简洁、色彩简单"),
            "3": ("chibi", "Q版萌化 - 大头小身、超级可爱"),
            "4": ("mascot", "吉祥物风 - 友好亲切、企业级可用"),
            "5": ("emoji", "表情包风 - 情感明确、通用易懂")
        }
        
        print("可选风格：")
        for key, (style, desc) in styles.items():
            print(f"  {key}. {desc}")
        
        while True:
            choice = input("请选择风格 (1-5): ").strip()
            if choice in styles:
                selected_style = styles[choice][0]
                print(f"✅ 已选择：{styles[choice][1]}")
                break
            print("请输入有效的选择 (1-5)")
        
        # 选择贴图数量
        print("\n📊 第三步：选择贴图数量")
        counts = {
            "1": (8, "基础套装 - 8张贴图 (约3.3元)"),
            "2": (16, "标准套装 - 16张贴图 (约6.6元)"),
            "3": (24, "豪华套装 - 24张贴图 (约9.9元)")
        }
        
        print("可选数量：")
        for key, (count, desc) in counts.items():
            print(f"  {key}. {desc}")
        
        while True:
            choice = input("请选择数量 (1-3): ").strip()
            if choice in counts:
                sticker_count = counts[choice][0]
                print(f"✅ 已选择：{counts[choice][1]}")
                break
            print("请输入有效的选择 (1-3)")
        
        # 自定义短语（可选）
        print("\n💬 第四步：自定义常用短语 (可选)")
        print("我们会自动生成适合的短语，你也可以添加自己想要的：")
        
        custom_phrases = []
        while len(custom_phrases) < sticker_count:
            phrase = input(f"短语 {len(custom_phrases)+1}/{sticker_count} (直接回车跳过): ").strip()
            if not phrase:
                break
            custom_phrases.append(phrase)
        
        # 构建创意对象
        idea = {
            "character": character,
            "character_description": description,
            "style": f"{selected_style} style, cute, friendly, LINE sticker optimized",
            "palette": self._get_style_palette(selected_style),
            "phrases": custom_phrases if custom_phrases else self._generate_default_phrases(sticker_count)
        }
        
        if len(idea["phrases"]) < sticker_count:
            # 补充默认短语
            default_phrases = self._generate_default_phrases(sticker_count)
            needed = sticker_count - len(idea["phrases"])
            idea["phrases"].extend(default_phrases[:needed])
        
        # 确认生成
        print(f"\n🎯 生成预览")
        print(f"角色：{idea['character']}")
        print(f"描述：{idea['character_description']}")
        print(f"风格：{selected_style}")
        print(f"数量：{sticker_count}张")
        print(f"短语：{', '.join(idea['phrases'][:3])}...")
        
        confirm = input("\n确认生成？(y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消生成")
            return None
        
        return self.generate_stickers(idea, selected_style, sticker_count)
    
    def auto_mode(self, topics: List[str] = None, count: int = 1):
        """自动模式：基于热词自动生成"""
        
        print("🤖 自动模式：基于热词生成LINE贴图")
        print("=" * 40)
        
        if not topics:
            print("📊 获取今日热词...")
            topics = get_hot_topics(force_refresh=True)
            if not topics:
                print("❌ 无法获取热词，使用默认主题")
                topics = ["可爱动物", "日常生活", "工作学习"]
        
        print(f"✅ 获取到 {len(topics)} 个热词")
        
        # 选择最适合的热词
        selected_topics = topics[:count]
        print(f"🎯 选择热词: {', '.join(selected_topics)}")
        
        # 生成创意
        print("💡 生成创意中...")
        ideas = make_ideas(selected_topics, mock=False)
        
        results = []
        for i, idea in enumerate(ideas, 1):
            print(f"\n🎨 生成第{i}套贴图: {idea['character']}")
            result = self.generate_stickers(idea, "kawaii", 8)
            if result:
                results.append(result)
        
        return results
    
    def generate_stickers(self, idea: Dict, style: str = "kawaii", 
                         sticker_count: int = 8) -> Optional[Dict]:
        """核心生成函数"""
        
        print("\n" + "=" * 50)
        print(f"🚀 开始生成LINE贴图: {idea['character']}")
        print("=" * 50)
        
        # 创建输出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"output/line_stickers_{idea['character'].replace(' ', '_')}_{timestamp}"
        
        try:
            # 生成贴图
            print("🎨 正在生成贴图图像...")
            image_paths = create_line_stickers(
                idea=idea,
                mock=False,  # 使用真实API生成
                style=style,
                sticker_count=sticker_count,
                out_dir=output_dir
            )
            
            if not image_paths:
                print("❌ 贴图生成失败")
                return None
            
            print(f"✅ 成功生成 {len(image_paths)} 个文件")
            
            # 打包为LINE格式
            print("📦 正在打包为LINE标准格式...")
            zip_path, package_info = package_line_stickers(
                image_paths=image_paths,
                idea=idea,
                out_dir="output",
                sticker_type="static"
            )
            
            if not zip_path:
                print(f"❌ 打包失败: {package_info.get('error', '未知错误')}")
                return None
            
            # 验证包
            print("🔍 验证LINE兼容性...")
            validation = validate_line_package(zip_path)
            
            if not validation['valid']:
                print("❌ 验证失败:")
                for issue in validation['issues']:
                    print(f"  - {issue}")
                return None
            
            # 成功！
            result = {
                "character": idea['character'],
                "zip_path": zip_path,
                "package_info": package_info,
                "validation": validation,
                "created_at": datetime.now().isoformat()
            }
            
            self.generated_packages.append(result)
            
            print("\n🎉 LINE贴图生成成功！")
            print(f"📁 文件: {package_info['zip_name']}")
            print(f"📊 大小: {package_info['size_mb']:.2f}MB")
            print(f"🎯 贴图数量: {package_info['sticker_count']}")
            print(f"✅ LINE兼容: {package_info['line_ready']}")
            print(f"🗂️ 可直接上传到: https://creator.line.me/")
            
            return result
            
        except Exception as e:
            print(f"❌ 生成过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_style_palette(self, style: str) -> List[str]:
        """根据风格返回适合的色板"""
        palettes = {
            "kawaii": ["#FFB6C1", "#87CEEB", "#F0E68C", "#DDA0DD"],
            "minimal": ["#F5F5F5", "#E0E0E0", "#BDBDBD", "#757575"],
            "chibi": ["#FFCDD2", "#F8BBD9", "#E1BEE7", "#D1C4E9"],
            "mascot": ["#FFF8E1", "#F3E5F5", "#E8F5E8", "#E3F2FD"],
            "emoji": ["#FFE082", "#FFAB91", "#A5D6A7", "#90CAF9"]
        }
        return palettes.get(style, palettes["kawaii"])
    
    def _generate_default_phrases(self, count: int) -> List[str]:
        """生成默认短语"""
        default_phrases = [
            "你好", "谢谢", "再见", "加油", "开心", "难过", "生气", "爱你",
            "早上好", "晚安", "对不起", "没关系", "棒棒", "哈哈", "嗯嗯", "好的",
            "想你", "累了", "饿了", "困了", "忙碌", "放松", "惊讶", "期待"
        ]
        return default_phrases[:count]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LINE贴图AI生成器")
    parser.add_argument("--mode", choices=["interactive", "auto", "test"], 
                       default="interactive", help="运行模式")
    parser.add_argument("--count", type=int, default=1, 
                       help="自动模式下生成的套装数量")
    parser.add_argument("--topics", nargs="+", 
                       help="自定义热词列表")
    parser.add_argument("--style", choices=["kawaii", "minimal", "chibi", "mascot", "emoji"],
                       default="kawaii", help="贴图风格")
    parser.add_argument("--dry-run", action="store_true", 
                       help="测试模式，不调用API")
    
    args = parser.parse_args()
    
    generator = LineStickerGenerator()
    
    print("🎨 LINE贴图AI生成器")
    print("=" * 50)
    print("专为LINE Creators Market优化的AI贴图生成工具")
    print()
    
    try:
        if args.mode == "interactive":
            # 交互式模式
            result = generator.interactive_mode()
            if result:
                print("\n🎊 恭喜！你的专属LINE贴图已生成完成！")
                
        elif args.mode == "auto":
            # 自动模式
            results = generator.auto_mode(args.topics, args.count)
            print(f"\n🎊 自动生成完成！共生成 {len(results)} 套贴图")
            
        elif args.mode == "test":
            # 测试模式
            print("🧪 运行系统测试...")
            os.system("python test_line_stickers.py")
            
        # 发送通知
        if generator.generated_packages:
            total = len(generator.generated_packages)
            message = f"🎉 LINE贴图生成完成！\n生成套装: {total} 套\n可直接上传到LINE Creators Market"
            
            # 尝试发送通知
            send_line_messaging(message)
            send_discord_notify(message)
            send_telegram_notify(message)
            
    except KeyboardInterrupt:
        print("\n\n👋 用户取消，再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
