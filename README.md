# Auto Typo

A lightweight, portable desktop keyboard automation utility built with Python and PySide6.

## Download

<a href="https://github.com/hozoboroloTonu/AutoTypo/releases/download/v3.1.1/AutoTypo.exe">
  <img src="assets/get_it_on_github.png" alt="Get it on GitHub" height="68" />
</a>

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
