
import datetime, tkinter as tk
from tkinter import ttk, messagebox
from conexao.repo import Repo
from shared.config import COLORS, CANVAS_BG, currency_br

class ItemDialog(tk.Toplevel):
    def __init__(self, master, title, initial=None):
        super().__init__(master); self.title(title); self.resizable(False,False); self.transient(master); self.grab_set()
        self.configure(bg=COLORS["bg"]); self.result=None
        frm=ttk.Frame(self,padding=12); frm.pack(fill="both",expand=True)
        for i,t in enumerate(("Código *","Descrição *","Categoria *","Estoque *","Preço *")):
            ttk.Label(frm,text=t).grid(row=i,column=0,sticky="w",padx=(0,8),pady=4)
        import tkinter as tk
        self.v_code=tk.StringVar(value=initial["code"] if initial else "")
        self.v_descr=tk.StringVar(value=initial["descr"] if initial else "")
        self.v_cat=tk.StringVar(value=initial["category"] if initial else "")
        self.v_stock=tk.StringVar(value=str(initial["stock"]) if initial else "0")
        self.v_price=tk.StringVar(value=str(initial["price"]) if initial else "0.00")
        ttk.Entry(frm,textvariable=self.v_code,width=28).grid(row=0,column=1,sticky="ew",pady=4)
        ttk.Entry(frm,textvariable=self.v_descr,width=28).grid(row=1,column=1,sticky="ew",pady=4)
        ttk.Entry(frm,textvariable=self.v_cat,width=28).grid(row=2,column=1,sticky="ew",pady=4)
        ttk.Entry(frm,textvariable=self.v_stock,width=28).grid(row=3,column=1,sticky="ew",pady=4)
        ttk.Entry(frm,textvariable=self.v_price,width=28).grid(row=4,column=1,sticky="ew",pady=4)
        frm.columnconfigure(1,weight=1)
        btns=ttk.Frame(frm); btns.grid(row=5,column=0,columnspan=2,pady=(10,0),sticky="ew")
        ttk.Button(btns,text="Salvar",command=self._on_save).pack(side="left",expand=True,fill="x",padx=(0,6))
        ttk.Button(btns,text="Cancelar",command=self.destroy).pack(side="left",expand=True,fill="x",padx=(6,0))
        self.bind("<Return>",lambda e:self._on_save()); self.bind("<Escape>",lambda e:self.destroy())
        self.wait_visibility(); self.focus()
    def _on_save(self):
        try:
            code=self.v_code.get().strip(); descr=self.v_descr.get().strip(); cat=self.v_cat.get().strip()
            stock=int(self.v_stock.get().strip()); price=float(self.v_price.get().strip().replace(",","."))
            if not code or not descr or not cat: raise ValueError("Preencha os campos obrigatórios.")
        except Exception as e:
            messagebox.showerror("Erro",f"Dados inválidos: {e}"); return
        self.result={"code":code,"descr":descr,"category":cat,"stock":stock,"price":price}; self.destroy()

class OrderDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master); self.title("Novo Pedido"); self.resizable(True, True); self.transient(master); self.grab_set()
        self.configure(bg=COLORS["bg"])
        self.items = []
        root = ttk.Frame(self, padding=10); root.pack(expand=True, fill="both")
        top = ttk.Frame(root); top.pack(fill="x")
        ttk.Label(top, text="Cliente:").pack(side="left")
        import tkinter as tk
        self.v_customer = tk.StringVar(); ttk.Entry(top, textvariable=self.v_customer, width=30).pack(side="left", padx=6)
        ttk.Label(top, text="Status:").pack(side="left", padx=(12,0))
        self.v_status = tk.StringVar(value="Concluído")
        ttk.Combobox(top, textvariable=self.v_status, values=["Concluído","Aberto","Cancelado"], state="readonly", width=12).pack(side="left", padx=6)
        ttk.Label(top, text="Data:").pack(side="left", padx=(12,0))
        self.v_date = tk.StringVar(value=datetime.date.today().isoformat()); ttk.Entry(top, textvariable=self.v_date, width=12).pack(side="left", padx=6)

        body = ttk.PanedWindow(root, orient="horizontal"); body.pack(expand=True, fill="both", pady=8)
        left = ttk.Frame(body, padding=(0,0,8,0)); right = ttk.Frame(body)
        body.add(left, weight=1); body.add(right, weight=1)

        sbar = ttk.Frame(left); sbar.pack(fill="x", pady=(0,6))
        ttk.Label(sbar, text="Buscar item:").pack(side="left")
        self.search_var = tk.StringVar(); ent = ttk.Entry(sbar, textvariable=self.search_var, width=28); ent.pack(side="left", padx=6)
        ttk.Button(sbar, text="Filtrar", command=self._reload_catalog).pack(side="left")

        self.cat = ttk.Treeview(left, columns=("id","Código","Descrição","Categoria","Estoque","Preço"), show="headings", height=12)
        for col, w in (("id",60),("Código",120),("Descrição",220),("Categoria",120),("Estoque",80),("Preço",80)):
            self.cat.heading(col, text=col); self.cat.column(col, width=w, anchor="w")
        self.cat.pack(expand=True, fill="both"); self.cat.bind("<Double-1>", lambda e: self._add_selected())

        qtybar = ttk.Frame(left); qtybar.pack(fill="x", pady=6)
        ttk.Label(qtybar, text="Qtd:").pack(side="left")
        self.v_qty = tk.StringVar(value="1"); ttk.Entry(qtybar, textvariable=self.v_qty, width=6).pack(side="left", padx=6)
        ttk.Button(qtybar, text="Adicionar ➜", command=self._add_selected).pack(side="left")

        self.ord = ttk.Treeview(right, columns=("Código","Descrição","Qtd","Preço","Total"), show="headings", height=12)
        for col, w in (("Código",120),("Descrição",220),("Qtd",60),("Preço",80),("Total",80)):
            self.ord.heading(col, text=col); self.ord.column(col, width=w, anchor="w")
        self.ord.pack(expand=True, fill="both")
        rbar = ttk.Frame(right); rbar.pack(fill="x", pady=6)
        ttk.Button(rbar, text="Remover", command=self._remove_selected).pack(side="left")
        self.total_lbl = ttk.Label(rbar, text="Total: R$ 0,00", font=("Segoe UI", 11, "bold")); self.total_lbl.pack(side="right")

        fbtn = ttk.Frame(root); fbtn.pack(fill="x", pady=(8,0))
        ttk.Button(fbtn, text="Salvar", command=self._save).pack(side="right")
        ttk.Button(fbtn, text="Cancelar", command=self.destroy).pack(side="right", padx=6)

        self._reload_catalog(); ent.focus_set()

    def _reload_catalog(self):
        term = self.search_var.get().strip() or None
        for i in self.cat.get_children(): self.cat.delete(i)
        for r in Repo.list_items(term, limit=200, offset=0):
            self.cat.insert("", "end", values=(r["id"], r["code"], r["descr"], r["category"], r["stock"], f"{r['price']:.2f}"))

    def _add_selected(self):
        sel = self.cat.selection()
        if not sel: return
        try:
            qty = int(self.v_qty.get())
        except:
            messagebox.showerror("Erro","Quantidade inválida."); return
        if qty <= 0:
            messagebox.showerror("Erro","Quantidade deve ser positiva."); return
        vals = self.cat.item(sel[0], "values")
        item_id, code, descr, cat, stock, price = int(vals[0]), vals[1], vals[2], vals[3], int(vals[4]), float(vals[5].replace(",","."))
        for it in self.items:
            if it["item_id"] == item_id:
                it["qty"] += qty; self._refresh_order_list(); return
        self.items.append({"item_id": item_id, "code": code, "descr": descr, "price": price, "qty": qty})
        self._refresh_order_list()

    def _refresh_order_list(self):
        for i in self.ord.get_children(): self.ord.delete(i)
        total = 0.0
        for it in self.items:
            line = it["qty"] * it["price"]; total += line
            self.ord.insert("", "end", values=(it["code"], it["descr"], it["qty"], f"{it['price']:.2f}", f"{line:.2f}"))
        self.total_lbl.config(text=f"Total: {currency_br(total)}")

    def _remove_selected(self):
        sel = self.ord.selection()
        if not sel: return
        code = self.ord.item(sel[0], "values")[0]
        self.items = [i for i in self.items if i["code"] != code]
        self._refresh_order_list()

    def _save(self):
        import datetime
        from tkinter import messagebox
        customer = self.v_customer.get().strip() or "Cliente"
        status = self.v_status.get()
        date_str = self.v_date.get().strip() or datetime.date.today().isoformat()
        try:
            items = [{"item_id": it["item_id"], "code": it["code"], "descr": it["descr"], "qty": int(it["qty"]), "price": float(it["price"])} for it in self.items]
            order_id = Repo.create_order(customer, status, items, date=date_str)
            messagebox.showinfo("Pedido", f"Pedido #{order_id} salvo com sucesso!")
            self.result = order_id
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao salvar", str(e))
