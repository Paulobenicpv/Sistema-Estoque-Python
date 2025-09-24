
import datetime, sqlite3
from .db import db_connect
class Repo:
    @staticmethod
    def list_items(term=None, limit=None, offset=0):
        sql = "SELECT * FROM items"; params = []
        if term:
            sql += " WHERE code LIKE ? OR descr LIKE ? OR category LIKE ?"
            v = f"%{term}%"; params += [v,v,v]
        sql += " ORDER BY id"
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"; params += [int(limit), int(offset)]
        with db_connect() as conn:
            return list(conn.execute(sql, params))

    @staticmethod
    def count_items(term=None):
        sql = "SELECT COUNT(*) FROM items"; params=[]
        if term:
            sql += " WHERE code LIKE ? OR descr LIKE ? OR category LIKE ?"
            v = f"%{term}%"; params += [v,v,v]
        with db_connect() as conn:
            return conn.execute(sql, params).fetchone()[0]

    @staticmethod
    def add_item(code, descr, category, stock, price):
        with db_connect() as conn:
            cur = conn.execute("INSERT INTO items(code,descr,category,stock,price) VALUES(?,?,?,?,?)",
                               (code, descr, category, stock, price)); conn.commit(); return cur.lastrowid

    @staticmethod
    def update_item(item_id, code, descr, category, stock, price):
        with db_connect() as conn:
            conn.execute("UPDATE items SET code=?, descr=?, category=?, stock=?, price=? WHERE id=?",
                         (code, descr, category, stock, price, item_id)); conn.commit()

    @staticmethod
    def delete_item(item_id):
        with db_connect() as conn:
            conn.execute("DELETE FROM items WHERE id=?", (item_id,)); conn.commit()

    @staticmethod
    def metrics():
        with db_connect() as conn:
            total_value = conn.execute("SELECT COALESCE(SUM(stock*price),0) FROM items").fetchone()[0] or 0.0
            by_cat = dict(conn.execute("SELECT category, SUM(stock) FROM items GROUP BY category").fetchall())
            low = conn.execute("SELECT COUNT(*) FROM items WHERE stock < 15").fetchone()[0]
            total_items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
            orders_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            return {"total_value": total_value, "category_distribution": by_cat, "low": low, "ok": max(0,total_items-low), "orders_count": orders_count}

    @staticmethod
    def list_orders(term=None, status=None, limit=500, offset=0):
        sql = "SELECT * FROM orders"; params = []; where=[]
        if term:
            where.append("(customer LIKE ? OR id LIKE ?)"); v = f"%{term}%"; params += [v, v]
        if status and status != "Todos":
            where.append("status = ?"); params.append(status)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY id DESC LIMIT ? OFFSET ?"; params += [int(limit), int(offset)]
        with db_connect() as conn:
            return list(conn.execute(sql, params))

    @staticmethod
    def get_order(order_id):
        with db_connect() as conn:
            o = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
            items = list(conn.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,)))
        return o, items

    @staticmethod
    def create_order(customer, status, items, date=None):
        if not items: raise ValueError("Inclua ao menos um item no pedido.")
        date = date or datetime.date.today().isoformat()
        total = sum(i["qty"] * i["price"] for i in items)
        with db_connect() as conn:
            try:
                conn.execute("BEGIN")
                cur = conn.execute("INSERT INTO orders(customer,date,status,total) VALUES(?,?,?,?)",
                                   (customer, date, status, total))
                order_id = cur.lastrowid
                if status == "Concluído":
                    for it in items:
                        stock = conn.execute("SELECT stock FROM items WHERE id=?", (it["item_id"],)).fetchone()[0]
                        if stock < it["qty"]:
                            raise ValueError(f"Estoque insuficiente para {it['code']} (disp: {stock}, qtd: {it['qty']}).")
                    for it in items:
                        conn.execute("UPDATE items SET stock=stock-? WHERE id=?", (it["qty"], it["item_id"]))
                for it in items:
                    line_total = it["qty"] * it["price"]
                    conn.execute("""INSERT INTO order_items(order_id,item_id,code,descr,qty,price,total)
                                    VALUES(?,?,?,?,?,?,?)""",
                                 (order_id, it["item_id"], it["code"], it["descr"], it["qty"], it["price"], line_total))
                conn.commit()
                return order_id
            except Exception as e:
                conn.rollback(); raise e

    @staticmethod
    def cancel_order(order_id, restock=True):
        with db_connect() as conn:
            try:
                conn.execute("BEGIN")
                ord_row = conn.execute("SELECT status FROM orders WHERE id=?", (order_id,)).fetchone()
                if not ord_row: raise ValueError("Pedido não encontrado.")
                status = ord_row["status"]
                if status == "Cancelado":
                    raise ValueError("Pedido já está cancelado.")
                conn.execute("UPDATE orders SET status=? WHERE id=?", ("Cancelado", order_id))
                if restock and status == "Concluído":
                    for it in conn.execute("SELECT item_id, qty FROM order_items WHERE order_id=?", (order_id,)):
                        conn.execute("UPDATE items SET stock=stock+? WHERE id=?", (it["qty"], it["item_id"]))
                conn.commit()
            except Exception as e:
                conn.rollback(); raise e

    @staticmethod
    def approve_order(order_id):
        with db_connect() as conn:
            try:
                conn.execute("BEGIN")
                row = conn.execute("SELECT status FROM orders WHERE id=?", (order_id,)).fetchone()
                if not row: raise ValueError("Pedido não encontrado.")
                status = row["status"]
                if status == "Concluído": return
                if status in ("Cancelado", "Reprovado"):
                    raise ValueError("Pedido cancelado/reprovado não pode ser aprovado.")
                for it in conn.execute("SELECT item_id, qty FROM order_items WHERE order_id=?", (order_id,)):
                    stock = conn.execute("SELECT stock FROM items WHERE id=?", (it["item_id"],)).fetchone()[0]
                    if stock < it["qty"]:
                        raise ValueError(f"Estoque insuficiente para item {it['item_id']} (disp: {stock}, qtd: {it['qty']}).")
                for it in conn.execute("SELECT item_id, qty FROM order_items WHERE order_id=?", (order_id,)):
                    conn.execute("UPDATE items SET stock = stock - ? WHERE id=?", (it["qty"], it["item_id"]))
                conn.execute("UPDATE orders SET status='Concluído' WHERE id=?", (order_id,))
                conn.commit()
            except Exception as e:
                conn.rollback(); raise e

    @staticmethod
    def reject_order(order_id):
        with db_connect() as conn:
            row = conn.execute("SELECT status FROM orders WHERE id=?", (order_id,)).fetchone()
            if not row: raise ValueError("Pedido não encontrado.")
            status = row["status"]
            if status == "Concluído":
                raise ValueError("Use 'Cancelar/Repor' para desfazer um pedido já concluído.")
            if status in ("Cancelado", "Reprovado"):
                raise ValueError("Pedido já está cancelado/reprovado.")
            conn.execute("UPDATE orders SET status='Reprovado' WHERE id=?", (order_id,))
            conn.commit()
