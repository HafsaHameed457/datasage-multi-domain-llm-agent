import pandas as pd
from db_connections import pg_engine, mongo_client
from sqlalchemy import text

# --- Drop and recreate schema ---
with pg_engine.begin() as conn:
    conn.execute(text("DROP SCHEMA IF EXISTS music CASCADE"))
    conn.execute(text("CREATE SCHEMA music"))

# --- Load tracks CSV (Spotify) ---
tracks = pd.read_csv("data/raw/spotify_tracks.csv")

# Tracks table – rename track_id to domain_id
cols = ['track_id', 'track_name', 'artists', 'popularity', 'danceability', 'energy', 'valence', 'tempo', 'track_genre']
tracks_table = tracks[cols].rename(columns={'track_id': 'domain_id', 'track_name': 'name'})
tracks_table.to_sql('tracks', pg_engine, schema='music', if_exists='replace', index=False)

print("PostgreSQL music schema rebuilt.")

# --- MongoDB (lyrics) ---
try:
    lyrics_df = pd.read_csv("data/raw/songs.csv")
    lyrics_df.columns = lyrics_df.columns.str.lower().str.strip()

    # Auto-detect columns
    song_col = next((c for c in lyrics_df.columns if 'song' in c), None)
    lyric_col = next((c for c in lyrics_df.columns if 'lyric' in c), None)

    if not song_col or not lyric_col:
        print("Lyrics columns not recognised, skipping MongoDB. Found:", lyrics_df.columns.tolist())
    else:
        track_ids = tracks['track_id'].tolist()
        lyrics_df['domain_id'] = [str(track_ids[i % len(track_ids)]) for i in range(len(lyrics_df))]

        db = mongo_client['music_db']
        coll = db['lyrics']
        coll.drop()
        docs = [
            {
                'domain_id': str(row['domain_id']),
                'title': str(row[song_col]),
                'text': str(row[lyric_col]),
            }
            for _, row in lyrics_df.iterrows()
        ]
        coll.insert_many(docs)
        print(f"Inserted {coll.count_documents({})} lyrics.")
except FileNotFoundError:
    print("No songs.csv found – skipping MongoDB for music.")