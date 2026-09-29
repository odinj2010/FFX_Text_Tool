# Final Fantasy X Text & Dialogue Editor (FFX Text Tool)

A modern desktop GUI utility designed to view, decode, edit, and repack text and dialogue binary tables (e.g., `item_txt.bin`, `arms_txt.bin`, `status_txt.bin`, `summon_txt.bin`, `menu_txt.bin`, `mmain_txt.bin`, `monster1.bin`, `monster2.bin`, `monster3.bin`, etc.) from *Final Fantasy X*.

[![Repository](https://img.shields.io/badge/GitHub-FFX__Text__Tool-blue?logo=github)](https://github.com/odinj2010/FFX_Text_Tool)

---

## Features

- **Broad File Support**: View, edit, and repack core battle, system, and monster binary text tables:
  - Battle & System: `item_txt.bin`, `arms_txt.bin`, `status_txt.bin`, `summon_txt.bin`, `menu_txt.bin`, `mmain_txt.bin`, `config_txt.bin`, `name_txt.bin`, `save_txt.bin`, `btlend_txt.bin`, `btl_txt.bin`, `build_txt.bin`, `help_txt.bin`, `panel.bin`, `a_ability.bin`, `important.bin`
  - Abilities & Magic: `item.bin`, `command.bin`, `monmagic1.bin`, `monmagic2.bin`
  - Monsters (New in v1.1.0): `monster1.bin`, `monster2.bin`, `monster3.bin` (Sensor advice & Scan descriptions)
- **Custom FFX Character Encoding**: Decodes and encodes text using FFX's proprietary translation mappings (`ffxsjistbl_us.bin`, `ffxsjistbl_jp.bin`, etc.).
- **Control Codes Support**: Full decoding and reconstruction of in-game control codes, including:
  - Colors (`{CLR:YELLOW}`, `{CLR:RED}`, `{CLR:OL_CYAN}`, etc.)
  - Timing & formatting (`{PAUSE}`, `{SPACE:XX}`, `{TIME:XX}`)
  - Variables and buttons (`{VAR:XX}`, `{KEY:XX}`, `{PC:XX}`)
  - Choices and line breaks (`{CHOICE:XX}`, `{CHOICE-END}`, `\n`)
- **Bulk CSV Export / Import**: Single-file or batch directory export and import to CSV for easy localization and mass text translations.
- **Global Search & Replace**: Batch find and replace terms across entries or entire localization sets.
- **Safe Repacking**: Safeguards against the game's 16-bit offset limitation (65,535 bytes) by calculating the total unique string pool size before saving and warning if it is exceeded to prevent game crashes.
- **Built-in Backups**: Automatically creates a `.bak` backup copy of the target file before any saving operations.
- **Damage Formula Editor**: Interactive editing with human-readable damage formulas (e.g., `STR vs DEF`, `Celestial HP-based`, `MAG ignore MDF`) mapped directly to their hex codes.
- **Modern Dark UI**: A responsive, clean dark-theme user interface built with Python's Tkinter.

---

## Release Changelog

### v1.1.0
- **Added Monster Support**: Added full support for `monster1.bin`, `monster2.bin`, and `monster3.bin` (covering enemy names, Sensor tips, and full Scan text boxes across all 365 enemy entries).
- **Search & Display Enhancements**: Improved treeview search and list previews to display Sensor/Scan information cleanly for monster tables.
- **Repack & Stability Improvements**: Tested round-trip repacking across all localized monster files.

### v1.0.0
- Initial public release supporting abilities, items, menus, commands, and key item tables with full FFX charset encoding/decoding and CSV batch tools.

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
