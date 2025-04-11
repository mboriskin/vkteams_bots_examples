from loguru import logger

from serious_bot.core.product import Product


STRUCTURE_ID = 999


class VKTeamsPlatform:
    def __init__(
        self,
        product: Product,
    ) -> None:
        self.product = product
        self.logger = logger

        self.structure_id = STRUCTURE_ID

    def prepare(self) -> None:
        self.logger.warning("prepare method is not implemented")

    def process(self, bot, event, back_markup, version, product_raw):
        self.logger.warning("process method is not implemented")

    def cleanup(self) -> None:
        self.logger.warning("Cleanup method is not implemented")
