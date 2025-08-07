import os
import requests

def send_line_messaging(message, channel_access_token=None, user_id=None):
    """
    通过 LINE Messaging API 发送消息
    """
    channel_access_token = channel_access_token or os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = user_id or os.getenv("LINE_USER_ID")
    if not channel_access_token or not user_id:
        print("[notifier] 未配置 LINE_CHANNEL_ACCESS_TOKEN 或 LINE_USER_ID，跳过通知。")
        return False
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {channel_access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    try:
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        print("[notifier] LINE Messaging API 通知发送成功。")
        return True
    except Exception as e:
        print(f"[notifier] LINE Messaging API 通知发送失败: {e}")
        return False


def send_discord_notify(message, webhook_url=None):
    """
    通过 Discord Webhook 发送消息
    """
    webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("[notifier] 未配置 DISCORD_WEBHOOK_URL，跳过通知。")
        return False
    data = {"content": message}
    try:
        resp = requests.post(webhook_url, json=data)
        resp.raise_for_status()
        print("[notifier] Discord 通知发送成功。")
        return True
    except Exception as e:
        print(f"[notifier] Discord 通知发送失败: {e}")
        return False


def send_telegram_notify(message, bot_token=None, chat_id=None):
    """
    通过 Telegram Bot 发送消息
    """
    bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("[notifier] 未配置 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID，跳过通知。")
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        resp = requests.post(url, json=data)
        resp.raise_for_status()
        print("[notifier] Telegram 通知发送成功。")
        return True
    except Exception as e:
        print(f"[notifier] Telegram 通知发送失败: {e}")
        return False


def send_email_notify(subject, content, to_emails, user=None, password=None):
    """
    通过 yagmail 发送邮件通知
    """
    try:
        import yagmail
    except ImportError:
        print("[notifier] 未安装 yagmail，无法发送邮件。")
        return False
    user = user or os.getenv("EMAIL_USER")
    password = password or os.getenv("EMAIL_PASSWORD")
    if not user or not password:
        print("[notifier] 未配置邮箱账号或密码，跳过邮件通知。")
        return False
    try:
        yag = yagmail.SMTP(user=user, password=password)
        yag.send(to=to_emails, subject=subject, contents=content)
        print("[notifier] 邮件发送成功。")
        return True
    except Exception as e:
        print(f"[notifier] 邮件发送失败: {e}")
        return False


# 兼容性函数（已废弃）
def send_line_notify(message, token=None):
    """
    LINE Notify 已停止服务，建议使用 LINE Messaging API
    """
    print("[notifier] LINE Notify 已停止服务，请使用 LINE Messaging API、Discord、Telegram 或邮件通知。")
    return False