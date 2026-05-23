import sqlite3
try:
    conn = sqlite3.connect('nexus.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables:", c.fetchall())
    c.execute("SELECT count(*) FROM applications;")
    print("Applications:", c.fetchall())
except Exception as e:
    print(e)
