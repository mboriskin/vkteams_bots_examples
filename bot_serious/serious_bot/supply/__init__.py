import json
import time
from functools import wraps


class JSONEncoder(json.JSONEncoder):

    serializers = {}

    def default(self, o):
        marshaller = self.serializers.get(type(o), super(JSONEncoder, self).default)
        return marshaller(o)


class JSONDecoder:

    decoders = {}

    def __call__(self, dct):
        if dct.get("__class__") in self.decoders:
            return self.decoders[dct["__class__"]](dct)
        return dct


class MatchMock:
    def group(self, index):
        return False


def retry_in_rc(max_attempts=10, notify_after=7):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            product = kwargs.get('product', 'Unknown')
            version = kwargs.get('version', 'Unknown')
            bot = kwargs.get('bot', None)
            event = kwargs.get('event', {})
            back_markup = kwargs.get('back_markup', [])

            while attempts < max_attempts:
                result = func(*args, **kwargs)
                latest_rc_name, rc_status, rc_issue_key, rc_version = result

                if latest_rc_name and rc_status and rc_issue_key and rc_version:
                    return result

                attempts += 1
                if attempts == notify_after:
                    if bot and event and back_markup:
                        bot.edit_text(
                            chat_id=event.from_chat,
                            msg_id=event.data['message'].get('msgId'),
                            text=f"Поиск информации по {product} версии {version} "
                                 f"занимает больше времени, чем ожидалось... ⏳",
                            parse_mode="HTML",
                            inline_keyboard_markup=f"{json.dumps(back_markup)}"
                        )
                if attempts >= notify_after:
                    time.sleep(1)

            return None, None, None, None

        return wrapper
    return decorator
