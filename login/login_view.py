
import tkinter as tk
from tkinter import ttk
from shared.config import VALID_USER, VALID_PASS, COLORS, load_logo
from shared.ui import build_toggle_btn

class LoginFrame(ttk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master,padding=20); self.on_success=on_success
        card=ttk.Frame(self,padding=20, style="Card.TFrame"); card.pack(expand=True)
        topbar = ttk.Frame(card); topbar.pack(fill="x")
        build_toggle_btn(topbar).pack(side="right")
        self.logo_img=load_logo(96)
        if self.logo_img: ttk.Label(card,image=self.logo_img).pack(pady=(0,10))
        else: ttk.Label(card,text="Sua Empresa",font=("Segoe UI",18,"bold")).pack(pady=(0,10))
        ttk.Label(card,text="Login",font=("Segoe UI",16,"bold")).pack(pady=(0,10))
        form=ttk.Frame(card); form.pack(pady=10,fill="x")
        ttk.Label(form,text="Usuário").grid(row=0,column=0,sticky="w",padx=(0,8),pady=6)
        ttk.Label(form,text="Senha").grid(row=1,column=0,sticky="w",padx=(0,8),pady=6)
        self.user_var=tk.StringVar(); self.pass_var=tk.StringVar()
        ue=ttk.Entry(form,textvariable=self.user_var,width=28); pe=ttk.Entry(form,textvariable=self.pass_var,width=28,show="•")
        ue.grid(row=0,column=1,pady=6,sticky="ew"); pe.grid(row=1,column=1,pady=6,sticky="ew"); form.columnconfigure(1,weight=1)
        btns=ttk.Frame(card); btns.pack(pady=(10,0),fill="x")
        self.msg=ttk.Label(card,text="",foreground="#fca5a5"); self.msg.pack(pady=(6,0))
        ttk.Button(btns,text="Entrar",command=self.try_login).pack(side="left",expand=True,fill="x",padx=(0,6))
        ttk.Button(btns,text="Sair",command=self.master.quit).pack(side="left",expand=True,fill="x",padx=(6,0))
        ue.focus_set()
    def try_login(self):
        if self.user_var.get().strip()==VALID_USER and self.pass_var.get().strip()==VALID_PASS: self.on_success()
        else: self.msg.configure(text="Usuário ou senha inválidos.")
