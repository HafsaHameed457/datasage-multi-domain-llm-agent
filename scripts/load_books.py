import pandas as pd
from db_connections import pg_engine, mongo_client
from sqlalchemy import text

# --- PostgreSQL ---
books_df = pd.read_csv("data/raw/books.csv")  # Goodreads

with pg_engine.begin() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS books"))

cols = ['book_id', 'title', 'authors', 'average_rating', 'ratings_count']
books_df[cols].rename(columns={'book_id': 'id'}).to_sql(
    'books', pg_engine, schema='books', if_exists='replace', index=False
)

# --- MongoDB (reviews) ---
reviews_df = pd.read_csv("data/raw/amazon_books_reviews_sample_20k.csv")

book_ids = books_df['id'].tolist()
reviews_df['domain_id'] = [int(book_ids[i % len(book_ids)]) for i in range(len(reviews_df))]

db = mongo_client['books_db']
coll = db['reviews']
coll.delete_many({})
docs = []
for _, row in reviews_df.iterrows():
    review_text = row.get('review_text') or row.get('reviewText', '')
    if review_text:
        docs.append({
            'domain_id': int(row['domain_id']),
            'text': review_text,
            'sentiment': 'neutral'
        })

coll.insert_many(docs)
print(f"Inserted {coll.count_documents({})} book reviews.")