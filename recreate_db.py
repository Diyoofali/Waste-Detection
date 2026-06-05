import sqlite3

conn = sqlite3.connect("waste.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS detections")

cursor.execute("""
CREATE TABLE detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_name TEXT,
    category TEXT,
    confidence REAL,
    timestamp TEXT
)
""")

conn.commit()
conn.close()

print("Database recreated")
