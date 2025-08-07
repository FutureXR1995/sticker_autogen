import argparse
import os
from data_scraper import get_hot_topics
from idea_generator import make_ideas
from image_generator import create_stickers
from packager import package_set
from notifier import send_line_messaging, send_discord_notify, send_telegram_notify, send_email_notify


def pick_two(topics):
    """选取前两个热词用于生成"""
    return topics[:2]


def main(dry_run=False, local_preview=False, budget_mode=False, ideas_only=False):
    """主流程：热词抓取 → 创意生成 → 图像生成 → 打包 → 通知"""
    print("=" * 50)
    print("🚀 自动化 LINE 贴图生成流程开始")
    print("=" * 50)
    
    try:
        # 1. 获取热词
        print("\n📊 步骤1: 获取今日热词...")
        topics = get_hot_topics(force_refresh=True)
        if not topics:
            print("❌ 未获取到热词，流程终止。")
            return
        print(f"✅ 获取到 {len(topics)} 个热词: {topics[:5]}...")
        
        # 2. 选取热词
        if budget_mode:
            # 预算模式：只生成1套贴图
            selected = topics[:1]
            print(f"💰 预算模式：只生成1套贴图以节省费用")
        else:
            selected = pick_two(topics)
        print(f"🎯 选取用于生成的热词: {selected}")
        
        # 3. 生成创意
        print("\n💡 步骤2: 生成创意信息...")
        ideas = make_ideas(selected, mock=dry_run)
        for idx, idea in enumerate(ideas, 1):
            print(f"  创意{idx}: {idea['character']} - {idea['phrases'][:3]}...")
            if ideas_only:
                # 详细显示创意内容
                print(f"    角色描述: {idea.get('character_description', '无')}")
                print(f"    风格: {idea['style']}")
                print(f"    色板: {idea['palette']}")
                print(f"    短语: {idea['phrases']}")
                print()
        
        if ideas_only:
            print("\n" + "=" * 50)
            print("💡 创意预览完成！如满意可运行:")
            if budget_mode:
                print("  python main.py --budget-mode")
            else:
                print("  python main.py")
            print("=" * 50)
            return
        
        # 4. 生成图像
        print("\n🎨 步骤3: 生成贴图图像...")
        all_image_paths = []
        for idx, idea in enumerate(ideas, 1):
            print(f"  生成第{idx}套贴图: {idea['character']}")
            try:
                image_paths = create_stickers(idea, mock=dry_run, out_dir=f"output/set_{idx}")
                all_image_paths.extend(image_paths)
                print(f"    ✅ 生成 {len(image_paths)} 个文件")
            except Exception as e:
                print(f"    ❌ 生成失败: {e}")
                continue
        
        # 5. 打包
        print("\n📦 步骤4: 打包贴图套件...")
        zip_paths = []
        for idx, idea in enumerate(ideas, 1):
            try:
                image_paths = [p for p in all_image_paths if f"set_{idx}" in p]
                if image_paths:
                    zip_path = package_set(image_paths, idea, out_dir="output")
                    zip_paths.append(zip_path)
                    print(f"  ✅ 打包完成: {os.path.basename(zip_path)}")
            except Exception as e:
                print(f"  ❌ 打包失败: {e}")
        
        # 6. 通知（多种方式，优先 LINE）
        if zip_paths and not dry_run:
            print("\n📢 步骤5: 发送通知...")
            message = f"🎉 今日贴图生成完成！\n生成套件: {len(zip_paths)} 套\n热词: {', '.join(selected)}"
            
            # 尝试多种通知方式，优先 LINE
            notify_sent = False
            
            # LINE Messaging API 通知（优先）
            if send_line_messaging(message):
                notify_sent = True
            
            # Discord 通知
            if not notify_sent and send_discord_notify(message):
                notify_sent = True
            
            # Telegram 通知
            if not notify_sent and send_telegram_notify(message):
                notify_sent = True
            
            # 邮件通知（可选）
            email_user = os.getenv("EMAIL_USER")
            if email_user:
                send_email_notify(
                    subject="贴图生成完成",
                    content=message,
                    to_emails=[email_user]
                )
                notify_sent = True
            
            if not notify_sent:
                print("  ⚠️ 未配置任何通知方式，跳过通知")
        
        # 7. 本地预览
        if local_preview:
            print("\n🌐 本地预览模式:")
            print("  运行以下命令启动 Web 预览:")
            print("  python app.py")
            print("  然后访问: http://localhost:5000")
        
        print("\n" + "=" * 50)
        print(f"🎊 流程完成！生成 {len(zip_paths)} 套贴图")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 流程执行失败: {e}")
        if not dry_run:
            error_message = f"❌ 贴图生成失败: {e}"
            send_line_messaging(error_message)
            send_discord_notify(error_message)
            send_telegram_notify(error_message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自动化 LINE 贴图生成主流程")
    parser.add_argument("--dry-run", action="store_true", help="仅生成日志，不请求 API")
    parser.add_argument("--local-preview", action="store_true", help="本地预览模式")
    parser.add_argument("--budget-mode", action="store_true", help="预算模式：只生成1套贴图节省费用")
    parser.add_argument("--ideas-only", action="store_true", help="仅生成创意不生成图片，完全免费")
    args = parser.parse_args()
    
    main(dry_run=args.dry_run, local_preview=args.local_preview, budget_mode=args.budget_mode, ideas_only=args.ideas_only)