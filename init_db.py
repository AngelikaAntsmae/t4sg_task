import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
            ('FN1', 'LN1', '1@2.com', '123456')
            )

cur.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
            ('FN2', 'LN2', '2@2.com', '123456')
            )
cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('News from the UK', 'The UK has approved Pfizer-Biontech vaccine')
            )

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('News from the US', 'The US has approved Moderna')
            )

connection.commit()
connection.close()
