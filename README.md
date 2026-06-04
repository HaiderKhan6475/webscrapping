# 🌐 Web Scraping Practice & Projects

A comprehensive **monorepo** containing a full progression of Python web scraping projects built with **Scrapy** — starting from a bare-bones beginner spider all the way to production-ready database pipelines using **SQLite**, **MongoDB**, and **PostgreSQL**.

> **Author:** [Haider Khan](https://github.com/HaiderKhan6475)
> **License:** MIT
> **Language:** Python 3.11
> **Target Website:** [books.toscrape.com](https://books.toscrape.com) — a public scraping sandbox

---

## 📋 Table of Contents

- [Repository Overview](#-repository-overview)
- [Repository Structure](#-repository-structure)
- [Project Progression — Learning Path](#-project-progression--learning-path)
- [Quick Comparison of All Projects](#-quick-comparison-of-all-projects)
- [Project 1 — bookscraper](#-project-1--bookscraper)
- [Project 2 — item_pipeline](#-project-2--item_pipeline)
- [Project 3 — mongodb_webscrap](#-project-3--mongodb_webscrap)
- [Project 4 — postgre_webscrap](#-project-4--postgre_webscrap)
- [Tech Stack](#-tech-stack)
- [Data Extracted](#-data-extracted)
- [Storage Formats Used](#-storage-formats-used)
- [Git Commit History](#-git-commit-history)
- [Global Setup](#-global-setup)
- [How to Run Each Project](#-how-to-run-each-project)
- [License](#-license)

---

## 🔍 Repository Overview

This repository documents a **structured learning journey** through Scrapy web scraping. Each sub-project introduces a new concept, building directly on top of the previous one:

| Concept Introduced | Project |
|---|---|
| Basic spider, CSS selectors, dict output | `bookscraper` |
| Scrapy Items, Item Pipelines, SQLite storage, pagination | `item_pipeline` |
| NoSQL database storage with MongoDB | `mongodb_webscrap` |
| Production SQL storage with PostgreSQL | `postgre_webscrap` |

All four projects scrape the same website — **books.toscrape.com** — so the focus stays entirely on learning the Scrapy framework and different data storage strategies, not on the complexity of the target site.

---

## 📁 Repository Structure

```
webscrapping/                           ← Root repository
│
├── README.md                           ← This file — master overview
├── LICENSE                             ← MIT License (Haider Khan, 2026)
├── .gitignore                          ← Ignores __pycache__, *.pyc, venv/
│
├── bookscraper/                        ← Project 1: Beginner spider
│   ├── scrapy.cfg
│   ├── books_data.csv                  ← Output: 20 books (page 1 only)
│   └── bookscraper/
│       ├── items.py                    ← Empty Item class (unused)
│       ├── pipelines.py                ← Pass-through only (inactive)
│       ├── settings.py                 ← ITEM_PIPELINES commented out
│       └── spiders/
│           └── books.py               ← ✅ Spider: title + availability, page 1
│
├── item_pipeline/                      ← Project 2: Full pipeline + SQLite
│   ├── scrapy.cfg
│   └── item_pipeline/
│       ├── items.py                    ← ItemPipelineItem: 5 fields
│       ├── pipelines.py                ← BookscraperPipeline + SQLitePipeline
│       ├── settings.py                 ← Both pipelines active
│       ├── books_data.db               ← SQLite DB (288 KB, ~2000 rows)
│       ├── check_db.py                 ← DB verification utility
│       └── spiders/
│           ├── books.py               ← ✅ Spider: 5 fields, 50 pages
│           ├── books_data.db          ← Duplicate DB (from alternate run dir)
│           ├── item_pipeline_data.csv ← CSV export (1000 rows)
│           ├── item_pipeline_data2.csv
│           ├── item_pipeline_data3.csv ← Empty (interrupted run)
│           └── item_pipeline_data4.csv
│
├── mongodb_webscrap/                   ← Project 3: MongoDB storage
│   ├── scrapy.cfg
│   └── mongodb_webscrap/
│       ├── items.py                    ← MongodbWebscrapItem: 5 fields
│       ├── pipelines.py                ← BookscraperPipeline + MongoDBPipeline
│       ├── settings.py                 ← Both pipelines active
│       ├── check_mongo.py              ← MongoDB verification utility
│       └── spiders/
│           └── books.py               ← ✅ Spider: 5 fields, 50 pages
│
└── postgre_webscrap/                   ← Project 4: PostgreSQL storage
    ├── scrapy.cfg
    └── postgre_webscrap/
        ├── items.py                    ← PostgresWebscrapItem: 5 fields
        ├── pipelines.py                ← BookscraperPipeline + PostgresPipeline
        ├── settings.py                 ← Both pipelines active
        └── spiders/
            └── books.py               ← ✅ Spider: 5 fields, 50 pages
```

---

## 📈 Project Progression — Learning Path

Each project builds on the previous one by introducing exactly one or two new concepts:

```
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1 — bookscraper                                               │
│  ✔ Basic Scrapy spider structure                                    │
│  ✔ CSS selectors (article, h3, p)                                   │
│  ✔ Yield plain Python dict                                          │
│  ✔ Save output with -o flag (CSV/JSON)                              │
│  ✘ No Item class | No pipeline | No pagination | Page 1 only        │
└───────────────────┬─────────────────────────────────────────────────┘
                    │  + Item class, Pipelines, SQLite, Pagination
┌───────────────────▼─────────────────────────────────────────────────┐
│  STEP 2 — item_pipeline                                             │
│  ✔ scrapy.Item class with 5 defined fields                          │
│  ✔ Pagination — follows all 50 pages (1,000 books)                  │
│  ✔ BookscraperPipeline — cleans price, rating, availability         │
│  ✔ SQLitePipeline — stores into local books_data.db                 │
│  ✔ check_db.py — verifies stored data                               │
└───────────────────┬─────────────────────────────────────────────────┘
                    │  + NoSQL, pymongo, server-based storage
┌───────────────────▼─────────────────────────────────────────────────┐
│  STEP 3 — mongodb_webscrap                                          │
│  ✔ Same spider & cleaning pipeline as item_pipeline                 │
│  ✔ MongoDBPipeline — connects via pymongo to localhost:27017        │
│  ✔ Stores JSON documents in mongodb_books_db.scraped_books          │
│  ✔ check_mongo.py — verifies stored data                            │
│  ✘ No explicit close_spider (relies on garbage collector)           │
└───────────────────┬─────────────────────────────────────────────────┘
                    │  + Production SQL, psycopg2, NUMERIC type
┌───────────────────▼─────────────────────────────────────────────────┐
│  STEP 4 — postgre_webscrap                                          │
│  ✔ Same spider & cleaning pipeline                                  │
│  ✔ PostgresPipeline — connects via psycopg2 to localhost:5432       │
│  ✔ NUMERIC(10,2) for price — correct monetary type                  │
│  ✔ Auto-creates scraped_books table on first run                    │
│  ✔ Explicit close_spider — proper connection management             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Quick Comparison of All Projects

| Feature | bookscraper | item_pipeline | mongodb_webscrap | postgre_webscrap |
|---|---|---|---|---|
| **Status** | ✅ Complete | ✅ Complete | ✅ Complete | ✅ Complete |
| **Fields scraped** | 2 | 5 | 5 | 5 |
| **Pagination** | ❌ Page 1 only | ✅ 50 pages | ✅ 50 pages | ✅ 50 pages |
| **Total items** | 20 | ~1,000 | ~1,000 | ~1,000 |
| **Item class** | ❌ plain dict | ✅ Yes | ✅ Yes | ✅ Yes |
| **Cleaning pipeline** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| **Storage** | CSV only | SQLite file | MongoDB server | PostgreSQL server |
| **Library** | — | `sqlite3` (built-in) | `pymongo` | `psycopg2` |
| **External server** | ❌ No | ❌ No | ✅ Port 27017 | ✅ Port 5432 |
| **DB type** | — | Relational (SQL) | NoSQL (document) | Relational (SQL) |
| **Price stored as** | string | REAL (float) | float (Python) | NUMERIC(10,2) |
| **close_spider** | — | ✅ Yes | ❌ No | ✅ Yes |
| **Verify script** | — | check_db.py | check_mongo.py | — |
| **Output files** | books_data.csv | books_data.db + CSVs | MongoDB server | PostgreSQL server |

---

## 🕷️ Project 1 — bookscraper

**Path:** `bookscraper/`
**Purpose:** Learn the fundamental structure of a Scrapy spider.

### What it does
Visits the homepage of `books.toscrape.com` and extracts **title** and **availability** from all 20 books on page 1. Yields each book as a plain Python dictionary. No pagination, no Item class, no pipeline.

### Spider code (core logic)
```python
def parse(self, response):
    books = response.css("article.product_pod")
    for book in books:
        title = book.css("h3 a::text").get()
        stock_text = book.css("p.instock.availability::text").getall()
        availability = "".join(stock_text).strip() if stock_text else None
        yield {"title": title, "availability": availability}
```

### Output
- `books_data.csv` — 20 rows, 2 columns (`title`, `availability`)

### Run
```bash
cd bookscraper
scrapy crawl books -o books_data.csv
```

### Key learning points
- `response.css()` for selecting HTML elements
- `::text` pseudo-element to extract text content
- `::attr(src)` to extract attribute values
- `.get()` vs `.getall()` — single vs multiple matches
- Why `getall()` + `join` + `strip` is needed for availability text nodes
- `yield dict` to produce output items

---

## 🕷️ Project 2 — item_pipeline

**Path:** `item_pipeline/`
**Purpose:** Learn Scrapy Items, Item Pipelines, and SQLite database storage.

### What it does
Crawls all 50 pages of `books.toscrape.com` and extracts **5 fields** per book. Passes each item through two pipelines: one for cleaning, one for storing into a local SQLite database.

### Pipelines

**Pipeline 1 — `BookscraperPipeline` (priority 300):**
- Strips `£` from price → converts to `float`
- Lowercases rating string
- Strips whitespace from availability

**Pipeline 2 — `SQLitePipeline` (priority 400):**
- Opens `books_data.db` using Python's built-in `sqlite3`
- `CREATE TABLE IF NOT EXISTS books` on spider open
- `INSERT INTO books` for each item
- Closes connection on spider close

### Output
- `item_pipeline/books_data.db` — SQLite database, ~2,000 rows (spider ran twice)
- `spiders/item_pipeline_data.csv` / `...data2.csv` / `...data4.csv` — CSV exports

### Database
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

### Run
```bash
cd item_pipeline
scrapy crawl books
python item_pipeline/check_db.py   # verify data
```

### Key learning points
- Defining a `scrapy.Item` subclass
- Two-pipeline architecture with priority ordering
- `open_spider` / `close_spider` lifecycle methods
- SQLite `sqlite3` — zero-setup local database
- `CREATE TABLE IF NOT EXISTS` for idempotent schema creation
- Pagination with `response.follow(next_page, callback=self.parse)`

---

## 🕷️ Project 3 — mongodb_webscrap

**Path:** `mongodb_webscrap/`
**Purpose:** Learn NoSQL database storage using MongoDB and `pymongo`.

### What it does
Same spider and cleaning pipeline as `item_pipeline`, but replaces `SQLitePipeline` with `MongoDBPipeline` that connects to a running MongoDB server and stores each item as a JSON document.

### Pipelines

**Pipeline 1 — `BookscraperPipeline` (priority 300):** Same cleaning logic as Project 2.

**Pipeline 2 — `MongoDBPipeline` (priority 500):**
- Connects to `mongodb://localhost:27017/` in `__init__`
- Selects database `mongodb_books_db` and collection `scraped_books`
- Calls `insert_one(dict(item))` for each item

### Output
```
MongoDB Server (localhost:27017)
└── Database: mongodb_books_db
    └── Collection: scraped_books
        └── ~1,000 JSON documents
```

### Example document
```json
{
  "_id": "ObjectId('...')",
  "title": "A Light in the Attic",
  "price": 51.77,
  "rating": "three",
  "availability": "In stock",
  "image_url": "https://books.toscrape.com/media/cache/..."
}
```

### Run
```bash
# Start MongoDB first
brew services start mongodb-community   # macOS
sudo systemctl start mongodb            # Linux

cd mongodb_webscrap
scrapy crawl books
python mongodb_webscrap/check_mongo.py  # verify data
```

### Key learning points
- MongoDB vs SQLite — document model vs relational model
- `pymongo.MongoClient` — connecting to a server-based DB
- `insert_one(dict(item))` — inserting documents
- MongoDB `_id` (ObjectId) vs SQL `AUTOINCREMENT`
- No `open_spider` / `close_spider` needed — connection managed in `__init__`

---

## 🕷️ Project 4 — postgre_webscrap

**Path:** `postgre_webscrap/`
**Purpose:** Learn production-grade SQL storage using PostgreSQL and `psycopg2`.

### What it does
Same spider and cleaning pipeline as Projects 2 and 3, but uses `PostgresPipeline` to connect to a running PostgreSQL server and insert each cleaned item into a structured SQL table with proper column types.

### Pipelines

**Pipeline 1 — `BookscraperPipeline` (priority 300):** Same cleaning logic.

**Pipeline 2 — `PostgresPipeline` (priority 500):**
- Connects to `localhost:5432` via `psycopg2.connect()` in `__init__`
- Runs `CREATE TABLE IF NOT EXISTS scraped_books` automatically
- `INSERT INTO scraped_books` with parameterised query per item
- `connection.commit()` after every insert
- `close_spider` explicitly closes cursor and connection

### Output
```
PostgreSQL Server (localhost:5432)
└── Database: postgres_books_db
    └── Table: scraped_books
        └── ~1,000 rows
```

### Database schema
```sql
CREATE TABLE IF NOT EXISTS scraped_books (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(500),
    price        NUMERIC(10, 2),     -- Exact decimal — correct for money
    rating       VARCHAR(50),
    availability VARCHAR(100),
    image_url    TEXT
);
```

### Setup & Run
```bash
# Create the database first
psql -U postgres -c "CREATE DATABASE postgres_books_db;"

# Update credentials in postgre_webscrap/pipelines.py

cd postgre_webscrap
scrapy crawl books

# Verify in psql
psql -U postgres -d postgres_books_db -c "SELECT COUNT(*) FROM scraped_books;"
```

### Key learning points
- PostgreSQL vs MongoDB — when to use relational vs document storage
- `psycopg2` — the standard Python PostgreSQL adapter
- `SERIAL PRIMARY KEY` — PostgreSQL auto-increment
- `NUMERIC(10, 2)` vs `FLOAT` — exact decimal for monetary values
- Parameterised queries (`%s`) — prevents SQL injection
- `SERIAL` / `CREATE TABLE IF NOT EXISTS` — idempotent schema creation
- Explicit `close_spider` — proper connection lifecycle in SQL databases

---

## 🛠️ Tech Stack

| Tool / Library | Role |
|---|---|
| **Python 3.11** | Primary programming language |
| **Scrapy** | Web crawling and scraping framework |
| **sqlite3** | Built-in Python library for SQLite storage |
| **pymongo** | Python driver for MongoDB |
| **psycopg2-binary** | Python driver for PostgreSQL |
| **MongoDB** | NoSQL document database (Project 3) |
| **PostgreSQL** | Relational database server (Project 4) |
| **Git** | Version control |

---

## 📦 Data Extracted

All four projects target the same website and extract (some or all of) these fields:

| Field | CSS Selector | Description |
|---|---|---|
| `title` | `h3 a::text` | Book title (truncated on listing page) |
| `price` | `.price_color::text` | Price including £ symbol (cleaned in pipeline) |
| `rating` | `p.star-rating::attr(class)` | Word-based star rating (e.g. `Three`) |
| `availability` | `p.instock.availability::text` | Stock status (e.g. `In stock`) |
| `image_url` | `img.thumbnail::attr(src)` | Relative thumbnail path (resolved to full URL) |

**Sample data (after cleaning):**

| title | price | rating | availability | image_url |
|---|---|---|---|---|
| A Light in the Attic | 51.77 | three | In stock | https://books.toscrape.com/media/... |
| Tipping the Velvet | 53.74 | one | In stock | https://books.toscrape.com/media/... |
| Soumission | 50.10 | one | In stock | https://books.toscrape.com/media/... |

---

## 💾 Storage Formats Used

| Format | Used In | Details |
|---|---|---|
| **CSV** | bookscraper, item_pipeline | Scrapy's built-in `-o` flag export |
| **SQLite** | item_pipeline | `books_data.db` — local file, no server needed |
| **MongoDB** | mongodb_webscrap | `mongodb_books_db.scraped_books` collection |
| **PostgreSQL** | postgre_webscrap | `postgres_books_db.scraped_books` table |

---

## 📜 Git Commit History

| Commit | Date | Message |
|---|---|---|
| `7d8f731` | 2026-06-04 | Revise README for completed PostgreSQL scraper project |
| `5edc11d` | 2026-06-04 | Add README for bookscraper project |
| `507ee73` | 2026-06-04 | Add README for postgre_webscrap project |
| `97cc427` | 2026-06-04 | Revise README for mongodb_webscrap project |
| `9903dd8` | 2026-06-04 | Add README for item_pipeline project |
| `1afe294` | 2026-06-04 | Add README for web scraping project with MongoDB |
| `bfae254` | 2026-06-04 | Enhance README with project details and tech stack |
| `4dd4fea` | 2026-06-04 | Added webscraping tasks and configured .gitignore |
| `fd7e215` | 2026-06-04 | Initial commit |

---

## 🚀 Global Setup

### Prerequisites

- Python 3.8 or higher
- pip

### Install all dependencies

```bash
pip install scrapy pymongo psycopg2-binary
```

### Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
pip install scrapy pymongo psycopg2-binary
```

### Dependencies per project

| Project | Install Command |
|---|---|
| bookscraper | `pip install scrapy` |
| item_pipeline | `pip install scrapy` |
| mongodb_webscrap | `pip install scrapy pymongo` |
| postgre_webscrap | `pip install scrapy psycopg2-binary` |

---

## ▶️ How to Run Each Project

### Project 1 — bookscraper
```bash
cd bookscraper
scrapy crawl books -o books_data.csv
```

### Project 2 — item_pipeline
```bash
cd item_pipeline
scrapy crawl books                        # stores into books_data.db
python item_pipeline/check_db.py          # verify the database
```

### Project 3 — mongodb_webscrap
```bash
# Ensure MongoDB is running
brew services start mongodb-community     # macOS
sudo systemctl start mongodb              # Linux

cd mongodb_webscrap
scrapy crawl books
python mongodb_webscrap/check_mongo.py   # verify the database
```

### Project 4 — postgre_webscrap
```bash
# Ensure PostgreSQL is running and database exists
psql -U postgres -c "CREATE DATABASE postgres_books_db;"

# Update credentials in postgre_webscrap/pipelines.py if needed

cd postgre_webscrap
scrapy crawl books

# Verify
psql -U postgres -d postgres_books_db -c "SELECT COUNT(*) FROM scraped_books;"
```

---

## 📝 License

This project is licensed under the **MIT License**.

Copyright (c) 2026 **Haider Khan**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.

See the `LICENSE` file for full details.

---

*Maintained with ❤️ by [Haider Khan](https://github.com/HaiderKhan6475)*
