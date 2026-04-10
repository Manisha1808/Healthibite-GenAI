import sqlite3

def init_db():
    conn = sqlite3.connect("healthibite.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        query TEXT,
        age TEXT,
        goal TEXT,
        activity TEXT,
        severity TEXT,
        response TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_history(query, age, goal, activity, severity, response):
    conn = sqlite3.connect("healthibite.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO history (
        query, age, goal, activity, severity, response
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (query, age, goal, activity, severity, response))

    conn.commit()
    conn.close()