# G515 RGB Controller

Contrôlez les couleurs RGB de votre clavier **Logitech G515** depuis une interface graphique, indépendamment de LGHUB.

![Interface](https://i.imgur.com/placeholder.png)

## Fonctionnalités

- 🎨 Clavier AZERTY visuel cliquable — clic gauche pour choisir la couleur d'une touche
- 🖱️ Clic droit sur une touche pour la réinitialiser
- 🌈 Couleur de fond uniforme + personnalisation par touche
- ☀️ Slider de luminosité global
- 🔋 Affichage du niveau de batterie en temps réel
- 💾 Sauvegarde / chargement de presets JSON
- 🎨 Palette de 8 couleurs favorites
- ↩️ Historique annulation (20 niveaux)
- 🌊 Effets vague et breathing
- 🔄 Chargement automatique du dernier preset au démarrage
- 📦 Icône dans le system tray (barre des tâches)
- 🚀 Démarrage automatique avec Windows (optionnel)

## Prérequis

- Windows 10/11
- [LGHUB](https://www.logitechg.com/fr-fr/innovation/g-hub.html) installé et lancé
- Python 3.10+

## Installation

```bash
pip install requests pystray pillow
```

## Lancement

Double-cliquez sur `launch.bat` ou :

```bash
python gui.py
```

## Presets inclus

| Preset | Description |
|--------|-------------|
| `gaming.json` | ZQSD en rouge, espace en bleu |
| `rainbow.json` | Arc-en-ciel par touche |

## Structure

```
├── gui.py          # Interface graphique + system tray
├── bridge.py       # SDK Logitech LED + Razer Chroma
├── launch.bat      # Lancement sans console
└── presets/        # Configurations sauvegardées
```

## Comment ça marche

L'app utilise le **SDK Logitech LED** (`sdk_legacy_led_x64.dll`) fourni avec LGHUB pour contrôler les couleurs du G515 directement, sans passer par l'interface LGHUB.

La batterie est lue depuis la base de données locale de LGHUB.

## Licence

MIT
