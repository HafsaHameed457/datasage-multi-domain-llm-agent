import pandas as pd
from db_connections import pg_engine, mongo_client
from sqlalchemy import text
import os

# --- Drop and recreate schema ---
with pg_engine.begin() as conn:
    conn.execute(text("DROP SCHEMA IF EXISTS books CASCADE"))
    conn.execute(text("CREATE SCHEMA books"))

# --- Load Goodreads books CSV ---
try:
    books_df = pd.read_csv(
        "data/raw/books.csv",
        on_bad_lines='skip',
        engine='python'
    )
except Exception as e:
    print("Error loading books.csv:", e)
    exit(1)

# Clean column names
books_df.columns = books_df.columns.str.strip()

# Auto-generate domain_id
books_df.insert(0, 'domain_id', range(1, len(books_df) + 1))

needed_cols = ['domain_id', 'title', 'authors', 'average_rating', 'ratings_count']
existing_cols = [c for c in needed_cols if c in books_df.columns]
books_table = books_df[existing_cols].copy()

books_table.to_sql('books', pg_engine, schema='books', if_exists='replace', index=False)
print(f"PostgreSQL books schema rebuilt with {len(books_table)} rows.")

# --- MongoDB (reviews) ---
db = mongo_client['books_db']
coll = db['reviews']
coll.drop()

reviews_df = None
# Try to load the real reviews file
if os.path.exists("data/raw/amazon_books_reviews_sample_20k.csv"):
    try:
        reviews_df = pd.read_csv(
            "data/raw/amazon_books_reviews_sample_20k.csv",
            on_bad_lines='skip',
            engine='python'
        )
        print("Loaded real reviews file.")
    except Exception as e:
        print("Error reading reviews file, will use synthetic reviews:", e)

docs = []
if reviews_df is not None and not reviews_df.empty:
    # Use real reviews
    domain_ids = books_table['domain_id'].tolist()
    reviews_df['domain_id'] = [str(domain_ids[i % len(domain_ids)]) for i in range(len(reviews_df))]
    for _, row in reviews_df.iterrows():
        review_text = row.get('review_text') or row.get('reviewText', '')
        if review_text:
            docs.append({
                'domain_id': str(row['domain_id']),
                'text': review_text,
                'sentiment': 'neutral'
            })
else:
    print("No reviews file found. Creating synthetic reviews from book data.")
    # Generate one review per book (or a random subset) using title and rating
    for _, book in books_table.iterrows():
        rating = book.get('average_rating', 3.0)
        if rating >= 4.0:
            sentiment = 'positive'
            opinion = "loved it"
        elif rating <= 2.5:
            sentiment = 'negative'
            opinion = "didn't enjoy it"
        else:
            sentiment = 'neutral'
            opinion = "it was okay"

        review_text = f"I {opinion}. The book '{book['title']}' has an average rating of {rating}."
        docs.append({
            'domain_id': str(book['domain_id']),
            'text': review_text,
            'sentiment': sentiment
        })

# At this point docs is guaranteed non‑empty
if docs:
    coll.insert_many(docs)
    print(f"Inserted {coll.count_documents({})} book reviews.")
else:
    print("No reviews to insert – this should not happen.")