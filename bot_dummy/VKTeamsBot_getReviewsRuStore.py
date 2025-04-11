#!/usr/bin/env python3

import os
import sys
import base64
from pathlib import Path
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import requests

from loguru import logger

import configparser

from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA

import pickle

from bot.bot import Bot


class Config:
    def __init__(self, project_dir: str):
        configs_path = project_dir
        for config in ["config.ini"]:
            if not os.path.isfile(os.path.join(configs_path, config)):
                raise FileExistsError(f"File {config} not found in {configs_path}")

        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(configs_path, "config.ini"))

current_dir = Path(__file__)
project_dir = [p for p in current_dir.parents if p.parts[-1] == "vkteams_bots_examples"][0]
sys.path.insert(1, str(project_dir))
config = Config(project_dir=str(project_dir)).config


SCOPE = "https://public-api.rustore.ru/public"

PKL_HISTORY_PATH = f"{project_dir}/bot_dummy/rustore_reviews.pkl"


def get_auth_token_from_private_key_file(private_key_file) -> str:
    logger.info(f"getting auth token from: {private_key_file}")

    config = configparser.ConfigParser()
    config.read(private_key_file)

    private_key = config.get('main', 'KEY')
    private_key_id = config.get('main', 'ID')

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
    logger.info(auth_result)

    try:
        if "OK" != auth_result["code"]:
            print(f"Couldn't get auth JWE token from response: {auth_result['message']}")
            return ""
        auth_token = auth_result["body"]["jwe"]
        return auth_token
    except KeyError as k_err:
        logger.error(f"Couldn't get auth JWE token from response: {k_err}")
    except BaseException as exc:
        logger.error(f"Couldn't get auth JWE token from response, exception occurred: {exc}")

    return ""


def generate(private_key, key_id_or_company_id):
    key = RSA.import_key(base64.b64decode(private_key))

    sdt = datetime.now().isoformat()+"+03:00"
    to_sign = key_id_or_company_id + sdt
    logger.info("Get hash from: " + to_sign)

    hash = SHA512.new(to_sign.encode())
    binary_signature = pkcs1_15.new(key).sign(hash)
    signature = base64.b64encode(binary_signature).decode('utf-8')
    logger.info("SIGN: " + signature)

    return sdt, signature


def get_known_comments_ids() -> []:
    try:
        reviews = pickle.load(open(PKL_HISTORY_PATH, "rb"))
    except FileNotFoundError:
        logger.error(f"No {PKL_HISTORY_PATH} was found!")
        reviews = {
            "comments_ids": ["example"]
        }

    logger.info(f"Got comments with ids: {reviews}")
    return reviews


def send_message_to_chat(
    bot: Bot,
    chat_id: str,
    message: str,
    msg_id_reply_to=None,
    parse_mode=None,
) -> bool:
    """
    Метод для отправки сообщений в указанный чат. Чаще всего ответом на сообщение-триггер.
    В случае неудачи: отправить сообщение о неудаче в резервный чат / на электронную почту.
    """
    logger.info(f"\n{message}")
    if msg_id_reply_to:
        r = bot.send_text(
            chat_id=chat_id,
            text=message,
            reply_msg_id=msg_id_reply_to,
            parse_mode=parse_mode,
        )
    else:
        r = bot.send_text(chat_id=chat_id, text=message, parse_mode=parse_mode)
    logger.info(f"status code: {r.status_code}")
    logger.info(f"response: {r.text}")
    if not r.json()["ok"]:
        logger.error(f"Error while reply to msgId: {msg_id_reply_to}")
        logger.info("Retrying with send text as plain message...")
        retry_r = bot.send_text(chat_id=chat_id, text=message)
        if not retry_r.json()["ok"]:
            alarm_message = f"{message}\n\n"
            alarm_message += f"в чат {chat_id}\n\n"
            alarm_message += f"response: {r.text}"
            # send_message_to_email_or_alarm_another_chat(alarm_message)
            return False
        else:
            return True
    else:
        return True


def setup_parser(parser):
    parser.add_argument('--token',
                        required=True,
                        help='Bot token')


def main():
    parser = ArgumentParser(
        add_help=True,
        prog="Get users' reviews from VK Teams app RuStore",
        description="tool to publish reviews from RuStore to VK Teams chat",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    # authentication and app details
    setup_parser(parser)
    args = parser.parse_args()

    if not args.token:
        raise Exception("Нужно задать токен бота")

    bot = Bot(
        token=args.token,
        name="reviews_bot",
        api_url_base=config.get("main", "API_URL"),
    )

    auth_token = get_auth_token_from_private_key_file(f'{project_dir}/bot_dummy/rustore_config.ini')
    package_name = "ru.mail.biz.avocado"
    logger.info(f"\n\nAUTH TOKEN:\n{auth_token}\n\n")

    headers = {
        "Content-Type": "application/json",
        "Public-Token": auth_token
    }
    response = requests.get(f"{SCOPE}/v1/application/{package_name}/comment", headers=headers)
    reviews_result = response.json()
    try:
        if "OK" != reviews_result["code"]:
            logger.error(f"Couldn't get auth JWE token from response: {reviews_result['message']}")
            return ""
    except KeyError as k_err:
        logger.error(f"Couldn't get reviews from response: {k_err}")
    except BaseException as exc:
        logger.error(f"Couldn't get auth reviews from response, exception occurred: {exc}")

    known_comments_ids_list = get_known_comments_ids()

    try:
        reviews_list = reviews_result.get("body", [])
        for review in reviews_list[::-1]:
            try:
                if review.get("commentId", "") in known_comments_ids_list["comments_ids"]:
                    continue
            except Exception as exc:
                logger.error("WTF")

            message = "💎[RuStore](https://apps.rustore.ru/app/ru.mail.biz.avocado/reviews)\n"
            comment_text = ""
            user = ""
            app_rating = ""
            app_version = ""

            try:
                comment_text = review.get("commentText", "")
            except KeyError as k_err:
                logger.error(f"Couldn't get commentText from response body reviews list: {k_err}")
            if comment_text:
                message += f"📖{comment_text}\n"

            try:
                user = review.get("userName", "")
            except KeyError as k_err:
                logger.error(f"Couldn't get userName from response body reviews list: {k_err}")
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
                logger.error(f"Couldn't get appRating from response body reviews list: {k_err}")
            if app_rating:
                message += f"Оценка: {app_rating}\n"
            else:
                message += f"Без оценки\n"

            try:
                app_version = review.get("appVersionName", "")
            except KeyError as k_err:
                logger.error(f"Couldn't get appVersionName from response body reviews list: {k_err}")
            if app_version:
                message += f"Версия: {app_version}\n"

            if comment_text:
                if send_message_to_chat(
                    bot=bot,
                    chat_id=config.get("chats", "MY_CHAT"),
                    message=message,
                    parse_mode="MarkdownV2",
                ):
                    known_comments_ids_list["comments_ids"].append(review["commentId"])

    except KeyError as k_err:
        logger.error(f"Couldn't get reviews body list from response: {k_err}")
    except BaseException as exc:
        logger.error(f"Couldn't get reviews body list from response, exception occurred: {exc}")

    with open(PKL_HISTORY_PATH, "wb") as f:
        try:
            pickle.dump(known_comments_ids_list, f)
            logger.info("\nReviews was successfully dumped to .pkl.")
        except Exception as e:
            logger.error(f"\nFailed to dump reviews to .pkl.\nReason: {e}")


if __name__ == '__main__':
    main()