"""
ETL Ingestion Script for MovieAnalytics
Extracts, cleans, normalizes, and loads Kaggle's 'The Movies Dataset' (movies_metadata.csv)
into the 3NF relational schema (Movie, Genre, MovieGenre).
"""

import os
import ast
import json
import argparse
import pandas as pd
from typing import List, Dict, Any, Tuple
from config import DBConfig
from database import DatabaseManager


def parse_genres(genre_field: Any) -> List[Dict[str, Any]]:
    """Safely extracts genre dictionaries from JSON or Python string representation."""
    if not genre_field or pd.isna(genre_field):
        return []
    if isinstance(genre_field, list):
        return genre_field
    try:
        return json.loads(genre_field)
    except Exception:
        try:
            return ast.literal_eval(str(genre_field))
        except Exception:
            return []


def clean_movies_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Cleans raw movies_metadata.csv and normalizes it into 3 relational tables:
    1. Genre (genre_id, genre_name)
    2. Movie (tmdb_id, title, release_date, budget, revenue, runtime, vote_average, vote_count)
    3. MovieGenre (tmdb_id, genre_id)
    """
    print(f"[*] Processing {len(df)} raw movie records...")

    # Ensure required columns exist
    required_cols = ["id", "title", "release_date", "budget", "revenue", "runtime", "vote_average", "vote_count", "genres"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # 1. Clean TMDb IDs (discard corrupted rows in Kaggle dataset)
    df["tmdb_id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["tmdb_id"])
    df["tmdb_id"] = df["tmdb_id"].astype(int)

    # 2. Clean Titles
    df["title"] = df["title"].fillna("Untitled").astype(str).str.strip()
    df["title"] = df["title"].apply(lambda t: t[:250])  # ensure within VARCHAR(255)

    # 3. Clean Release Date
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # 4. Clean Financials & Metrics
    df["budget"] = pd.to_numeric(df["budget"], errors="coerce").fillna(0).astype(int)
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0).astype(int)
    df["runtime"] = pd.to_numeric(df["runtime"], errors="coerce").round(2)
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").round(1)
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0).astype(int)

    # De-duplicate movies by tmdb_id
    df_movies = df.drop_duplicates(subset=["tmdb_id"])[
        ["tmdb_id", "title", "release_date", "budget", "revenue", "runtime", "vote_average", "vote_count"]
    ].copy()

    # 5. Extract Normalized Genres and Bridge Relationships
    genres_dict = {}
    movie_genre_pairs = set()

    for _, row in df.iterrows():
        movie_id = row["tmdb_id"]
        parsed = parse_genres(row["genres"])
        for g in parsed:
            if isinstance(g, dict) and "id" in g and "name" in g:
                try:
                    gid = int(g["id"])
                    gname = str(g["name"]).strip()
                    if gid and gname:
                        genres_dict[gid] = gname
                        movie_genre_pairs.add((movie_id, gid))
                except (ValueError, TypeError):
                    continue

    df_genres = pd.DataFrame(
        [{"genre_id": gid, "genre_name": gname} for gid, gname in genres_dict.items()]
    )
    df_movie_genres = pd.DataFrame(
        list(movie_genre_pairs), columns=["tmdb_id", "genre_id"]
    )

    print(f"[+] Cleaned successfully:")
    print(f"    - Unique Movies: {len(df_movies)}")
    print(f"    - Unique Genres: {len(df_genres)}")
    print(f"    - Movie-Genre Mappings: {len(df_movie_genres)}")

    return df_movies, df_genres, df_movie_genres


def create_sample_csv_if_missing(file_path: str):
    """Generates a realistic Kaggle-style sample CSV if movies_metadata.csv is absent."""
    if os.path.exists(file_path):
        return

    print(f"[*] Generating realistic Kaggle sample dataset at: {file_path}")
    sample_records = [
        {"id": 19995, "title": "Avatar", "release_date": "2009-12-10", "budget": 237000000, "revenue": 2787965087, "runtime": 162.0, "vote_average": 7.2, "vote_count": 11800, "genres": "[{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}, {'id': 14, 'name': 'Fantasy'}, {'id': 878, 'name': 'Science Fiction'}]"},
        {"id": 597, "title": "Titanic", "release_date": "1997-11-18", "budget": 200000000, "revenue": 1845034188, "runtime": 194.0, "vote_average": 7.5, "vote_count": 7562, "genres": "[{'id': 18, 'name': 'Drama'}, {'id': 10749, 'name': 'Romance'}]"},
        {"id": 27205, "title": "Inception", "release_date": "2010-07-14", "budget": 160000000, "revenue": 825532764, "runtime": 148.0, "vote_average": 8.1, "vote_count": 13752, "genres": "[{'id': 28, 'name': 'Action'}, {'id': 878, 'name': 'Science Fiction'}, {'id': 12, 'name': 'Adventure'}]"},
        {"id": 155, "title": "The Dark Knight", "release_date": "2008-07-16", "budget": 185000000, "revenue": 1004558444, "runtime": 152.0, "vote_average": 8.2, "vote_count": 12002, "genres": "[{'id': 18, 'name': 'Drama'}, {'id': 28, 'name': 'Action'}, {'id': 80, 'name': 'Crime'}, {'id': 53, 'name': 'Thriller'}]"},
        {"id": 680, "title": "Pulp Fiction", "release_date": "1994-09-10", "budget": 8000000, "revenue": 213928762, "runtime": 154.0, "vote_average": 8.3, "vote_count": 8428, "genres": "[{'id': 53, 'name': 'Thriller'}, {'id': 80, 'name': 'Crime'}]"},
        {"id": 238, "title": "The Godfather", "release_date": "1972-03-14", "budget": 6000000, "revenue": 245066411, "runtime": 175.0, "vote_average": 8.5, "vote_count": 5893, "genres": "[{'id': 18, 'name': 'Drama'}, {'id': 80, 'name': 'Crime'}]"},
        {"id": 278, "title": "The Shawshank Redemption", "release_date": "1994-09-23", "budget": 25000000, "revenue": 28341469, "runtime": 142.0, "vote_average": 8.5, "vote_count": 8205, "genres": "[{'id': 18, 'name': 'Drama'}, {'id': 80, 'name': 'Crime'}]"},
        {"id": 157336, "title": "Interstellar", "release_date": "2014-11-05", "budget": 165000000, "revenue": 675120017, "runtime": 169.0, "vote_average": 8.1, "vote_count": 10867, "genres": "[{'id': 12, 'name': 'Adventure'}, {'id': 18, 'name': 'Drama'}, {'id': 878, 'name': 'Science Fiction'}]"},
        {"id": 24428, "title": "The Avengers", "release_date": "2012-04-25", "budget": 220000000, "revenue": 1519557910, "runtime": 143.0, "vote_average": 7.4, "vote_count": 11776, "genres": "[{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}, {'id': 878, 'name': 'Science Fiction'}]"},
        {"id": 862, "title": "Toy Story", "release_date": "1995-10-30", "budget": 30000000, "revenue": 373554033, "runtime": 81.0, "vote_average": 7.7, "vote_count": 5269, "genres": "[{'id': 16, 'name': 'Animation'}, {'id': 35, 'name': 'Comedy'}, {'id': 10751, 'name': 'Family'}]"},
        {"id": 329, "title": "Jurassic Park", "release_date": "1993-06-11", "budget": 63000000, "revenue": 920100000, "runtime": 127.0, "vote_average": 7.6, "vote_count": 4856, "genres": "[{'id': 12, 'name': 'Adventure'}, {'id': 878, 'name': 'Science Fiction'}]"},
        {"id": 13, "title": "Forrest Gump", "release_date": "1994-07-06", "budget": 55000000, "revenue": 677945399, "runtime": 142.0, "vote_average": 8.2, "vote_count": 7927, "genres": "[{'id': 35, 'name': 'Comedy'}, {'id': 18, 'name': 'Drama'}, {'id': 10749, 'name': 'Romance'}]"},
        {"id": 603, "title": "The Matrix", "release_date": "1999-03-30", "budget": 63000000, "revenue": 463517383, "runtime": 136.0, "vote_average": 7.9, "vote_count": 8907, "genres": "[{'id': 28, 'name': 'Action'}, {'id': 878, 'name': 'Science Fiction'}]"},
        {"id": 550, "title": "Fight Club", "release_date": "1999-10-15", "budget": 63000000, "revenue": 100853753, "runtime": 139.0, "vote_average": 8.3, "vote_count": 9413, "genres": "[{'id': 18, 'name': 'Drama'}]"},
        {"id": 129, "title": "Spirited Away", "release_date": "2001-07-20", "budget": 15000000, "revenue": 274925095, "runtime": 125.0, "vote_average": 8.3, "vote_count": 3840, "genres": "[{'id': 16, 'name': 'Animation'}, {'id': 10751, 'name': 'Family'}, {'id': 14, 'name': 'Fantasy'}]"},
        {"id": 354912, "title": "Coco", "release_date": "2017-10-27", "budget": 175000000, "revenue": 807082196, "runtime": 105.0, "vote_average": 8.2, "vote_count": 17000, "genres": "[{'id': 16, 'name': 'Animation'}, {'id': 10751, 'name': 'Family'}, {'id': 10402, 'name': 'Music'}, {'id': 12, 'name': 'Adventure'}]"},
        {"id": 496243, "title": "Parasite", "release_date": "2019-05-30", "budget": 11400000, "revenue": 258773045, "runtime": 132.0, "vote_average": 8.5, "vote_count": 16000, "genres": "[{'id': 35, 'name': 'Comedy'}, {'id': 53, 'name': 'Thriller'}, {'id': 18, 'name': 'Drama'}]"},
        {"id": 98, "title": "Gladiator", "release_date": "2000-05-01", "budget": 103000000, "revenue": 457640427, "runtime": 155.0, "vote_average": 7.9, "vote_count": 5439, "genres": "[{'id': 28, 'name': 'Action'}, {'id': 18, 'name': 'Drama'}, {'id': 12, 'name': 'Adventure'}]"},
        {"id": 105, "title": "Back to the Future", "release_date": "1985-07-03", "budget": 19000000, "revenue": 381109762, "runtime": 116.0, "vote_average": 8.0, "vote_count": 6079, "genres": "[{'id': 12, 'name': 'Adventure'}, {'id': 35, 'name': 'Comedy'}, {'id': 878, 'name': 'Science Fiction'}, {'id': 10751, 'name': 'Family'}]"},
        {"id": 120, "title": "The Lord of the Rings: The Fellowship of the Ring", "release_date": "2001-12-18", "budget": 93000000, "revenue": 871368364, "runtime": 178.0, "vote_average": 8.0, "vote_count": 8770, "genres": "[{'id': 12, 'name': 'Adventure'}, {'id': 14, 'name': 'Fantasy'}, {'id': 28, 'name': 'Action'}]"},
        {"id": 122, "title": "The Lord of the Rings: The Return of the King", "release_date": "2003-12-01", "budget": 94000000, "revenue": 1118888979, "runtime": 201.0, "vote_average": 8.1, "vote_count": 8064, "genres": "[{'id': 12, 'name': 'Adventure'}, {'id': 14, 'name': 'Fantasy'}, {'id': 28, 'name': 'Action'}]"},
        {"id": 299536, "title": "Avengers: Infinity War", "release_date": "2018-04-25", "budget": 300000000, "revenue": 2048359754, "runtime": 149.0, "vote_average": 8.3, "vote_count": 27000, "genres": "[{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}, {'id': 878, 'name': 'Science Fiction'}]"},
        {"id": 299534, "title": "Avengers: Endgame", "release_date": "2019-04-24", "budget": 356000000, "revenue": 2797800564, "runtime": 181.0, "vote_average": 8.3, "vote_count": 23000, "genres": "[{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}, {'id': 878, 'name': 'Science Fiction'}]"},
        {"id": 49026, "title": "The Dark Knight Rises", "release_date": "2012-07-16", "budget": 250000000, "revenue": 1084939099, "runtime": 165.0, "vote_average": 7.6, "vote_count": 9106, "genres": "[{'id': 28, 'name': 'Action'}, {'id': 80, 'name': 'Crime'}, {'id': 18, 'name': 'Drama'}, {'id': 53, 'name': 'Thriller'}]"},
        {"id": 77, "title": "Memento", "release_date": "2000-10-11", "budget": 9000000, "revenue": 39723096, "runtime": 113.0, "vote_average": 8.1, "vote_count": 4028, "genres": "[{'id': 9648, 'name': 'Mystery'}, {'id': 53, 'name': 'Thriller'}]"},
        {"id": 11, "title": "Star Wars", "release_date": "1977-05-25", "budget": 11000000, "revenue": 775398007, "runtime": 121.0, "vote_average": 8.1, "vote_count": 6624, "genres": "[{'id': 12, 'name': 'Adventure'}, {'id': 28, 'name': 'Action'}, {'id': 878, 'name': 'Science Fiction'}]"},
        {"id": 1891, "title": "The Empire Strikes Back", "release_date": "1980-05-17", "budget": 18000000, "revenue": 538400000, "runtime": 124.0, "vote_average": 8.2, "vote_count": 5879, "genres": "[{'id': 12, 'name': 'Adventure'}, {'id': 28, 'name': 'Action'}, {'id': 878, 'name': 'Science Fiction'}]"},
        {"id": 598, "title": "City of God", "release_date": "2002-02-05", "budget": 3300000, "revenue": 30595293, "runtime": 130.0, "vote_average": 8.1, "vote_count": 1814, "genres": "[{'id': 18, 'name': 'Drama'}, {'id': 80, 'name': 'Crime'}]"},
        {"id": 694, "title": "The Shining", "release_date": "1980-05-22", "budget": 19000000, "revenue": 44017374, "runtime": 144.0, "vote_average": 8.1, "vote_count": 3790, "genres": "[{'id': 27, 'name': 'Horror'}, {'id': 53, 'name': 'Thriller'}]"},
        {"id": 424, "title": "Schindler's List", "release_date": "1993-11-29", "budget": 22000000, "revenue": 321365567, "runtime": 195.0, "vote_average": 8.3, "vote_count": 4329, "genres": "[{'id': 18, 'name': 'Drama'}, {'id': 36, 'name': 'History'}, {'id': 10752, 'name': 'War'}]"}
    ]
    pd.DataFrame(sample_records).to_csv(file_path, index=False)
    print(f"[+] Sample Kaggle dataset created with {len(sample_records)} entries.")


def load_into_mysql(df_movies: pd.DataFrame, df_genres: pd.DataFrame, df_movie_genres: pd.DataFrame, config: DBConfig):
    """Loads normalized DataFrames into MySQL database."""
    print(f"[*] Connecting to MySQL ({config.database}@{config.host}:{config.port})...")
    import mysql.connector

    conn = mysql.connector.connect(**config.connection_dict)
    cursor = conn.cursor()

    # 1. Insert Genres
    print("[*] Inserting Genres...")
    genre_sql = "INSERT INTO Genre (genre_id, genre_name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE genre_name=VALUES(genre_name);"
    genre_data = [tuple(x) for x in df_genres[["genre_id", "genre_name"]].values]
    cursor.executemany(genre_sql, genre_data)
    conn.commit()

    # 2. Insert Movies
    print("[*] Inserting Movies...")
    movie_sql = """
    INSERT INTO Movie (tmdb_id, title, release_date, budget, revenue, runtime, vote_average, vote_count)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        title=VALUES(title),
        release_date=VALUES(release_date),
        budget=VALUES(budget),
        revenue=VALUES(revenue),
        runtime=VALUES(runtime),
        vote_average=VALUES(vote_average),
        vote_count=VALUES(vote_count);
    """
    movie_data = []
    for _, row in df_movies.iterrows():
        movie_data.append((
            int(row["tmdb_id"]),
            str(row["title"]),
            row["release_date"] if pd.notnull(row["release_date"]) else None,
            int(row["budget"]) if pd.notnull(row["budget"]) else None,
            int(row["revenue"]) if pd.notnull(row["revenue"]) else None,
            float(row["runtime"]) if pd.notnull(row["runtime"]) else None,
            float(row["vote_average"]) if pd.notnull(row["vote_average"]) else None,
            int(row["vote_count"]) if pd.notnull(row["vote_count"]) else None
        ))
    cursor.executemany(movie_sql, movie_data)
    conn.commit()

    # 3. Insert MovieGenre links
    print("[*] Inserting MovieGenre mappings...")
    mg_sql = "INSERT IGNORE INTO MovieGenre (tmdb_id, genre_id) VALUES (%s, %s);"
    mg_data = [tuple(x) for x in df_movie_genres[["tmdb_id", "genre_id"]].values]
    cursor.executemany(mg_sql, mg_data)
    conn.commit()

    cursor.close()
    conn.close()
    print("[+] ETL successfully completed! Data loaded into MySQL.")


def main():
    parser = argparse.ArgumentParser(description="ETL Loader for Kaggle The Movies Dataset into MovieAnalytics MySQL DB")
    parser.add_argument("--csv", type=str, default="movies_metadata.csv", help="Path to movies_metadata.csv")
    parser.add_argument("--target", type=str, default="mysql", choices=["mysql", "sqlite"], help="Target DB")
    args = parser.parse_args()

    # If user-specified file doesn't exist, fallback to sample
    csv_file = args.csv
    if not os.path.exists(csv_file):
        sample_path = os.path.join(os.path.dirname(__file__), "sample_movies_metadata.csv")
        create_sample_csv_if_missing(sample_path)
        csv_file = sample_path

    print(f"[*] Reading data from {csv_file}...")
    # Low memory=False handles mixed types in Kaggle CSV
    df_raw = pd.read_csv(csv_file, low_memory=False)

    df_movies, df_genres, df_movie_genres = clean_movies_dataframe(df_raw)

    if args.target == "mysql":
        config = DBConfig()
        load_into_mysql(df_movies, df_genres, df_movie_genres, config)
    else:
        # SQLite demo loader
        db_mgr = DatabaseManager(use_sqlite_demo=True)
        print("[+] Demo SQLite DB ready.")


if __name__ == "__main__":
    main()
