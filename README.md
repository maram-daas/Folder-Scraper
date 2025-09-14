# 📂 Folder Scraper (GUI)

A desktop application built with **Python + Tkinter** that helps you search through folders for files by **keyword in the file name**. It supports **classification by parent folder name**, customizable **search depth**, and **result limits**, all with a simple and interactive GUI.

---

## ✨ Features

- 🔍 **Smart File Search**: Search for files whose names contain a given keyword
- 🗂️ **Intelligent Classification**:
  - Files are grouped by category if their parent folder contains a category keyword
  - Uncategorized files go to **"Other"** (or **"All Results"** if no categories are defined)
- ⚙️ **Customizable Search Options**:
  - **Max depth** → control how deep into subfolders to search
  - **Max results** → stop after a set number of matches
- 🖥️ **User-Friendly GUI Features**:
  - Save default folder and categories between sessions
  - Add/remove/clear classification categories dynamically
  - Real-time progress bar and live result counter
  - Stop searches at any time
  - Double-click results to open them in your file explorer
- 🐧 **Cross-Platform Support**:
  - ✅ **Windows**: Fully tested and working
  - ⚠️ **macOS & Linux**: Integration exists, but not yet tested

---

## 🚀 Installation & Usage

### 🖥️ For Non-Developers
1. Download the latest release from the [Releases](../../releases) page, or download the .exe file.
2. On Windows, run the `.exe` file directly — **no Python installation required**

### 🧑‍💻 For Developers
1. Clone this repository or download `FolderScraper.py`
2. Run with Python 3.8+:
   ```bash
   python FolderScraper.py
   ```
3. Feel free to modify and improve the code — contributions welcome!

---

## 🖼️ GUI Overview

| Component | Description |
|-----------|-------------|
| **Select Folder** | Choose the root directory to search |
| **Classification Categories** | Add/remove category keywords that match against parent folder names |
| **Search Keyword** | Type the keyword to search in file names |
| **Search Settings** | Adjust max depth and max results |
| **Results Tree** | Shows matches grouped by category (double-click to open) |

---

## ⚙️ How Classification Works

**Example** with categories `finance`, `legal` and search keyword `report`:

```
Root/
├── finance/
│   └── annual_report.txt   → classified as "finance"
├── legal/
│   └── contract_report.pdf → classified as "legal"
├── misc/
│   └── old_report.docx     → classified as "Other"
```

If no categories are defined, all results are grouped under **"All Results"**.

---

## 📜 Settings Persistence

The app automatically saves:
- ✅ Last selected folder
- ✅ Current classification categories

Settings are stored in: `~/.folder_scraper_settings.txt`

This way, your preferences persist between sessions!

---

## 🛠️ Tech Stack

- **Python 3.x**
- **Tkinter** (built-in GUI library)
- **Standard libraries**: `os`, `pathlib`, `threading`, `subprocess`, `collections`

---

## 🔧 Development & Contributing

This project welcomes contributions! Whether you want to:
- 🐛 Fix bugs
- ✨ Add new features
- 📱 Improve the UI
- 🧪 Test on macOS/Linux
- 📝 Improve documentation

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for people struggling with their files like I was.**

---
