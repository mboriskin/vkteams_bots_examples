import time

from bot.bot import Bot
from bot.handler import MessageHandler

from loguru import logger


instance_url = "myteam.mail.ru"  # ваш инстанс
BOT_API_URL = f"https://api.{instance_url}/bot/v1"
BOT_TOKEN = "токен_вашего_бота"

# создаём бота
bot = Bot(token=BOT_TOKEN, api_url_base=BOT_API_URL)


def send_in_loop(bot, count, target_chat, message):
    for i in range(count):
        try:
            logger.info(
                bot.send_text(chat_id=target_chat, text=message)
            )
            logger.info(
                f"Sent message {i+1}/{count} to {target_chat}"
            )
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
        time.sleep(1)


def message_cb(bot, event):
    count = 4  # по-умолчанию спамлю в ответ 4 раза
    logger.info(
        f"Received message: {event.text}"
    )
    for word in event.text.split(" "):
        if "#" == word[0]:
            try:
                count = int(word[1:])
            except ValueError:
                logger.error("Invalid count format")
                count = -1

    if count == -1:
        logger.info(
            bot.send_text(chat_id=event.from_chat, text="Спам не удался. Нужно написать #число_раз и дальше текст")
        )
    else:
        logger.info(
            bot.send_text(chat_id=event.from_chat, text=f"Спамлю {count} раз")
        )
        send_in_loop(bot, count, event.from_chat, event.text)

try:
    bot.dispatcher.add_handler(MessageHandler(callback=message_cb))
    logger.info(
        "Starting bot polling"
    )
    bot.start_polling()
    bot.idle()
except BaseException as exc:
    logger.error(
        f"Error starting bot: {exc}"
    )
