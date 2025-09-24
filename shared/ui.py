
import tkinter as tk
from tkinter import ttk
from .config import COLORS, CANVAS_BG, THEMES

class Card(ttk.Frame):
    def __init__(self, parent, title, **grid):
        super().__init__(parent, padding=12, style="Card.TFrame")
        if grid: self.grid(**grid)
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text=title, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0,6))

def draw_line_chart(canvas, data, padding=20):
    c = COLORS
    canvas.delete("all"); w=int(canvas["width"]); h=int(canvas["height"])
    canvas.configure(bg=CANVAS_BG, highlightthickness=0)
    for i in range(5):
        y=padding+i*(h-2*padding)/4
        canvas.create_line(padding,y,w-padding,y,fill=c["grid"])
    if not data: return
    m=max(data) or 1
    total = sum(data) or 1
    step=(w-2*padding)/max(1,len(data)-1); pts=[]
    for i,yv in enumerate(data):
        x=padding+step*i; y=h-padding-(yv/m)*(h-2*padding); pts.append((x,y))
    for i in range(1,len(pts)):
        canvas.create_line(pts[i-1][0],pts[i-1][1],pts[i][0],pts[i][1],width=2,fill=c["accent2"])
    for i,(x,y) in enumerate(pts):
        val = data[i]; pct = int(round((val/total)*100))
        canvas.create_oval(x-3,y-3,x+3,y+3,fill=c["accent2"],outline="")
        canvas.create_text(x, y-12, text=f"{val} ({pct}%)", font=("Segoe UI", 9, "bold"), fill=COLORS["fg"])

def draw_bar_chart(canvas, labels, values, padding=24):
    c = COLORS
    canvas.delete("all"); w=int(canvas["width"]); h=int(canvas["height"])
    canvas.configure(bg=CANVAS_BG, highlightthickness=0)
    if not values: return
    total = sum(values) or 1
    M=max(values); n=len(values); bar=(w-2*padding)/(n*1.6); gap=bar*0.6; x=padding
    for i,v in enumerate(values):
        bh=(v/M)*(h-2*padding)
        canvas.create_rectangle(x,h-padding-bh,x+bar,h-padding,fill=c["accent"],width=0)
        pct = int(round((v/total)*100))
        canvas.create_text(x+bar/2,h-padding-bh-10,text=f"{v} ({pct}%)",font=("Segoe UI",9,"bold"),fill=COLORS["fg"])
        canvas.create_text(x+bar/2,h-padding+12,text=str(labels[i]),font=("Segoe UI",9),fill=COLORS["fg"])
        x+=bar+gap

def draw_progress_bar(canvas, value, total, color=None):
    color = color or COLORS["good"]
    canvas.delete("all"); w=int(canvas["width"]); h=int(canvas["height"])
    canvas.configure(bg=CANVAS_BG, highlightthickness=0)
    pct=0 if total==0 else value/total
    canvas.create_rectangle(4,4,w-4,h-4, fill=COLORS["grid"], width=0)
    fw=4+pct*(w-8)
    canvas.create_rectangle(4,4,fw,h-4, fill=color, width=0)
    txt = f"{value} / {total} ({int(round(pct*100))}%)"
    canvas.create_text(w/2, h/2, text=txt, font=("Segoe UI", 9, "bold"), fill=COLORS["fg"])

def draw_donut(canvas, data):
    c = COLORS
    canvas.delete("all"); w=int(canvas["width"]); h=int(canvas["height"]); canvas.configure(bg=CANVAS_BG, highlightthickness=0)
    cx,cy=w//2,h//2; r=min(w,h)//2-4; r_in=int(r*0.6); tot=sum(data.values()) or 1; start=0
    pal=["#60A5FA","#10B981","#F59E0B","#EF4444","#8B5CF6","#06B6D4"]; labels=list(data.keys())
    for i,k in enumerate(labels):
        frac=(data[k]/tot); ext=frac*360; col=pal[i%len(pal)]
        canvas.create_arc(cx-r,cy-r,cx+r,cy+r,start=start,extent=ext,fill=col,outline=COLORS["bg"],width=1); start+=ext
    canvas.create_oval(cx-r_in,cy-r_in,cx+r_in,cy+r_in,fill=CANVAS_BG,outline=CANVAS_BG)
    lx=w-140; ly=10
    for i,k in enumerate(labels[:6]):
        col=pal[i%len(pal)]; val=data[k]; pct=int(round((val/tot)*100))
        canvas.create_rectangle(lx,ly+2,lx+12,ly+14,fill=col,outline="")
        canvas.create_text(lx+18,ly+8,text=f"{k} · {val} ({pct}%)",anchor="w",font=("Segoe UI",9), fill=COLORS["fg"])
        ly+=18
    canvas.create_text(cx, cy, text=f"Total: {tot}", font=("Segoe UI", 11, "bold"), fill=COLORS["fg"])

def build_sidebar(parent, title, cards):
    sb = ttk.Frame(parent, padding=10, style="Card.TFrame")
    ttk.Label(sb, text=title, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0,6))
    for value, label, sub in cards:
        box = ttk.Frame(sb, padding=10)
        big = ttk.Label(box, text=value, font=("Segoe UI", 22, "bold"))
        big.pack(anchor="w")
        ttk.Label(box, text=label, font=("Segoe UI", 10), style="Muted.TLabel").pack(anchor="w")
        if sub:
            ttk.Label(box, text=sub, font=("Segoe UI", 9), style="Muted.TLabel").pack(anchor="w")
        box.pack(fill="x", pady=6)
        sep = ttk.Separator(sb, orient="horizontal"); sep.pack(fill="x", pady=(4,4))
    return sb

def build_top_links(parent, on_select, active_idx):
    nav = ttk.Frame(parent)
    labels = ["Dashboard","Inventário","Pedidos","Relatórios"]
    for i,txt in enumerate(labels):
        style = {"font":("Segoe UI", 11, "bold")} if i==active_idx else {"font":("Segoe UI", 11)}
        lbl = ttk.Label(nav, text=txt, **style, cursor="hand2")
        lbl.pack(side="left", padx=(0,14), pady=8)
        lbl.bind("<Button-1>", lambda e, idx=i: on_select(idx))
    nav.pack(fill="x")
    sep = ttk.Separator(parent, orient="horizontal"); sep.pack(fill="x")
    return nav

def build_toggle_btn(parent):
    try:
        app = parent.winfo_toplevel()
        label = "☀️ Claro" if getattr(app, "theme_mode", "dark") == "dark" else "🌙 Escuro"
        return ttk.Button(parent, text=label, command=getattr(app, "toggle_theme"))
    except Exception:
        return ttk.Button(parent, text="Tema", command=lambda: None)
