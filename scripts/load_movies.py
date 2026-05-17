import pandas as pd
from db_connections import pg_engine, mongo_client
from sqlalchemy import text
import json

# --- PostgreSQL ---
movies_df = pd.read_csv("data/raw/tmdb_5000_movies.csv")

with pg_engine.begin() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS movies"))

# Movies table
cols = ['id', 'title', 'release_date', 'budget', 'revenue', 'vote_average', 'popularity']
movies_df[cols].to_sql('movies', pg_engine, schema='movies', if_exists='replace', index=False)

# Extract genres from JSON
genres_json = movies_df['genres'].apply(json.loads)
genres_set = set()
for lst in genres_json:
    for g in lst:
        genres_set.add((g['id'], g['name']))
genres_df = pd.DataFrame(list(genres_set), columns=['id', 'name'])
genres_df.to_sql('genres', pg_engine, schema='movies', if_exists='replace', index=False)

# Movie-genre join table
movie_genres_rows = []
for _, row in movies_df.iterrows():
    movie_id = row['id']
    for g in json.loads(row['genres']):
        movie_genres_rows.append({'movie_id': movie_id, 'genre_id': g['id']})
movie_genres_df = pd.DataFrame(movie_genres_rows)
movie_genres_df.to_sql('movie_genres', pg_engine, schema='movies', if_exists='replace', index=False)

# --- MongoDB ---
reviews_df = pd.read_csv("data/raw/IMDB Dataset.csv")  # columns: review, sentiment
movie_ids = movies_df['id'].tolist()
reviews_df['domain_id'] = [int(movie_ids[i % len(movie_ids)]) for i in range(len(reviews_df))]

db = mongo_client['movies_db']
coll = db['reviews']
coll.delete_many({})
coll.insert_many(reviews_df[['domain_id', 'review', 'sentiment']].rename(columns={'review': 'text'}).to_dict('records'))
print(f"Inserted {coll.count_documents({})} movie reviews.")