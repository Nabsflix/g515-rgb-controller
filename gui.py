"""
Interface graphique - Razer Chroma / Logitech G515 Bridge
Clavier AZERTY visuel cliquable
"""

import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
import json
import threading
import subprocess
import time
import sys
import os
import winreg
from pathlib import Path

import pystray
from PIL import Image, ImageDraw

from bridge import LogitechLED, ChromaBridge, LOGITECH_KEY_MAP, load_preset, save_preset

AUTOSTART_NAME = "G515 RGB Controller"
AUTOSTART_CMD  = f'"{sys.executable}" "{Path(__file__).resolve()}"'

# ── Layout clavier AZERTY G515 TKL ───────────────────────────────────────────

ROW0 = [
    ("ESC", "ESC", 1), ("GAP", None, 0.5),
    ("F1", "F1", 1), ("F2", "F2", 1), ("F3", "F3", 1), ("F4", "F4", 1),
    ("GAP", None, 0.5),
    ("F5", "F5", 1), ("F6", "F6", 1), ("F7", "F7", 1), ("F8", "F8", 1),
    ("GAP", None, 0.5),
    ("F9", "F9", 1), ("F10", "F10", 1), ("F11", "F11", 1), ("F12", "F12", 1),
    ("GAP", None, 0.5),
    ("Impr", "PRINT_SCREEN", 1), ("Arrêt\nDéf", "SCROLL_LOCK", 1), ("Pause", "PAUSE_BREAK", 1),
]

ROW1 = [
    ("²~", "TWO_TILDE", 1), ("&\n1", "AMPERSAND", 1), ("é\n2", "EACUTE", 1),
    ("\"\n3", "QUOTE", 1), ("'\n4", "APOSTROPHE", 1), ("(\n5", "LPAREN", 1),
    ("-\n6", "MINUS", 1), ("è\n7", "EGRAVE", 1), ("_\n8", "UNDERSCORE", 1),
    ("ç\n9", "CCEDILLA", 1), ("à\n0", "AGRAVE", 1), (")\n°", "RPAREN", 1),
    ("=\n+", "EQUALS", 1), ("⌫", "BACKSPACE", 2),
    ("GAP", None, 0.5),
    ("Inser", "INSERT", 1), ("Début", "HOME", 1), ("PgUp", "PAGE_UP", 1),
]

ROW2 = [
    ("Tab", "TAB", 1.5), ("A", "A", 1), ("Z", "Z", 1), ("E", "E", 1),
    ("R", "R", 1), ("T", "T", 1), ("Y", "Y", 1), ("U", "U", 1),
    ("I", "I", 1), ("O", "O", 1), ("P", "P", 1), ("^\n¨", "OPEN_BRACKET", 1),
    ("$\n£", "CLOSE_BRACKET", 1), ("Entrée", "ENTER", 1.5),
    ("GAP", None, 0.5),
    ("Suppr", "KEYBOARD_DELETE", 1), ("Fin", "END", 1), ("PgDn", "PAGE_DOWN", 1),
]

ROW3 = [
    ("Verr\nMaj", "CAPS_LOCK", 1.75), ("Q", "Q", 1), ("S", "S", 1),
    ("D", "D", 1), ("F", "F", 1), ("G", "G", 1), ("H", "H", 1),
    ("J", "J", 1), ("K", "K", 1), ("L", "L", 1), ("M", "M", 1),
    ("ù\n%", "UGRAVE", 1), ("*\nµ", "BACKSLASH", 1), ("⏎", "ENTER", 1.25),
]

ROW4 = [
    ("⇧", "LEFT_SHIFT", 1.25), ("!", "EXCLAMATION", 1), ("W", "W", 1),
    ("X", "X", 1), ("C", "C", 1), ("V", "V", 1), ("B", "B", 1),
    ("N", "N", 1), (",\n?", "COMMA", 1), (";\n.", "SEMICOLON", 1),
    (":\n/", "COLON", 1), ("!\n§", "EXCLAMATION", 1), ("⇧", "RIGHT_SHIFT", 2.75),
    ("GAP", None, 0.5), ("GAP", None, 1),
    ("↑", "ARROW_UP", 1),
]

ROW5 = [
    ("Ctrl", "LEFT_CONTROL", 1.25), ("⊞", "LEFT_WINDOWS", 1.25),
    ("Alt", "LEFT_ALT", 1.25), ("Espace", "SPACE", 6.25),
    ("AltGr", "RIGHT_ALT", 1.25), ("Fn", None, 1.25),
    ("≡", "APPLICATION_SELECT", 1.25), ("Ctrl", "RIGHT_CONTROL", 1.25),
    ("GAP", None, 0.5),
    ("←", "ARROW_LEFT", 1), ("↓", "ARROW_DOWN", 1), ("→", "ARROW_RIGHT", 1),
]

ROWS = [ROW0, ROW1, ROW2, ROW3, ROW4, ROW5]

KEY_SIZE   = 44
KEY_MARGIN = 3
FONT_KEY   = ("Segoe UI", 7, "bold")
FONT_LABEL = ("Segoe UI", 9)
BG_COLOR   = "#1a1a1a"
ACCENT     = "#7c3aed"


def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def luminance(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b


def scale_color(r, g, b, brightness: float):
    """Applique la luminosité (0.0 – 1.0) à une couleur."""
    return (int(r * brightness), int(g * brightness), int(b * brightness))


LGHUB_DB = Path(os.environ.get("LOCALAPPDATA", "")) / "LGHUB" / "settings.db"

def get_battery_percent() -> str:
    """Lit le niveau de batterie du G515 depuis la base LGHUB."""
    try:
        import sqlite3
        con = sqlite3.connect(f"file:{LGHUB_DB}?mode=ro", uri=True)
        cur = con.cursor()
        cur.execute("SELECT file FROM data ORDER BY _id DESC LIMIT 1")
        row = cur.fetchone()
        con.close()
        if row:
            data = json.loads(row[0])
            # Cherche /battery/<model>/percentage
            for k, v in data.items():
                if "battery" in k and "percentage" in k and "warning" not in k:
                    pct = v.get("percentage") if isinstance(v, dict) else v
                    if pct is not None:
                        return f"{int(pct)}%"
    except Exception:
        pass
    return "N/A"


# ── Widget touche ─────────────────────────────────────────────────────────────

class KeyButton(tk.Canvas):
    def __init__(self, parent, label, key_name, width_u, app, **kwargs):
        w = int(width_u * KEY_SIZE)
        super().__init__(parent, width=w, height=KEY_SIZE,
                         bg=BG_COLOR, highlightthickness=0, **kwargs)
        self.label    = label
        self.key_name = key_name
        self.app      = app
        self.color    = (45, 45, 45)
        self.width_u  = width_u
        self._draw()
        if key_name:
            self.bind("<Button-1>", self._on_click)
            self.bind("<Button-3>", self._on_right_click)
            self.bind("<Enter>",    self._on_enter)
            self.bind("<Leave>",    self._on_leave)

    def _draw(self, hover=False):
        self.delete("all")
        r, g, b = self.color
        fill   = rgb_to_hex(r, g, b)
        border = "#666666" if hover else "#3a3a3a"
        w = int(self.width_u * KEY_SIZE)
        m = KEY_MARGIN
        self.create_rectangle(m, m, w - m, KEY_SIZE - m,
                               fill=fill, outline=border, width=1)
        fg = "#000000" if luminance(r, g, b) > 128 else "#ffffff"
        self.create_text(w // 2, KEY_SIZE // 2,
                         text=self.label, fill=fg,
                         font=FONT_KEY, justify="center")

    def set_color(self, r, g, b):
        self.color = (r, g, b)
        self._draw()

    def _on_click(self, _):
        if self.key_name:
            self.app.pick_color_for_key(self.key_name, self)

    def _on_right_click(self, _):
        """Clic droit : réinitialise la touche à la couleur de fond."""
        if self.key_name:
            self.app.reset_key(self.key_name, self)

    def _on_enter(self, _): self._draw(hover=True)
    def _on_leave(self, _): self._draw(hover=False)


# ── Application principale ────────────────────────────────────────────────────

class BridgeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("G515 RGB — Logitech × Chroma")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self.logi        = LogitechLED()
        self.bridge      = ChromaBridge()
        self.bridge.logi = self.logi
        self.key_buttons = {}
        self.key_colors  = {}
        self.base_color  = (0, 0, 0)
        self.brightness  = 1.0          # 0.0 – 1.0
        self._undo_stack = []           # historique pour annuler

        self._init_sdk()
        self._build_ui()
        self._load_last_preset()
        self._start_battery_poll()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── SDK ───────────────────────────────────────────────────────────────────

    def _init_sdk(self):
        if not self.logi.init():
            messagebox.showerror("Erreur",
                "Impossible d'initialiser le SDK Logitech.\n"
                "Assurez-vous que LGHUB est lancé.")
            sys.exit(1)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Barre supérieure : titre + batterie ──
        top = tk.Frame(self, bg=BG_COLOR)
        top.pack(fill="x", padx=16, pady=(12, 2))

        tk.Label(top, text="G515 RGB CONTROLLER",
                 bg=BG_COLOR, fg=ACCENT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")

        batt_frame = tk.Frame(top, bg=BG_COLOR)
        batt_frame.pack(side="right")
        tk.Label(batt_frame, text="🔋", bg=BG_COLOR, fg="#aaaaaa",
                 font=("Segoe UI", 11)).pack(side="left")
        self.battery_var = tk.StringVar(value="…")
        tk.Label(batt_frame, textvariable=self.battery_var,
                 bg=BG_COLOR, fg="#aaaaaa",
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(2, 0))

        # ── Clavier ──
        kb_frame = tk.Frame(self, bg=BG_COLOR)
        kb_frame.pack(padx=16, pady=4)

        for row_keys in ROWS:
            row_frame = tk.Frame(kb_frame, bg=BG_COLOR)
            row_frame.pack(anchor="w", pady=1)
            seen = set()
            for label, key_name, width in row_keys:
                if label == "GAP":
                    tk.Frame(row_frame, width=int(width * KEY_SIZE),
                             height=KEY_SIZE, bg=BG_COLOR).pack(side="left")
                    continue
                btn = KeyButton(row_frame, label, key_name, width, self)
                btn.pack(side="left", padx=0)
                if key_name and key_name not in seen:
                    self.key_buttons[key_name] = btn
                    seen.add(key_name)

        # ── Slider luminosité ──
        lum_frame = tk.Frame(self, bg=BG_COLOR)
        lum_frame.pack(fill="x", padx=20, pady=(6, 2))
        tk.Label(lum_frame, text="☀  Luminosité", bg=BG_COLOR, fg="#aaaaaa",
                 font=FONT_LABEL).pack(side="left")
        self.brightness_var = tk.IntVar(value=100)
        slider = tk.Scale(lum_frame, from_=5, to=100,
                          orient="horizontal", variable=self.brightness_var,
                          bg=BG_COLOR, fg="#ffffff", troughcolor="#333333",
                          highlightthickness=0, length=300,
                          command=self._on_brightness_change)
        slider.pack(side="left", padx=10)
        self.brightness_label = tk.Label(lum_frame, text="100%",
                                          bg=BG_COLOR, fg="#ffffff",
                                          font=FONT_LABEL, width=4)
        self.brightness_label.pack(side="left")

        # ── Palette de couleurs favorites ──
        fav_frame = tk.Frame(self, bg=BG_COLOR)
        fav_frame.pack(fill="x", padx=20, pady=(4, 2))
        tk.Label(fav_frame, text="Favoris", bg=BG_COLOR, fg="#aaaaaa",
                 font=FONT_LABEL).pack(side="left", padx=(0, 8))
        self.fav_colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 165, 0), (255, 0, 255), (0, 255, 255),
            (255, 255, 255), (128, 0, 255),
        ]
        self.fav_canvases = []
        for i, (r, g, b) in enumerate(self.fav_colors):
            c = tk.Canvas(fav_frame, width=24, height=24,
                          bg=BG_COLOR, highlightthickness=0, cursor="hand2")
            c.create_rectangle(2, 2, 22, 22, fill=rgb_to_hex(r, g, b), outline="#555")
            c.pack(side="left", padx=2)
            c.bind("<Button-1>", lambda e, idx=i: self._fav_click(idx))
            c.bind("<Button-3>", lambda e, idx=i: self._fav_save(idx))
            self.fav_canvases.append(c)
        tk.Label(fav_frame, text="(clic gauche = appliquer au fond | clic droit = sauvegarder couleur)",
                 bg=BG_COLOR, fg="#555555", font=("Segoe UI", 7)).pack(side="left", padx=6)

        # ── Panneau de contrôle ──
        ctrl = tk.Frame(self, bg="#222222", pady=10)
        ctrl.pack(fill="x", padx=16, pady=(6, 4))

        # Couleur de fond
        left = tk.Frame(ctrl, bg="#222222")
        left.pack(side="left", padx=12)
        tk.Label(left, text="Fond clavier", bg="#222222", fg="#aaaaaa",
                 font=FONT_LABEL).pack(anchor="w")
        self.base_btn = tk.Button(left, text="  Choisir  ", bg="#2d2d2d",
                                   fg="white", relief="flat", cursor="hand2",
                                   font=FONT_LABEL, command=self._pick_base_color)
        self.base_btn.pack(pady=3)

        # Preset
        mid = tk.Frame(ctrl, bg="#222222")
        mid.pack(side="left", padx=12)
        tk.Label(mid, text="Presets", bg="#222222", fg="#aaaaaa",
                 font=FONT_LABEL).pack(anchor="w")
        btn_row = tk.Frame(mid, bg="#222222")
        btn_row.pack()
        self._btn(btn_row, "💾 Sauvegarder", self._save_preset).pack(side="left", padx=2)
        self._btn(btn_row, "📂 Charger",     self._load_preset).pack(side="left", padx=2)

        # Effets
        eff = tk.Frame(ctrl, bg="#222222")
        eff.pack(side="left", padx=12)
        tk.Label(eff, text="Effets", bg="#222222", fg="#aaaaaa",
                 font=FONT_LABEL).pack(anchor="w")
        eff_row = tk.Frame(eff, bg="#222222")
        eff_row.pack()
        self._btn(eff_row, "🌊 Vague →",   lambda: self._apply_wave(1)).pack(side="left", padx=2)
        self._btn(eff_row, "🫧 Breathing", self._pick_breathing).pack(side="left", padx=2)
        self._btn(eff_row, "↩ Annuler",    self._undo).pack(side="left", padx=2)
        self._btn(eff_row, "⬛ Éteindre",  self._clear).pack(side="left", padx=2)

        # Status
        self.status_var = tk.StringVar(value="Prêt  •  Clic gauche = couleur  •  Clic droit = réinitialiser touche")
        tk.Label(self, textvariable=self.status_var,
                 bg=BG_COLOR, fg="#555555",
                 font=("Segoe UI", 8)).pack(pady=(2, 8))

    def _btn(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd,
                         bg="#3a3a3a", fg="white", relief="flat",
                         font=("Segoe UI", 8), cursor="hand2", padx=8, pady=4,
                         activebackground="#555555", activeforeground="white")

    # ── Luminosité ────────────────────────────────────────────────────────────

    def _on_brightness_change(self, val):
        self.brightness = int(val) / 100
        self.brightness_label.config(text=f"{val}%")
        self._apply_current()

    def _apply_brightness(self, r, g, b):
        return scale_color(r, g, b, self.brightness)

    # ── Batterie ──────────────────────────────────────────────────────────────

    def _start_battery_poll(self):
        def poll():
            while True:
                pct = get_battery_percent()
                self.battery_var.set(pct)
                time.sleep(60)
        t = threading.Thread(target=poll, daemon=True)
        t.start()
        # Premier appel immédiat
        threading.Thread(target=lambda: self.battery_var.set(get_battery_percent()),
                         daemon=True).start()

    # ── Actions ───────────────────────────────────────────────────────────────

    def pick_color_for_key(self, key_name, btn_widget):
        current = self.key_colors.get(key_name, (255, 255, 255))
        result = colorchooser.askcolor(color=rgb_to_hex(*current),
                                       title=f"Couleur — {key_name}")
        if result[0] is None:
            return
        r, g, b = (int(x) for x in result[0])
        self._push_undo()
        self.key_colors[key_name] = (r, g, b)
        btn_widget.set_color(r, g, b)
        self._apply_current()
        self._set_status(f"Touche {key_name} → #{r:02X}{g:02X}{b:02X}")

    def reset_key(self, key_name, btn_widget):
        """Clic droit : supprime la couleur personnalisée de la touche."""
        if key_name in self.key_colors:
            self._push_undo()
            del self.key_colors[key_name]
            btn_widget.set_color(45, 45, 45)
            self._apply_current()
            self._set_status(f"Touche {key_name} réinitialisée")

    def _pick_base_color(self):
        result = colorchooser.askcolor(color=rgb_to_hex(*self.base_color),
                                       title="Couleur de fond")
        if result[0] is None:
            return
        r, g, b = (int(x) for x in result[0])
        self._push_undo()
        self.base_color = (r, g, b)
        self.base_btn.configure(
            bg=rgb_to_hex(r, g, b),
            fg="#000" if luminance(r, g, b) > 128 else "#fff"
        )
        self._apply_current()
        self._set_status(f"Fond → #{r:02X}{g:02X}{b:02X}")

    def _fav_click(self, idx):
        """Clic gauche sur favori : applique comme couleur de fond."""
        r, g, b = self.fav_colors[idx]
        self._push_undo()
        self.base_color = (r, g, b)
        self.base_btn.configure(
            bg=rgb_to_hex(r, g, b),
            fg="#000" if luminance(r, g, b) > 128 else "#fff"
        )
        self._apply_current()
        self._set_status(f"Fond favori → #{r:02X}{g:02X}{b:02X}")

    def _fav_save(self, idx):
        """Clic droit sur favori : sauvegarde la couleur de fond actuelle."""
        self.fav_colors[idx] = self.base_color
        r, g, b = self.base_color
        c = self.fav_canvases[idx]
        c.delete("all")
        c.create_rectangle(2, 2, 22, 22, fill=rgb_to_hex(r, g, b), outline="#555")
        self._set_status(f"Favori {idx+1} sauvegardé")

    def _apply_current(self):
        br, bg_, bb = self._apply_brightness(*self.base_color)
        self.bridge._base_color = (br, bg_, bb)
        self.bridge.apply_static(br, bg_, bb)
        if self.key_colors:
            bright_colors = {k: self._apply_brightness(*v) for k, v in self.key_colors.items()}
            self.bridge.apply_custom(bright_colors)

    def _apply_wave(self, direction):
        self.bridge.apply_wave(direction)
        self._set_status("Effet vague actif")

    def _pick_breathing(self):
        result = colorchooser.askcolor(title="Couleur breathing")
        if result[0] is None:
            return
        r, g, b = (int(x) for x in result[0])
        self.bridge.apply_breathing(r, g, b)
        self._set_status(f"Breathing #{r:02X}{g:02X}{b:02X}")

    def _clear(self):
        self._push_undo()
        self.key_colors = {}
        self.base_color = (0, 0, 0)
        self.logi.set_all(0, 0, 0)
        for btn in self.key_buttons.values():
            btn.set_color(45, 45, 45)
        self.base_btn.configure(bg="#2d2d2d", fg="white")
        self._set_status("Clavier éteint")

    # ── Undo ──────────────────────────────────────────────────────────────────

    def _push_undo(self):
        self._undo_stack.append((dict(self.key_colors), self.base_color))
        if len(self._undo_stack) > 20:
            self._undo_stack.pop(0)

    def _undo(self):
        if not self._undo_stack:
            self._set_status("Rien à annuler")
            return
        self.key_colors, self.base_color = self._undo_stack.pop()
        for key_name, btn in self.key_buttons.items():
            if key_name in self.key_colors:
                btn.set_color(*self.key_colors[key_name])
            else:
                btn.set_color(45, 45, 45)
        br, bg_, bb = self.base_color
        self.base_btn.configure(
            bg=rgb_to_hex(br, bg_, bb),
            fg="#000" if luminance(br, bg_, bb) > 128 else "#fff"
        )
        self._apply_current()
        self._set_status("Annulé")

    # ── Presets ───────────────────────────────────────────────────────────────

    def _save_preset(self):
        path = filedialog.asksaveasfilename(
            initialdir="presets", defaultextension=".json",
            filetypes=[("JSON", "*.json")], title="Sauvegarder le preset"
        )
        if not path:
            return
        data = {k: list(v) for k, v in self.key_colors.items()}
        data["__base__"] = list(self.base_color)
        data["__brightness__"] = self.brightness_var.get()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        Path("presets/.last").write_text(path)
        self._set_status(f"Preset sauvegardé : {Path(path).name}")

    def _load_preset(self, path=None):
        if path is None:
            path = filedialog.askopenfilename(
                initialdir="presets", filetypes=[("JSON", "*.json")],
                title="Charger un preset"
            )
        if not path or not Path(path).exists():
            return
        try:
            with open(path) as f:
                data = json.load(f)
            base       = data.pop("__base__", [0, 0, 0])
            brightness = data.pop("__brightness__", 100)
            self.base_color  = tuple(base)
            self.key_colors  = {k: tuple(v) for k, v in data.items()}
            self.brightness_var.set(brightness)
            self.brightness = brightness / 100
            self.brightness_label.config(text=f"{brightness}%")
            for key_name, btn in self.key_buttons.items():
                if key_name in self.key_colors:
                    btn.set_color(*self.key_colors[key_name])
                else:
                    btn.set_color(45, 45, 45)
            br, bg_, bb = self.base_color
            self.base_btn.configure(
                bg=rgb_to_hex(br, bg_, bb),
                fg="#000" if luminance(br, bg_, bb) > 128 else "#fff"
            )
            self._apply_current()
            Path("presets/.last").write_text(path)
            self._set_status(f"Preset chargé : {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le preset :\n{e}")

    def _load_last_preset(self):
        last_file = Path("presets/.last")
        if last_file.exists():
            last = last_file.read_text().strip()
            if last and Path(last).exists():
                self._load_preset(last)

    def _set_status(self, msg):
        self.status_var.set(msg)

    # ── Tray ──────────────────────────────────────────────────────────────────

    def _make_tray_icon(self):
        """Crée une icône RGB pour le system tray."""
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # Cercle de fond violet
        d.ellipse([4, 4, 60, 60], fill=(124, 58, 237, 255))
        # Lettre G blanche
        d.rectangle([20, 28, 44, 36], fill=(255, 255, 255, 255))
        d.rectangle([36, 28, 44, 48], fill=(255, 255, 255, 255))
        d.ellipse([16, 20, 48, 52], outline=(255, 255, 255, 255), width=4)
        return img

    def _build_tray(self):
        icon_img = self._make_tray_icon()
        self._tray = pystray.Icon(
            "G515 RGB",
            icon_img,
            "G515 RGB Controller",
            menu=pystray.Menu(
                pystray.MenuItem("Ouvrir", self._show_window, default=True),
                pystray.MenuItem("Démarrage automatique", self._toggle_autostart,
                                 checked=lambda item: self._autostart_enabled()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Éteindre le clavier", lambda: self.after(0, self._clear)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quitter", self._quit_app),
            )
        )
        threading.Thread(target=self._tray.run, daemon=True).start()

    def _show_window(self):
        self.after(0, self._do_show)

    def _do_show(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _hide_window(self):
        self.withdraw()

    # ── Démarrage automatique ─────────────────────────────────────────────────

    def _autostart_enabled(self) -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                  r"Software\Microsoft\Windows\CurrentVersion\Run")
            winreg.QueryValueEx(key, AUTOSTART_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False

    def _toggle_autostart(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Run",
                              0, winreg.KEY_SET_VALUE)
        if self._autostart_enabled():
            winreg.DeleteValue(key, AUTOSTART_NAME)
            self.after(0, lambda: self._set_status("Démarrage automatique désactivé"))
        else:
            winreg.SetValueEx(key, AUTOSTART_NAME, 0, winreg.REG_SZ, AUTOSTART_CMD)
            self.after(0, lambda: self._set_status("Démarrage automatique activé"))
        winreg.CloseKey(key)

    # ── Fermeture ─────────────────────────────────────────────────────────────

    def _on_close(self):
        """Fermer la fenêtre = réduire dans le tray."""
        self._hide_window()

    def _quit_app(self):
        """Quitter complètement depuis le tray."""
        self._tray.stop()
        self.bridge.disconnect()
        self.logi.shutdown()
        self.after(0, self.destroy)


if __name__ == "__main__":
    app = BridgeApp()
    app._build_tray()
    app.mainloop()
