#!/usr/bin/env python3
"""
LINE贴图生成系统测试脚本
演示从创意生成到最终ZIP包的完整流程
"""

import os
import json
from datetime import datetime
from idea_generator import make_idea
from image_generator import create_line_stickers
from packager import package_line_stickers, validate_line_package


def test_line_sticker_generation():
    """测试完整的LINE贴图生成流程"""
    
    print("🚀 开始LINE贴图生成系统测试")
    print("=" * 60)
    
    # 第一步：生成创意
    print("\n📝 步骤1: 生成贴图创意")
    test_topic = "可爱小猫"
    print(f"热词: {test_topic}")
    
    # 使用mock模式生成创意（避免消耗API）
    idea = make_idea(test_topic, mock=True)
    print(f"角色: {idea['character']}")
    print(f"描述: {idea.get('character_description', '无')}")
    print(f"短语: {idea['phrases'][:3]}...")
    print(f"风格: {idea['style']}")
    print(f"色板: {idea['palette']}")
    
    # 第二步：生成LINE贴图
    print("\n🎨 步骤2: 生成LINE标准贴图")
    
    output_dir = f"output/test_line_stickers_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # 使用mock模式（避免消耗DALL-E API）
        image_paths = create_line_stickers(
            idea=idea,
            mock=True,  # 使用mock模式进行测试
            style="kawaii",
            sticker_count=8,
            out_dir=output_dir
        )
        
        if not image_paths:
            print("❌ 贴图生成失败")
            return False
            
        print(f"✅ 生成了 {len(image_paths)} 个文件")
        for path in image_paths:
            filename = os.path.basename(path)
            size_kb = os.path.getsize(path) / 1024
            print(f"  - {filename}: {size_kb:.1f}KB")
    
    except Exception as e:
        print(f"❌ 贴图生成失败: {e}")
        return False
    
    # 第三步：打包为LINE格式
    print("\n📦 步骤3: 打包为LINE标准ZIP")
    
    try:
        zip_path, package_info = package_line_stickers(
            image_paths=image_paths,
            idea=idea,
            out_dir="output",
            sticker_type="static"
        )
        
        if not zip_path:
            print(f"❌ 打包失败: {package_info.get('error', '未知错误')}")
            return False
            
        print(f"✅ ZIP包创建成功:")
        print(f"  文件: {package_info['zip_name']}")
        print(f"  大小: {package_info['size_mb']:.2f}MB")
        print(f"  贴图数量: {package_info['sticker_count']}")
        print(f"  LINE兼容: {package_info['line_ready']}")
        
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        return False
    
    # 第四步：验证ZIP包
    print("\n🔍 步骤4: 验证LINE兼容性")
    
    try:
        validation = validate_line_package(zip_path)
        
        print(f"验证结果: {'✅ 通过' if validation['valid'] else '❌ 不通过'}")
        print(f"文件数量: {validation['file_count']}")
        print(f"包大小: {validation['package_size_mb']:.2f}MB")
        
        if validation['issues']:
            print("❌ 发现问题:")
            for issue in validation['issues']:
                print(f"  - {issue}")
        
        if validation['suggestions']:
            print("💡 建议:")
            for suggestion in validation['suggestions']:
                print(f"  - {suggestion}")
                
        if validation['valid']:
            print("\n🎉 恭喜！ZIP包完全符合LINE Creators Market要求！")
            print(f"📁 可以直接上传到: https://creator.line.me/")
            print(f"🗂️ 文件位置: {zip_path}")
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ LINE贴图生成系统测试完成！")
    
    return validation['valid']


def test_content_compliance():
    """测试内容合规性检查"""
    
    print("\n🛡️ 内容合规性测试")
    print("-" * 40)
    
    from line_compliance import LineComplianceChecker
    checker = LineComplianceChecker()
    
    test_cases = [
        # (提示词, 角色名, 描述, 预期结果)
        ("cute happy cat", "小花猫", "一只可爱的小猫咪", True),
        ("disney mickey mouse", "米老鼠", "迪士尼角色", False),
        ("pokemon pikachu", "皮卡丘", "口袋妖怪", False),
        ("original rabbit character", "小兔子", "原创兔子角色", True),
        ("violent fighting", "战士", "暴力战斗", False),
    ]
    
    passed = 0
    for prompt, name, desc, expected in test_cases:
        result = checker.validate_content_compliance(prompt, name, desc)
        success = result['valid'] == expected
        status = "✅" if success else "❌"
        
        print(f"{status} {prompt[:30]:<30} -> {'通过' if result['valid'] else '不通过'} (风险: {result['risk_level']})")
        
        if not result['valid'] and result['issues']:
            print(f"    问题: {', '.join(result['issues'][:2])}")
        
        if success:
            passed += 1
    
    print(f"\n合规性测试: {passed}/{len(test_cases)} 通过")
    return passed == len(test_cases)


def test_prompt_optimization():
    """测试提示词优化"""
    
    print("\n🎯 AI提示词优化测试")
    print("-" * 40)
    
    from line_compliance import create_line_sticker_prompt
    
    test_cases = [
        ("小猫咪", "一只可爱的橘猫", "你好", "kawaii", ["#FFB6C1", "#87CEEB"]),
        ("小狗狗", "活泼的柴犬", "加油", "minimal", ["#F0E68C", "#DDA0DD"]),
        ("小兔子", "温柔的白兔", "谢谢", "chibi", ["#FFF8DC", "#F5DEB3"]),
    ]
    
    for character, desc, phrase, style, palette in test_cases:
        prompt = create_line_sticker_prompt(character, desc, phrase, style, palette)
        
        print(f"角色: {character} -> {phrase}")
        print(f"优化后提示词: {prompt[:100]}...")
        print()
    
    print("✅ 提示词优化测试完成")
    return True


if __name__ == "__main__":
    print("🧪 LINE贴图生成系统 - 全面测试")
    print("=" * 60)
    
    try:
        # 运行所有测试
        test1 = test_content_compliance()
        test2 = test_prompt_optimization() 
        test3 = test_line_sticker_generation()
        
        print(f"\n📊 测试总结:")
        print(f"  合规性检查: {'✅' if test1 else '❌'}")
        print(f"  提示词优化: {'✅' if test2 else '❌'}")
        print(f"  完整生成流程: {'✅' if test3 else '❌'}")
        
        if all([test1, test2, test3]):
            print(f"\n🎉 所有测试通过！LINE贴图生成系统已就绪！")
        else:
            print(f"\n⚠️ 部分测试失败，需要进一步调试")
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
