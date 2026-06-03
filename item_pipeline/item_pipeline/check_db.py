import os
import sqlite3

# Yeh line automatic aapki file jahan padi hai, wahan ka rasta nikal legi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "books_data.db")

print(f"Dhoond raha hoon database ko yahan: {db_path}")

if not os.path.exists(db_path):
    print(
        " Database file hi nahi mili! Iska matlab pehle 'scrapy crawl books' sahi se run nahi hua."
    )
else:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    try:
        cur.execute("SELECT * FROM books LIMIT 5;")
        rows = cur.fetchall()

        print("\n--- DATABASE DATA ---")
        if not rows:
            print("Database khali hai!")
        else:
            for row in rows:
                print(
                    f"ID: {row[0]} | Title: {row[1][:20]}... | Price: {row[2]} | Rating: {row[3]}"
                )
    except sqlite3.OperationalError as e:
        print(f" Table Error: {e}")
        print(
            "Tip: settings.py me check karein ki ITEM_PIPELINES uncommented aur active ho!"
        )

    con.close()