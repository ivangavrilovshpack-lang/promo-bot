import sqlite3

def init_db():
    conn = sqlite3.connect('promo.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            subscribed INTEGER DEFAULT 0,
            vip_until TEXT DEFAULT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS promocodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            description TEXT,
            link TEXT,
            expires TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = sqlite3.connect('promo.db')
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def save_promo(code, desc, link, expires):
    conn = sqlite3.connect('promo.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO promocodes (code, description, link, expires) VALUES (?, ?, ?, ?)", (code, desc, link, expires))
    conn.commit()
    conn.close()

def get_random_promo():
    conn = sqlite3.connect('promo.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM promocodes ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row
