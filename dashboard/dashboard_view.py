
import tkinter as tk
from tkinter import ttk
from conexao.repo import Repo
from conexao.db import db_connect
from shared.config import CANVAS_BG, COLORS, THEMES, currency_br
from shared.ui import Card, draw_line_chart, draw_bar_chart, draw_progress_bar, draw_donut, build_sidebar, build_top_links

def _orders_today():
    import datetime
    today = datetime.date.today().isoformat()
    with db_connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM orders WHERE date=?", (today,)).fetchone()[0]

def _orders_week():
    import datetime
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    with db_connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM orders WHERE date BETWEEN ? AND ?", (monday.isoformat(), sunday.isoformat())).fetchone()[0]

def _orders_open():
    with db_connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM orders WHERE status='Aberto'").fetchone()[0]

def build(container, on_tab_select):
    root = ttk.PanedWindow(container, orient="horizontal"); root.pack(expand=True, fill="both")
    left = ttk.Frame(root, width=240); right = ttk.Frame(root); root.add(left, weight=0); root.add(right, weight=1)
    m = Repo.metrics()
    sb_cards = [
        (str(_orders_open()), "Pendências", "Pedidos em Aberto"),
        (str(_orders_today()), "Hoje", "Pedidos criados"),
        (str(_orders_week()), "Esta Semana", "Total de pedidos"),
    ]
    build_sidebar(left, "Visão Geral", sb_cards)
    build_top_links(right, on_tab_select, 0)

    grid = ttk.Frame(right, padding=10); grid.pack(expand=True, fill="both")
    for i in range(2): grid.columnconfigure(i, weight=1)

    k1 = Card(grid, "Valor Total do Estoque", row=0, column=0, sticky="nsew", padx=6, pady=6)
    ttk.Label(k1, text=currency_br(m["total_value"]), font=("Segoe UI", 22, "bold")).grid(row=1, column=0, sticky="w")

    k2 = Card(grid, "Pedidos", row=0, column=1, sticky="nsew", padx=6, pady=6)
    ttk.Label(k2, text=str(m["orders_count"]), font=("Segoe UI", 22, "bold")).grid(row=1, column=0, sticky="w")

    c1 = Card(grid, "Vendas Mensais", row=1, column=0, sticky="nsew", padx=6, pady=6)
    canv1 = tk.Canvas(c1, width=460, height=200, bg=CANVAS_BG, highlightthickness=0); canv1.grid(row=1,column=0,sticky="nsew")
    draw_line_chart(canv1, [12,15,13,18,16,22])

    c2 = Card(grid, "Nível de Estoque", row=1, column=1, sticky="nsew", padx=6, pady=6)
    canv2 = tk.Canvas(c2, width=460, height=200, bg=CANVAS_BG, highlightthickness=0); canv2.grid(row=1,column=0,sticky="nsew")
    with db_connect() as conn:
        rows = conn.execute("SELECT code, stock FROM items ORDER BY stock DESC, id LIMIT 5").fetchall()
    draw_bar_chart(canv2, [r["code"] for r in rows], [r["stock"] for r in rows])

    c3 = Card(grid, "Reposições Necessárias", row=2, column=0, sticky="nsew", padx=6, pady=6)
    canv3 = tk.Canvas(c3, width=460, height=60, bg=CANVAS_BG, highlightthickness=0); canv3.grid(row=1,column=0,sticky="ew")
    canv4 = tk.Canvas(c3, width=460, height=60, bg=CANVAS_BG, highlightthickness=0); canv4.grid(row=2,column=0,sticky="ew", pady=(8,0))
    total = max(1, m["low"] + m["ok"])
    draw_progress_bar(canv3, m["low"], total, color=THEMES["dark"]["good"] if COLORS is THEMES["dark"] else THEMES["light"]["good"])
    draw_progress_bar(canv4, m["ok"], total, color=THEMES["dark"]["accent2"] if COLORS is THEMES["dark"] else THEMES["light"]["accent2"])
    ttk.Label(c3, text=f"Abaixo do mínimo: {m['low']}", style="Muted.TLabel").grid(row=3, column=0, sticky="w", pady=(6,0))
    ttk.Label(c3, text=f"Itens ok: {m['ok']}", style="Muted.TLabel").grid(row=4, column=0, sticky="w")

    c4 = Card(grid, "Divisão do Estoque por Categoria", row=2, column=1, sticky="nsew", padx=6, pady=6)
    canv5 = tk.Canvas(c4, width=460, height=200, bg=CANVAS_BG, highlightthickness=0); canv5.grid(row=1,column=0,sticky="nsew")
    draw_donut(canv5, m["category_distribution"])
