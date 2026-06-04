# 🐘 postgre_webscrap — Scrapy Books Scraper with PostgreSQL Storage (In Progress)

A **Scrapy web scraping project** scaffold set up to scrape [books.toscrape.com](https://books.toscrape.com) and store the extracted data into a **PostgreSQL relational database**.

> ⚠️ **Current Status: Work In Progress**
> This project is a **starter skeleton**. The project structure, settings, and item model have been created, but the spider logic, pipeline implementation, and PostgreSQL integration are **not yet written**. This README documents both what currently exists and what needs to be completed to make it fully functional.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Project Structure](#-project-structure)
- [Current State of Each File](#-current-state-of-each-file)
- [What Is Missing / To Be Implemented](#-what-is-missing--to-be-implemented)
- [How It Should Work (Planned Architecture)](#-how-it-should-work-planned-architecture)
- [Data Fields](#-data-fields)
- [How to Complete the Spider](#-how-to-complete-the-spider)
- [How to Complete the Pipeline](#-how-to-complete-the-pipeline)
- [How to Enable the Pipeline in Settings](#-how-to-enable-the-pipeline-in-settings)
- [PostgreSQL Setup](#-postgresql-setup)
- [Database Schema (To Be Created)](#-database-schema-to-be-created)
- [Settings & Configuration](#-settings--configuration)
- [Requirements](#-requirements)
- [Installation & Setup](#-installation--setup)
- [Running the Spider](#-running-the-spider)
- [Comparison With Previous Projects](#-comparison-with-previous-projects)
- [Known Issues & Bugs](#-known-issues--bugs)

---

## 🔍 Project Overview

This project is the **third in a series** of Scrapy pipeline projects, each using a different database backend:

| Project | Database | Status |
|---|---|---|
| `item_pipeline` | SQLite | ✅ Complete |
| `mongodb_webscrap` | MongoDB | ✅ Complete |
| `postgre_webscrap` | PostgreSQL | 🚧 Skeleton only |

The goal is to scrape book data (title, price, rating, availability, image URL) from [books.toscrape.com](https://books.toscrape.com) and store it in a **PostgreSQL** database using the `psycopg2` library. PostgreSQL is a powerful, production-grade relational database — more robust than SQLite while retaining the structured, SQL-based approach.

---

## 📁 Project Structure

```
postgre_webscrap/
│
├── scrapy.cfg                                  # Scrapy deployment configuration
│
└── postgre_webscrap/
    ├── __init__.py
    ├── items.py                                # ✅ Item model defined
    ├── middlewares.py                          # ✅ Auto-generated (unused)
    ├── pipelines.py                            # ❌ Empty — PostgreSQL logic not written
    ├── settings.py                             # ⚠️ Pipeline is commented out
    │
    └── spiders/
        ├── __init__.py
        └── books.py                            # ❌ Spider body is empty (pass)
```

---

## 📄 Current State of Each File

### ✅ `items.py` — Complete

The data model is fully defined. `PostgresWebscrapItem` has all five fields needed:

```python
class PostgresWebscrapItem(scrapy.Item):
    title        = scrapy.Field()
    price        = scrapy.Field()
    rating       = scrapy.Field()
    availability = scrapy.Field()
    image_url    = scrapy.Field()
```

---

### ❌ `spiders/books.py` — Incomplete

The spider was created with `scrapy genspider` but the `parse()` method body is empty. It also has a **bug in the domain/URL**:

```python
# Current (WRONG):
class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.books.toscrape.com"]   # ❌ Doubled "books."
    start_urls = ["https://books.books.toscrape.com"] # ❌ Wrong URL

    def parse(self, response):
        pass  # ❌ No scraping logic
```

The correct domain is `books.toscrape.com` (not `books.books.toscrape.com`).

---

### ❌ `pipelines.py` — Incomplete

The pipeline class `PostgreWebscrapPipeline` exists but `process_item()` does nothing — it just returns the item without any cleaning or database insertion:

```python
class PostgreWebscrapPipeline:
    def process_item(self, item, spider):
        return item   # ❌ No cleaning, no PostgreSQL logic
```

---

### ⚠️ `settings.py` — Pipeline Commented Out

The `ITEM_PIPELINES` section exists but is entirely commented out, meaning no pipeline will run even if the spider produces items:

```python
# ITEM_PIPELINES = {
#    "postgre_webscrap.pipelines.PostgreWebscrapPipeline": 300,
# }
```

---

## 🚧 What Is Missing / To Be Implemented

| Component | Status | What Needs to Be Done |
|---|---|---|
| Spider domain & URL | ❌ Bug | Fix `allowed_domains` and `start_urls` |
| Spider `parse()` method | ❌ Empty | Add CSS selectors and pagination logic |
| `BookscraperPipeline` | ❌ Missing | Add data cleaning (price, rating, availability) |
| `PostgreSQLPipeline` | ❌ Missing | Add `psycopg2` connection and `INSERT` logic |
| `ITEM_PIPELINES` in settings | ⚠️ Commented | Uncomment and configure |
| PostgreSQL table | ❌ Missing | Create `books` table in PostgreSQL |
| `check_postgres.py` | ❌ Missing | Add a verification utility script |

---

## 🏗️ How It Should Work (Planned Architecture)

```
books.toscrape.com
        │
        ▼
  [BooksSpider]
  CSS selectors extract book data
  Follows pagination across 50 pages
        │
        ▼  (yields PostgresWebscrapItem)
        │
  ┌──────────────────────────────┐
  │    BookscraperPipeline       │  Priority: 300
  │  ✔ Strip £ from price        │
  │  ✔ Convert price to float    │
  │  ✔ Lowercase rating          │
  │  ✔ Strip availability spaces │
  └─────────────┬────────────────┘
                │
  ┌─────────────▼────────────────┐
  │     PostgreSQLPipeline       │  Priority: 400
  │  ✔ Connect via psycopg2      │
  │  ✔ CREATE TABLE IF NOT EXISTS│
  │  ✔ INSERT INTO books         │
  │  ✔ Commit & close connection │
  └──────────────────────────────┘
                │
                ▼
    PostgreSQL Server
    Database : books_db
    Table    : books
    ~1,000 rows ✅
```

---

## 📊 Data Fields

Defined in `items.py`:

| Field | Raw Value (from website) | After Cleaning |
|---|---|---|
| `title` | `A Light in the ...` | Unchanged |
| `price` | `£51.77` | `51.77` (float, £ removed) |
| `rating` | `Three` | `three` (lowercased) |
| `availability` | ` In stock ` | `In stock` (stripped) |
| `image_url` | `media/cache/2c/da/...jpg` | Full absolute URL |

---

## 🔧 How to Complete the Spider

Replace the contents of `spiders/books.py` with:

```python
import scrapy
from postgre_webscrap.items import PostgresWebscrapItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]         # ✅ Fixed domain
    start_urls = ["https://books.toscrape.com/"]     # ✅ Fixed URL

    def parse(self, response):
        books = response.css("article.product_pod")

        for book in books:
            book_item = PostgresWebscrapItem()

            book_item["title"] = book.css("h3 a::text").get()
            book_item["price"] = book.css(".price_color::text").get()

            relative_url = book.css("img.thumbnail::attr(src)").get()
            book_item["image_url"] = response.urljoin(relative_url)

            rating_classes = book.css("p.star-rating::attr(class)").get()
            book_item["rating"] = (
                rating_classes.replace("star-rating", "").strip()
                if rating_classes else None
            )

            stock_text = book.css("p.instock.availability::text").getall()
            book_item["availability"] = (
                "".join(stock_text).strip() if stock_text else None
            )

            yield book_item

        # Follow pagination
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
```

---

## 🔧 How to Complete the Pipeline

Replace the contents of `pipelines.py` with:

```python
import psycopg2


# =====================================================================
# Pipeline 1: Data Cleaning
# =====================================================================
class BookscraperPipeline:
    def process_item(self, item, spider):

        # Remove £ symbol and convert price to float
        price_str = item.get("price")
        if price_str:
            item["price"] = float(price_str.replace("£", ""))

        # Lowercase the rating
        rating_str = item.get("rating")
        if rating_str:
            item["rating"] = rating_str.lower()

        # Strip whitespace from availability
        avail_str = item.get("availability")
        if avail_str:
            item["availability"] = avail_str.strip()

        return item


# =====================================================================
# Pipeline 2: PostgreSQL Storage
# =====================================================================
class PostgreSQLPipeline:

    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="books_db",
            user="your_username",       # ← Replace with your PostgreSQL username
            password="your_password"    # ← Replace with your PostgreSQL password
        )
        self.cur = self.conn.cursor()

    def open_spider(self, spider):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id           SERIAL PRIMARY KEY,
                title        TEXT,
                price        FLOAT,
                rating       TEXT,
                availability TEXT,
                image_url    TEXT
            )
        """)
        self.conn.commit()

    def process_item(self, item, spider):
        self.cur.execute("""
            INSERT INTO books (title, price, rating, availability, image_url)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            item.get("title"),
            item.get("price"),
            item.get("rating"),
            item.get("availability"),
            item.get("image_url"),
        ))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
```

---

## 🔧 How to Enable the Pipeline in Settings

In `settings.py`, uncomment and update `ITEM_PIPELINES`:

```python
ITEM_PIPELINES = {
    "postgre_webscrap.pipelines.BookscraperPipeline": 300,
    "postgre_webscrap.pipelines.PostgreSQLPipeline": 400,
}
```

---

## 🐘 PostgreSQL Setup

### Install PostgreSQL

**Windows:**
Download and install from [postgresql.org/download/windows](https://www.postgresql.org/download/windows). During installation, set a password for the `postgres` superuser.

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

```bash
# Open PostgreSQL shell
psql -U postgres

# Create a new database
CREATE DATABASE books_db;

# Create a user (optional but recommended)
CREATE USER scraper_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE books_db TO scraper_user;

# Exit
\q
```

### Verify the Connection

```bash
psql -U scraper_user -d books_db
# If it connects successfully, PostgreSQL is ready
```

### Install the Python Driver

```bash
pip install psycopg2-binary
```

---

## 🗄️ Database Schema (To Be Created)

The pipeline will auto-create this table when the spider starts:

```sql
CREATE TABLE IF NOT EXISTS books (
    id           SERIAL PRIMARY KEY,
    title        TEXT,
    price        FLOAT,
    rating       TEXT,
    availability TEXT,
    image_url    TEXT
);
```

**Column descriptions:**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL (auto-increment) | Unique identifier for each row |
| `title` | TEXT | Book title |
| `price` | FLOAT | Price as a decimal number (e.g. `51.77`) |
| `rating` | TEXT | Star rating in lowercase words (e.g. `three`) |
| `availability` | TEXT | Stock status (e.g. `In stock`) |
| `image_url` | TEXT | Full URL to the book's thumbnail image |

> **Note:** `SERIAL` in PostgreSQL is the equivalent of `AUTOINCREMENT` in SQLite — it auto-generates a unique integer for each new row.

---

## 🛠️ Settings & Configuration

**File:** `settings.py`

| Setting | Value | Purpose |
|---|---|---|
| `BOT_NAME` | `postgre_webscrap` | Project bot name |
| `SPIDER_MODULES` | `["postgre_webscrap.spiders"]` | Where Scrapy looks for spiders |
| `ROBOTSTXT_OBEY` | `True` | Respects robots.txt rules |
| `CONCURRENT_REQUESTS_PER_DOMAIN` | `1` | Only 1 simultaneous request |
| `DOWNLOAD_DELAY` | `1` | 1 second delay between requests |
| `FEED_EXPORT_ENCODING` | `utf-8` | Encoding for CSV/JSON exports |
| `ITEM_PIPELINES` | ⚠️ Commented out | Must be uncommented manually |

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
- PostgreSQL server installed and running locally (default port: `5432`)

---

## 🚀 Installation & Setup

**1. Extract the project:**

```bash
unzip postgre_webscrap.zip
cd postgre_webscrap
```

**2. Create a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

**3. Install dependencies:**

```bash
pip install scrapy psycopg2-binary
```

**4. Set up PostgreSQL** (see [PostgreSQL Setup](#-postgresql-setup) above)

**5. Complete the missing code** (see [What Is Missing](#-what-is-missing--to-be-implemented) above)

**6. Verify spider is found:**

```bash
scrapy list
# Expected output: books
```

---

## ▶️ Running the Spider

After completing all the missing implementations and ensuring PostgreSQL is running:

```bash
scrapy crawl books
```

**Optional — also export to CSV:**

```bash
scrapy crawl books -o books_output.csv
```

**Verify in PostgreSQL:**

```bash
psql -U scraper_user -d books_db

-- Check total rows
SELECT COUNT(*) FROM books;

-- View first 10 rows
SELECT * FROM books LIMIT 10;

-- Filter by rating
SELECT * FROM books WHERE rating = 'five';

-- Sort by price
SELECT title, price FROM books ORDER BY price ASC LIMIT 5;

-- Average price
SELECT ROUND(AVG(price)::numeric, 2) AS avg_price FROM books;
```

---

## 📊 Comparison With Previous Projects

| Feature | `item_pipeline` (SQLite) | `mongodb_webscrap` (MongoDB) | `postgre_webscrap` (PostgreSQL) |
|---|---|---|---|
| Database type | Relational (file-based) | NoSQL (document) | Relational (server-based) |
| Library | `sqlite3` (built-in) | `pymongo` | `psycopg2` |
| Server needed | ❌ No | ✅ Yes (port 27017) | ✅ Yes (port 5432) |
| Schema | Fixed SQL table | Flexible / schema-less | Fixed SQL table |
| Primary key | `AUTOINCREMENT` | `ObjectId` (auto) | `SERIAL` (auto) |
| Query language | SQL | MongoDB Query Language | SQL (more powerful) |
| Suitable for | Small / local projects | Large / flexible data | Production / enterprise apps |
| Project status | ✅ Complete | ✅ Complete | 🚧 Skeleton only |

---

## 🐛 Known Issues & Bugs

**1. Wrong domain in spider — causes zero results**

```python
# Current (WRONG):
allowed_domains = ["books.books.toscrape.com"]
start_urls = ["https://books.books.toscrape.com"]

# Correct:
allowed_domains = ["books.toscrape.com"]
start_urls = ["https://books.toscrape.com/"]
```
This is a critical bug — with the wrong domain, Scrapy will block all requests and scrape nothing.

**2. `parse()` method is empty**

The spider has `pass` in the body, meaning it connects to the website but extracts no data at all.

**3. Pipeline does nothing**

`PostgreWebscrapPipeline.process_item()` just returns the item — no cleaning, no database insertion.

**4. `ITEM_PIPELINES` is commented out**

Even if the pipeline were implemented, it would not run because it is disabled in `settings.py`.

**5. No `check_postgres.py` utility**

Unlike the previous projects (`check_db.py`, `check_mongo.py`), there is no verification script included. One should be added after the pipeline is implemented.

**6. Duplicate records on re-run**

Like the previous projects, there is no `ON CONFLICT` or duplicate check planned. Running the spider multiple times will duplicate all rows. To handle this, use:
```sql
-- Add a unique constraint on title to prevent duplicates
ALTER TABLE books ADD CONSTRAINT unique_title UNIQUE (title);

-- Then use INSERT ... ON CONFLICT DO NOTHING in the pipeline
INSERT INTO books (title, price, rating, availability, image_url)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (title) DO NOTHING;
```

---

## 📝 License

This project is intended for **educational purposes**. The target website `books.toscrape.com` is a scraping practice sandbox with no real commercial data.
