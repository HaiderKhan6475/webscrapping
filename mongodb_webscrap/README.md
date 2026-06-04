# 📚 mongodb_webscrap — Scrapy Books Scraper with MongoDB Storage

A fully functional **Scrapy web scraping project** that crawls [books.toscrape.com](https://books.toscrape.com), extracts structured book data, cleans it through a custom item pipeline, and stores it directly into a **MongoDB database**.

This project is an **upgraded version** of the previous `item_pipeline` project — replacing SQLite with **MongoDB (NoSQL)**, which is more scalable and flexible for real-world applications.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Project Structure](#-project-structure)
- [SQLite vs MongoDB — What's the Difference?](#-sqlite-vs-mongodb--whats-the-difference)
- [How It Works](#-how-it-works)
- [Data Fields](#-data-fields)
- [Item Pipeline Architecture](#-item-pipeline-architecture)
- [Spider Details](#-spider-details)
- [Settings & Configuration](#-settings--configuration)
- [MongoDB Database Structure](#-mongodb-database-structure)
- [Requirements](#-requirements)
- [Installation & Setup](#-installation--setup)
- [MongoDB Setup](#-mongodb-setup)
- [Running the Spider](#-running-the-spider)
- [Verifying the Data in MongoDB](#-verifying-the-data-in-mongodb)
- [Pipeline Flow Diagram](#-pipeline-flow-diagram)
- [Differences From the Previous Project](#-differences-from-the-previous-project)
- [Known Issues & Tips](#-known-issues--tips)

---

## 🔍 Project Overview

This project does two things:

1. **Web Scraping** — Extracts data (title, price, rating, availability, image URL) for 1,000 books from `books.toscrape.com` across all 50 pages
2. **MongoDB Storage** — Cleans each scraped item through a pipeline and stores it directly into MongoDB

The target website [books.toscrape.com](https://books.toscrape.com) is a public sandbox site designed specifically for web scraping practice — it contains no real commercial data.

---

## 📁 Project Structure

```
mongodb_webscrap/
│
├── scrapy.cfg                              # Scrapy deployment configuration
│
└── mongodb_webscrap/
    ├── __init__.py
    ├── items.py                            # Scrapy Item definition (data model)
    ├── middlewares.py                      # Spider & downloader middlewares
    ├── pipelines.py                        # Pipeline 1: Cleaning + Pipeline 2: MongoDB
    ├── settings.py                         # Project-wide Scrapy settings
    ├── check_mongo.py                      # MongoDB data verification utility
    │
    └── spiders/
        ├── __init__.py
        └── books.py                        # Main spider — crawls books.toscrape.com
```

> **Note:** This project contains no `.db` file or `.csv` file — all data goes directly into the **running MongoDB server**, not onto the local disk.

---

## ⚖️ SQLite vs MongoDB — What's the Difference?

| Feature | SQLite (Previous Project) | MongoDB (This Project) |
|---|---|---|
| Type | Relational (SQL) | NoSQL (Document-based) |
| Storage | Local `.db` file on disk | Running server (port 27017) |
| Data format | Rows & Columns (Table) | JSON-like Documents |
| Schema | Fixed (CREATE TABLE) | Flexible (any fields) |
| Scalability | Small projects | Large-scale applications |
| Query language | SQL | MongoDB Query Language (MQL) |
| Setup required | Zero setup | MongoDB server must be installed & running |
| Duplicate check | Not implemented | Not implemented |

---

## ⚙️ How It Works

```
1. Spider starts at https://books.toscrape.com/
2. Each page has 20 books → data is extracted using CSS selectors
3. Spider follows the "Next page" link → repeats across all 50 pages
4. Each scraped book item passes through two pipelines:
   a. BookscraperPipeline  → cleans the raw data
   b. MongoDBPipeline      → inserts the cleaned data into MongoDB
5. ~1,000 documents are stored in the MongoDB collection
```

---

## 📊 Data Fields

Defined in `items.py` using `MongodbWebscrapItem(scrapy.Item)`:

| Field | Raw Value (from website) | After Cleaning (stored in MongoDB) |
|---|---|---|
| `title` | `A Light in the ...` | `A Light in the ...` (unchanged) |
| `price` | `£51.77` | `51.77` (float, £ symbol removed) |
| `rating` | `Three` | `three` (lowercased) |
| `availability` | ` In stock ` (with spaces) | `In stock` (whitespace stripped) |
| `image_url` | `media/cache/2c/da/...jpg` | `https://books.toscrape.com/media/cache/...jpg` (full URL) |

---

## 🔧 Item Pipeline Architecture

### Pipeline 1 — `BookscraperPipeline` (Priority: 300)

**File:** `pipelines.py`

Runs **first** — cleans raw data before it reaches MongoDB.

**What it does:**

- **Price cleaning:** Strips the `£` symbol from the price string and converts it to a Python `float`. e.g. `"£51.77"` → `51.77`
- **Rating normalisation:** Converts the word-based rating to lowercase. e.g. `"Three"` → `"three"`
- **Availability trim:** Strips leading/trailing whitespace. e.g. `" In stock "` → `"In stock"`

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

### Pipeline 2 — `MongoDBPipeline` (Priority: 500)

**File:** `pipelines.py`

Runs **second** — takes the cleaned item and inserts it into MongoDB.

**What it does:**

- **`__init__`**: Connects to `localhost:27017` via `pymongo.MongoClient`, selects the database `mongodb_books_db` and the collection `scraped_books`
- **`process_item`**: Converts each item to a Python `dict` and calls `insert_one()` to store it in MongoDB

```python
class MongoDBPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["mongodb_books_db"]
        self.collection = self.db["scraped_books"]

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item
```

> **Notice:** Unlike the previous SQLite pipeline, this pipeline has **no `open_spider` or `close_spider` methods**. The MongoDB connection is opened in `__init__` and closed automatically when the object is destroyed by Python's garbage collector.

---

## 🕷️ Spider Details

**File:** `spiders/books.py`  
**Spider name:** `books`

```
Target URL  : https://books.toscrape.com/
Domain      : books.toscrape.com
Item class  : MongodbWebscrapItem
Pagination  : Automatic (follows li.next a)
Items/page  : 20 books
Total pages : 50
Total items : ~1,000 books
```

**CSS Selectors used:**

| Data Point | CSS Selector |
|---|---|
| Book container | `article.product_pod` |
| Title | `h3 a::text` |
| Price | `.price_color::text` |
| Image URL | `img.thumbnail::attr(src)` |
| Rating | `p.star-rating::attr(class)` |
| Availability | `p.instock.availability::text` |
| Next page | `li.next a::attr(href)` |

**Rating extraction logic:**  
The rating is embedded as a CSS class on the `<p>` element — e.g. `class="star-rating Three"`. The spider extracts the full class string and strips `"star-rating"` to get `"Three"`, which the pipeline then lowercases to `"three"`.

**Image URL resolution:**  
`response.urljoin(relative_url)` converts relative image paths into full absolute URLs, ensuring consistency across all pages.

---

## 🛠️ Settings & Configuration

**File:** `settings.py`

| Setting | Value | Purpose |
|---|---|---|
| `BOT_NAME` | `mongodb_webscrap` | Project bot name |
| `SPIDER_MODULES` | `["mongodb_webscrap.spiders"]` | Where Scrapy looks for spiders |
| `ROBOTSTXT_OBEY` | `True` | Respects robots.txt rules |
| `CONCURRENT_REQUESTS_PER_DOMAIN` | `1` | Only 1 simultaneous request per domain |
| `DOWNLOAD_DELAY` | `1` | 1 second wait between requests |
| `FEED_EXPORT_ENCODING` | `utf-8` | Encoding for any CSV/JSON exports |

**Active pipelines:**

```python
ITEM_PIPELINES = {
    "mongodb_webscrap.pipelines.BookscraperPipeline": 300,  # Runs first — cleans data
    "mongodb_webscrap.pipelines.MongoDBPipeline": 500,      # Runs second — stores data
}
```

> Lower priority numbers run **first**. `300 < 500`, so cleaning always happens before storage.

---

## 🗄️ MongoDB Database Structure

```
MongoDB Server (localhost:27017)
└── Database: mongodb_books_db
    └── Collection: scraped_books
        ├── Document 1: { _id, title, price, rating, availability, image_url }
        ├── Document 2: { _id, title, price, rating, availability, image_url }
        └── ... (~1,000 documents total)
```

**Example of a single stored document (JSON format):**

```json
{
  "_id": "ObjectId('64abc123...')",
  "title": "A Light in the Attic",
  "price": 51.77,
  "rating": "three",
  "availability": "In stock",
  "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg"
}
```

> MongoDB automatically adds the `_id` field to every document — it is a unique `ObjectId` identifier generated by the database itself.

---

## 📦 Requirements

**Python packages:**

```
scrapy
pymongo
```

Install with pip:

```bash
pip install scrapy pymongo
```

**System requirement:**
- **MongoDB Community Server** must be installed and running locally
- Default port: `27017`

---

## 🚀 Installation & Setup

**1. Extract the project:**

```bash
unzip mongodb_webscrap.zip
cd mongodb_webscrap
```

**2. Create and activate a virtual environment (recommended):**

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

**3. Install dependencies:**

```bash
pip install scrapy pymongo
```

**4. Verify the spider is found:**

```bash
scrapy list
# Expected output: books
```

---

## 🍃 MongoDB Setup

The MongoDB server **must be running** before you start the spider. If it's not running, the pipeline will throw a `ServerSelectionTimeoutError`.

### Install MongoDB

**Windows:**
1. Download the installer from [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
2. Run the installer and check **"Install MongoDB as a Service"**

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
sudo apt install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### Verify MongoDB is running

```bash
mongosh
# If connected successfully, you'll see:
# connecting to: mongodb://127.0.0.1:27017/
```

---

## ▶️ Running the Spider

Once MongoDB is running, execute from the project root (where `scrapy.cfg` is located):

```bash
scrapy crawl books
```

This will:
- Crawl all 50 pages of `books.toscrape.com`
- Clean each item via `BookscraperPipeline`
- Insert ~1,000 documents into MongoDB

**Optional — also export to CSV:**

```bash
scrapy crawl books -o books_output.csv
```

**Optional — also export to JSON:**

```bash
scrapy crawl books -o books_output.json
```

---

## ✅ Verifying the Data in MongoDB

### Method 1 — check_mongo.py script

```bash
cd mongodb_webscrap
python check_mongo.py
```

**Expected output:**

```
Total Books in MongoDB: 1000

--- FIRST 5 RECORDS ---
 Title: A Light in the Attic...
 Price: 51.77 (Cleaned)
 Rating: three
 URL: https://books.toscrape.com/media/cache/...
----------------------------------------
 Title: Tipping the Velvet...
 Price: 53.74 (Cleaned)
 Rating: one
 ...
```

### Method 2 — MongoDB Shell (mongosh)

```bash
mongosh

use mongodb_books_db

# Count total documents
db.scraped_books.countDocuments()

# View first 5 documents
db.scraped_books.find().limit(5).pretty()

# Filter by rating
db.scraped_books.find({ rating: "five" }).count()

# Sort by price ascending (cheapest first)
db.scraped_books.find().sort({ price: 1 }).limit(5)

# Most expensive book
db.scraped_books.find().sort({ price: -1 }).limit(1)

# All books under £15
db.scraped_books.find({ price: { $lt: 15 } })
```

### Method 3 — Query via Python

```python
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mongodb_books_db"]
collection = db["scraped_books"]

# Total count
print("Total books:", collection.count_documents({}))

# Average price
pipeline = [{"$group": {"_id": None, "avg_price": {"$avg": "$price"}}}]
result = list(collection.aggregate(pipeline))
print("Average price: £", round(result[0]["avg_price"], 2))

# Rating distribution
pipeline = [{"$group": {"_id": "$rating", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}]
for r in collection.aggregate(pipeline):
    print(r["_id"], "->", r["count"], "books")
```

---

## 🔄 Pipeline Flow Diagram

```
books.toscrape.com
        │
        ▼
  [BooksSpider]
  Extracts 20 items per page
  Follows pagination (50 pages)
        │
        ▼  (yields MongodbWebscrapItem)
        │
  ┌──────────────────────────────┐
  │    BookscraperPipeline       │  Priority: 300  ← Runs FIRST
  │  ✔ "£51.77"  →  51.77 float │
  │  ✔ "Three"   →  "three"     │
  │  ✔ " In stock " → stripped  │
  └─────────────┬────────────────┘
                │
  ┌─────────────▼────────────────┐
  │       MongoDBPipeline        │  Priority: 500  ← Runs SECOND
  │  ✔ Connect localhost:27017   │
  │  ✔ insert_one(dict(item))   │
  │  ✔ DB: mongodb_books_db      │
  │  ✔ Collection: scraped_books │
  └──────────────────────────────┘
                │
                ▼
    MongoDB Server
    Database  : mongodb_books_db
    Collection: scraped_books
    ~1,000 JSON documents ✅
```

---

## 📝 Differences From the Previous Project

| | `item_pipeline` (SQLite) | `mongodb_webscrap` (MongoDB) |
|---|---|---|
| Storage engine | SQLite | MongoDB |
| Storage location | `.db` file on disk | MongoDB server |
| Data format | Relational table | JSON documents |
| Storage pipeline class | `SQLitePipeline` | `MongoDBPipeline` |
| Library used | `sqlite3` (Python built-in) | `pymongo` (must install) |
| Connection opened in | `open_spider()` | `__init__()` |
| Connection closed in | `close_spider()` | Automatic (garbage collected) |
| Schema | Fixed (SQL CREATE TABLE) | Flexible (schema-less) |
| Query language | SQL | MongoDB Query Language |
| Output files on disk | `books_data.db` | None (data lives in server) |
| Verification script | `check_db.py` | `check_mongo.py` |
| External server needed | No | Yes (MongoDB must be running) |

---

## 🐛 Known Issues & Tips

**1. MongoDB server must be running before the spider starts**

If MongoDB is not running, you will get:
```
pymongo.errors.ServerSelectionTimeoutError: localhost:27017
```
**Fix:** Start MongoDB first, then run the spider.

**2. Duplicate records on re-run**

The `MongoDBPipeline` uses `insert_one()` without any duplicate check. Running the spider multiple times will add another 1,000 documents each time. To clear the collection before a fresh run:
```javascript
// In mongosh:
use mongodb_books_db
db.scraped_books.deleteMany({})
```

**3. No `close_spider` method in MongoDBPipeline**

The SQLite version explicitly closed the connection in `close_spider()`. The MongoDB version does not — Python's garbage collector handles it. If you want to close it explicitly, add:
```python
def close_spider(self, spider):
    self.client.close()
```

**4. Settings comment about a past bug**

`settings.py` contains the comment `# FIX: Shuruat me 'mongodb_webscrap' hona chahiye, 'item_pipeline' nahi!` — this indicates that during development the pipeline path was mistakenly set to the old project name (`item_pipeline`) and was later corrected to `mongodb_webscrap`.

**5. Politeness settings are already configured**

`DOWNLOAD_DELAY = 1` and `CONCURRENT_REQUESTS_PER_DOMAIN = 1` are set, ensuring the spider does not hammer the server. Do not remove these when scraping real-world websites.

---

## 📝 License

This project is intended for **educational purposes**. The target website `books.toscrape.com` is a scraping practice sandbox with no real commercial data.
