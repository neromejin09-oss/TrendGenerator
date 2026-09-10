# 📊 Excel Data Automation Pipeline

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

A Python-powered data automation and dashboard generation pipeline. Features a clean Tkinter GUI control panel that automatically routes files, converts CSV to XLSX in batch, extracts and cleans target columns, and generates Excel dashboards with statistical summary cards and line charts[cite: 4].

---

## ✨ Key Features

- **📁 Smart File Routing & Format Conversion**
  - Automatically routes files by extension upon import (`.csv` ➔ `input/` | `.xlsx` ➔ `convert/`).
  - Automatically detects table header offsets and converts CSV files into clean Excel (`.xlsx`) workbooks[cite: 1, 4].

- **🧹 Data Cleaning & Original Data Protection**
  - **Non-destructive**: Preserves original worksheets (`Raw_Data`) and unmodified original headers[cite: 1, 4].
  - Cleans empty rows and invalid fields, saving filtered data into a separate sheet (`Cleaned_Data`)[cite: 4].

- **📈 Automated Dashboard & Trend Visualization**
  - Built with `openpyxl` to automatically build data dashboards[cite: 4].
  - **Summary Cards**: Computes summary statistics including Count, Average, Max, and Min for numeric columns[cite: 4].
  - **Dynamic Charts**: Automatically creates line charts for numerical trends[cite: 4].

- **🖥️ Thread-Safe Execution & Progress Management**
  - Easy-to-use desktop GUI built with Tkinter.
  - Supports both single-step debugging and one-click full pipeline execution.
  - **Interrupt Control**: Thread-safe subprocess handling with `threading.Event`, enabling safe process interruption at any time without freezing the UI.

---

## 📂 Project Structure

```text
.
├── main_gui.py             # GUI Control Panel (Main Entrance)
├── convert_data.py         # Step 1: CSV to XLSX conversion script
├── extract_clean_data.py   # Step 2: Data extraction and cleaning script
├── run_dashboard.py        # Step 3: Dashboard and chart generation script
│
├── input/                  # [Auto-created] Directory for initial CSV files
├── convert/                # [Auto-created] Directory for converted XLSX files
├── extract/                # [Auto-created] Directory for cleaned data Excel files
└── board/                  # [Auto-created] Directory for final generated Excel Dashboards
