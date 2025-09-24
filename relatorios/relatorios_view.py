
import csv, datetime
from pathlib import Path
from tkinter import ttk, messagebox
from conexao.db import db_connect
from shared.config import EXPORT_DIR
from shared.ui import build_sidebar, build_top_links

def build(container, on_tab_select):
    root = ttk.PanedWindow(container, orient="horizontal"); root.pack(expand=True, fill="both")
    left = ttk.Frame(root, width=240); right = ttk.Frame(root); root.add(left, weight=0); root.add(right, weight=1)

    with db_connect() as conn:
        items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    exports = len(list(EXPORT_DIR.glob("*.csv"))) if EXPORT_DIR.exists() else 0
    sb_cards = [(str(items), "Itens", "no inventário"),
                (str(orders), "Pedidos", "registrados"),
                (str(exports), "Exportações", "arquivos CSV")]
    build_sidebar(left, "Visão Geral", sb_cards)
    build_top_links(right, on_tab_select, 3)

    parent = ttk.Frame(right, padding=10); parent.pack(expand=True, fill="both")
    ttk.Label(parent,text="Relatórios",font=("Segoe UI",14,"bold")).pack(anchor="w",pady=(0,8))
    ttk.Label(parent,text="Exportações rápidas (CSV). Os arquivos serão salvos na pasta 'exports' ao lado do app.", style="Muted.TLabel").pack(anchor="w",pady=(0,8))
    btns=ttk.Frame(parent); btns.pack(anchor="w",pady=6)
    ttk.Button(btns,text="Exportar Inventário (CSV)",command=_export_inv_csv).pack(side="left",padx=6)
    ttk.Button(btns,text="Exportar Pedidos (CSV)",command=_export_orders_csv).pack(side="left",padx=6)

def _export_inv_csv():
    EXPORT_DIR.mkdir(exist_ok=True)
    path = EXPORT_DIR / f"inventario_{datetime.date.today().isoformat()}.csv"
    with db_connect() as conn, open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f, delimiter=";")
        w.writerow(["id","code","descr","category","stock","price"])
        for r in conn.execute("SELECT id,code,descr,category,stock,price FROM items ORDER BY id"):
            w.writerow([r["id"],r["code"],r["descr"],r["category"],r["stock"],f"{r['price']:.2f}"])
    messagebox.showinfo("Relatórios", f"Inventário exportado:\n{path}")

def _export_orders_csv():
    EXPORT_DIR.mkdir(exist_ok=True)
    path = EXPORT_DIR / f"pedidos_{datetime.date.today().isoformat()}.csv"
    with db_connect() as conn, open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f, delimiter=";")
        w.writerow(["order_id","date","customer","status","total","item_code","item_descr","qty","price","line_total"])
        sql = """SELECT o.id as oid, o.date, o.customer, o.status, o.total,
                        oi.code, oi.descr, oi.qty, oi.price, oi.total as line_total
                 FROM orders o LEFT JOIN order_items oi ON oi.order_id=o.id
                 ORDER BY o.id DESC, oi.id"""
        for r in conn.execute(sql):
            w.writerow([r["oid"],r["date"],r["customer"],r["status"],f"{r['total']:.2f}",
                        r["code"] or "", r["descr"] or "", r["qty"] or 0, f"{(r['price'] or 0.0):.2f}", f"{(r['line_total'] or 0.0):.2f}"])
    messagebox.showinfo("Relatórios", f"Pedidos exportados:\n{path}")
