import sys

from google_play_scraper import reviews

from reviews_bot.sql_worker import load_from_db, save_to_db


def get_new_reviews(vkt_package_name: str) -> []:
    new_reviews = []

    latest_reviews, _ = reviews(
        vkt_package_name,
        lang='ru',
        country='ru',
        count=10
    )

    known_reviews = load_from_db(table_name="googleplay_reviews")
    sent_reviews = []
    for review in latest_reviews:
        try:
            if review.get("reviewId", "") in known_reviews:
                continue
        except BaseException as exc:
            print(f"WTF: {exc}", file=sys.stderr)

        message = "📖[GooglePlay](https://play.google.com/store/apps/details?id=ru.mail.biz.avocado&hl=ru)\n"
        comment_text = ""
        user = ""
        app_rating = ""
        app_version = ""
        answer = ""

        try:
            comment_text = review.get("content", "")
        except KeyError as k_err:
            print(f"Couldn't get commentText from response body reviews list: {k_err}", file=sys.stderr)
        if comment_text:
            message += f"📖{comment_text}\n"

        try:
            user = review.get("userName", "")
        except KeyError as k_err:
            print(f"Couldn't get userName from response body reviews list: {k_err}", file=sys.stderr)
        if user:
            message += f"Пользователь: {user}\n"

        try:
            app_rating = review.get("score", "")
            if 1 == app_rating:
                app_rating = "⭐"
            elif 2 == app_rating:
                app_rating = "⭐⭐"
            elif 3 == app_rating:
                app_rating = "⭐⭐⭐"
            elif 4 == app_rating:
                app_rating = "⭐⭐⭐⭐"
            elif 5 == app_rating:
                app_rating = "⭐⭐⭐⭐⭐"
        except KeyError as k_err:
            print(f"Couldn't get appRating from response body reviews list: {k_err}", file=sys.stderr)
        if app_rating:
            message += f"Оценка: {app_rating}\n"
        else:
            message += "Без оценки\n"

        try:
            app_version = review.get("appVersion", "")
        except KeyError as k_err:
            print(f"Couldn't get appVersionName from response body reviews list: {k_err}", file=sys.stderr)
        if app_version:
            message += f"Версия: {app_version}\n"

        try:
            answer = review.get("replyContent", "")
        except KeyError as k_err:
            print(f"Couldn't get replyContent from response body reviews list: {k_err}", file=sys.stderr)
        if answer:
            message += f"Ответ: {answer}\n"

        if comment_text:
            new_reviews.append(message)
            sent_reviews.append(review.get("reviewId", ""))

    if sent_reviews:
        save_to_db(table_name="googleplay_reviews", new_reviews=sent_reviews)

    return new_reviews
