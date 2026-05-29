"""
Razer Chroma → Logitech G515 Bridge
Lit les effets Razer Chroma et les applique sur le clavier Logitech G515
"""

import ctypes
import ctypes.wintypes
import json
import time
import threading
import requests
import sys
import os
from pathlib import Path

# ── Logitech LED SDK ──────────────────────────────────────────────────────────

LOGI_SDK_DLL = r"C:\Program Files\LGHUB\sdks\sdk_legacy_led_x64.dll"

LOGI_DEVICETYPE_PERKEY_RGB = 0x4
LOGI_DEVICETYPE_ALL        = 0x7

# Mapping touches AZERTY → scan codes physiques (positions QWERTY)
# Le SDK utilise toujours les positions physiques QWERTY
LOGITECH_KEY_MAP = {
    # Rangée fonction
    "ESC": 0x01, "F1": 0x3B, "F2": 0x3C, "F3": 0x3D, "F4": 0x3E,
    "F5": 0x3F, "F6": 0x40, "F7": 0x41, "F8": 0x42, "F9": 0x43,
    "F10": 0x44, "F11": 0x57, "F12": 0x58,
    # Rangée chiffres AZERTY
    "TWO_TILDE": 0x29,   # touche ² ~
    "AMPERSAND": 0x02,   # &  1
    "EACUTE": 0x03,      # é  2
    "QUOTE": 0x04,       # "  3
    "APOSTROPHE": 0x05,  # '  4
    "LPAREN": 0x06,      # (  5
    "MINUS": 0x07,       # -  6
    "EGRAVE": 0x08,      # è  7
    "UNDERSCORE": 0x09,  # _  8
    "CCEDILLA": 0x0A,    # ç  9
    "AGRAVE": 0x0B,      # à  0
    "RPAREN": 0x0C,      # )
    "EQUALS": 0x0D,      # =
    "BACKSPACE": 0x0E,
    # Rangée AZERTY (noms physiques des touches)
    "TAB": 0x0F,
    "A": 0x10,   # A azerty = position Q qwerty
    "Z": 0x11,   # Z azerty = position W qwerty
    "E": 0x12,
    "R": 0x13,
    "T": 0x14,
    "Y": 0x15,
    "U": 0x16,
    "I": 0x17,
    "O": 0x18,
    "P": 0x19,
    "OPEN_BRACKET": 0x1A,   # ^
    "CLOSE_BRACKET": 0x1B,  # $
    "ENTER": 0x1C,
    "BACKSLASH": 0x2B,      # *
    # Rangée home
    "CAPS_LOCK": 0x3A,
    "Q": 0x1E,   # Q azerty = position A qwerty
    "S": 0x1F,
    "D": 0x20,
    "F": 0x21,
    "G": 0x22,
    "H": 0x23,
    "J": 0x24,
    "K": 0x25,
    "L": 0x26,
    "M": 0x27,   # M azerty = position ; qwerty
    "UGRAVE": 0x28,          # ù
    # Rangée basse
    "LEFT_SHIFT": 0x2A,
    "W": 0x2C,   # W azerty = position Z qwerty
    "X": 0x2D,
    "C": 0x2E,
    "V": 0x2F,
    "B": 0x30,
    "N": 0x31,
    "COMMA": 0x33,   # ,
    "SEMICOLON": 0x34,  # ;
    "COLON": 0x35,      # :
    "EXCLAMATION": 0x56, # ! (touche ISO entre shift gauche et W)
    "RIGHT_SHIFT": 0x36,
    # Rangée espace
    "LEFT_CONTROL": 0x1D, "LEFT_WINDOWS": 0x5B, "LEFT_ALT": 0x38,
    "SPACE": 0x39, "RIGHT_ALT": 0x38, "RIGHT_WINDOWS": 0x5C,
    "APPLICATION_SELECT": 0x5D, "RIGHT_CONTROL": 0x1D,
    # Navigation
    "ARROW_UP": 0x48, "ARROW_LEFT": 0x4B, "ARROW_DOWN": 0x50, "ARROW_RIGHT": 0x4D,
    "INSERT": 0x52, "HOME": 0x47, "PAGE_UP": 0x49,
    "KEYBOARD_DELETE": 0x53, "END": 0x4F, "PAGE_DOWN": 0x51,
    "PRINT_SCREEN": 0x37, "SCROLL_LOCK": 0x46, "PAUSE_BREAK": 0x45,
    # Aliases pratiques
    "DEL": 0x53, "SUPPR": 0x53,
    "ENTREE": 0x1C, "RETOUR": 0x0E,
    "MAJUSCULE": 0x3A, "VERR_MAJ": 0x3A,
}


class LogitechLED:
    def __init__(self):
        self.dll = None
        self._load()

    def _load(self):
        if not Path(LOGI_SDK_DLL).exists():
            raise FileNotFoundError(f"SDK Logitech introuvable : {LOGI_SDK_DLL}")
        self.dll = ctypes.cdll.LoadLibrary(LOGI_SDK_DLL)
        self.dll.LogiLedInit.restype = ctypes.c_bool
        self.dll.LogiLedSetTargetDevice.restype = ctypes.c_bool
        self.dll.LogiLedSetLighting.restype = ctypes.c_bool
        self.dll.LogiLedSetLightingForKeyWithKeyName.restype = ctypes.c_bool
        self.dll.LogiLedSetLightingForKeyWithScanCode.restype = ctypes.c_bool
        self.dll.LogiLedShutdown.restype = None

    def init(self) -> bool:
        ok = self.dll.LogiLedInit()
        if ok:
            self.dll.LogiLedSetTargetDevice(LOGI_DEVICETYPE_PERKEY_RGB)
        return ok

    def set_all(self, r: int, g: int, b: int):
        """Applique une couleur à tout le clavier (0-100)."""
        self.dll.LogiLedSetLighting(
            ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
        )

    def set_key(self, key_name: str, r: int, g: int, b: int) -> bool:
        """Applique une couleur à une touche spécifique par son nom."""
        scan = LOGITECH_KEY_MAP.get(key_name.upper())
        if scan is None:
            return False
        return self.dll.LogiLedSetLightingForKeyWithKeyName(
            ctypes.c_int(scan),
            ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
        )

    def set_key_by_scan(self, scan_code: int, r: int, g: int, b: int) -> bool:
        return self.dll.LogiLedSetLightingForKeyWithScanCode(
            ctypes.c_int(scan_code),
            ctypes.c_int(r), ctypes.c_int(g), ctypes.c_int(b)
        )

    def shutdown(self):
        if self.dll:
            self.dll.LogiLedShutdown()


# ── Razer Chroma REST API ─────────────────────────────────────────────────────

CHROMA_BASE_URL = "http://localhost:54235/razer/chromasdk"
CHROMA_APP_INFO = {
    "title": "Logitech G515 Bridge",
    "description": "Synchronise le clavier Logitech G515 avec Razer Chroma",
    "author": {"name": "Bridge", "contact": "local"},
    "device_supported": ["keyboard"],
    "category": "application"
}

# Mapping touches Razer Chroma keyboard grid → scan codes Logitech
# Razer keyboard grid : 6 lignes × 22 colonnes
# On mappe les positions (row, col) aux scan codes Logitech
RAZER_TO_LOGITECH_SCAN = {
    # Row 0 : ESC, F1-F12, Print, Scroll, Pause
    (0, 0): 0x01,  # ESC
    (0, 1): 0x3B,  # F1
    (0, 2): 0x3C,  # F2
    (0, 3): 0x3D,  # F3
    (0, 4): 0x3E,  # F4
    (0, 5): 0x3F,  # F5
    (0, 6): 0x40,  # F6
    (0, 7): 0x41,  # F7
    (0, 8): 0x42,  # F8
    (0, 9): 0x43,  # F9
    (0, 10): 0x44, # F10
    (0, 11): 0x57, # F11
    (0, 12): 0x58, # F12
    # Row 1 : ` 1-0 - = Backspace
    (1, 0): 0x29,  # ~
    (1, 1): 0x02,  # 1
    (1, 2): 0x03,  # 2
    (1, 3): 0x04,  # 3
    (1, 4): 0x05,  # 4
    (1, 5): 0x06,  # 5
    (1, 6): 0x07,  # 6
    (1, 7): 0x08,  # 7
    (1, 8): 0x09,  # 8
    (1, 9): 0x0A,  # 9
    (1, 10): 0x0B, # 0
    (1, 11): 0x0C, # -
    (1, 12): 0x0D, # =
    (1, 13): 0x0E, # Backspace
    # Row 2 : Tab Q-P [ ] \
    (2, 0): 0x0F,  # Tab
    (2, 1): 0x10,  # Q
    (2, 2): 0x11,  # W
    (2, 3): 0x12,  # E
    (2, 4): 0x13,  # R
    (2, 5): 0x14,  # T
    (2, 6): 0x15,  # Y
    (2, 7): 0x16,  # U
    (2, 8): 0x17,  # I
    (2, 9): 0x18,  # O
    (2, 10): 0x19, # P
    (2, 11): 0x1A, # [
    (2, 12): 0x1B, # ]
    (2, 13): 0x2B, # \
    # Row 3 : Caps A-L ; ' Enter
    (3, 0): 0x3A,  # Caps
    (3, 1): 0x1E,  # A
    (3, 2): 0x1F,  # S
    (3, 3): 0x20,  # D
    (3, 4): 0x21,  # F
    (3, 5): 0x22,  # G
    (3, 6): 0x23,  # H
    (3, 7): 0x24,  # J
    (3, 8): 0x25,  # K
    (3, 9): 0x26,  # L
    (3, 10): 0x27, # ;
    (3, 11): 0x28, # '
    (3, 12): 0x1C, # Enter
    # Row 4 : LShift Z-M , . / RShift
    (4, 0): 0x2A,  # LShift
    (4, 1): 0x2C,  # Z
    (4, 2): 0x2D,  # X
    (4, 3): 0x2E,  # C
    (4, 4): 0x2F,  # V
    (4, 5): 0x30,  # B
    (4, 6): 0x31,  # N
    (4, 7): 0x32,  # M
    (4, 8): 0x33,  # ,
    (4, 9): 0x34,  # .
    (4, 10): 0x35, # /
    (4, 11): 0x36, # RShift
    # Row 5 : LCtrl Win LAlt Space RAlt Fn Menu RCtrl + arrows
    (5, 0): 0x1D,  # LCtrl
    (5, 1): 0x5B,  # Win
    (5, 2): 0x38,  # LAlt
    (5, 3): 0x39,  # Space
    (5, 9): 0x48,  # Up
    (5, 10): 0x4B, # Left
    (5, 11): 0x50, # Down
    (5, 12): 0x4D, # Right
}


def _hsv_to_rgb(h, s, v):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


class ChromaBridge:
    def __init__(self):
        self.session_url = None
        self.heartbeat_thread = None
        self.running = True
        self.logi = LogitechLED()
        self._current_effect = None
        self._effect_thread = None
        self._base_color = (0, 0, 0)  # couleur de fond actuelle

    def connect(self) -> bool:
        try:
            resp = requests.post(
                CHROMA_BASE_URL,
                json=CHROMA_APP_INFO,
                timeout=5
            )
            data = resp.json()
            if "uri" in data:
                self.session_url = data["uri"]
                print(f"[Chroma] Connecté : {self.session_url}")
                return True
            print(f"[Chroma] Erreur connexion : {data}")
            return False
        except Exception as e:
            print(f"[Chroma] Impossible de se connecter (Razer Synapse lancé ?) : {e}")
            return False

    def disconnect(self):
        self.running = False
        if self.session_url:
            try:
                requests.delete(self.session_url, timeout=3)
            except Exception:
                pass
            self.session_url = None

    def _heartbeat(self):
        while self.running and self.session_url:
            try:
                requests.put(f"{self.session_url}/heartbeat", timeout=3)
            except Exception:
                pass
            time.sleep(1)

    def start_heartbeat(self):
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat, daemon=True)
        self.heartbeat_thread.start()

    # ── Effets ────────────────────────────────────────────────────────────────

    def apply_static(self, r: int, g: int, b: int):
        """Couleur statique uniforme sur tout le clavier."""
        self._base_color = (r, g, b)
        color = (b << 16) | (g << 8) | r  # BGR format Razer
        payload = {"effect": "CHROMA_STATIC", "param": {"color": color}}
        if self.session_url:
            requests.put(f"{self.session_url}/keyboard", json=payload, timeout=3)
        self.logi.set_all(
            int(r / 255 * 100),
            int(g / 255 * 100),
            int(b / 255 * 100)
        )
        self._current_effect = ("static", r, g, b)
        print(f"[Bridge] Statique appliqué : RGB({r},{g},{b})")

    def apply_custom(self, key_colors: dict):
        """
        Couleurs personnalisées par touche, fond = _base_color.
        key_colors : { "A": (255,0,0), "S": (0,255,0), ... }
        """
        br, bg, bb = self._base_color
        scan_to_pos = {v: k for k, v in RAZER_TO_LOGITECH_SCAN.items()}

        # Grille Razer remplie avec la couleur de fond
        base_bgr = (bb << 16) | (bg << 8) | br
        grid = [[base_bgr] * 22 for _ in range(6)]

        # D'abord remettre tout le clavier Logitech à la couleur de fond
        self.logi.set_all(int(br/255*100), int(bg/255*100), int(bb/255*100))
        time.sleep(0.05)

        # Puis appliquer les touches personnalisées par-dessus
        for key_name, (r, g, b) in key_colors.items():
            key_upper = key_name.upper()
            if key_upper in LOGITECH_KEY_MAP:
                scan = LOGITECH_KEY_MAP[key_upper]
                self.logi.set_key_by_scan(scan, int(r/255*100), int(g/255*100), int(b/255*100))
                if scan in scan_to_pos:
                    row, col = scan_to_pos[scan]
                    grid[row][col] = (b << 16) | (g << 8) | r

        if self.session_url:
            payload = {"effect": "CHROMA_CUSTOM", "param": grid}
            requests.put(f"{self.session_url}/keyboard", json=payload, timeout=3)

        self._current_effect = ("custom", key_colors)
        print(f"[Bridge] Personnalisé appliqué : {len(key_colors)} touches")

    def _stop_effect(self):
        """Arrête tout effet en cours."""
        self.running = False
        if self._effect_thread and self._effect_thread.is_alive():
            self._effect_thread.join(timeout=1)
        self.running = True

    def apply_breathing(self, r: int, g: int, b: int):
        """Effet respiratoire natif Logitech."""
        self._stop_effect()

        def _run():
            import math
            step = 0
            while self.running and self._current_effect == "breathing":
                brightness = (math.sin(step * 0.05) + 1) / 2
                self.logi.set_all(
                    int(r / 255 * 100 * brightness),
                    int(g / 255 * 100 * brightness),
                    int(b / 255 * 100 * brightness)
                )
                step += 1
                time.sleep(0.03)

        self._current_effect = "breathing"
        self._effect_thread = threading.Thread(target=_run, daemon=True)
        self._effect_thread.start()
        print(f"[Bridge] Breathing : RGB({r},{g},{b})")

    def apply_wave(self, direction: int = 1):
        """Effet vague natif Logitech (gauche→droite ou droite→gauche)."""
        self._stop_effect()

        # Colonnes de touches ordonnées de gauche à droite (scan codes)
        COLUMNS = [
            [0x01],                              # ESC
            [0x3B, 0x02, 0x0F, 0x3A, 0x2A, 0x1D],  # F1, 1, Tab, Caps, LShift, LCtrl
            [0x3C, 0x03, 0x10, 0x1E, 0x56, 0x5B],  # F2, 2, A, Q, !, Win
            [0x3D, 0x04, 0x11, 0x1F, 0x2C, 0x38],  # F3, 3, Z, S, W, Alt
            [0x3E, 0x05, 0x12, 0x20, 0x2D],         # F4, 4, E, D, X
            [0x3F, 0x06, 0x13, 0x21, 0x2E],         # F5, 5, R, F, C
            [0x40, 0x07, 0x14, 0x22, 0x2F],         # F6, 6, T, G, V
            [0x41, 0x08, 0x15, 0x23, 0x30],         # F7, 7, Y, H, B
            [0x42, 0x09, 0x16, 0x24, 0x31],         # F8, 8, U, J, N
            [0x43, 0x0A, 0x17, 0x25, 0x32],         # F9, 9, I, K, M
            [0x44, 0x0B, 0x18, 0x26, 0x33],         # F10, 0, O, L, ,
            [0x57, 0x0C, 0x19, 0x27, 0x34],         # F11, -, P, M, ;
            [0x58, 0x0D, 0x1A, 0x28, 0x35],         # F12, =, [, ', :
            [0x0E, 0x1B, 0x2B, 0x1C, 0x36],         # Backspace, ], \, Enter, RShift
            [0x37, 0x52, 0x53],                      # Print, Insert, Delete
            [0x46, 0x47, 0x4F],                      # Scroll, Home, End
            [0x45, 0x49, 0x51],                      # Pause, PgUp, PgDn
            [0x48],                                  # Up
            [0x4B, 0x50, 0x4D],                      # Left, Down, Right
        ]

        cols = COLUMNS if direction == 1 else list(reversed(COLUMNS))
        n = len(cols)

        def _run():
            offset = 0
            while self.running and self._current_effect == "wave":
                for ci, col_scans in enumerate(cols):
                    idx = (ci - offset) % n
                    # Couleur arc-en-ciel basée sur position
                    hue = idx / n
                    r2, g2, b2 = _hsv_to_rgb(hue, 1.0, 1.0)
                    for scan in col_scans:
                        self.logi.set_key_by_scan(
                            scan,
                            int(r2 / 255 * 100),
                            int(g2 / 255 * 100),
                            int(b2 / 255 * 100)
                        )
                offset = (offset + 1) % n
                time.sleep(0.05)

        self._current_effect = "wave"
        self._effect_thread = threading.Thread(target=_run, daemon=True)
        self._effect_thread.start()
        print(f"[Bridge] Wave direction={direction}")


# ── Interface CLI ─────────────────────────────────────────────────────────────

def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def print_help():
    print("""
╔══════════════════════════════════════════════════════╗
║        Razer Chroma ↔ Logitech G515 Bridge           ║
╚══════════════════════════════════════════════════════╝

Commandes disponibles :
  static <#RRGGBB>          Couleur uniforme ex: static #FF0000
  key <TOUCHE> <#RRGGBB>    Colorier une touche  ex: key A #00FF00
  preset <fichier.json>     Charger un preset    ex: preset gaming.json
  save <fichier.json>       Sauvegarder config actuelle
  breathing <#RRGGBB>       Effet respiratoire   ex: breathing #0000FF
  wave [1|2]                Effet vague          ex: wave 1
  clear                     Tout éteindre
  help                      Afficher cette aide
  quit                      Quitter

Touches disponibles : A-Z, F1-F12, ESC, TAB, CAPS_LOCK,
  ENTER, SPACE, BACKSPACE, LEFT_SHIFT, RIGHT_SHIFT,
  LEFT_CONTROL, RIGHT_CONTROL, LEFT_ALT, RIGHT_ALT,
  LEFT_WINDOWS, ARROW_UP/DOWN/LEFT/RIGHT, etc.
""")


def save_preset(filepath: str, key_colors: dict):
    data = {k: list(v) for k, v in key_colors.items()}
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    Path("presets/.last").write_text(filepath)
    print(f"[Bridge] Preset sauvegardé : {filepath}")


def load_preset(filepath: str) -> dict:
    with open(filepath) as f:
        data = json.load(f)
    return {k: tuple(v) for k, v in data.items()}


def main():
    print("\n=== Razer Chroma ↔ Logitech G515 Bridge ===\n")

    # Init Logitech SDK
    logi = LogitechLED()
    if not logi.init():
        print("[ERREUR] Impossible d'initialiser le SDK Logitech.")
        print("  → Assurez-vous que LGHUB est lancé et que le G515 est connecté.")
        sys.exit(1)
    print("[Logitech] SDK initialisé ✓")

    bridge = ChromaBridge()
    bridge.logi = logi

    # Connexion Razer Chroma (optionnelle)
    chroma_ok = bridge.connect()
    if chroma_ok:
        bridge.start_heartbeat()
        print("[Razer] Chroma SDK connecté ✓")
    else:
        print("[Razer] Mode sans Chroma (contrôle Logitech uniquement)")

    print_help()

    current_custom = {}  # stocke les couleurs par touche en cours

    # Charge automatiquement le dernier preset utilisé
    last_preset_file = Path("presets/.last")
    if last_preset_file.exists():
        last = last_preset_file.read_text().strip()
        if last and Path(last).exists():
            try:
                current_custom = load_preset(last)
                bridge.apply_custom(current_custom)
                print(f"[Bridge] Dernier preset chargé : {last}")
            except Exception:
                pass

    try:
        while True:
            try:
                cmd = input("\n> ").strip()
            except EOFError:
                break

            if not cmd:
                continue

            parts = cmd.split()
            action = parts[0].lower()

            if action == "quit":
                break

            elif action == "help":
                print_help()

            elif action == "clear":
                logi.set_all(0, 0, 0)
                current_custom = {}
                print("[Bridge] Clavier éteint")

            elif action == "static" and len(parts) >= 2:
                try:
                    r, g, b = hex_to_rgb(parts[1])
                    bridge.apply_static(r, g, b)
                    current_custom = {}
                except ValueError:
                    print("Format invalide. Exemple : static #FF0000")

            elif action == "key" and len(parts) >= 3:
                key = parts[1].upper()
                try:
                    r, g, b = hex_to_rgb(parts[2])
                    current_custom[key] = (r, g, b)
                    bridge.apply_custom(current_custom)
                except ValueError:
                    print("Format invalide. Exemple : key A #FF0000")

            elif action == "preset" and len(parts) >= 2:
                try:
                    current_custom = load_preset(parts[1])
                    bridge.apply_custom(current_custom)
                    Path("presets/.last").write_text(parts[1])
                    print(f"[Bridge] Preset chargé : {parts[1]}")
                except FileNotFoundError:
                    print(f"Fichier introuvable : {parts[1]}")
                except json.JSONDecodeError:
                    print("Fichier JSON invalide")

            elif action == "save" and len(parts) >= 2:
                save_preset(parts[1], current_custom)

            elif action == "breathing" and len(parts) >= 2:
                try:
                    r, g, b = hex_to_rgb(parts[1])
                    bridge.apply_breathing(r, g, b)
                except ValueError:
                    print("Format invalide. Exemple : breathing #FF0000")

            elif action == "wave":
                direction = int(parts[1]) if len(parts) >= 2 else 1
                bridge.apply_wave(direction)

            else:
                print(f"Commande inconnue : '{action}'. Tapez 'help' pour l'aide.")

    except KeyboardInterrupt:
        pass
    finally:
        print("\n[Bridge] Fermeture...")
        bridge.disconnect()
        logi.shutdown()


if __name__ == "__main__":
    main()
