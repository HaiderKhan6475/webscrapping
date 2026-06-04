# 🍃 Web Scraping with Scrapy and MongoDB

This sub-project focuses on scraping book details from a live website and storing the extracted, cleaned data into a **MongoDB** database.

---

## 🚀 Features
- **Full Website Crawling:** Automatically navigates through all 50 pages of the bookstore.
- **Data Cleaning Pipeline:**
  - Removes currency symbols (`£`) from prices and converts them into `float`.
  - Normalizes ratings text to lowercase.
  - Strips extra spaces from the availability status.
- **Database Storage:** Establishes a connection with a local MongoDB instance and inserts data seamlessly into a structured collection.

---

## 🛠️ Tech Stack
- **Language:** Python 3.11
- **Framework:** Scrapy
- **Database:** MongoDB (NoSQL)
- **Database Driver:** PyMongo

---

## 📁 Project Structure & Key Files
- `spiders/books.py`: Contains the core spider logic for extraction and pagination.
- `pipelines.py`: Handles data cleaning and manages MongoDB server connection/insertions.
- `settings.py`: Registers and activates the scraping pipelines.
- `check_mongo.py`: A verification script to quickly check the total records stored in the database.

---

## 🏃‍♂️ How to Run Locally

### 1. Start MongoDB Service
Open your Command Prompt (CMD) as **Administrator** and run:
```bash
net start MongoDB
