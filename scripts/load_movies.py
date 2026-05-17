import pandas as pd
from db_connections import pg_engine, mongo_client
from sqlalchemy import text
import json

# --- Drop and recreate schema ---
with pg_engine.begin() as conn:
    conn.execute(text("DROP SCHEMA IF EXISTS movies CASCADE"))
    conn.execute(text("CREATE SCHEMA movies"))

# --- Load CSV ---
movies_df = pd.read_csv("data/raw/tmdb_5000_movies.csv")

# Movies table (rename id to domain_id)
movies_table = movies_df[['id', 'title', 'release_date', 'budget', 'revenue', 'vote_average', 'popularity']].rename(
    columns={'id': 'domain_id'}
)
movies_table.to_sql('movies', pg_engine, schema='movies', if_exists='replace', index=False)

# Genres table
genres_json = movies_df['genres'].apply(json.loads)
genres_set = set()
for lst in genres_json:
    for g in lst:
        genres_set.add((g['id'], g['name']))
genres_df = pd.DataFrame(list(genres_set), columns=['id', 'name'])
genres_df.to_sql('genres', pg_engine, schema='movies', if_exists='replace', index=False)

# Join table (movie_genres) – use domain_id
movie_genres_rows = []
for _, row in movies_df.iterrows():
    domain_id = row['id']
    for g in json.loads(row['genres']):
        movie_genres_rows.append({'domain_id': domain_id, 'genre_id': g['id']})
movie_genres_df = pd.DataFrame(movie_genres_rows)
movie_genres_df.to_sql('movie_genres', pg_engine, schema='movies', if_exists='replace', index=False)

print("PostgreSQL movies schema rebuilt.")

# --- MongoDB ---
reviews_df = pd.read_csv("data/raw/IMDB Dataset.csv")
movie_ids = movies_df['id'].tolist()                     # still called 'id' in the raw CSV
reviews_df['domain_id'] = [str(movie_ids[i % len(movie_ids)]) for i in range(len(reviews_df))]

db = mongo_client['movies_db']
coll = db['reviews']
coll.drop()                                              # empty collection
coll.insert_many(
    reviews_df[['domain_id', 'review', 'sentiment']]
    .rename(columns={'review': 'text'})
    .to_dict('records')
)
print(f"Inserted {coll.count_documents({})} movie reviews.")