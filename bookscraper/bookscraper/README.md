# 📚 bookscraper — Scrapy Beginner Spider (Title & Availability)

A **beginner-level Scrapy web scraping project** that crawls the first page of [books.toscrape.com](https://books.toscrape.com) and extracts just two fields — **book title** and **availability status** — yielding them directly as dictionaries to a CSV file.

> 📌 **Project Purpose:**
> This is a **foundational first step** project, focused on learning the core Scrapy spider structure — how to select elements with CSS selectors, how to extract data, and how to yield results. It intentionally keeps things minimal: no item classes, no pipelines, no pagination — just the bare essentials of a working spider.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Project Structure](#-project-structure)
- [Current State of Each File](#-current-state-of-each-file)
- [How It Works](#-how-it-works)
- [Spider Details](#-spider-details)
- [CSS Selectors Explained](#-css-selectors-explained)
- [Output Data](#-output-data)
- [Settings & Configuration](#-settings--configuration)
- [Requirements](#-requirements)
- [Installation & Setup](#-installation--setup)
- [Running the Spider](#-running-the-spider)
- [Limitations of This Project](#-limitations-of-this-project)
- [How to Extend This Project](#-how-to-extend-this-project)
- [Where This Fits in the Learning Series](#-where-this-fits-in-the-learning-series)

---

## 🔍 Project Overview

This is the **simplest, most beginner-friendly** Scrapy project in the series. It answers one question:

> *"How do I use Scrapy to extract data from a web page?"*

The spider visits the homepage of `books.toscrape.com`, finds all 20 book listings on that page, and extracts two pieces of information from each book:

- The **title** of the book
- The **availability** (whether it's in stock)

Results are yielded as plain Python dictionaries and can be saved directly to a CSV file using Scrapy's built-in feed export feature.

---

## 📁 Project Structure

```
bookscraper/
│
├── scrapy.cfg                              # Scrapy deployment configuration
├── books_data.csv                          # ✅ Output CSV (20 books, page 1 only)
│
└── bookscraper/
    ├── __init__.py
    ├── items.py                            # ⚠️ Defined but unused (empty Item class)
    ├── middlewares.py                      # Auto-generated, not used
    ├── pipelines.py                        # ⚠️ Defined but unused (pass-through only)
    ├── settings.py                         # Project settings (pipeline commented out)
    │
    └── spiders/
        ├── __init__.py
        └── books.py                        # ✅ The main spider — working and complete
```

---

## 📄 Current State of Each File

### ✅ `spiders/books.py` — Complete & Working

The spider is fully functional. It scrapes title and availability from the first page of `books.toscrape.com` and yields each book as a dictionary.

---

### ⚠️ `items.py` — Defined but Unused

A `BookscraperItem` class exists but has no fields defined — it only has `pass`. The spider does not use it; it yields plain dictionaries instead.

```python
class BookscraperItem(scrapy.Item):
    # No fields defined
    pass
```

This is fine for a beginner project but would need to be filled out for a more structured approach.

---

### ⚠️ `pipelines.py` — Defined but Unused

The `BookscraperPipeline` class exists but `process_item()` just returns the item without doing anything. The pipeline is also **commented out** in `settings.py`, so it never runs.

```python
class BookscraperPipeline:
    def process_item(self, item, spider):
        return item   # Does nothing
```

---

### ⚠️ `settings.py` — Pipeline Commented Out

`ITEM_PIPELINES` is commented out, which is correct for this project since the pipeline does nothing:

```python
# ITEM_PIPELINES = {
#    "bookscraper.pipelines.BookscraperPipeline": 300,
# }
```

---

### ✅ `books_data.csv` — Output File (Already Generated)

The CSV output from a previous run is included in the project. It contains **20 rows** (one per book on page 1) with two columns: `title` and `availability`.

---

## ⚙️ How It Works

```
1. Spider starts at https://books.toscrape.com/
2. Selects all 20 book blocks on the page using CSS: article.product_pod
3. For each book block:
   a. Extracts title using:        h3 a::text
   b. Extracts availability using: p.instock.availability::text  (getall + join + strip)
4. Yields each book as a Python dictionary: {"title": ..., "availability": ...}
5. Scrapy writes the dictionaries to a CSV file (when -o flag is used)
6. Spider stops — NO pagination, only page 1 is scraped
```

---

## 🕷️ Spider Details

**File:** `spiders/books.py`
**Spider name:** `books`

```
Target URL   : https://books.toscrape.com/
Domain       : books.toscrape.com
Fields       : title, availability
Pages scraped: 1 (first page only — no pagination)
Items/page   : 20 books
Total output : 20 rows
Output format: Plain Python dict (no Item class used)
```

**Full spider code:**

```python
import scrapy

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        # Select all 20 book containers on the page
        books = response.css("article.product_pod")

        for book in books:
            # Extract book title
            title = book.css("h3 a::text").get()

            # Extract availability — uses getall() because text is split across nodes
            stock_text = book.css("p.instock.availability::text").getall()
            availability = "".join(stock_text).strip() if stock_text else None

            # Yield as a plain dictionary (no Item class needed)
            yield {"title": title, "availability": availability}
```

---

## 🔍 CSS Selectors Explained

### Book Container
```css
article.product_pod
```
Each book on the page is wrapped in an `<article>` tag with the class `product_pod`. This selector picks all 20 of them at once.

---

### Title
```css
h3 a::text
```
Inside each book block, the title is inside an `<a>` tag nested within `<h3>`. The `::text` pseudo-element extracts just the text content (not the HTML tag itself). `.get()` returns the first (and only) match.

**Example HTML:**
```html
<h3><a href="..." title="A Light in the Attic">A Light in the ...</a></h3>
```
> Note: Titles are truncated on the listing page. To get full titles, you would need to follow the link to each book's detail page.

---

### Availability
```css
p.instock.availability::text
```
The availability text is inside a `<p>` tag with both classes `instock` and `availability`. However, the text is split across **multiple text nodes** inside that tag (whitespace nodes before and after the actual text). This is why:

- `.getall()` is used instead of `.get()` — it fetches all text nodes as a list
- `"".join(stock_text)` merges them into one string
- `.strip()` removes leading/trailing whitespace

**Example HTML:**
```html
<p class="instock availability">
    <i class="icon-ok"></i>
    In stock
</p>
```
Without `.getall()` + `join` + `strip`, you would get only a whitespace string or `None`.

---

## 📊 Output Data

The included `books_data.csv` contains **20 books** from page 1:

| title | availability |
|---|---|
| A Light in the ... | In stock |
| Tipping the Velvet | In stock |
| Soumission | In stock |
| Sharp Objects | In stock |
| Sapiens: A Brief History ... | In stock |
| The Requiem Red | In stock |
| The Dirty Little Secrets ... | In stock |
| The Coming Woman: A ... | In stock |
| The Boys in the ... | In stock |
| The Black Maria | In stock |
| Starving Hearts (Triangular Trade ... | In stock |
| Shakespeare's Sonnets | In stock |
| Set Me Free | In stock |
| Scott Pilgrim's Precious Little ... | In stock |
| Rip it Up and ... | In stock |
| Our Band Could Be ... | In stock |
| Olio | In stock |
| Mesaerion: The Best Science ... | In stock |
| Libertarianism for Beginners | In stock |
| It's Only the Himalayas | In stock |

> All 20 books on the first page show `In stock` — this is expected, as `books.toscrape.com` lists all books as available.

---

## 🛠️ Settings & Configuration

**File:** `settings.py`

| Setting | Value | Purpose |
|---|---|---|
| `BOT_NAME` | `bookscraper` | Project bot name |
| `SPIDER_MODULES` | `["bookscraper.spiders"]` | Where Scrapy looks for spiders |
| `ROBOTSTXT_OBEY` | `True` | Respects robots.txt rules |
| `CONCURRENT_REQUESTS_PER_DOMAIN` | `1` | Only 1 simultaneous request |
| `DOWNLOAD_DELAY` | `1` | 1 second delay between requests |
| `FEED_EXPORT_ENCODING` | `utf-8` | Encoding for CSV/JSON exports |
| `ITEM_PIPELINES` | Commented out | Pipeline not active (by design) |

---

## 📦 Requirements

Only one package needed:

```
scrapy
```

Install:

```bash
pip install scrapy
```

No database, no external libraries, no server required.

---

## 🚀 Installation & Setup

**1. Extract the project:**

```bash
unzip bookscraper.zip
cd bookscraper
```

**2. Create a virtual environment (recommended):**

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

**3. Install Scrapy:**

```bash
pip install scrapy
```

**4. Verify the spider is found:**

```bash
scrapy list
# Expected output: books
```

---

## ▶️ Running the Spider

**Run and print output to terminal only:**

```bash
scrapy crawl books
```

**Run and save to CSV:**

```bash
scrapy crawl books -o books_data.csv
```

**Run and save to JSON:**

```bash
scrapy crawl books -o books_data.json
```

**Run and save to JSON Lines:**

```bash
scrapy crawl books -o books_data.jsonl
```

> ⚠️ If `books_data.csv` already exists, Scrapy will **append** to it rather than overwrite. Delete the old file first for a clean run.

**Test a single URL in the Scrapy shell (without running the full spider):**

```bash
scrapy shell "https://books.toscrape.com/"

# Then in the shell, try selectors interactively:
response.css("article.product_pod").get()
response.css("h3 a::text").getall()
response.css("p.instock.availability::text").getall()
```

---

## ⚠️ Limitations of This Project

| Limitation | Detail |
|---|---|
| **Only page 1** | No pagination logic — stops after 20 books |
| **Only 2 fields** | No price, rating, or image URL extracted |
| **No Item class** | Yields plain dicts — less structured |
| **No pipeline** | No data cleaning or transformation |
| **No database** | Output is only to CSV/JSON via `-o` flag |
| **Truncated titles** | Listing page titles are cut short (e.g. `A Light in the ...`) |
| **No detail page** | Does not follow links to individual book pages |

---

## 🔨 How to Extend This Project

Here are natural next steps to build on this foundation:

**1. Add pagination (scrape all 1,000 books):**
```python
next_page = response.css("li.next a::attr(href)").get()
if next_page:
    yield response.follow(next_page, callback=self.parse)
```

**2. Extract more fields:**
```python
price = book.css(".price_color::text").get()
rating = book.css("p.star-rating::attr(class)").get()
image_url = response.urljoin(book.css("img.thumbnail::attr(src)").get())
```

**3. Use an Item class** instead of plain dicts (defined in `items.py`):
```python
from bookscraper.items import BookscraperItem
item = BookscraperItem()
item["title"] = title
item["availability"] = availability
yield item
```

**4. Add a cleaning pipeline** (uncomment `ITEM_PIPELINES` in `settings.py` and implement `BookscraperPipeline`)

**5. Add database storage** — SQLite, MongoDB, or PostgreSQL (see the other projects in this series)

---

## 📚 Where This Fits in the Learning Series

This project is the **starting point** of a series of Scrapy projects, each building on the previous:

| # | Project | What's New | Status |
|---|---|---|---|
| 1 | `bookscraper` | Basic spider, 2 fields, page 1 only, dict output | ✅ This project |
| 2 | `item_pipeline` | All 5 fields, pagination, Item class, SQLite storage | ✅ Complete |
| 3 | `mongodb_webscrap` | Same as #2 but stores in MongoDB | ✅ Complete |
| 4 | `postgre_webscrap` | Same concept but targets PostgreSQL | 🚧 Skeleton |

Each project introduces a new concept:

```
bookscraper         →  Learn: CSS selectors, yield dict, basic spider structure
     ↓
item_pipeline       →  Learn: scrapy.Item, Item Pipelines, SQLite storage, pagination
     ↓
mongodb_webscrap    →  Learn: NoSQL databases, pymongo, document storage
     ↓
postgre_webscrap    →  Learn: Production SQL databases, psycopg2, server-based storage
```

---

## 📝 License

This project is intended for **educational purposes**. The target website `books.toscrape.com` is a scraping practice sandbox with no real commercial data.
