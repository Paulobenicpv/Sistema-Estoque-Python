
import json, math, tkinter as tk
from pathlib import Path
from tkinter import ttk

APP_TITLE = "Sistema de Estoque — Local (Tkinter)"
VALID_USER = "paulobeni"
VALID_PASS = "475896"

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"
DB_PATH = BASE_DIR / "estoque.db"
EXPORT_DIR = BASE_DIR / "exports"
CONFIG_PATH = BASE_DIR / "config.json"

THEMES = {
    "dark": {
        "bg": "#0b1220", "surface": "#111827", "card": "#1f2937", "muted": "#9ca3af",
        "fg": "#e5e7eb", "accent": "#60a5fa", "accent2": "#3b82f6", "good": "#22c55e",
        "warn": "#f59e0b", "border": "#374151", "grid": "#2a3240", "canvas": "#1f2937",
    },
    "light": {
        "bg": "#f5f7fb", "surface": "#ffffff", "card": "#ffffff", "muted": "#6b7280",
        "fg": "#111827", "accent": "#2563eb", "accent2": "#3b82f6", "good": "#16a34a",
        "warn": "#f59e0b", "border": "#e5e7eb", "grid": "#e5e7eb", "canvas": "#ffffff",
    },
}
COLORS = THEMES["dark"]
CANVAS_BG = COLORS["canvas"]

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(cfg: dict):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("WARN: não foi possível salvar config:", e)

def apply_theme(root, mode="dark"):
    global COLORS, CANVAS_BG
    COLORS = THEMES.get(mode, THEMES["dark"])
    CANVAS_BG = COLORS["canvas"]
    c = COLORS

    root.configure(bg=c["bg"])
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(".", background=c["bg"], foreground=c["fg"])
    style.configure("TFrame", background=c["bg"])
    style.configure("TLabel", background=c["bg"], foreground=c["fg"])
    style.configure("Muted.TLabel", background=c["bg"], foreground=c["muted"])

    style.configure("Card.TFrame", background=c["card"], relief="groove", borderwidth=1)
    style.configure("TSeparator", background=c["border"])

    style.configure("TButton", padding=6, background=c["surface"], foreground=c["fg"], bordercolor=c["border"])
    style.map("TButton", background=[("active", c["border"])])

    style.configure("TNotebook", background=c["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=c["surface"], foreground=c["fg"], padding=(12,6))
    style.map("TNotebook.Tab", background=[("selected", c["card"])], foreground=[("selected", c["fg"])])

    style.configure("TEntry", fieldbackground=c["surface"], foreground=c["fg"])
    style.configure("TCombobox", fieldbackground=c["surface"], background=c["surface"], foreground=c["fg"])

    style.configure("Treeview",
                    background=c["surface"],
                    fieldbackground=c["surface"],
                    foreground=c["fg"],
                    bordercolor=c["border"])
    style.configure("Treeview.Heading", background=c["card"], foreground=c["fg"], bordercolor=c["border"])

def load_logo(max_h=56):
    try:
        img = tk.PhotoImage(file=str(LOGO_PATH))
        h = img.height()
        if h > max_h:
            factor = max(1, math.ceil(h / max_h))
            img = img.subsample(factor, factor)
        return img
    except Exception:
        return None

def currency_br(v):
    s = f"{v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
    return f"R$ {s}"
