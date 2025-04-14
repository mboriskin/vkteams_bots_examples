import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Google Play
cur.execute("INSERT INTO googleplay_reviews (review_id) VALUES ('c248accf-3203-47c2-9352-7379b12f948f')")
cur.execute("INSERT INTO googleplay_reviews (review_id) VALUES ('c248accf-3203-47c2-9352-7379b12f948f')")
cur.execute("INSERT INTO googleplay_reviews (review_id) VALUES ('a9e2cca0-15b8-4822-a6fe-e7e3010f1bd5')")
cur.execute("INSERT INTO googleplay_reviews (review_id) VALUES ('7ec8a6d6-c88f-43fd-8683-95c398c14db7')")
cur.execute("INSERT INTO googleplay_reviews (review_id) VALUES ('52934965-fe4a-4833-9ec7-62316c64f5d8')")

# RuStore
cur.execute("INSERT INTO rustore_reviews (review_id) VALUES ('abc1')")

connection.commit()
connection.close()
