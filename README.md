# G515 RGB Controller

Contrôlez les couleurs RGB de votre clavier **Logitech G515** depuis une interface graphique, sans passer par LGHUB. Compatible avec Razer Synapse — vos autres périphériques Razer continuent de fonctionner normalement.

---

## Fonctionnalités

- 🎨 Clavier AZERTY visuel cliquable — clic gauche pour choisir la couleur d'une touche
- 🖱️ Clic droit sur une touche pour la réinitialiser à la couleur de fond
- 🌈 Couleur de fond uniforme + personnalisation par touche
- ☀️ Slider de luminosité global (5% → 100%)
- 🔋 Affichage du niveau de batterie en temps réel
- 💾 Sauvegarde / chargement de presets JSON
- 🎨 Palette de 8 couleurs favorites (clic gauche = appliquer, clic droit = sauvegarder)
- ↩️ Historique d'annulation (20 niveaux)
- 🌊 Effets vague et breathing
- 🔄 Chargement automatique du dernier preset au démarrage
- 📦 Icône dans le system tray (barre des tâches Windows)
- 🚀 Démarrage automatique avec Windows (activable depuis le tray)

---

## Prérequis

- Windows 10 / 11
- [LGHUB](https://www.logitechg.com/fr-fr/innovation/g-hub.html) installé et lancé
- [Python 3.10+](https://www.python.org/downloads/) — cochez **"Add Python to PATH"** lors de l'installation

---

## Installation

**1. Clonez le projet**

```bash
git clone https://github.com/Nabsflix/g515-rgb-controller.git
cd g515-rgb-controller
```

Ou téléchargez le ZIP depuis GitHub → **Code → Download ZIP**, puis extrayez-le.

**2. Installez les dépendances**

```bash
pip install -r requirements.txt
```

**3. Lancez l'application**

```bash
python gui.py
```

Ou double-cliquez sur `launch.bat` pour lancer sans fenêtre console.

---

## Utilisation

### Première ouverture

1. Assurez-vous que **LGHUB est lancé** avant d'ouvrir l'app
2. Lancez `launch.bat` ou `python gui.py`
3. L'interface du clavier apparaît

### Colorier les touches

| Action | Résultat |
|--------|----------|
| Clic gauche sur une touche | Ouvre le sélecteur de couleur |
| Clic droit sur une touche | Réinitialise la touche à la couleur de fond |
| Bouton "Fond clavier" | Change la couleur de toutes les touches |
| Slider Luminosité | Ajuste la luminosité de 5% à 100% |

### Palette de favoris

- **Clic gauche** sur un carré de couleur → applique cette couleur comme fond
- **Clic droit** sur un carré → sauvegarde la couleur de fond actuelle dans ce favori

### Presets

| Action | Commande |
|--------|----------|
| Sauvegarder | Bouton 💾 → choisir un nom |
| Charger | Bouton 📂 → choisir un fichier |
| Chargement auto | Le dernier preset utilisé se recharge au démarrage |

Deux presets sont inclus :
- `presets/gaming.json` — ZQSD en rouge, espace en bleu
- `presets/rainbow.json` — arc-en-ciel par touche

### Effets

| Effet | Description |
|-------|-------------|
| 🌊 Vague → | Vague de couleurs de gauche à droite |
| 🫧 Breathing | Effet respiratoire avec la couleur de votre choix |
| ⬛ Éteindre | Éteint toutes les touches |

### Annuler

Le bouton **↩ Annuler** permet de revenir en arrière jusqu'à 20 étapes.

---

## System Tray

Une fois lancée, l'app se minimise dans la barre des tâches Windows (en bas à droite).

| Action | Résultat |
|--------|----------|
| Double-clic sur l'icône | Ouvre la fenêtre |
| Clic droit → Ouvrir | Ouvre la fenêtre |
| Clic droit → Démarrage automatique | Active/désactive le lancement au démarrage de Windows |
| Clic droit → Éteindre le clavier | Éteint toutes les touches |
| Clic droit → Quitter | Ferme complètement l'application |

> **Fermer la fenêtre** ne quitte pas l'app — elle reste active dans le tray. Utilisez **Quitter** depuis le menu tray pour l'arrêter complètement.

---

## Démarrage automatique avec Windows

1. Clic droit sur l'icône dans le tray
2. Cliquez sur **Démarrage automatique**
3. L'app se lancera automatiquement à chaque démarrage, sans fenêtre console

---

## Comment ça marche

L'app utilise le **SDK Logitech LED** (`sdk_legacy_led_x64.dll`) fourni avec LGHUB pour contrôler les couleurs du G515 directement, touche par touche.

Le niveau de batterie est lu depuis la base de données locale de LGHUB (`%LOCALAPPDATA%\LGHUB\settings.db`).

L'app **ne se connecte pas** à Razer Chroma, vos périphériques Razer (souris, casque, etc.) continuent d'être gérés normalement par Synapse.

---

## Structure du projet

```
├── gui.py              # Interface graphique + system tray
├── bridge.py           # SDK Logitech LED
├── launch.bat          # Lancement sans console
├── requirements.txt    # Dépendances Python
└── presets/
    ├── gaming.json     # Preset gaming (ZQSD rouge)
    └── rainbow.json    # Preset arc-en-ciel
```

---

## Dépendances

| Package | Utilisation |
|---------|-------------|
| `requests` | Communication HTTP |
| `pystray` | Icône system tray |
| `pillow` | Génération de l'icône tray |
| `websockets` | Communication WebSocket LGHUB |

---

## Licence

MIT — libre d'utilisation, modification et distribution.
