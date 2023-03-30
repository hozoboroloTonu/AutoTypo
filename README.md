# Auto Typo

A lightweight, portable desktop keyboard automation utility built with Python and PySide6.

## Features

- Configurable message, target count, and unlimited mode
- Adjustable message interval with a fixed 1000 ms initial delay
- Global approval (`Shift + Enter`) and emergency stop (`Esc`) hotkeys
- Activity logs and session history stored locally in `data/`
- Single-file portable Windows executable build via PyInstaller

## Run from Source

```bash
pip install -r requirements.txt
python main.py
```

## Build Executable

Run `build.bat` or build directly with PyInstaller:

```bash
python -m PyInstaller AutoTypo.spec --noconfirm --clean
```

The compiled executable will be generated at `dist/AutoTypo.exe`.

## Author

Mahmud Tonmoy — [github.com/hozoboroloTonu/AutoTypo](https://github.com/hozoboroloTonu/AutoTypo)
