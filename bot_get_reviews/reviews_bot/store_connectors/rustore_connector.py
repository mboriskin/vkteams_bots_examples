import sys
import requests
import base64
import pytz
from datetime import datetime
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA

from reviews_bot.sql_worker import load_from_db, save_to_db


SCOPE = "https://public-api.rustore.ru/public"


def get_auth_token_from_private_key_file(private_key, private_key_id) -> str:
    timestamp, signature = generate(private_key, private_key_id)

    params = {
        "keyId": private_key_id,
        "timestamp": timestamp,
        "signature": signature
    }
    headers = {
        "content-type": "application/json"
    }

    auth_response = requests.post(f"{SCOPE}/auth", headers=headers, json=params)
    auth_result = auth_response.json()

    try:
        if "OK" != auth_result["code"]:
            print(f"Couldn't get auth JWE token from response: {auth_result['message']}", file=sys.stderr)
            return ""
        auth_token = auth_result["body"]["jwe"]
        return auth_token
    except KeyError as k_err:
        print(f"Couldn't get auth JWE token from response: {k_err}", file=sys.stderr)
    except BaseException as exc:
        print(f"Couldn't get auth JWE token from response, exception occurred: {exc}", file=sys.stderr)

    return ""


def generate(private_key, key_id_or_company_id):
    key = RSA.import_key(base64.b64decode(private_key))

    sdt = datetime.now(pytz.timezone('Europe/Moscow')).isoformat()
    to_sign = str(key_id_or_company_id) + sdt

    hash = SHA512.new(to_sign.encode())
    binary_signature = pkcs1_15.new(key).sign(hash)
    signature = base64.b64encode(binary_signature).decode('utf-8')

    return sdt, signature


def get_new_reviews(vkt_package_name: str, project_key: str, project_key_id: str) -> []:
    new_reviews_list = []

    auth_token = get_auth_token_from_private_key_file(project_key, project_key_id)
    package_name = "ru.mail.biz.avocado"

    headers = {
        "Content-Type": "application/json",
        "Public-Token": auth_token
    }
    response = requests.get(f"{SCOPE}/v1/application/{package_name}/comment", headers=headers)
    reviews_result = response.json()
    try:
        if "OK" != reviews_result["code"]:
            print(f"Couldn't get auth JWE token from response: {reviews_result['message']}", file=sys.stderr)
            return ""
    except KeyError as k_err:
        print(f"Couldn't get reviews from response: {k_err}", file=sys.stderr)
    except BaseException as exc:
        print(f"Couldn't get auth reviews from response, exception occurred: {exc}", file=sys.stderr)

    known_comments_ids_list = load_from_db(table_name="rustore_reviews")
    new_comments_ids_list = []
    try:
        reviews_list = reviews_result.get("body", [])
        for review in reviews_list[::-1]:
            try:
                if str(review.get("commentId", "")) in known_comments_ids_list:
                    continue
            except BaseException as exc:
                print(f"WTF: {exc}", file=sys.stderr)

            message = "💎[RuStore](https://apps.rustore.ru/app/ru.mail.biz.avocado/reviews)\n"
            comment_text = ""
            user = ""
            app_rating = ""
            app_version = ""

            try:
                comment_text = review.get("commentText", "")
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
                app_rating = review.get("appRating", "")
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
                app_version = review.get("appVersionName", "")
            except KeyError as k_err:
                print(f"Couldn't get appVersionName from response body reviews list: {k_err}", file=sys.stderr)
            if app_version:
                message += f"Версия: {app_version}\n"

            if comment_text:
                new_reviews_list.append(message)
                new_comments_ids_list.append(review["commentId"])

    except KeyError as k_err:
        print(f"Couldn't get reviews body list from response: {k_err}", file=sys.stderr)
    except BaseException as exc:
        print(f"Couldn't get reviews body list from response, exception occurred: {exc}", file=sys.stderr)

    if new_comments_ids_list:
        save_to_db(table_name="rustore_reviews", new_reviews=new_comments_ids_list)

    return new_reviews_list
