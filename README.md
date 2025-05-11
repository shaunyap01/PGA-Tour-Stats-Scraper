# PGA Tour Stats Scraper 🏌️‍♂️📊

**A powerful Python tool for scraping ‘Tournament Only’ statistics from all PGA Tour events (2004–Present).**

---

## 📌 Overview

The **PGA Tour Stats Scraper** allows golf enthusiasts, data analysts, and developers to automatically download detailed tournament-level statistics for all tournaments and any stat category from the [PGA Tour website](https://www.pgatour.com/stats) dating back to **2004**.

It supports:
- 📆 Year-based scraping (e.g., 2010–2025)
- 🗓️ Date-range scraping (e.g., 2025-01-01 to 2025-03-31)
- 📑 Full stat category support with customisable stat codes
- 🧠 Jupyter Notebook version for exploration and visualisation

---

## 📂 Repository Contents

| File | Description |
|------|-------------|
| `PGA Tour Event Stats Scraper.py` | Scrapes statistics for specified **calendar years** |
| `PGA Tour Event Stats Between Scraper.py` | Scrapes data for specific **date ranges** (YYYY-MM-DD) to (YYYY-MM-DD). Use this to keep data updated |
| `Master Webscrape PGA Tour Stats.ipynb` | Interactive **Jupyter Notebook** for scraping and analysis |
| `Full List of PGA Tour Stats and Correlating Codes.md` | Reference list of all stat categories and their corresponding codes |
| `PGA Tour Event Stats/` | Folder containing compressed **complete scapred data** (as of present [2025-05-01]) |

---

## 📥 Installation

Clone the repository and install required dependencies:

```bash
git clone https://github.com/shaunyap01/PGA-Tour-Stats-Scraper.git
cd PGA-Tour-Stats-Scraper
pip install -r requirements.txt
```

**Requirements:**
- `pandas`
- `requests`
- `python-dateutil` (if used in notebook)

---

## How to Use

### Option 1: Scrape by Year (Calendar Year)

```bash
python "PGA Tour Event Stats Scraper.py"
```

- Edit the `YEARS` list in the script to your desired years.
- All stats are saved under `PGA Tour Event Stats/`.

#### 📁 File Structure

```bash
📂 PGA Tour Event Stats/
└── 2025/
    └── 2025-03-13, Masters Tournament/
        └── Scoring/
            └── Scoring Overall/
                └── 2025-03-14, Scoring Average.csv
```

---

### Option 2: Scrape by Date Range (YYYY-MM-DD)

```bash
python "PGA Tour Event Stats Between Scraper.py"
```

- Modify the script to include your `start_date` and `end_date`.
- By default, data is saved in PGA Tour Event Stats/, but this can be changed:

```python
# BASE_DIR = Path("PGA Tour Event Stats Between")   # Uncomment to save in a separate folder
BASE_DIR = Path("PGA Tour Event Stats")             # Default: saves to main folder
```

#### 📁 File Structure

```bash
📂 PGA Tour Event Stats/
└── 2025/
    └── 2025-03-13, Masters Tournament/
        └── Scoring/
            └── Scoring Overall/
                └── 2025-03-14, Scoring Average.csv
```

---

### Option 3: Use Jupyter Notebook

Open `Master Webscrape PGA Tour Stats.ipynb` to run and explore scrapes using code cells. Supports:
- Scraping by year (via embedded version of `PGA Tour Event Stats Scraper.py`)
- Scraping by date range (via embedded version of `PGA Tour Event Stats Between Scraper.py`)

Ideal for exploratory work or first-time users.
---

## 📚 Stat Codes Reference

All supported stats and their respective **IDs** are catalogued in:

📁 `Full List of PGA Tour Stats and Correlating Codes.md`

> New stats added? Add any stat code to the relevant script to include it in the scrape.
> Some stats (e.g., “Rounds in the 60s”) are excluded due to no available Tournament-Only data. More information can be found in `Full List of PGA Tour Stats and Correlating Codes.md`.

---

## ⚠️ Notes & Limitations

- Certain events (e.g., **The Masters**) may lack detailed stats as they do not use the **ShotLink** system.
- Tenth Tee start stats may be unavailable for Tournaments and rounds where no groups started on hole 10.

---

## 👨‍💻 Author

**Shaun**  
MSc Data Science & Statistics  
[GitHub](https://github.com/shaunyap01) | [Personal Website](https://shaunyap01.github.io) | [LinkedIn](https://www.linkedin.com/in/shaunyap0122)

Read more about this project: [shaunyap01.github.io/projects/pga-tour-stats-scraper](https://shaunyap01.github.io/projects/pga-tour-stats-scraper)
Browse other projects and articles: [shaunyap01.github.io](https://shaunyap01.github.io)

Saved some money using this instead of buying data elsewhere?
Consider [supporting via Buy Me a Coffee](https://buymeacoffee.com/shaunyap01) - thank you!

---