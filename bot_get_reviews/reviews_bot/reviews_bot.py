import os
import sys
import yaml

from apscheduler.schedulers import background

from bot.bot import Bot

from reviews_bot.store_connectors import appgallery_connector, google_play_connector, rustore_connector

config_template = os.getenv('CONFIG_TEMPLATE')
with open(config_template, 'r') as file:
    config_data = yaml.safe_load(file)

VKT_BOT_TOKEN = config_data['VKT_BOT_TOKEN']
VKT_BOT_NICK = config_data['VKT_BOT_NICK']
VKT_BASE_URL = config_data['VKT_BASE_URL']
VKT_REVIEWS_CHAT = config_data['VKT_REVIEWS_CHAT']
VKT_MONITORING_CHAT = config_data['VKT_MONITORING_CHAT']

VKT_PACKAGE_NAME = config_data['VKT_PACKAGE_NAME']

RUSTORE_PROJECT_KEY = config_data['RUSTORE_PROJECT_KEY']
RUSTORE_PROJECT_KEY_ID = config_data['RUSTORE_PROJECT_KEY_ID']


bot = Bot(token=VKT_BOT_TOKEN, name=VKT_BOT_NICK, api_url_base=VKT_BASE_URL)

scheduler = background.BlockingScheduler()


def send_review_to_chat(review: str) -> bool:
    result = bot.send_text(
        chat_id=VKT_REVIEWS_CHAT,
        text=review,
        parse_mode="MarkdownV2"
    )
    if result.ok:
        return True

    bot.send_text(
        chat_id=VKT_MONITORING_CHAT,
        text=f"{VKT_BOT_NICK} не смог отправить сообщение:\n\n{review}\n\nОшибка: {result.text}",
        parse_mode="MarkdownV2"
    )
    return False


def scrap_and_post_reviews():
    print("Начинаю сбор информации по отзывам из сторов", file=sys.stdout)

    google_play_new_reviews = google_play_connector.get_new_reviews(
        VKT_PACKAGE_NAME)
    print(f"Обработан GooglePlay, найдено {len(google_play_new_reviews)} новых отзывов", file=sys.stdout)

    rustore_new_reviews = rustore_connector.get_new_reviews(
        VKT_PACKAGE_NAME, RUSTORE_PROJECT_KEY, RUSTORE_PROJECT_KEY_ID)
    print(f"Обработан RuStore, найдено {len(rustore_new_reviews)} новых отзывов", file=sys.stdout)

    appgallery_new_reviews = appgallery_connector.get_new_reviews()
    print(f"Обработан AppGallery, найдено {len(appgallery_new_reviews)} новых отзывов", file=sys.stdout)

    for review in google_play_new_reviews:
        if send_review_to_chat(review):
            print(f"Сообщение об отзыве из Google Play отправлено успешно:\n{review}", file=sys.stdout)

    for review in rustore_new_reviews:
        if send_review_to_chat(review):
            print(f"Сообщение об отзыве из RuStore отправлено успешно:\n{review}", file=sys.stdout)

    for review in appgallery_new_reviews:
        if send_review_to_chat(review):
            print(f"Сообщение об отзыве из AppGallery отправлено успешно:\n{review}", file=sys.stdout)


if __name__ == "__main__":
    bot.send_text(
        chat_id="admin1",
        text=f"✅rebuild {VKT_BOT_NICK} выполнен",
    )

    scrap_and_post_reviews()

    scheduler.add_job(scrap_and_post_reviews, 'interval', minutes=30)
    scheduler.start()
