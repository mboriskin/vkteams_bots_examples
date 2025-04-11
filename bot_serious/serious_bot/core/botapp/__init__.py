from typing import Optional
from threading import Event
from bot.bot import Bot
from bot.handler import (
    HelpCommandHandler,
    BotButtonCommandHandler,
    MessageHandler,
    CommandHandler
)

from loguru import logger


class BotApp:
    def __init__(
        self,
        name: str,
        version: str,
        token: str,
        api_url: str,
        timeout: Optional[float] = None,
    ) -> None:
        self.name = name
        self.version = version
        self.timeout = timeout
        self.bot = self.create_bot(token=token, api_url=api_url)
        self._interruption_event = Event()

    @property
    def interrupted(self) -> bool:
        return self._interruption_event.is_set()

    @staticmethod
    def create_bot(token, api_url):
        return Bot(token=token, api_url_base=api_url)

    def prepare(self) -> None:
        logger.warning("Prepare method is not implemented in the QueueApp! Don't forget to subscribe to the topic.")

    def message_cb(self, bot, event):
        logger.warning("Message_cb method is not implemented in the QueueApp! Don't forget to subscribe to the topic.")

    def command_cb(self, bot, event):
        logger.warning("Command_cb method is not implemented in the QueueApp! Don't forget to subscribe to the topic.")

    def buttons_answer_cb(self, bot, event):
        logger.warning(
            "Buttons_answer_cb method is not implemented in the QueueApp! Don't forget to subscribe to the topic.")

    def help_command_cb(self, bot, event):
        logger.warning(
            "Help_command_cb method is not implemented in the QueueApp! Don't forget to subscribe to the topic.")

    def main(self) -> None:
        logger.info(f"Start {self.name} ver. {self.version}.")

        self.prepare()

        while not self.interrupted:
            try:
                logger.info("Create HelpCommand callback")
                self.bot.dispatcher.add_handler(HelpCommandHandler(callback=self.help_command_cb))
                logger.info("Create Message callback")
                self.bot.dispatcher.add_handler(MessageHandler(callback=self.message_cb))
                logger.info("Create Command callback")
                self.bot.dispatcher.add_handler(CommandHandler(callback=self.command_cb))
                logger.info("Create BotButtonCommand callback")
                self.bot.dispatcher.add_handler(BotButtonCommandHandler(callback=self.buttons_answer_cb))
                logger.info("Start polling")
                self.bot.start_polling()
                logger.info("Idle")
                self.bot.idle()
            except BaseException as exc:
                logger.info(f'Error: {exc}')

        self.cleanup()

        logger.info(f"End {self.name}.")

    def cleanup(self) -> None:
        logger.warning("Cleanup method is not implemented in the BotApp! Don't forget to close the connections.")
