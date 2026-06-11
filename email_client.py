"""SMTP 邮件发送封装。支持 QQ / 163 / Gmail 等，默认 SSL 465。"""

import smtplib
import json
from email.mime.text import MIMEText
from pathlib import Path
from dataclasses import dataclass


@dataclass
class SmtpConfig:
    host: str = "smtp.qq.com"
    port: int = 465
    user: str = ""
    password: str = ""
    to_addr: str = ""


# ============================================================
# [部署时修改] config.json 放在本文件同目录
# ============================================================
CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> SmtpConfig | None:
    """从 config.json 加载 SMTP 配置。"""
    if not CONFIG_PATH.exists():
        return None
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return SmtpConfig(
            host=data.get("host", "smtp.qq.com"),
            port=data.get("port", 465),
            user=data.get("user", ""),
            password=data.get("password", ""),
            to_addr=data.get("to_addr", ""),
        )
    except (json.JSONDecodeError, KeyError):
        return None


def send_email(
    to_addr: str,
    subject: str,
    html_body: str,
    config: SmtpConfig | None = None,
) -> bool:
    """发送 HTML 邮件。返回 True 表示发送成功。"""
    if config is None:
        config = load_config()
    if not config or not config.password:
        print("[email] 未配置 SMTP，跳过发送")
        return False

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = config.user
    msg["To"] = to_addr

    try:
        with smtplib.SMTP_SSL(config.host, config.port, timeout=10) as s:
            s.login(config.user, config.password)
            s.send_message(msg)
        print(f"[email] 已发送至 {to_addr}")
        return True
    except smtplib.SMTPException as e:
        print(f"[email] 发送失败: {e}")
        return False
