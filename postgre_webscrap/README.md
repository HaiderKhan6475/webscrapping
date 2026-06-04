# 🐘 postgre_webscrap — Scrapy Books Scraper with PostgreSQL Storage

A fully implemented **Scrapy web scraping project** that crawls all 50 pages of [books.toscrape.com](https://books.toscrape.com), extracts structured book data, cleans it through a two-stage item pipeline, and stores every record into a **PostgreSQL relational database** using `psycopg2`.

> ✅ **This is the completed version** of the PostgreSQL scraper — all components are fully written and active, unlike the earlier skeleton. The spider, both pipelines, and settings are all properly configured and ready to run.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Data Fields](#-data-fields)
- [Item Pipeline Architecture](#-item-pipeline-architecture)
- [Spider Details](#-spider-details)
- [CSS Selectors Explained](#-css-selectors-explained)
- [Settings & Configuration](#-settings--configuration)
- [PostgreSQL Database Structure](#-postgresql-database-structure)
- [Requirements](#-requirements)
- [Installation & Setup](#-installation--setup)
- [PostgreSQL Setup](#-postgresql-setup)
- [Running the Spider](#-running-the-spider)
- [Verifying the Data](#-verifying-the-data)
- [Pipeline Flow Diagram](#-pipeline-flow-diagram)
- [Comparison With Other Projects in the Series](#-comparison-with-other-projects-in-the-series)
- [Known Issues & Tips](#-known-issues--tips)

---

## 🔍 Project Overview

This project demonstrates how to integrate **Scrapy with PostgreSQL** — a production-grade, server-based relational database. It is the most advanced database backend in this scraping series, combining:

- A fully functional spider that crawls **all 1,000 books** across 50 pages
- A **data cleaning pipeline** that normalises price, rating, and availability
- A **PostgreSQL pipeline** that connects via `psycopg2` and inserts each record into a structured SQL table

The target website [books.toscrape.com](https://books.toscrape.com) is a public sandbox designed for scraping practice.

---

## 📁 Project Structure

```
postgre_webscrap/
│
├── scrapy.cfg                                  # Scrapy deployment configuration
│
└── postgre_webscrap/
    ├── __init__.py
    ├── items.py                                # ✅ Item model — 5 fields defined
    ├── middlewares.py                          # Auto-generated (not customised)
    ├── pipelines.py                            # ✅ Both pipelines fully implemented
    ├── settings.py                             # ✅ ITEM_PIPELINES active
    │
    └── spiders/
        ├── __init__.py
        └── books.py                            # ✅ Full spider with pagination
```

> **Note:** No `.db`, `.csv`, or data files are included — all scraped data is sent directly to the running PostgreSQL server.

---

## ⚙️ How It Works

```
1. Spider starts at https://books.toscrape.com/
2. Selects all 20 book blocks per page using CSS selector
3. Extracts 5 fields from each book: title, price, rating, availability, image_url
4. Follows the "Next" page link — repeats across all 50 pages
5. Each scraped item passes through two pipelines in order:
   a. BookscraperPipeline (priority 300) → cleans raw data
   b. PostgresPipeline    (priority 500) → inserts into PostgreSQL
6. ~1,000 rows are stored in the scraped_books table
```

---

## 📊 Data Fields

Defined in `items.py` using `PostgresWebscrapItem(scrapy.Item)`:

| Field | Raw Value (from website) | After Cleaning (stored in PostgreSQL) |
|---|---|---|
| `title` | `A Light in the ...` | `A Light in the ...` (unchanged) |
| `price` | `£51.77` | `51.77` (NUMERIC, £ removed) |
| `rating` | `Three` | `three` (lowercased) |
| `availability` | ` In stock ` | `In stock` (whitespace stripped) |
| `image_url` | `media/cache/2c/da/...jpg` | `https://books.toscrape.com/media/cache/...jpg` (full URL) |

---

## 🔧 Item Pipeline Architecture

### Pipeline 1 — `BookscraperPipeline` (Priority: 300)

**File:** `pipelines.py`

Runs **first** — cleans raw data before it is sent to PostgreSQL.

**What it does:**

- **Price:** Strips `£` symbol and converts to Python `float`. e.g. `"£51.77"` → `51.77`
- **Rating:** Converts to lowercase. e.g. `"Three"` → `"three"`
- **Availability:** Strips leading/trailing whitespace. e.g. `" In stock "` → `"In stock"`

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

### Pipeline 2 — `PostgresPipeline` (Priority: 500)

**File:** `pipelines.py`

Runs **second** — connects to PostgreSQL and inserts each cleaned item.

**What it does:**

- **`__init__`:** Connects to PostgreSQL via `psycopg2.connect()` using `localhost:5432`, database `postgres_books_db`. Also creates the `scraped_books` table using `CREATE TABLE IF NOT EXISTS` — so the table is auto-created on first run.
- **`process_item`:** Inserts one row per item using a parameterised `INSERT INTO` query and commits the transaction immediately.
- **`close_spider`:** Closes both the cursor and the connection cleanly when the spider finishes.

```python
class PostgresPipeline:

    def __init__(self):
        self.connection = psycopg2.connect(
            host="localhost",
            database="postgres_books_db",
            user="postgres",
            password="P0stgree45",   # ← Update with your password
            port="5432",
        )
        self.cur = self.connection.cursor()

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS scraped_books(
                id           SERIAL PRIMARY KEY,
                title        VARCHAR(500),
                price        NUMERIC(10, 2),
                rating       VARCHAR(50),
                availability VARCHAR(100),
                image_url    TEXT
            );
        """)
        self.connection.commit()

    def process_item(self, item, spider):
        self.cur.execute("""
            INSERT INTO scraped_books (title, price, rating, availability, image_url)
            VALUES (%s, %s, %s, %s, %s);
        """, (
            item.get("title"),
            item.get("price"),
            item.get("rating"),
            item.get("availability"),
            item.get("image_url"),
        ))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
```

> **Key difference from MongoDB pipeline:** This pipeline uses `close_spider()` to explicitly close the database connection, following SQL best practices. The MongoDB pipeline relied on Python's garbage collector — this is more reliable for production use.

---

## 🕷️ Spider Details

**File:** `spiders/books.py`
**Spider name:** `books`

```
Target URL   : https://books.toscrape.com/
Domain       : books.toscrape.com
Item class   : PostgresWebscrapItem
Fields       : title, price, rating, availability, image_url
Pagination   : Automatic (follows li.next a)
Items/page   : 20 books
Total pages  : 50
Total items  : ~1,000 books
```

---

## 🔍 CSS Selectors Explained

| Field | CSS Selector | Method | Notes |
|---|---|---|---|
| Book container | `article.product_pod` | `.css()` | Selects all 20 book blocks per page |
| Title | `h3 a::text` | `.get()` | Truncated on listing page |
| Price | `.price_color::text` | `.get()` | Includes £ symbol — cleaned in pipeline |
| Image URL | `img.thumbnail::attr(src)` | `.get()` | Relative path — resolved via `urljoin()` |
| Rating | `p.star-rating::attr(class)` | `.get()` | Returns `"star-rating Three"` — stripped in spider |
| Availability | `p.instock.availability::text` | `.getall()` | Text split across nodes — joined + stripped |
| Next page | `li.next a::attr(href)` | `.get()` | Returns `None` on last page — stops pagination |

**Rating extraction detail:**
The star rating is encoded as a CSS class: `class="star-rating Three"`. The spider strips `"star-rating"` to extract just `"Three"`, then the pipeline lowercases it to `"three"`.

**Image URL resolution:**
`response.urljoin(relative_url)` converts the relative path `media/cache/2c/da/...jpg` into the full URL `https://books.toscrape.com/media/cache/2c/da/...jpg`, ensuring all image links are valid regardless of which page they come from.

---

## 🛠️ Settings & Configuration

**File:** `settings.py`

| Setting | Value | Purpose |
|---|---|---|
| `BOT_NAME` | `postgre_webscrap` | Project bot name |
| `SPIDER_MODULES` | `["postgre_webscrap.spiders"]` | Spider discovery path |
| `ROBOTSTXT_OBEY` | `True` | Respects robots.txt |
| `CONCURRENT_REQUESTS_PER_DOMAIN` | `1` | One request at a time |
| `DOWNLOAD_DELAY` | `1` | 1 second between requests (polite crawl) |
| `FEED_EXPORT_ENCODING` | `utf-8` | Encoding for optional CSV/JSON exports |

**Active pipelines (fully enabled):**

```python
ITEM_PIPELINES = {
    "postgre_webscrap.pipelines.BookscraperPipeline": 300,  # Runs first — cleans
    "postgre_webscrap.pipelines.PostgresPipeline": 500,     # Runs second — stores
}
```

> Unlike the previous skeleton version, `ITEM_PIPELINES` here is **uncommented and active**.

---

## 🗄️ PostgreSQL Database Structure

```
PostgreSQL Server (localhost:5432)
└── Database : postgres_books_db
    └── Table: scraped_books
        ├── Row 1: { id, title, price, rating, availability, image_url }
        ├── Row 2: { id, title, price, rating, availability, image_url }
        └── ... (~1,000 rows)
```

**Table schema (auto-created by the pipeline):**

```sql
CREATE TABLE IF NOT EXISTS scraped_books (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(500),
    price        NUMERIC(10, 2),
    rating       VARCHAR(50),
    availability VARCHAR(100),
    image_url    TEXT
);
```

**Column details:**

| Column | PostgreSQL Type | Description |
|---|---|---|
| `id` | `SERIAL PRIMARY KEY` | Auto-incrementing unique ID |
| `title` | `VARCHAR(500)` | Book title (up to 500 characters) |
| `price` | `NUMERIC(10, 2)` | Price as decimal — e.g. `51.77` |
| `rating` | `VARCHAR(50)` | Star rating word — e.g. `three` |
| `availability` | `VARCHAR(100)` | Stock status — e.g. `In stock` |
| `image_url` | `TEXT` | Full image URL (unlimited length) |

> **`NUMERIC(10, 2)` vs `FLOAT`:** This project uses `NUMERIC(10, 2)` for price, which stores exact decimal values (no floating-point rounding errors). This is the correct choice for monetary data — better than using `FLOAT`.

---

## 📦 Requirements

```
scrapy
psycopg2-binary
```

Install:

```bash
pip install scrapy psycopg2-binary
```

**System requirement:**
- PostgreSQL server installed and running (default port: `5432`)

---

## 🚀 Installation & Setup

**1. Extract the project:**

```bash
unzip postgre_webscrap.zip
cd postgre_webscrap
```

**2. Create a virtual environment (recommended):**

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

**3. Install dependencies:**

```bash
pip install scrapy psycopg2-binary
```

**4. Update database credentials in `pipelines.py`:**

Open `postgre_webscrap/pipelines.py` and update these lines in `PostgresPipeline.__init__()`:

```python
self.connection = psycopg2.connect(
    host="localhost",
    database="postgres_books_db",   # Must match the DB you created
    user="postgres",                # Your PostgreSQL username
    password="P0stgree45",          # ← Change this to your actual password
    port="5432",
)
```

**5. Verify spider is found:**

```bash
scrapy list
# Expected output: books
```

---

## 🐘 PostgreSQL Setup

The PostgreSQL server **must be running** before starting the spider.

### Install PostgreSQL

**Windows:**
Download from [postgresql.org/download/windows](https://www.postgresql.org/download/windows). During setup, note the password you set for the `postgres` user.

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Create the Database

Open the PostgreSQL shell and create the database:

```bash
psql -U postgres
```

```sql
CREATE DATABASE postgres_books_db;

-- Optional: create a dedicated user
CREATE USER scraper WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE postgres_books_db TO scraper;

\q
```

### Verify Connection

```bash
psql -U postgres -d postgres_books_db
# Successfully connected = ready to run the spider
```

> **Note:** The `scraped_books` table does **not** need to be created manually — the `PostgresPipeline.__init__()` method runs `CREATE TABLE IF NOT EXISTS` automatically when the spider starts.

---

## ▶️ Running the Spider

Once PostgreSQL is running and credentials are set:

```bash
scrapy crawl books
```

This will:
- Crawl all 50 pages of `books.toscrape.com`
- Clean each item (price, rating, availability)
- Insert ~1,000 rows into `postgres_books_db.scraped_books`

**Optional — also save to CSV:**

```bash
scrapy crawl books -o output.csv
```

---

## ✅ Verifying the Data

### Via psql shell

```bash
psql -U postgres -d postgres_books_db

-- Check total rows
SELECT COUNT(*) FROM scraped_books;

-- View first 10 rows
SELECT * FROM scraped_books LIMIT 10;

-- Cheapest 5 books
SELECT title, price FROM scraped_books ORDER BY price ASC LIMIT 5;

-- Most expensive 5 books
SELECT title, price FROM scraped_books ORDER BY price DESC LIMIT 5;

-- Average price
SELECT ROUND(AVG(price), 2) AS avg_price FROM scraped_books;

-- Rating distribution
SELECT rating, COUNT(*) FROM scraped_books GROUP BY rating ORDER BY COUNT(*) DESC;

-- All five-star books
SELECT title, price FROM scraped_books WHERE rating = 'five';

-- Books under £15
SELECT title, price FROM scraped_books WHERE price < 15 ORDER BY price;
```

### Via Python

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="postgres_books_db",
    user="postgres",
    password="P0stgree45"
)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM scraped_books;")
print("Total books:", cur.fetchone()[0])

cur.execute("SELECT title, price, rating FROM scraped_books LIMIT 5;")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
```

---

## 🔄 Pipeline Flow Diagram

```
books.toscrape.com
        │
        ▼
  [BooksSpider]
  Extracts 20 items per page
  Follows pagination (50 pages total)
  Uses PostgresWebscrapItem
        │
        ▼  (yields PostgresWebscrapItem)
        │
  ┌───────────────────────────────┐
  │     BookscraperPipeline       │  Priority: 300  ← Runs FIRST
  │  ✔ "£51.77"  →  51.77 float  │
  │  ✔ "Three"   →  "three"      │
  │  ✔ " In stock " → stripped   │
  └──────────────┬────────────────┘
                 │
  ┌──────────────▼────────────────┐
  │       PostgresPipeline        │  Priority: 500  ← Runs SECOND
  │  ✔ psycopg2 connect           │
  │  ✔ CREATE TABLE IF NOT EXISTS │
  │  ✔ INSERT INTO scraped_books  │
  │  ✔ connection.commit()        │
  │  ✔ close_spider → conn.close  │
  └───────────────────────────────┘
                 │
                 ▼
    PostgreSQL Server (port 5432)
    Database  : postgres_books_db
    Table     : scraped_books
    ~1,000 rows ✅
```

---

## 📊 Comparison With Other Projects in the Series

| Feature | `bookscraper` | `item_pipeline` | `mongodb_webscrap` | `postgre_webscrap` |
|---|---|---|---|---|
| Fields scraped | 2 | 5 | 5 | 5 |
| Pagination | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| Item class | ❌ dict | ✅ Yes | ✅ Yes | ✅ Yes |
| Cleaning pipeline | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| Storage | CSV only | SQLite file | MongoDB server | PostgreSQL server |
| Library | — | `sqlite3` (built-in) | `pymongo` | `psycopg2` |
| Server required | ❌ No | ❌ No | ✅ Yes (27017) | ✅ Yes (5432) |
| Schema type | — | Relational (SQL) | Schema-less (NoSQL) | Relational (SQL) |
| Price column type | — | `REAL` | float (Python) | `NUMERIC(10,2)` |
| `close_spider` used | — | ✅ Yes | ❌ No | ✅ Yes |
| Status | ✅ Complete | ✅ Complete | ✅ Complete | ✅ Complete |

---

## 🐛 Known Issues & Tips

**1. Update credentials before running**

The pipeline has hardcoded credentials (`user="postgres"`, `password="P0stgree45"`). These must be updated in `pipelines.py` to match your local PostgreSQL setup, or the spider will fail with an authentication error.

**2. Database must exist before running**

The pipeline creates the **table** automatically, but the **database** (`postgres_books_db`) must be created manually in PostgreSQL first. Running the spider without creating the database first will raise:
```
psycopg2.OperationalError: FATAL: database "postgres_books_db" does not exist
```

**3. Duplicate records on re-run**

Each run inserts another ~1,000 rows. There is no `ON CONFLICT` or duplicate check. To clear before a fresh run:
```sql
TRUNCATE TABLE scraped_books RESTART IDENTITY;
```
Or to prevent duplicates entirely, add a unique constraint:
```sql
ALTER TABLE scraped_books ADD CONSTRAINT unique_title UNIQUE (title);
```
And change the insert to:
```sql
INSERT INTO scraped_books (...) VALUES (...) ON CONFLICT (title) DO NOTHING;
```

**4. `NUMERIC(10, 2)` is better than `FLOAT` for price**

Unlike the SQLite version which used `REAL`, this project correctly uses `NUMERIC(10, 2)` — which stores exact decimal values with no floating-point rounding errors. This matters for monetary data.

**5. Credentials should not be hardcoded in production**

For real projects, move database credentials to environment variables or a config file:
```python
import os
self.connection = psycopg2.connect(
    host=os.environ.get("PG_HOST", "localhost"),
    database=os.environ.get("PG_DB", "postgres_books_db"),
    user=os.environ.get("PG_USER", "postgres"),
    password=os.environ.get("PG_PASSWORD"),
    port=os.environ.get("PG_PORT", "5432"),
)
```

**6. No `check_postgres.py` verification script**

Unlike the SQLite project (`check_db.py`) and MongoDB project (`check_mongo.py`), this project has no utility script to verify data after a run. Use `psql` shell queries or the Python snippet in the [Verifying the Data](#-verifying-the-data) section above.

---

## 📝 License

This project is intended for **educational purposes**. The target website `books.toscrape.com` is a scraping practice sandbox with no real commercial data.
