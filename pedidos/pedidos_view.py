
import tkinter as tk
from tkinter import ttk, messagebox
from conexao.repo import Repo
from shared.config import currency_br
from shared.ui import build_sidebar, build_top_links
from shared.dialogs import OrderDialog
from conexao.db import db_connect

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

class PedidosView:
    def __init__(self, container, on_tab_select):
        self.container = container; self.on_tab_select = on_tab_select
        self._build(container)

    def _build(self, container):
        root = ttk.PanedWindow(container, orient="horizontal"); root.pack(expand=True, fill="both")
        left = ttk.Frame(root, width=240); right = ttk.Frame(root); root.add(left, weight=0); root.add(right, weight=1)

        sb_cards = [
            (str(_orders_open()), "Pendências", "Pedidos em Aberto"),
            (str(_orders_today()), "Hoje", "Pedidos criados"),
            (str(_orders_week()), "Esta Semana", "Total de pedidos"),
        ]
        build_sidebar(left, "Visão Geral", sb_cards)
        build_top_links(right, self.on_tab_select, 2)

        parent = ttk.Frame(right, padding=10); parent.pack(expand=True, fill="both")
        head=ttk.Frame(parent); head.pack(fill="x")
        ttk.Label(head,text="Pedidos",font=("Segoe UI",14,"bold")).pack(side="left")
        ttk.Button(head,text="Atualizar",command=self._load_orders).pack(side="right")

        bar=ttk.Frame(parent); bar.pack(fill="x",pady=6)
        ttk.Button(bar,text="Novo Pedido",command=self._new_order).pack(side="left",padx=(0,6))
        ttk.Button(bar,text="Detalhes",command=self._view_order).pack(side="left",padx=6)
        ttk.Button(bar,text="Aprovar",command=self._approve_order).pack(side="left",padx=6)
        ttk.Button(bar,text="Reprovar",command=self._reject_order).pack(side="left",padx=6)
        ttk.Button(bar,text="Cancelar/Repor",command=self._cancel_order).pack(side="left",padx=6)
        ttk.Button(bar,text="Excluir",command=self._delete_order).pack(side="left",padx=6)
        self.order_status=tk.StringVar(value="Todos")
        ttk.Label(bar,text="Status:").pack(side="right"); ttk.Combobox(bar,textvariable=self.order_status,values=["Todos","Aberto","Concluído","Cancelado"],state="readonly",width=12).pack(side="right",padx=(6,12))
        self.order_search=tk.StringVar(); ttk.Entry(bar,textvariable=self.order_search,width=24).pack(side="right",padx=6); ttk.Label(bar,text="Buscar:").pack(side="right")

        cols=("id","Data","Cliente","Status","Total")
        self.orders=ttk.Treeview(parent,columns=cols,show="headings",height=16)
        for col,w in (("id",60),("Data",100),("Cliente",200),("Status",100),("Total",100)):
            self.orders.heading(col,text=col); self.orders.column(col,width=w,anchor="w")
        self.orders.pack(expand=True,fill="both")

        nav=ttk.Frame(parent); nav.pack(fill="x",pady=(6,0))
        ttk.Button(nav,text="Filtrar",command=self._load_orders).pack(side="left")
        ttk.Button(nav,text="Limpar",command=lambda:(self.order_search.set(""),self.order_status.set("Todos"),self._load_orders())).pack(side="left",padx=6)

        self._load_orders()

    def _get_selected_order_id(self):
        sel=self.orders.selection()
        if not sel: messagebox.showinfo("Pedidos","Selecione um pedido."); return None
        return int(self.orders.item(sel[0],"values")[0])

    def _load_orders(self):
        children = self.orders.get_children()
        if children:
            for i in children:
                self.orders.delete(i)
        term = getattr(self, "order_search", tk.StringVar()).get().strip() or None
        status = getattr(self, "order_status", tk.StringVar(value="Todos")).get()
        for r in Repo.list_orders(term, status, limit=500, offset=0):
            self.orders.insert("", "end", values=(r["id"], r["date"], r["customer"], r["status"], currency_br(r["total"])))

    def _new_order(self):
        dlg=OrderDialog(self.container)
        if getattr(dlg, "result", None):
            self._load_orders()

    def _view_order(self):
        oid=self._get_selected_order_id()
        if oid is None: return
        o, items = Repo.get_order(oid)
        top=tk.Toplevel(self.container); top.title(f"Pedido #{oid}"); top.transient(self.container); top.grab_set()
        from shared.config import COLORS
        top.configure(bg=COLORS["bg"])
        frm=ttk.Frame(top,padding=10); frm.pack(expand=True,fill="both")
        ttk.Label(frm,text=f"Cliente: {o['customer']}").grid(row=0,column=0,sticky="w",padx=4,pady=4)
        ttk.Label(frm,text=f"Data: {o['date']}").grid(row=0,column=1,sticky="w",padx=4,pady=4)
        ttk.Label(frm,text=f"Status: {o['status']}").grid(row=0,column=2,sticky="w",padx=4,pady=4)
        cols=("Código","Descrição","Qtd","Preço","Total"); tv=ttk.Treeview(frm,columns=cols,show="headings",height=12)
        for col,w in (("Código",120),("Descrição",220),("Qtd",60),("Preço",80),("Total",80)):
            tv.heading(col,text=col); tv.column(col,width=w,anchor="w")
        tv.grid(row=1,column=0,columnspan=3,sticky="nsew",padx=4,pady=6); frm.rowconfigure(1,weight=1); frm.columnconfigure(0,weight=1)
        tot=0.0
        for it in items:
            tv.insert("", "end", values=(it["code"], it["descr"], it["qty"], f"{it['price']:.2f}", f"{it['total']:.2f}"))
            tot += it["total"]
        ttk.Label(frm,text=f"Total: {currency_br(tot)}",font=("Segoe UI",11,"bold")).grid(row=2,column=0,sticky="w",padx=4,pady=6)
        btns=ttk.Frame(frm); btns.grid(row=3,column=0,sticky="e",columnspan=3,pady=(6,0))
        ttk.Button(btns,text="Fechar",command=top.destroy).pack(side="right")

    def _cancel_order(self):
        oid=self._get_selected_order_id()
        if oid is None: return
        if not messagebox.askyesno("Cancelar Pedido","Cancelar o pedido selecionado e repor estoque (se concluído)?"):
            return
        try:
            Repo.cancel_order(oid, restock=True)
            messagebox.showinfo("Pedidos","Pedido cancelado com sucesso.")
            self._load_orders()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _delete_order(self):
        oid=self._get_selected_order_id()
        if oid is None: return
        if not messagebox.askyesno("Excluir Pedido","Excluir definitivamente este pedido?"):
            return
        from conexao.db import db_connect
        with db_connect() as conn:
            conn.execute("DELETE FROM orders WHERE id=?", (oid,)); conn.execute("DELETE FROM order_items WHERE order_id=?", (oid,)); conn.commit()
        self._load_orders()

    def _approve_order(self):
        oid=self._get_selected_order_id()
        if oid is None: return
        try:
            Repo.approve_order(oid)
            messagebox.showinfo('Pedidos', 'Pedido aprovado e concluído com sucesso.')
            self._load_orders()
        except Exception as e:
            messagebox.showerror('Erro', str(e))

    def _reject_order(self):
        oid=self._get_selected_order_id()
        if oid is None: return
        if not messagebox.askyesno('Reprovar Pedido','Deseja marcar este pedido como REPROVADO?'):
            return
        try:
            Repo.reject_order(oid)
            messagebox.showinfo('Pedidos', 'Pedido marcado como reprovado.')
            self._load_orders()
        except Exception as e:
            messagebox.showerror('Erro', str(e))
