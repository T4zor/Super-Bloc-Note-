# Bloc Note Épinglé

Bloc-note flottant PySide6 (rich text, thèmes, textures, couleurs/dégradés, polices personnalisées, opacité, redimensionnement, raccourci global) avec persistance en AppData.

## Installation locale
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Build binaire
```bash
.\.venv\Scripts\activate
python -m PyInstaller --clean --noconfirm BlocNoteEpinglé.spec
```

## Installateur Windows
- Requiert Inno Setup 6 (ISCC).
- Après avoir généré `dist/BlocNoteEpinglé.exe` :
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" blocnote.iss
```
- Le setup se trouve dans `Output/`.

## Dépôts / données
- Les données utilisateur (notes, configs) sont stockées en AppData et sont exclues du dépôt via `.gitignore`.
- Ressources embarquées : `icon.ico`, `app image/`, `nav/`, `fonts/`.
