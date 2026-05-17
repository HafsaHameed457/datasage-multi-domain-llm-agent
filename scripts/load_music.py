import pandas as pd
from db_connections import pg_engine, mongo_client
from sqlalchemy import text

# --- PostgreSQL ---
tracks = pd.read_csv("data/raw/spotify_tracks.csv")

with pg_engine.begin() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS music"))

cols = ['track_id', 'track_name', 'artists', 'popularity', 'danceability', 'energy', 'valence', 'tempo', 'track_genre']
tracks[cols].rename(columns={'track_id': 'id', 'track_name': 'name'}).to_sql(
    'tracks', pg_engine, schema='music', if_exists='replace', index=False
)

# --- MongoDB (lyrics) ---
try:
    lyrics_df = pd.read_csv("data/raw/songs.csv")  # columns: Song Name, Artist, Lyrics, Mood
    track_ids = tracks['track_id'].tolist()
    lyrics_df['domain_id'] = [int(track_ids[i % len(track_ids)]) for i in range(len(lyrics_df))]

    db = mongo_client['music_db']
    coll = db['lyrics']
    coll.delete_many({})
    coll.insert_many(lyrics_df[['domain_id', 'Song Name', 'Lyrics']].rename(
        columns={'Song Name': 'title', 'Lyrics': 'text'}
    ).to_dict('records'))
    print(f"Inserted {coll.count_documents({})} lyrics.")
except FileNotFoundError:
    print("No songs.csv found – skipping MongoDB for music.")