import sqlite3


def save_to_db(table_name: str, new_reviews: []):
    try:
        connection = sqlite3.connect('/etc/database.db')
        cursor = connection.cursor()

        for review_id in new_reviews:
            cursor.execute(f"INSERT INTO {table_name} (review_id) VALUES ('{review_id}')")

        connection.commit()
        connection.close()
    except BaseException as exc:
        print(f"Exception occurred while performing database connection to put new reviews: {exc}")


def load_from_db(table_name: str) -> []:
    try:
        connection = sqlite3.connect('/etc/database.db')
        cursor = connection.cursor()

        sequence = f"""SELECT * FROM {table_name}"""
        known_reviews_ids = []
        for row in cursor.execute(sequence):
            known_reviews_ids.append(row[2])

        connection.commit()
        connection.close()
    except BaseException as exc:
        print(f"Exception occurred while performing database connection to get known reviews: {exc}")
        known_reviews_ids = []

    return known_reviews_ids
