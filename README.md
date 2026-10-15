# Ragebait Game

## Lancer le jeu
```bash
python -m pip install pygame
python menu.py
```

Un niveau se lance aussi directement :
```bash
python core/1.py
```

## Commandes
- **Q/D**, **A/D** ou **←/→** : se déplacer
- **Espace**, **Z**, **W** ou **↑** : sauter
- **R** : recommencer
- **Échap** : retour au menu

## Structure
- `menu.py` : menu principal
- `core/moteur.py` : moteur commun aux niveaux
- `core/1.py` à `core/10.py` : un fichier par niveau
- `img/` et `audio/` : ressources, inchangées
