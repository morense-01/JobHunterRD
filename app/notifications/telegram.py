from typing import Optional

from loguru import logger

from app.database.models import Vacancy


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._enabled = bool(bot_token and chat_id)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def send_vacancy(self, vacancy: Vacancy) -> tuple[bool, str]:
        if not self._enabled:
            logger.warning("Telegram notifier disabled: missing bot_token or chat_id")
            return False, "Notifier disabled"

        message = self._format_message(vacancy)
        try:
            import requests
            url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
            payload = {
                "chat_id": self._chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            }
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            logger.info(f"Telegram: vacancy '{vacancy.title}' sent successfully")
            return True, ""
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Telegram: failed to send vacancy '{vacancy.title}': {error_msg}")
            return False, error_msg

    def _format_message(self, vacancy: Vacancy) -> str:
        lines = [
            "🚀 <b>Nueva Vacante</b>\n",
            f"<b>Cargo:</b> {vacancy.title}",
            f"<b>Empresa:</b> {vacancy.company}",
            f"<b>Ubicación:</b> {vacancy.location or 'No especificada'}",
            f"<b>Modalidad:</b> {vacancy.remote or 'No especificada'}",
        ]

        if vacancy.salary:
            lines.append(f"<b>Salario:</b> {vacancy.salary}")

        lines.append(f"<b>Portal:</b> {vacancy.portal}")
        lines.append(f"<b>Enlace:</b> {vacancy.url}")

        return "\n".join(lines)
