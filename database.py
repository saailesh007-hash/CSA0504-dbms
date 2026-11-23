"""
Database Layer for MovieAnalytics
Handles MySQL database connections, failover demo storage (SQLite), and the 10 Analytical Reports.
"""

import os
import sqlite3
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
from config import DBConfig

# SQL queries defined as constants matching MySQL standards
SQL_R01_MOVIES_BY_YEAR = """
SELECT 
    YEAR(release_date) AS release_year, 
    COUNT(*) AS movie_count 
FROM Movie 
WHERE release_date IS NOT NULL 
GROUP BY YEAR(release_date) 
ORDER BY release_year ASC;
"""

SQL_R02_AVG_RATING_BY_GENRE = """
SELECT 
    g.genre_name, 
    ROUND(AVG(m.vote_average), 2) AS avg_tmdb_rating,
    COUNT(m.tmdb_id) AS movie_count
FROM Genre g
JOIN MovieGenre mg ON g.genre_id = mg.genre_id
JOIN Movie m ON mg.tmdb_id = m.tmdb_id
WHERE m.vote_average IS NOT NULL
GROUP BY g.genre_id, g.genre_name
ORDER BY avg_tmdb_rating DESC;
"""

SQL_R03_TOP_MOVIES_BY_RATING = """
SELECT 
    m.tmdb_id, 
    m.title, 
    YEAR(m.release_date) AS release_year,
    m.vote_average, 
    m.vote_count,
    m.revenue,
    m.budget
FROM Movie m
WHERE m.vote_average IS NOT NULL 
  AND m.vote_count >= {min_votes}
ORDER BY m.vote_average DESC, m.vote_count DESC
LIMIT {limit};
"""

SQL_R04_REVENUE_BY_YEAR = """
SELECT 
    YEAR(release_date) AS release_year, 
    SUM(revenue) AS total_revenue,
    COUNT(*) AS movie_count,
    ROUND(AVG(revenue), 2) AS avg_revenue
FROM Movie 
WHERE release_date IS NOT NULL AND revenue > 0
GROUP BY YEAR(release_date) 
ORDER BY release_year ASC;
"""

SQL_R05_REVENUE_BY_GENRE = """
SELECT 
    g.genre_name, 
    SUM(m.revenue) AS total_revenue,
    COUNT(m.tmdb_id) AS movie_count,
    ROUND(AVG(m.revenue), 2) AS avg_revenue
FROM Genre g
JOIN MovieGenre mg ON g.genre_id = mg.genre_id
JOIN Movie m ON mg.tmdb_id = m.tmdb_id
WHERE m.revenue > 0
GROUP BY g.genre_id, g.genre_name
ORDER BY total_revenue DESC;
"""

SQL_R06_BUDGET_VS_REVENUE = """
SELECT 
    tmdb_id, 
    title, 
    YEAR(release_date) AS release_year,
    budget, 
    revenue, 
    (revenue - budget) AS gap,
    CASE 
        WHEN budget > 0 THEN ROUND(((revenue - budget) * 100.0 / budget), 2)
        ELSE NULL 
    END AS gap_pct
FROM Movie 
WHERE budget > 0 AND revenue > 0
ORDER BY gap DESC;
"""

SQL_R07_RATING_DISTRIBUTION = """
SELECT 
    CONCAT(FLOOR(vote_average), '.0 - ', FLOOR(vote_average) + 0.9) AS rating_interval,
    FLOOR(vote_average) AS interval_lower,
    COUNT(*) AS movie_count
FROM Movie 
WHERE vote_average IS NOT NULL
GROUP BY FLOOR(vote_average)
ORDER BY interval_lower ASC;
"""

SQL_R08_MOST_VOTED_MOVIES = """
SELECT 
    tmdb_id, 
    title, 
    YEAR(release_date) AS release_year,
    vote_count, 
    vote_average,
    revenue
FROM Movie 
WHERE vote_count IS NOT NULL
ORDER BY vote_count DESC 
LIMIT {limit};
"""

SQL_R09_MOVIE_COUNT_BY_GENRE = """
SELECT 
    g.genre_name, 
    COUNT(DISTINCT mg.tmdb_id) AS movie_count
FROM Genre g
LEFT JOIN MovieGenre mg ON g.genre_id = mg.genre_id
GROUP BY g.genre_id, g.genre_name
ORDER BY movie_count DESC;
"""

SQL_R10_AVG_RUNTIME_BY_GENRE = """
SELECT 
    g.genre_name, 
    ROUND(AVG(m.runtime), 2) AS avg_runtime,
    COUNT(m.tmdb_id) AS movie_count
FROM Genre g
JOIN MovieGenre mg ON g.genre_id = mg.genre_id
JOIN Movie m ON mg.tmdb_id = m.tmdb_id
WHERE m.runtime IS NOT NULL AND m.runtime > 0
GROUP BY g.genre_id, g.genre_name
ORDER BY avg_runtime DESC;
"""


class DatabaseManager:
    """Manages database connection and queries across MySQL and SQLite Demo fallback."""

    def __init__(self, config: Optional[DBConfig] = None, use_sqlite_demo: bool = False):
        self.config = config or DBConfig()
        self.use_sqlite_demo = use_sqlite_demo
        self.sqlite_path = os.path.join(os.path.dirname(__file__), "movie_analytics_demo.db")
        if self.use_sqlite_demo:
            self._ensure_sqlite_demo_db()

    def get_mysql_connection(self):
        """Attempts to connect to MySQL using mysql.connector or pymysql."""
        try:
            import mysql.connector
            return mysql.connector.connect(**self.config.connection_dict)
        except ImportError:
            try:
                import pymysql
                return pymysql.connect(**self.config.connection_dict)
            except ImportError:
                raise RuntimeError(
                    "No MySQL driver found! Install either 'mysql-connector-python' or 'pymysql'."
                )

    def test_connection(self) -> Tuple[bool, str]:
        """Tests if the database connection succeeds."""
        if self.use_sqlite_demo:
            return True, f"Connected to Demo SQLite Database ({os.path.basename(self.sqlite_path)})"
        try:
            conn = self.get_mysql_connection()
            conn.close()
            return True, f"Connected to MySQL: {self.config.database}@{self.config.host}:{self.config.port}"
        except Exception as e:
            return False, f"MySQL Connection Error: {str(e)}"

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Executes a SQL query and returns a pandas DataFrame with automatic fallback."""
        if self.use_sqlite_demo:
            return self._execute_sqlite_query(query, params)

        try:
            conn = self.get_mysql_connection()
            try:
                df = pd.read_sql(query, conn, params=params)
                return df
            finally:
                conn.close()
        except Exception:
            # Automatically fallback to demo database if MySQL server is unreachable
            self.use_sqlite_demo = True
            self._ensure_sqlite_demo_db()
            return self._execute_sqlite_query(query, params)

    def _execute_sqlite_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Adapts MySQL query dialect functions for SQLite demo fallback."""
        adapted = query.replace("YEAR(release_date)", "CAST(strftime('%Y', release_date) AS INTEGER)")
        adapted = adapted.replace("YEAR(m.release_date)", "CAST(strftime('%Y', m.release_date) AS INTEGER)")
        adapted = adapted.replace(
            "CONCAT(FLOOR(vote_average), '.0 - ', FLOOR(vote_average) + 0.9)",
            "(CAST(ROUND(vote_average - 0.5) AS TEXT) || '.0 - ' || CAST(ROUND(vote_average - 0.5) + 0.9 AS TEXT))"
        )
        adapted = adapted.replace("FLOOR(vote_average)", "CAST(ROUND(vote_average - 0.5) AS INTEGER)")
        
        conn = sqlite3.connect(self.sqlite_path)
        try:
            df = pd.read_sql_query(adapted, conn, params=params)
            return df
        finally:
            conn.close()

    def _ensure_sqlite_demo_db(self):
        """Creates the local demo SQLite DB seeded with data if not already existing."""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()

        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Movie (
            tmdb_id INT PRIMARY KEY,
            title TEXT NOT NULL,
            release_date TEXT,
            budget INTEGER,
            revenue INTEGER,
            runtime REAL,
            vote_average REAL,
            vote_count INTEGER
        );

        CREATE TABLE IF NOT EXISTS Genre (
            genre_id INT PRIMARY KEY,
            genre_name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS MovieGenre (
            tmdb_id INT,
            genre_id INT,
            PRIMARY KEY (tmdb_id, genre_id),
            FOREIGN KEY (tmdb_id) REFERENCES Movie(tmdb_id),
            FOREIGN KEY (genre_id) REFERENCES Genre(genre_id)
        );
        """)

        # Check if already seeded
        row_count = cursor.execute("SELECT COUNT(*) FROM Movie").fetchone()[0]
        if row_count > 0:
            conn.close()
            return

        # Seed from sample CSV using etl_loader
        csv_path = os.path.join(os.path.dirname(__file__), "sample_movies_metadata.csv")
        if os.path.exists(csv_path):
            import etl_loader
            df_raw = pd.read_csv(csv_path, low_memory=False)
            df_movies, df_genres, df_movie_genres = etl_loader.clean_movies_dataframe(df_raw)
            df_genres.to_sql("Genre", conn, if_exists="append", index=False)
            df_movies.to_sql("Movie", conn, if_exists="append", index=False)
            df_movie_genres.to_sql("MovieGenre", conn, if_exists="append", index=False)
            conn.commit()

        conn.close()

    # -------------------------------------------------------------------------
    # Core Metadata & Filter Lookups
    # -------------------------------------------------------------------------
    def get_filter_options(self) -> Dict[str, Any]:
        """Returns bounds for years and list of genres for UI filters."""
        query_years = "SELECT MIN(YEAR(release_date)) AS min_year, MAX(YEAR(release_date)) AS max_year FROM Movie WHERE release_date IS NOT NULL;"
        df_years = self.execute_query(query_years)
        
        query_genres = "SELECT genre_name FROM Genre ORDER BY genre_name;"
        df_genres = self.execute_query(query_genres)
        
        min_year = int(df_years["min_year"].iloc[0]) if not df_years.empty and pd.notnull(df_years["min_year"].iloc[0]) else 1970
        max_year = int(df_years["max_year"].iloc[0]) if not df_years.empty and pd.notnull(df_years["max_year"].iloc[0]) else 2024
        genres = df_genres["genre_name"].tolist() if not df_genres.empty else []
        
        return {
            "min_year": min_year,
            "max_year": max_year,
            "genres": genres
        }

    # -------------------------------------------------------------------------
    # KPI Metrics
    # -------------------------------------------------------------------------
    def get_kpis(self, min_year: int, max_year: int, selected_genres: Optional[List[str]] = None) -> Dict[str, Any]:
        """Computes Total Movies, Total Genres, Mean TMDb Rating, Total Positive Revenue."""
        where_clauses = ["m.release_date IS NOT NULL", f"YEAR(m.release_date) BETWEEN {min_year} AND {max_year}"]
        
        if selected_genres:
            genres_formatted = ", ".join([f"'{g}'" for g in selected_genres])
            where_clauses.append(f"g.genre_name IN ({genres_formatted})")
            
        where_str = " AND ".join(where_clauses)
        
        query = f"""
        SELECT 
            COUNT(DISTINCT m.tmdb_id) AS total_movies,
            COUNT(DISTINCT g.genre_id) AS total_genres,
            ROUND(AVG(m.vote_average), 2) AS mean_rating,
            COALESCE(SUM(CASE WHEN m.revenue > 0 THEN m.revenue ELSE 0 END), 0) AS total_revenue
        FROM Movie m
        LEFT JOIN MovieGenre mg ON m.tmdb_id = mg.tmdb_id
        LEFT JOIN Genre g ON mg.genre_id = g.genre_id
        WHERE {where_str};
        """
        df = self.execute_query(query)
        if not df.empty:
            row = df.iloc[0]
            return {
                "total_movies": int(row["total_movies"] or 0),
                "total_genres": int(row["total_genres"] or 0),
                "mean_rating": float(row["mean_rating"] or 0.0),
                "total_revenue": int(row["total_revenue"] or 0)
            }
        return {"total_movies": 0, "total_genres": 0, "mean_rating": 0.0, "total_revenue": 0}

    # -------------------------------------------------------------------------
    # Catalogue Query
    # -------------------------------------------------------------------------
    def get_catalogue(self, min_year: int, max_year: int, selected_genres: Optional[List[str]] = None,
                      min_rating: float = 0.0, search_title: str = "") -> pd.DataFrame:
        """Retrieves filtered movie catalogue records with grouped genre names."""
        where_clauses = [
            f"YEAR(m.release_date) BETWEEN {min_year} AND {max_year}",
            f"m.vote_average >= {min_rating}"
        ]
        
        if search_title:
            cleaned_search = search_title.replace("'", "''")
            where_clauses.append(f"LOWER(m.title) LIKE LOWER('%{cleaned_search}%')")

        where_str = " AND ".join(where_clauses)

        # In SQLite, group_concat is supported directly; in MySQL GROUP_CONCAT is used
        concat_func = "GROUP_CONCAT(DISTINCT g.genre_name)"
        query = f"""
        SELECT 
            m.tmdb_id,
            m.title,
            YEAR(m.release_date) AS release_year,
            m.release_date,
            m.budget,
            m.revenue,
            (m.revenue - m.budget) AS gap,
            m.runtime,
            m.vote_average,
            m.vote_count,
            {concat_func} AS genres
        FROM Movie m
        LEFT JOIN MovieGenre mg ON m.tmdb_id = mg.tmdb_id
        LEFT JOIN Genre g ON mg.genre_id = g.genre_id
        WHERE {where_str}
        GROUP BY m.tmdb_id, m.title, m.release_date, m.budget, m.revenue, m.runtime, m.vote_average, m.vote_count
        ORDER BY m.release_date DESC;
        """
        df = self.execute_query(query)
        
        if selected_genres and not df.empty:
            # Filter rows where at least one selected genre matches
            def matches_genre(genre_str):
                if not genre_str or pd.isna(genre_str):
                    return False
                item_genres = [x.strip() for x in str(genre_str).split(",")]
                return any(g in selected_genres for g in item_genres)
            df = df[df["genres"].apply(matches_genre)]
            
        return df

    # -------------------------------------------------------------------------
    # 10 SQL Analytical Reports (R01 - R10)
    # -------------------------------------------------------------------------
    def get_report_r01(self) -> Tuple[pd.DataFrame, str]:
        """R01 – Movies released by year: Count movies grouped by release year."""
        return self.execute_query(SQL_R01_MOVIES_BY_YEAR), SQL_R01_MOVIES_BY_YEAR

    def get_report_r02(self) -> Tuple[pd.DataFrame, str]:
        """R02 – Average rating by genre: Calculate the average TMDb rating for each genre."""
        return self.execute_query(SQL_R02_AVG_RATING_BY_GENRE), SQL_R02_AVG_RATING_BY_GENRE

    def get_report_r03(self, min_votes: int = 50, limit: int = 25) -> Tuple[pd.DataFrame, str]:
        """R03 – Top movies by rating: Rank movies by vote_average DESC using vote_count as secondary sort."""
        sql = SQL_R03_TOP_MOVIES_BY_RATING.format(min_votes=min_votes, limit=limit)
        return self.execute_query(sql), sql

    def get_report_r04(self) -> Tuple[pd.DataFrame, str]:
        """R04 – Revenue by release year: Sum recorded revenue for movies released in each year (WHERE revenue > 0)."""
        return self.execute_query(SQL_R04_REVENUE_BY_YEAR), SQL_R04_REVENUE_BY_YEAR

    def get_report_r05(self) -> Tuple[pd.DataFrame, str]:
        """R05 – Revenue by genre: Group total movie revenue by genre."""
        return self.execute_query(SQL_R05_REVENUE_BY_GENRE), SQL_R05_REVENUE_BY_GENRE

    def get_report_r06(self) -> Tuple[pd.DataFrame, str]:
        """R06 – Budget compared with revenue: Compare recorded budget and revenue (revenue - budget AS gap)."""
        return self.execute_query(SQL_R06_BUDGET_VS_REVENUE), SQL_R06_BUDGET_VS_REVENUE

    def get_report_r07(self) -> Tuple[pd.DataFrame, str]:
        """R07 – Rating distribution: Count movies in rating intervals from 0 to 10."""
        return self.execute_query(SQL_R07_RATING_DISTRIBUTION), SQL_R07_RATING_DISTRIBUTION

    def get_report_r08(self, limit: int = 10) -> Tuple[pd.DataFrame, str]:
        """R08 – Most-voted movies: Rank movies using TMDb vote_count DESC LIMIT 10."""
        sql = SQL_R08_MOST_VOTED_MOVIES.format(limit=limit)
        return self.execute_query(sql), sql

    def get_report_r09(self) -> Tuple[pd.DataFrame, str]:
        """R09 – Movie count by genre: Count distinct movies linked to each genre."""
        return self.execute_query(SQL_R09_MOVIE_COUNT_BY_GENRE), SQL_R09_MOVIE_COUNT_BY_GENRE

    def get_report_r10(self) -> Tuple[pd.DataFrame, str]:
        """R10 – Average runtime by genre: Calculate average movie duration for each genre (AVG(runtime))."""
        return self.execute_query(SQL_R10_AVG_RUNTIME_BY_GENRE), SQL_R10_AVG_RUNTIME_BY_GENRE

    def get_runtime_distribution_by_genre(self) -> pd.DataFrame:
        """Retrieves raw runtime records per genre for box plot visualization."""
        sql = """
        SELECT 
            g.genre_name, 
            m.runtime,
            m.title
        FROM Genre g
        JOIN MovieGenre mg ON g.genre_id = mg.genre_id
        JOIN Movie m ON mg.tmdb_id = m.tmdb_id
        WHERE m.runtime IS NOT NULL AND m.runtime > 0;
        """
        return self.execute_query(sql)

    def get_database_summary_stats(self) -> Dict[str, Any]:
        """Calculates comprehensive database table counts and aggregate metrics."""
        sql_counts = """
        SELECT 
            (SELECT COUNT(*) FROM Movie) AS total_movies,
            (SELECT COUNT(*) FROM Genre) AS total_genres,
            (SELECT COUNT(*) FROM MovieGenre) AS total_mappings,
            (SELECT COALESCE(SUM(revenue), 0) FROM Movie WHERE revenue > 0) AS total_revenue,
            (SELECT COALESCE(SUM(budget), 0) FROM Movie WHERE budget > 0) AS total_budget,
            (SELECT COALESCE(SUM(revenue - budget), 0) FROM Movie WHERE revenue > 0 AND budget > 0) AS total_gap,
            (SELECT ROUND(AVG(vote_average), 2) FROM Movie WHERE vote_average IS NOT NULL) AS mean_rating,
            (SELECT COALESCE(SUM(vote_count), 0) FROM Movie WHERE vote_count IS NOT NULL) AS total_votes,
            (SELECT ROUND(AVG(runtime), 1) FROM Movie WHERE runtime IS NOT NULL AND runtime > 0) AS avg_runtime;
        """
        df_counts = self.execute_query(sql_counts)
        row = df_counts.iloc[0] if not df_counts.empty else {}

        # Top individual movie records
        sql_top_rev = "SELECT title, revenue FROM Movie WHERE revenue IS NOT NULL ORDER BY revenue DESC LIMIT 1;"
        df_top_rev = self.execute_query(sql_top_rev)
        top_rev_title = df_top_rev.iloc[0]["title"] if not df_top_rev.empty else "N/A"
        top_rev_val = int(df_top_rev.iloc[0]["revenue"]) if not df_top_rev.empty else 0

        sql_top_voted = "SELECT title, vote_count, vote_average FROM Movie WHERE vote_count IS NOT NULL ORDER BY vote_count DESC LIMIT 1;"
        df_top_voted = self.execute_query(sql_top_voted)
        top_voted_title = df_top_voted.iloc[0]["title"] if not df_top_voted.empty else "N/A"
        top_voted_val = int(df_top_voted.iloc[0]["vote_count"]) if not df_top_voted.empty else 0

        sql_top_rated = "SELECT title, vote_average, vote_count FROM Movie WHERE vote_average IS NOT NULL AND vote_count >= 1000 ORDER BY vote_average DESC, vote_count DESC LIMIT 1;"
        df_top_rated = self.execute_query(sql_top_rated)
        top_rated_title = df_top_rated.iloc[0]["title"] if not df_top_rated.empty else "N/A"
        top_rated_val = float(df_top_rated.iloc[0]["vote_average"]) if not df_top_rated.empty else 0.0

        return {
            "total_tables": 3,
            "total_views": 1,
            "total_movies": int(row.get("total_movies", 0)),
            "total_genres": int(row.get("total_genres", 0)),
            "total_mappings": int(row.get("total_mappings", 0)),
            "total_revenue": int(row.get("total_revenue", 0)),
            "total_budget": int(row.get("total_budget", 0)),
            "total_gap": int(row.get("total_gap", 0)),
            "mean_rating": float(row.get("mean_rating", 0.0)),
            "total_votes": int(row.get("total_votes", 0)),
            "avg_runtime": float(row.get("avg_runtime", 0.0)),
            "top_revenue_movie": f"{top_rev_title} (${top_rev_val:,.0f})",
            "top_voted_movie": f"{top_voted_title} ({top_voted_val:,} votes)",
            "top_rated_movie": f"{top_rated_movie_str(top_rated_title, top_rated_val)}"
        }

def top_rated_movie_str(title: str, rating: float) -> str:
    return f"{title} (⭐ {rating:.1f}/10)" if title != "N/A" else "N/A"

