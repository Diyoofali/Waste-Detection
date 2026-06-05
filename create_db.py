import sqlite3

conn = sqlite3.connect("waste.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    confidence REAL,
    timestamp TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully")