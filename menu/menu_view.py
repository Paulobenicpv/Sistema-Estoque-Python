
from tkinter import ttk
from shared.config import load_logo
from shared.ui import build_toggle_btn

class MenuFrame(ttk.Frame):
    def __init__(self, master, open_tabs_callback):
        super().__init__(master,padding=20); self.open_tabs_callback=open_tabs_callback
        header=ttk.Frame(self); header.pack(fill="x")
        self.header_logo=load_logo(56)
        if self.header_logo: ttk.Label(header,image=self.header_logo).pack(side="left",padx=(0,16))
        else: ttk.Label(header,text="Sua Empresa",font=("Segoe UI",18,"bold")).pack(side="left",padx=(0,16))
        ttk.Label(header,text="Menu Principal",font=("Segoe UI",20,"bold")).pack(side="left",pady=8)
        build_toggle_btn(header).pack(side="right", padx=6)
        ttk.Button(header,text="Sair",command=self.master.quit).pack(side="right")
        grid=ttk.Frame(self); grid.pack(expand=True,fill="both",pady=20)
        def add_card(r,c,text,idx):
            frm=ttk.Frame(grid,padding=20,style="Card.TFrame"); frm.grid(row=r,column=c,padx=12,pady=12,sticky="nsew")
            ttk.Label(frm,text=text,font=("Segoe UI",16,"bold")).pack(pady=(0,10))
            ttk.Label(frm,text="Clique para abrir",font=("Segoe UI",10),style="Muted.TLabel").pack(pady=(0,12))
            ttk.Button(frm,text=f"Abrir {text}",command=lambda i=idx:self.open_tabs_callback(i)).pack(fill="x")
            grid.columnconfigure(c,weight=1)
        add_card(0,0,"Dashboard",0); add_card(0,1,"Inventário",1); add_card(1,0,"Pedidos",2); add_card(1,1,"Relatórios",3)
        grid.rowconfigure(0,weight=1); grid.rowconfigure(1,weight=1)
