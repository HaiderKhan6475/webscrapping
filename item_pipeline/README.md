# 📚 item_pipeline — Scrapy Books Scraper with SQLite Storage

A fully functional **Scrapy web scraping project** that crawls [books.toscrape.com](https://books.toscrape.com), extracts structured book data, cleans it through a custom item pipeline, and persists it into a local **SQLite database**. Optionally, data can also be exported to CSV format.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Data Fields](#-data-fields)
- [Item Pipeline Architecture](#-item-pipeline-architecture)
- [Spider Details](#-spider-details)
- [Settings & Configuration](#-settings--configuration)
- [Database Schema](#-database-schema)
- [Output Files](#-output-files)
- [Requirements](#-requirements)
- [Installation & Setup](#-installation--setup)
- [Running the Spider](#-running-the-spider)
- [Verifying the Database](#-verifying-the-database)
- [Exporting to CSV](#-exporting-to-csv)
- [Scrapy Pipeline Flow Diagram](#-scrapy-pipeline-flow-diagram)
- [Known Issues & Tips](#-known-issues--tips)

---

## 🔍 Project Overview

This project demonstrates the use of **Scrapy Item Pipelines** — the mechanism Scrapy uses to post-process scraped data. Instead of dumping raw, messy data directly to a file, the pipeline:

1. **Cleans** the data (removes currency symbols, normalises text casing)
2. **Stores** the cleaned data into a **SQLite relational database**

The target website, [books.toscrape.com](https://books.toscrape.com), is a publicly available sandbox site designed specifically for web scraping practice. It contains **1,000 books** spread across **50 pages**.

---

## 📁 Project Structure

```
item_pipeline/
│
├── scrapy.cfg                          # Scrapy deployment configuration
│
└── item_pipeline/
    ├── __init__.py
    ├── items.py                        # Scrapy Item definition (data model)
    ├── middlewares.py                  # Scrapy spider & downloader middlewares
    ├── pipelines.py                    # Item pipeline: cleaning + SQLite storage
    ├── settings.py                     # Project-wide Scrapy settings
    ├── books_data.db                   # SQLite database (generated after crawl)
    ├── check_db.py                     # Utility script to verify database contents
    │
    └── spiders/
        ├── __init__.py
        ├── books.py                    # Main spider that crawls books.toscrape.com
        ├── books_data.db               # SQLite DB copy inside spiders/ folder
        ├── item_pipeline_data.csv      # CSV export (1,000 records)
        ├── item_pipeline_data2.csv     # CSV export variant 2 (1,000 records)
        ├── item_pipeline_data3.csv     # CSV export variant 3 (empty)
        └── item_pipeline_data4.csv     # CSV export variant 4 (1,000 records)
```

---

## ⚙️ How It Works

The spider visits `https://books.toscrape.com/` and for each book on the page, extracts:

- Title
- Price (raw, e.g. `£51.77`)
- Star rating (as word, e.g. `Three`)
- Availability (e.g. `In stock`)
- Thumbnail image URL

It then **follows the "next page" link** automatically, repeating this process across all 50 pages until all 1,000 books have been collected.

Each scraped item passes through **two pipelines** in sequence:

| Order | Pipeline Class          | Responsibility                                 |
|-------|-------------------------|------------------------------------------------|
| 300   | `BookscraperPipeline`   | Cleans and normalises the raw data             |
| 400   | `SQLitePipeline`        | Inserts the cleaned data into SQLite database  |

---

## 📊 Data Fields

Defined in `items.py` using `scrapy.Item`:

| Field          | Type    | Raw Example                                      | After Cleaning         |
|----------------|---------|--------------------------------------------------|------------------------|
| `title`        | Text    | `A Light in the ...`                             | Unchanged              |
| `price`        | Float   | `£51.77`                                         | `51.77`                |
| `rating`       | Text    | `Three`                                          | `three`                |
| `availability` | Text    | ` In stock ` (with whitespace)                   | `In stock`             |
| `image_url`    | Text    | `media/cache/2c/da/2cdad67c...jpg`               | Unchanged (full URL)   |

---

## 🔧 Item Pipeline Architecture

### Pipeline 1 — `BookscraperPipeline` (Priority: 300)

Defined in `pipelines.py`. Runs **first** on every scraped item.

**Responsibilities:**

- **Price cleaning**: Strips the `£` (pound) symbol from the price string and converts it to a Python `float`. For example, `"£51.77"` becomes `51.77`.
- **Rating normalisation**: Converts the word-based rating (e.g. `"Three"`) to lowercase (`"three"`) for consistent querying.
- **Availability cleanup**: Strips any leading/trailing whitespace from the availability field.

```python
class BookscraperPipeline:
    def process_item(self, item, spider):
        price_str = item.get("price")
        if price_str:
            item["price"] = float(price_str.replace("£", ""))

        rating_str = item.get("rating")
        if rating_str:
            item["rating"] = rating_str.lower()

        avail_str = item.get("availability")
        if avail_str:
            item["availability"] = avail_str.strip()

        return item
```

---

### Pipeline 2 — `SQLitePipeline` (Priority: 400)

Runs **second**, after the data has been cleaned by `BookscraperPipeline`.

**Responsibilities:**

- Opens a connection to `books_data.db` in the same directory as `pipelines.py`
- On spider open (`open_spider`): Creates the `books` table if it doesn't exist
- On each item (`process_item`): Inserts one row into the `books` table
- On spider close (`close_spider`): Closes the database connection

**Database path resolution** uses `os.path.abspath(__file__)` to ensure the `.db` file is always created relative to the pipeline file, regardless of where `scrapy crawl` is invoked from.

---

## 🕷️ Spider Details

**File:** `item_pipeline/spiders/books.py`
**Spider name:** `books`

```
Target URL  : https://books.toscrape.com/
Domain      : books.toscrape.com
Pagination  : Follows <li class="next"> link automatically
Items/page  : 20 books
Total pages : 50
Total items : ~1,000 books
```

**CSS Selectors used:**

| Data Point    | CSS Selector                              |
|---------------|-------------------------------------------|
| Book container| `article.product_pod`                     |
| Title         | `h3 a::text`                              |
| Price         | `.price_color::text`                      |
| Image URL     | `img.thumbnail::attr(src)`                |
| Rating        | `p.star-rating::attr(class)`              |
| Availability  | `p.instock.availability::text`            |
| Next page     | `li.next a::attr(href)`                   |

**Rating extraction logic:**  
The rating is encoded as a CSS class on the `<p>` element, e.g. `class="star-rating Three"`. The spider extracts the full class string and strips the `"star-rating"` prefix to get just `"Three"`.

---

## 🛠️ Settings & Configuration

**File:** `item_pipeline/settings.py`

| Setting                          | Value                              | Purpose                                         |
|----------------------------------|------------------------------------|-------------------------------------------------|
| `BOT_NAME`                       | `item_pipeline`                    | Project bot name                                |
| `SPIDER_MODULES`                 | `["item_pipeline.spiders"]`        | Where Scrapy looks for spiders                  |
| `ROBOTSTXT_OBEY`                 | `True`                             | Respects robots.txt (ethical scraping)          |
| `CONCURRENT_REQUESTS_PER_DOMAIN` | `1`                                | Only 1 request at a time per domain             |
| `DOWNLOAD_DELAY`                 | `1`                                | 1 second delay between requests (polite crawl)  |
| `FEED_EXPORT_ENCODING`           | `utf-8`                            | Ensures proper encoding in CSV/JSON exports     |
| `ITEM_PIPELINES`                 | See below                          | Activates both pipeline classes                 |

**Active pipelines (from settings.py):**

```python
ITEM_PIPELINES = {
    "item_pipeline.pipelines.BookscraperPipeline": 300,
    "item_pipeline.pipelines.SQLitePipeline": 400,
}
```

> Lower priority numbers run **first**. `BookscraperPipeline` (300) cleans the data before `SQLitePipeline` (400) saves it.

---

## 🗄️ Database Schema

**Database file:** `item_pipeline/books_data.db` (SQLite)

**Table:** `books`

| Column         | Type    | Constraints              | Description                          |
|----------------|---------|--------------------------|--------------------------------------|
| `id`           | INTEGER | PRIMARY KEY AUTOINCREMENT| Auto-incremented unique identifier   |
| `title`        | TEXT    | —                        | Book title                           |
| `price`        | REAL    | —                        | Price as a float (e.g. `51.77`)      |
| `rating`       | TEXT    | —                        | Star rating in lowercase words       |
| `availability` | TEXT    | —                        | Stock status (e.g. `In stock`)       |
| `image_url`    | TEXT    | —                        | Full URL to the book's thumbnail     |

**SQL used to create the table:**

```sql
CREATE TABLE IF NOT EXISTS books (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT,
    price        REAL,
    rating       TEXT,
    availability TEXT,
    image_url    TEXT
);
```

---

## 📄 Output Files

| File                                        | Records | Notes                                          |
|---------------------------------------------|---------|------------------------------------------------|
| `item_pipeline/books_data.db`               | ~1,000  | Primary SQLite database (main output)          |
| `spiders/books_data.db`                     | ~1,000  | Duplicate DB created from spider directory run |
| `spiders/item_pipeline_data.csv`            | 1,000   | CSV export with raw data (price as string)     |
| `spiders/item_pipeline_data2.csv`           | 1,000   | Second CSV run                                 |
| `spiders/item_pipeline_data3.csv`           | 0       | Empty — likely an interrupted run              |
| `spiders/item_pipeline_data4.csv`           | 1,000   | Fourth CSV run                                 |

> **Note:** CSV files contain the **raw scraped data** (e.g. price includes `£` symbol), while the SQLite database stores the **cleaned data** (price as float, rating lowercased).

---

## 📦 Requirements

- Python 3.8+
- Scrapy 2.x or higher

Install dependencies:

```bash
pip install scrapy
```

No other external libraries are required. The project uses only Python's built-in `sqlite3` and `os` modules for database operations.

---

## 🚀 Installation & Setup

**1. Clone or unzip the project:**

```bash
unzip item_pipeline.zip
cd item_pipeline
```

**2. (Optional) Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

**3. Install Scrapy:**

```bash
pip install scrapy
```

**4. Verify the project structure:**

```bash
scrapy list
# Expected output: books
```

---

## ▶️ Running the Spider

From the root of the project (where `scrapy.cfg` is located), run:

```bash
scrapy crawl books
```

This will:
- Start crawling `https://books.toscrape.com/`
- Follow all 50 pages automatically
- Clean each item via `BookscraperPipeline`
- Store all ~1,000 books in `item_pipeline/books_data.db`

**Optional — Export to CSV simultaneously:**

```bash
scrapy crawl books -o output.csv
```

**Optional — Export to JSON:**

```bash
scrapy crawl books -o output.json
```

---

## ✅ Verifying the Database

After the spider finishes, run the built-in verification script:

```bash
cd item_pipeline
python check_db.py
```

**Expected output:**

```
Dhoond raha hoon database ko yahan: /path/to/item_pipeline/books_data.db

--- DATABASE DATA ---
ID: 1 | Title: A Light in the ... | Price: 51.77 | Rating: three
ID: 2 | Title: Tipping the Velvet | Price: 53.74 | Rating: one
ID: 3 | Title: Soumission        | Price: 50.1  | Rating: one
ID: 4 | Title: Sharp Objects     | Price: 47.82 | Rating: four
ID: 5 | Title: Sapiens: A Brief  | Price: 54.23 | Rating: five
```

You can also inspect the database directly using the SQLite CLI:

```bash
sqlite3 item_pipeline/books_data.db

-- Inside sqlite3 shell:
.tables
SELECT COUNT(*) FROM books;
SELECT * FROM books LIMIT 10;
SELECT * FROM books WHERE rating = 'five';
SELECT * FROM books ORDER BY price ASC LIMIT 5;
.quit
```

---

## 📤 Exporting to CSV

While the primary storage is SQLite, you can export all data from the database to CSV at any time using Python:

```python
import sqlite3
import csv

con = sqlite3.connect("item_pipeline/books_data.db")
cur = con.cursor()
cur.execute("SELECT * FROM books")

with open("exported_books.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "title", "price", "rating", "availability", "image_url"])
    writer.writerows(cur.fetchall())

con.close()
print("Export complete.")
```

---

## 🔄 Scrapy Pipeline Flow Diagram

```
books.toscrape.com
        │
        ▼
  [BooksSpider]
  Extracts 20 items per page
  Follows pagination (50 pages)
        │
        ▼  (yields ItemPipelineItem)
        │
  ┌─────────────────────────┐
  │  BookscraperPipeline    │  Priority: 300
  │  - Strip £ from price   │
  │  - Convert price→float  │
  │  - Lowercase rating     │
  │  - Strip availability   │
  └────────────┬────────────┘
               │
  ┌────────────▼────────────┐
  │    SQLitePipeline       │  Priority: 400
  │  - Connect to .db       │
  │  - CREATE TABLE IF ...  │
  │  - INSERT INTO books    │
  │  - Commit & close       │
  └─────────────────────────┘
               │
               ▼
       books_data.db (SQLite)
       ~1,000 rows stored
```

---

## 🐛 Known Issues & Tips

**1. Duplicate records on re-run**  
The `SQLitePipeline` uses `CREATE TABLE IF NOT EXISTS` but does not check for duplicate entries before inserting. Running `scrapy crawl books` multiple times will **duplicate** all records. To avoid this, either:
- Delete the `books_data.db` file before each run, or
- Add a `UNIQUE` constraint on the `title` column and use `INSERT OR IGNORE`

**2. Image URLs are relative on page 1, absolute on subsequent pages**  
Page 1 image URLs look like `media/cache/.../image.jpg` while later pages return `../media/cache/.../image.jpg`. The spider uses `response.urljoin(relative_url)` to resolve them into full absolute URLs — this is handled correctly.

**3. Empty CSV file (`item_pipeline_data3.csv`)**  
This was likely produced by an interrupted crawl run. It is safe to delete.

**4. Two `books_data.db` files**  
There is one database inside `item_pipeline/` and another inside `item_pipeline/spiders/`. Both are generated by the same spider; the one in `item_pipeline/` is the correct/primary one (created by `pipelines.py` using `os.path.abspath(__file__)`). The one in `spiders/` may have been created by running the spider from a different working directory.

**5. Politeness settings**  
The project is configured with `DOWNLOAD_DELAY = 1` and `CONCURRENT_REQUESTS_PER_DOMAIN = 1`. This ensures the spider is respectful to the server and does not hammer it with rapid requests. Do not remove these settings when scraping production websites.

---

## 📝 License

This project is intended for **educational purposes**. The target website [books.toscrape.com](https://books.toscrape.com) is a sandbox scraping site with no real commercial data.
