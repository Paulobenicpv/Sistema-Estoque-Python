
import tkinter as tk
from tkinter import ttk, messagebox
from conexao.repo import Repo
from shared.config import currency_br
from shared.ui import build_sidebar, build_top_links
from shared.dialogs import ItemDialog

class InventarioView:
    def __init__(self, container, on_tab_select):
        self.container = container
        self.on_tab_select = on_tab_select
        self._build(container)

    def _build(self, container):
        root = ttk.PanedWindow(container, orient="horizontal"); root.pack(expand=True, fill="both")
        left = ttk.Frame(root, width=240); right = ttk.Frame(root); root.add(left, weight=0); root.add(right, weight=1)

        m = Repo.metrics()
        sb_cards = [
            (str(m["ok"]+m["low"]), "Itens", "Total cadastrados"),
            (str(m["low"]), "Baixo Estoque", "Abaixo do mínimo"),
            (str(len(m["category_distribution"])), "Categorias", ""),
        ]
        build_sidebar(left, "Visão Geral", sb_cards)
        build_top_links(right, self.on_tab_select, 1)

        parent = ttk.Frame(right, padding=10); parent.pack(expand=True, fill="both")
        header=ttk.Frame(parent); header.pack(fill="x",pady=(0,4))
        ttk.Label(header,text="Inventário",font=("Segoe UI",14,"bold")).pack(side="left")
        ttk.Button(header,text="Atualizar Dados",command=self._refresh_all_kpis).pack(side="right")

        toolbar=ttk.Frame(parent); toolbar.pack(fill="x",pady=6)
        ttk.Button(toolbar,text="Novo Item",command=self._add_item).pack(side="left",padx=4)
        ttk.Button(toolbar,text="Editar",command=self._edit_item).pack(side="left",padx=4)
        ttk.Button(toolbar,text="Excluir",command=self._delete_item).pack(side="left",padx=4)
        self.search_var=tk.StringVar(); ttk.Entry(toolbar,textvariable=self.search_var,width=28).pack(side="right",padx=4); ttk.Label(toolbar,text="Buscar:").pack(side="right")

        cols=("id","Código","Descrição","Categoria","Estoque","Preço"); self.tree=ttk.Treeview(parent,columns=cols,show="headings",height=18)
        for col in cols:
            self.tree.heading(col,text=col); w=80 if col in ("id","Estoque","Preço") else 180; self.tree.column(col,width=w,anchor="w")
        self.tree.column("id",width=60,anchor="w"); self.tree.pack(expand=True,fill="both"); self.tree.bind("<Double-1>",lambda e:self._edit_item())

        nav=ttk.Frame(parent); nav.pack(fill="x",pady=(6,0))
        ttk.Button(nav,text="Filtrar",command=self._apply_filter).pack(side="left")
        ttk.Button(nav,text="Limpar",command=lambda:(self.search_var.set(""),self._apply_filter())).pack(side="left",padx=6)
        ttk.Label(nav,text="Itens por página:").pack(side="left",padx=(12,4)); self.page_size_var=tk.StringVar(value="500")
        ttk.Combobox(nav,textvariable=self.page_size_var,values=["100","250","500","1000"],width=6,state="readonly").pack(side="left")
        ttk.Button(nav,text="⟨ Anterior",command=self._prev_page).pack(side="right")
        ttk.Button(nav,text="Próxima ⟩",command=self._next_page).pack(side="right",padx=(6,0))
        self.page_label=ttk.Label(nav,text="Página 1/1 — 0 itens", style="Muted.TLabel"); self.page_label.pack(side="right",padx=(0,12))

        self._current_page=1; self._total_pages=1; self._total_items=0; self._load_items()

    def _apply_filter(self): self._current_page=1; self._load_items()
    def _get_page_params(self):
        try: ps=int(self.page_size_var.get())
        except Exception: ps=500
        term=self.search_var.get().strip() or None; total=Repo.count_items(term); pages=max(1, (total+ps-1)//ps)
        self._total_pages=pages; self._total_items=total; self._current_page=min(max(1,self._current_page),pages); offset=(self._current_page-1)*ps
        return term, ps, offset
    def _load_items(self):
        term,ps,offset=self._get_page_params()
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in Repo.list_items(term,limit=ps,offset=offset):
            self.tree.insert("", "end", values=(r["id"],r["code"],r["descr"],r["category"],r["stock"],currency_br(r["price"])))
        self.page_label.config(text=f"Página {self._current_page}/{self._total_pages} — {self._total_items} itens")
    def _next_page(self):
        if self._current_page < self._total_pages: self._current_page+=1; self._load_items()
    def _prev_page(self):
        if self._current_page > 1: self._current_page-=1; self._load_items()
    def _get_selected_id(self):
        sel=self.tree.selection(); 
        if not sel: messagebox.showinfo("Inventário","Selecione um item."); return None
        return int(self.tree.item(sel[0],"values")[0])
    def _add_item(self):
        dlg=ItemDialog(self.container,"Novo Item")
        if dlg.result:
            try: 
                Repo.add_item(**dlg.result); self._apply_filter()
            except Exception as e:
                messagebox.showerror("Erro", str(e))
    def _edit_item(self):
        item_id=self._get_selected_id()
        if item_id is None: return
        import sqlite3
        from conexao.db import db_connect
        with db_connect() as conn: row=conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        dlg=ItemDialog(self.container,"Editar Item",initial=row)
        if dlg.result:
            try: 
                Repo.update_item(item_id, **dlg.result); self._load_items()
            except sqlite3.IntegrityError: messagebox.showerror("Erro","Código já existente.")
            except Exception as e: messagebox.showerror("Erro", str(e))
    def _delete_item(self):
        item_id=self._get_selected_id()
        if item_id is None: return
        if messagebox.askyesno("Excluir","Tem certeza que deseja excluir este item?"):
            Repo.delete_item(item_id); self._load_items()
    def _refresh_all_kpis(self):
        return
