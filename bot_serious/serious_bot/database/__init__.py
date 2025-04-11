"""Базовый класс для наследования."""


class Database:
    """Шаблон БД.

    Работа с парами key/value в БД.

    """

    def __init__(self, config):
        """Создание БД.

        """
        self.name = ""
        self.config = config
        self.client = None
        self.database = None

    async def connect(self):
        """Подключение с БД

        """
        raise NotImplementedError

    async def disconnect(self):
        """Закрытие соединения с БД

        """

    async def put(self, key, data):
        """Сохранить данные в БД по ключу

        Объект данных должен быть сериализован

        Args:
            key (string): ключ
            data (object): объект данных

        Returns:
            bool: True успешное сохранение, False в ином случае

        """
        raise NotImplementedError

    async def get(self, key):
        """Получить объект из БД по ключу

        Args:
            key (string): ключ

        Returns:
            object or None: объект данных

        """
        raise NotImplementedError

    async def delete(self, key):
        """Удалить объект из БД по ключу

        Args:
            key (string): ключ

        Returns:
            object or None: объект данных

        """
        raise NotImplementedError
