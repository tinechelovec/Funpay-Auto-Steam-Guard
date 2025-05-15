import os
import hmac
import base64
import time
import logging
from dotenv import load_dotenv
from FunPayAPI import Account
from FunPayAPI.updater.runner import Runner
from FunPayAPI.updater.events import NewMessageEvent

# ─── Настройка логирования ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ─── Загрузка переменных окружения ─────────────────────────────────────
load_dotenv()


# ─── Генерация Steam Guard кода ────────────────────────────────────────
def generate_steam_guard_code():
    try:
        shared_secret = os.getenv("STEAM_SHARED_SECRET")
        if not shared_secret:
            logger.error("STEAM_SHARED_SECRET не найден в .env")
            return "❌ Ошибка: отсутствует STEAM_SHARED_SECRET"

        key = base64.b64decode(shared_secret)
        timestamp = int(time.time()) // 30
        msg = timestamp.to_bytes(8, byteorder="big")
        hmac_result = hmac.new(key, msg, digestmod="sha1").digest()
        offset = hmac_result[-1] & 0xF
        code_bytes = hmac_result[offset:offset+4]
        full_code = int.from_bytes(code_bytes, byteorder="big") & 0x7FFFFFFF
        chars = "23456789BCDFGHJKMNPQRTVWXY"
        code = ""
        for _ in range(5):
            code += chars[full_code % len(chars)]
            full_code //= len(chars)
        return code

    except Exception as e:
        logger.error(f"Ошибка генерации кода: {str(e)}")
        return "❌ Ошибка генерации кода"


# ─── Основная логика ────────────────────────────────────────────────────
def main():
    try:
        golden_key = os.getenv("FUNPAY_AUTH_TOKEN")
        if not golden_key:
            logger.error("FUNPAY_AUTH_TOKEN не найден в .env")
            return

        account = Account(golden_key)
        account.get()

        if not account.username:
            logger.error("Не удалось получить имя пользователя. Проверьте токен.")
            return

        logger.info(f"Авторизован как {account.username}")

        runner = Runner(account)
        logger.info("Бот запущен. Ожидание сообщений...")

        for event in runner.listen(requests_delay=5.0):
            try:
                if isinstance(event, NewMessageEvent):
                    msg = event.message
                    if msg.author_id != 0 and msg.text.strip().lower() == "!код":
                        code = generate_steam_guard_code()
                        account.send_message(msg.chat_id, f"✅ Ваш код: {code}")
                        logger.info(f"Отправлен код для чата {msg.chat_id}")
            except Exception as e:
                logger.error(f"Ошибка обработки события: {str(e)}")

    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}")


# ─── Точка входа ───────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
