"""Telegram bot for Muse daily push notifications."""

from __future__ import annotations

import os
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes


class MuseTelegramBot:
    """Sends daily briefings and handles user interactions via Telegram."""

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.app: Optional[Application] = None

    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id)

    async def send_daily_briefing(self, items: list[dict], top_n: int = 5) -> bool:
        """Send top-N items as a Telegram message."""
        if not self.is_configured():
            return False

        top = items[:top_n]
        if not top:
            return False

        lines = ["🌅 *Daily Muse Briefing*", "━━━━━━━━━━━━━━━━━━━━━━"]
        for i, item in enumerate(top, 1):
            score = item.get("score", 0)
            score_str = f" ({score * 100:.0f}%)" if score else ""
            lines.append(f"{i}. [{item['title']}]({item['url']}){score_str}")

        lines.append("")
        lines.append("Open dashboard: http://localhost:8000")

        keyboard = [
            [
                InlineKeyboardButton("👍", callback_data="like_0"),
                InlineKeyboardButton("👎", callback_data="dislike_0"),
                InlineKeyboardButton("📖 Read", url="http://localhost:8000"),
            ]
        ]

        try:
            from telegram import Bot
            bot = Bot(token=self.token)
            await bot.send_message(
                chat_id=self.chat_id,
                text="\n".join(lines),
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return True
        except Exception as exc:
            print(f"[Telegram] send failed: {exc}")
            return False

    async def send_text(self, text: str) -> bool:
        """Send a plain text message."""
        if not self.is_configured():
            return False
        try:
            from telegram import Bot
            bot = Bot(token=self.token)
            await bot.send_message(chat_id=self.chat_id, text=text)
            return True
        except Exception as exc:
            print(f"[Telegram] send failed: {exc}")
            return False
