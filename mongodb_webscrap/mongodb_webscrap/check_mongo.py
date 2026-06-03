import pymongo

try:
    # MongoDB se connect karein
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    
    # Apne database aur collection ko select karein
    db = client["mongodb_books_db"]
    collection = db["scraped_books"]
    
    # Total documents count check karein
    total_books = collection.count_documents({})
    print(f"\n Total Books in MongoDB: {total_books}\n")
    
    # Shuru ke 5 records print karke dekhein
    print("--- FIRST 5 RECORDS ---")
    for doc in collection.find().limit(5):
        print(f" Title: {doc.get('title')[:30]}...")
        print(f" Price: {doc.get('price')} (Cleaned)")
        print(f" Rating: {doc.get('rating')}")
        print(f" URL: {doc.get('image_url')}")
        print("-" * 40)

except Exception as e:
    print(f" Connection Error: {e}")