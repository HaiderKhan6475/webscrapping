import psycopg2


# =====================================================================
# 1. PIPELINE: Data Cleaning
# =====================================================================
class BookscraperPipeline:

    def process_item(self, item, spider):
        # Price se '£' hatane aur float banane ka logic
        price_str = item.get("price")
        if price_str:
            clean_price = price_str.replace("£", "")
            item["price"] = float(clean_price)

        # Rating ko lowercase karne ke liye
        rating_str = item.get("rating")
        if rating_str:
            item["rating"] = rating_str.lower()

        # Availability ke extra spaces saaf karne ke liye
        avail_str = item.get("availability")
        if avail_str:
            item["availability"] = avail_str.strip()

        return item


# =====================================================================
# 2. PIPELINE: PostgreSQL Storage
# =====================================================================
class PostgresPipeline:

    def __init__(self):
        # ⚠️ APNI DATABASE DETAILS YAHAN UPDATE KAREIN
        self.connection = psycopg2.connect(
            host="localhost",
            database="postgres_books_db",  # PgAdmin me pehle yeh DB bana lein
            user="postgres",  # Aapka postgres username
            password="P0stgree45",  # Aapka postgres password
            port="5432",
        )
        self.cur = self.connection.cursor()

        # Agar table nahi bani hui, toh automatically ban jaye
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS scraped_books(
            id SERIAL PRIMARY KEY,
            title VARCHAR(500),
            price NUMERIC(10, 2),
            rating VARCHAR(50),
            availability VARCHAR(100),
            image_url TEXT
        );
        """)
        self.connection.commit()

    def process_item(self, item, spider):
        # Data ko PostgreSQL table me insert karne ki query
        self.cur.execute(
            """
        INSERT INTO scraped_books (title, price, rating, availability, image_url)
        VALUES (%s, %s, %s, %s, %s);
        """,
            (
                item.get("title"),
                item.get("price"),
                item.get("rating"),
                item.get("availability"),
                item.get("image_url"),
            ),
        )

        self.connection.commit()
        return item

    def close_spider(self, spider):
        # Spider khatam hone par connection close karein
        self.cur.close()
        self.connection.close()
        