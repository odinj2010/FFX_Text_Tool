# Final Fantasy X Text & Dialogue Editor (FFX Text Tool)

A modern desktop GUI utility designed to view, decode, edit, and repack text and dialogue binary tables (e.g., `item_txt.bin`, `arms_txt.bin`, `status_txt.bin`, `summon_txt.bin`, `menu_txt.bin`, `mmain_txt.bin`, etc.) from *Final Fantasy X*.

[![Repository](https://img.shields.io/badge/GitHub-FFX__Text__Tool-blue?logo=github)](https://github.com/odinj2010/FFX_Text_Tool)

---

## Features

- **Custom FFX Character Encoding**: Decodes and encodes text using FFX's proprietary translation mappings (such as `ffxsjistbl_us.bin`, `ffxsjistbl_jp.bin`).
- **Control Codes Support**: Full decoding and reconstruction of in-game control codes, including:
  - Colors (`{CLR:YELLOW}`, `{CLR:RED}`, etc.)
  - Timing & formatting (`{PAUSE}`, `{SPACE:XX}`, `{TIME:XX}`)
  - Variables and buttons (`{VAR:XX}`, `{KEY:XX}`, `{PC:XX}`)
  - Choices and line breaks (`{CHOICE:XX}`, `{CHOICE-END}`, `\n`)
- **Safe Repacking**: Safeguards against the game's 16-bit offset limitation (65,535 bytes) by calculating the total unique string pool size before saving and warning if it is exceeded to prevent game crashes.
- **Built-in Backups**: Automatically creates a `.bak` backup copy of the target file before any saving operations.
- **Damage Formula Editor**: Interactive editing with human-readable damage formulas (e.g., `STR vs DEF`, `Celestial HP-based`, `MAG ignore MDF`) mapped directly to their hex codes.
- **Modern Dark UI**: A responsive, clean dark-theme user interface built with Python's Tkinter.

---

## Getting Started

### Prerequisites

- **Python 3.8 or higher**
- **Tkinter** (usually included with standard Python installations)

### Running the Application

Simply execute the main script using python:

```bash
python FFX_Text_Tool.py
```

### Packaging into a Executable

You can compile the tool into a standalone Windows executable using PyInstaller with the provided `.spec` configuration:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the executable:
   ```bash
   pyinstaller FFX_Text_Tool.spec
   ```
3. Find your built executable in the `dist` folder.

---

## Contributing & Repository

For updates, issues, and contributions, visit the repository:
[https://github.com/odinj2010/FFX_Text_Tool](https://github.com/odinj2010/FFX_Text_Tool)

Developed by **NfgOdin** (Copyright © 2026).
All rights reserved.
