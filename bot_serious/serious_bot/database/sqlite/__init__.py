"""Модуль sqlite"""

import json
import aiosqlite
from loguru import logger

from serious_bot.database import Database
from serious_bot.supply import JSONEncoder, JSONDecoder

DEFAULT_DB_PATH = "/etc/database.db"
CONFIG_SCHEMA = {
    "path": str,
    "table": str
}


class DatabaseSqlite(Database):
    """SQLite.

    SQLite Database для хранения данных с помощью sqlite.

    """

    def __init__(self, config):
        """Инициализация.

        Определение установочных параметров БД

        Args:
            config (dict): см. CONFIG_SCHEMA

        """
        super().__init__(config)
        self.name = "sqlite"
        self.config = config
        self.conn_args = {
            "isolation_level": None
        }
        self.db_file = self.config.get(
            "path", DEFAULT_DB_PATH
        )
        self.table = self.config.get("table", "white_list")

        logger.debug("Loaded sqlite database connector")

    async def connect(self):
        """Подключение к БД.

        Подключение к sqlite database.
        Создание БД DEFAULT_ROOT_PATH and установка имени БД
        БД будет создана если не существует

        """
        self.client = await aiosqlite.connect(self.db_file, **self.conn_args)

        cur = await self.client.cursor()
        await cur.execute(
            "CREATE TABLE IF NOT EXISTS {}"
            "(key text PRIMARY KEY, data text)".format(self.table)
        )
        await self.client.commit()

        logger.info(f"Connected to sqlite {self.db_file}")

    async def put(self, key, data):
        """Положить данные в БД.

        Вставка или замена объекта в БД по заданному ключу.
        Вставляемый объект сериализуется в JSON data, используя класс JSONEncoder

        Args:
            key (string): ключ.
            data (object): данные для хранения.

        """
        logger.debug(f"Putting {key} into sqlite")

        json_data = json.dumps(data, cls=JSONEncoder)

        cur = await self.client.cursor()
        await cur.execute("DELETE FROM {} WHERE key=?".format(self.table), (key,))
        await cur.execute(
            "INSERT INTO {} VALUES (?, ?)".format(self.table), (key, json_data)
        )
        await self.client.commit()

    async def get(self, key):
        """Получение данных по ключу.

        Args:
            key (string): ключ.

        Returns:
            object or None: объект, который хранится по ключу

        """
        logger.debug(f"Getting {key} from sqlite")
        data = None

        cur = await self.client.cursor()
        await cur.execute("SELECT data FROM {} WHERE key=?".format(self.table), (key,))
        row = await cur.fetchone()
        if row:
            data = json.loads(row[0], object_hook=JSONDecoder())

        return data

    async def delete(self, key):
        """Удаление данных из БД по ключу.

        Args:
            key (string): ключ.

        """
        logger.debug(f"Deleting {key} from sqlite")

        cur = await self.client.cursor()
        await cur.execute("DELETE FROM {} WHERE key=?".format(self.table), (key,))
        await self.client.commit()

    async def disconnect(self):
        """Закрыть соединение с БД"""
        if self.client:
            await self.client.close()
