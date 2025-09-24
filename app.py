
import traceback
import tkinter as tk
from tkinter import ttk
from shared.config import APP_TITLE, apply_theme, load_config, save_config
from conexao.db import db_init
from login.login_view import LoginFrame
from menu.menu_view import MenuFrame
from dashboard.dashboard_view import build as build_dashboard
from inventario.inventario_view import InventarioView
from pedidos.pedidos_view import PedidosView
from relatorios.relatorios_view import build as build_relatorios

def get_initial_theme():
    cfg = load_config()
    return cfg.get("theme", "dark")

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title(APP_TITLE)
        self.geometry("1120x720")
        self.theme_mode = get_initial_theme()
        apply_theme(self, self.theme_mode)
        db_init(12000)
        self.login=LoginFrame(self,on_success=self.show_menu); self.menu=None; self.tabs=None
        self.login.pack(expand=True,fill="both")

    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        apply_theme(self, self.theme_mode)
        save_config({"theme": self.theme_mode})
        self._redraw_view()

    def _redraw_view(self):
        if self.tabs is not None:
            idx = self.notebook.index(self.notebook.select())
            self._build_tabs(); self.focus_tab(idx)
        elif self.menu is not None:
            self.show_menu()
        elif self.login is not None:
            self.show_login()

    def show_login(self):
        if self.tabs is not None: self.tabs.destroy(); self.tabs=None
        if self.menu is not None: self.menu.destroy(); self.menu=None
        if self.login is not None: self.login.destroy(); self.login=None
        self.login=LoginFrame(self,on_success=self.show_menu); self.login.pack(expand=True,fill="both")

    def show_menu(self):
        if self.tabs is not None:
            self.tabs.destroy(); self.tabs=None
        if self.login is not None:
            self.login.destroy(); self.login=None
        if self.menu is not None:
            self.menu.destroy(); self.menu=None
        self.menu=MenuFrame(self,self.open_tabs); self.menu.pack(expand=True,fill="both")

    def open_tabs(self,start_index=0):
        if self.menu is not None:
            self.menu.destroy(); self.menu=None
        self._build_tabs()
        self.focus_tab(start_index)

    def _build_tabs(self):
        if getattr(self, "notebook", None):
            self.notebook.destroy()
        container = ttk.Frame(self, padding=8); container.pack(expand=True, fill="both")
        header=ttk.Frame(container); header.pack(fill="x",pady=(0,6))
        ttk.Button(header,text="← Menu",command=self.show_menu).pack(side="left")
        ttk.Label(header,text="Controle de Estoque",font=("Segoe UI",18,"bold")).pack(side="left",padx=10)
        from shared.ui import build_toggle_btn
        build_toggle_btn(header).pack(side="right")

        self.notebook=ttk.Notebook(container); self.notebook.pack(expand=True,fill="both")
        self.tab_dash=ttk.Frame(self.notebook); self.tab_inv=ttk.Frame(self.notebook)
        self.tab_ped=ttk.Frame(self.notebook); self.tab_rel=ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dash,text="Dashboard"); self.notebook.add(self.tab_inv,text="Inventário")
        self.notebook.add(self.tab_ped,text="Pedidos"); self.notebook.add(self.tab_rel,text="Relatórios")

        build_dashboard(self.tab_dash, self.focus_tab)
        InventarioView(self.tab_inv, self.focus_tab)
        PedidosView(self.tab_ped, self.focus_tab)
        build_relatorios(self.tab_rel, self.focus_tab)

    def focus_tab(self, idx): 
        try:
            self.notebook.select(idx)
        except Exception:
            pass

def safe_main():
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        tb = traceback.format_exc()
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(tb)
        try:
            import tkinter as _tk
            from tkinter import messagebox as _mb
            root=_tk.Tk(); root.withdraw()
            _mb.showerror("Erro ao abrir", f"O programa encontrou um erro e foi encerrado.\n\nDetalhes salvos em error.log.\n\n{e}")
        except Exception:
            pass
        raise

if __name__ == "__main__":
    safe_main()
