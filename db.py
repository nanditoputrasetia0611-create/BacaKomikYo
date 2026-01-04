import sqlite3
from datetime import datetime

DB_PATH = "stats.db"


# ================== INIT DATABASE ==================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS comic_reads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT,
            views INTEGER DEFAULT 0,
            last_read TEXT,
            UNIQUE(category, title)
        )
    """)

    conn.commit()
    conn.close()


# ================== RECORD READ ==================
def record_read(category, title):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO comic_reads (category, title, views, last_read)
        VALUES (?, ?, 1, ?)
        ON CONFLICT(category, title)
        DO UPDATE SET
            views = views + 1,
            last_read = ?
    """, (category, title, datetime.now().isoformat(), datetime.now().isoformat()))

    conn.commit()
    conn.close()


# ================== GET TOP COMICS ==================
def get_top_comics(limit=5):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT title, views
        FROM comic_reads
        ORDER BY views DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()

    return [
        {"title": r[0], "views": r[1]}
        for r in rows
    ]
