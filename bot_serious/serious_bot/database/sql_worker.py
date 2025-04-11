import sqlite3

"""Временная заглушка - не используйте.

Используйте SQLiteDatabase реализацию.

"""


def save_to_db(table_name: str, new_users: []) -> bool:
    try:
        connection = sqlite3.connect('/etc/database.db')
        cursor = connection.cursor()

        for user_id in new_users:
            cursor.execute(f"INSERT INTO {table_name} (user_id) VALUES ('{user_id}')")

        connection.commit()
        connection.close()
    except BaseException as exc:
        print(f"Exception occurred while performing database connection to put new users to {table_name}: {exc}")
        return False

    return True


def load_from_db(table_name: str) -> []:
    try:
        connection = sqlite3.connect('/etc/database.db')
        cursor = connection.cursor()

        sequence = f"""SELECT * FROM {table_name}"""
        known_users_ids = []
        for row in cursor.execute(sequence):
            known_users_ids.append(row[2])

        connection.commit()
        connection.close()
    except BaseException as exc:
        print(f"Exception occurred while performing database connection to get known users from {table_name}: {exc}")
        known_users_ids = []

    return known_users_ids


def delete_from_db(table_name: str, drop_users: []) -> bool:
    try:
        connection = sqlite3.connect('/etc/database.db')
        cursor = connection.cursor()

        for user_id in drop_users:
            cursor.execute(f"DELETE FROM {table_name} WHERE user_id = '{user_id}'")

        connection.commit()
        connection.close()
    except BaseException as exc:
        print(f"Exception occurred while performing database connection to drop users from the {table_name}: {exc}")
        return False

    return True
