import pytest
import notifier

class DummyResp:
    def raise_for_status(self):
        pass


def test_send_line_messaging_success(monkeypatch):
    def mock_post(url, headers=None, json=None):
        return DummyResp()
    monkeypatch.setattr("requests.post", mock_post)
    assert notifier.send_line_messaging("测试消息", channel_access_token="dummy", user_id="dummy") is True

def test_send_line_messaging_fail(monkeypatch):
    def mock_post(url, headers=None, json=None):
        raise Exception("fail")
    monkeypatch.setattr("requests.post", mock_post)
    assert notifier.send_line_messaging("测试消息", channel_access_token="dummy", user_id="dummy") is False

def test_send_line_messaging_no_token(monkeypatch):
    assert notifier.send_line_messaging("测试消息", channel_access_token=None, user_id=None) is False

def test_send_line_notify_deprecated(monkeypatch):
    # LINE Notify 已停止服务，应该返回 False
    assert notifier.send_line_notify("测试消息", token="dummy") is False

def test_send_email_notify_success(monkeypatch):
    class DummySMTP:
        def __init__(self, user, password):
            pass
        def send(self, to, subject, contents):
            return True
    monkeypatch.setattr("yagmail.SMTP", DummySMTP)
    assert notifier.send_email_notify("subj", "content", ["a@b.com"], user="u", password="p") is True

def test_send_email_notify_fail(monkeypatch):
    class DummySMTP:
        def __init__(self, user, password):
            pass
        def send(self, to, subject, contents):
            raise Exception("fail")
    monkeypatch.setattr("yagmail.SMTP", DummySMTP)
    assert notifier.send_email_notify("subj", "content", ["a@b.com"], user="u", password="p") is False

def test_send_email_notify_no_user(monkeypatch):
    monkeypatch.setattr("yagmail.SMTP", lambda *a, **k: None)
    assert notifier.send_email_notify("subj", "content", ["a@b.com"], user=None, password=None) is False