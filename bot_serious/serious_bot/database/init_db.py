import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# White list

# release managers
cur.execute("INSERT INTO white_list (user_id) VALUES ('email_коллеги_из_vk_teams')")

connection.commit()
connection.close()
