import sqlite3

conn = sqlite3.connect("waste.db")

cursor = conn.cursor()

cursor.execute(
    "SELECT * FROM detections"
)

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()