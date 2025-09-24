
import sqlite3, datetime, math
from shared.config import DB_PATH

def db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA temp_store = MEMORY;")
        conn.execute("PRAGMA cache_size = -40000;")
        conn.execute("PRAGMA busy_timeout = 3000;")
    except Exception:
        pass
    return conn

def db_init(seed_target=12000):
    with db_connect() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            descr TEXT NOT NULL,
            category TEXT NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            price REAL NOT NULL DEFAULT 0.0
        );""")
        c.execute("""CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT, date TEXT, status TEXT, total REAL DEFAULT 0.0
        );""")
        c.execute("""CREATE TABLE IF NOT EXISTS order_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            descr TEXT NOT NULL,
            qty INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE RESTRICT
        );""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_items_code ON items(code);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_items_cat ON items(category);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_items_stock ON items(stock);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_ord_date ON orders(date);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_ord_status ON orders(status);")
        count = c.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        if count < seed_target:
            if count == 0:
                base = [
                    ("SKU-00001","Teclado Mecânico","Periféricos",35,199.90),
                    ("SKU-00002","Mouse Óptico","Periféricos",80,69.90),
                    ("SKU-00003","Monitor 24\"", "Monitores",12,999.00),
                    ("SKU-00004","Headset USB","Áudio",18,149.00),
                    ("SKU-00005","Webcam HD","Vídeo",9,229.00),
                    ("SKU-00006","Notebook 14\"", "Computadores",6,3999.00),
                ]
                c.executemany("INSERT INTO items(code,descr,category,stock,price) VALUES(?,?,?,?,?)", base)
                count = len(base)
            need = seed_target - count
            c.execute("PRAGMA synchronous=OFF;"); c.execute("PRAGMA journal_mode=MEMORY;")
            cats = ["Periféricos","Monitores","Áudio","Vídeo","Computadores","Redes","Impressão","Acessórios","Armazenamento","Energia"]
            batch = []; start = 10000
            for i in range(need):
                n = start + i
                code = f"SKU-{n:05d}"
                cat = cats[i % len(cats)]
                stock = (i*7) % 120
                price = round(19.9 + (i % 500) * 3.47, 2)
                descr = f"Item {n} {cat} - Modelo {(i%100)+1}"
                batch.append((code, descr, cat, stock, price))
                if len(batch) >= 2000:
                    c.executemany("INSERT OR IGNORE INTO items(code,descr,category,stock,price) VALUES(?,?,?,?,?)", batch); batch.clear()
            if batch:
                c.executemany("INSERT OR IGNORE INTO items(code,descr,category,stock,price) VALUES(?,?,?,?,?)", batch)
        conn.commit()
