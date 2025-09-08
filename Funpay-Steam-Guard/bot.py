import os
import hmac
import base64
import time
import logging
import json
from dotenv import load_dotenv
from FunPayAPI import Account
from FunPayAPI.updater.runner import Runner
from FunPayAPI.updater.events import NewMessageEvent

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SteamGuardBot")

load_dotenv()
FUNPAY_TOKEN = os.getenv("FUNPAY_AUTH_TOKEN")

USAGE_FILE = "usage.json"
if not os.path.exists(USAGE_FILE):
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4, ensure_ascii=False)


def load_usage():
    with open(USAGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_usage(data):
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def format_time_left(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}ч {m}м"
    if m:
        return f"{m}м"
    return f"{s}с"

def generate_steam_guard_code(shared_secret: str):
    try:
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
        logger.error(f"Ошибка генерации кода: {e}")
        return None

secrets = []
index = 1
while True:
    shared_secret = os.getenv(f"SHARED_SECRET_{index}")
    command = os.getenv(f"COMMAND_SECRET_{index}")
    limit = os.getenv(f"LIMIT_SECRET_{index}")
    period = os.getenv(f"PERIOD_SECRET_{index}")

    if not shared_secret or not command:
        break

    limit = None if not limit or limit == "-" else int(limit)
    period = None if not period or period == "-" else int(period) * 3600  # часы -> секунды

    secrets.append({
        "secret": shared_secret,
        "command": command.lower().strip(),
        "limit": limit,
        "period": period
    })
    index += 1

if not secrets:
    logger.critical("❌ В .env не найдено ни одного SHARED_SECRET_X")
    exit(1)

def handle_message(account: Account, event: NewMessageEvent):
    text = (getattr(event.message, "text", "") or "").strip().lower()
    if not text:
        return

    buyer_id = str(event.message.author_id)
    usage = load_usage()
    now = int(time.time())

    for sec in secrets:
        if text != sec["command"]:
            continue

        limit, period = sec["limit"], sec["period"]

        usage.setdefault(buyer_id, {}).setdefault(sec["command"], {"count": 0, "reset_time": 0})
        record = usage[buyer_id][sec["command"]]

        if period and now > record["reset_time"]:
            record["count"] = 0
            record["reset_time"] = now + period

        if limit is not None and record["count"] >= limit:
            if period:
                left_seconds = record["reset_time"] - now
                msg = f"❌ Лимит {limit}/{period//3600}ч исчерпан.\n⏳ Новый запрос будет доступен через {format_time_left(left_seconds)}."
            else:
                msg = f"❌ Лимит {limit} навсегда исчерпан."
            account.send_message(event.message.chat_id, msg)
            logger.warning(f"🔒 Пользователь {buyer_id} исчерпал лимит ({sec['command']}).")
            save_usage(usage)
            return

        code = generate_steam_guard_code(sec["secret"])
        if not code:
            account.send_message(event.message.chat_id, "❌ Ошибка генерации кода.")
            return

        if limit is not None:
            record["count"] += 1
            if period and record["reset_time"] == 0:
                record["reset_time"] = now + period
            save_usage(usage)

        left = "∞" if limit is None else f"{max(0, limit - record['count'])}/{limit}"

        account.send_message(
            event.message.chat_id,
            f"✅ Ваш код: {code}\n📊 Осталось: {left}"
        )

        logger.info(
            f"📤 Код {code} отправлен пользователю {buyer_id} "
            f"(осталось {left}, команда {sec['command']})"
        )
        return


def main():
    if not FUNPAY_TOKEN:
        logger.critical("❌ Проверь .env файл: отсутствует токен FunPay.")
        return

    account = Account(FUNPAY_TOKEN)
    account.get()
    if not account.username:
        logger.critical("❌ Неверный FunPay токен.")
        return

    logger.info(f"✅ Авторизован в FunPay как {account.username}")
    runner = Runner(account)

    logger.info("🕵️ Ожидание команд...")

    for event in runner.listen(requests_delay=5):
        try:
            if isinstance(event, NewMessageEvent):
                if event.message.author_id == 0:
                    continue
                handle_message(account, event)
        except Exception as e:
            logger.error(f"Ошибка в обработке события: {str(e)}")


if __name__ == "__main__":
    main()
