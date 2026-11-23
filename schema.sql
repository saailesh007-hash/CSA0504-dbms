-- ============================================================================
-- Database: MovieAnalytics
-- Description: Normalized Relational DBMS Architecture (1NF, 2NF, 3NF compliant)
-- Source Dataset: Kaggle's 'The Movies Dataset' (movies_metadata.csv by Rounak Banik)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS MovieAnalytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE MovieAnalytics;

-- ----------------------------------------------------------------------------
-- Table 1: Movie
-- Stores fundamental movie metadata keyed by the TMDb identifier.
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS MovieGenre;
DROP TABLE IF EXISTS Movie;
DROP TABLE IF EXISTS Genre;

CREATE TABLE Movie (
    tmdb_id       INT PRIMARY KEY,
    title         VARCHAR(255) NOT NULL,
    release_date  DATE NULL,
    budget        BIGINT NULL,
    revenue       BIGINT NULL,
    runtime       DECIMAL(6,2) NULL,
    vote_average  DECIMAL(3,1) NULL,
    vote_count    INT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_movie_release_date (release_date),
    INDEX idx_movie_vote_average (vote_average),
    INDEX idx_movie_vote_count (vote_count),
    INDEX idx_movie_revenue (revenue),
    INDEX idx_movie_budget (budget)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- Table 2: Genre
-- Stores unique genre categories to eliminate transitive dependencies (3NF).
-- ----------------------------------------------------------------------------
CREATE TABLE Genre (
    genre_id    INT PRIMARY KEY,
    genre_name  VARCHAR(100) UNIQUE NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- Table 3: MovieGenre (Many-to-Many Bridge Table)
-- Resolves the many-to-many relationship between Movies and Genres (1NF/2NF compliant).
-- ----------------------------------------------------------------------------
CREATE TABLE MovieGenre (
    tmdb_id   INT NOT NULL,
    genre_id  INT NOT NULL,
    PRIMARY KEY (tmdb_id, genre_id),
    CONSTRAINT fk_moviegenre_movie 
        FOREIGN KEY (tmdb_id) REFERENCES Movie(tmdb_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_moviegenre_genre 
        FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_moviegenre_genre_tmdb (genre_id, tmdb_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SQL Analytical Views for Common Queries
-- ============================================================================

CREATE OR REPLACE VIEW v_movie_full_catalogue AS
SELECT 
    m.tmdb_id,
    m.title,
    YEAR(m.release_date) AS release_year,
    m.release_date,
    m.budget,
    m.revenue,
    (m.revenue - m.budget) AS financial_gap,
    m.runtime,
    m.vote_average,
    m.vote_count,
    GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') AS genres
FROM Movie m
LEFT JOIN MovieGenre mg ON m.tmdb_id = mg.tmdb_id
LEFT JOIN Genre g ON mg.genre_id = g.genre_id
GROUP BY m.tmdb_id, m.title, m.release_date, m.budget, m.revenue, m.runtime, m.vote_average, m.vote_count;
