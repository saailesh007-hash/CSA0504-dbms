# 🎬 Movie Catalogue, Ratings & Revenue Dashboard

A complete, full-stack interactive web application built with **Streamlit**, **MySQL (`MovieAnalytics`)**, and **Plotly** based on a normalized relational database management system (DBMS) architecture.

The project models and analyzes Kaggle's *The Movies Dataset* (`movies_metadata.csv` originally curated by Rounak Banik), featuring a searchable movie catalogue, 10 formal SQL analytical reports, interactive data visualizations, and functional CSV data export capabilities.

---

## 🏗️ 1. Tech Stack & Architecture

- **Frontend / Dashboard**: Streamlit with custom CSS, interactive sidebar filters, responsive KPI metric cards, and responsive tabs.
- **Backend / Relational Database**: MySQL 8.x / MariaDB database named `MovieAnalytics`.
- **Data Visualizations**: Plotly Express & Plotly Graph Objects (dynamic bar charts, revenue share pie charts, dual-axis trend lines, scatter plots with break-even threshold).
- **Data Pipeline**: Python ETL script (`etl_loader.py`) for data cleaning, JSON genre parsing, and automated relational loading.

---

## 🗄️ 2. Relational Database Schema & Normalization

The database architecture is designed in strict compliance with **1NF, 2NF, and 3NF** normalization rules:

### Normalization Breakdown
1. **First Normal Form (1NF)**:
   - In the raw Kaggle dataset, genres are stored as JSON strings containing nested arrays of dictionaries (e.g. `[{'id': 28, 'name': 'Action'}, ...]`).
   - The ETL pipeline extracts each genre into atomic tuples. All table columns store atomic, non-divisible scalar values.
2. **Second Normal Form (2NF)**:
   - Eliminates partial dependencies. All non-key attributes in `Movie` depend fully on the primary key `tmdb_id`.
   - The bridge table `MovieGenre` uses a composite primary key `(tmdb_id, genre_id)` where foreign keys link back to independent entities.
3. **Third Normal Form (3NF)**:
   - Eliminates transitive dependencies. Genre metadata is isolated in the `Genre` table rather than stored repeatedly alongside movie titles.

### Schema Specification
```sql
CREATE DATABASE IF NOT EXISTS MovieAnalytics;
USE MovieAnalytics;

-- Table 1: Movie
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
);

-- Table 2: Genre
CREATE TABLE Genre (
    genre_id    INT PRIMARY KEY,
    genre_name  VARCHAR(100) UNIQUE NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: MovieGenre (Many-to-Many Bridge Table)
CREATE TABLE MovieGenre (
    tmdb_id   INT NOT NULL,
    genre_id  INT NOT NULL,
    PRIMARY KEY (tmdb_id, genre_id),
    CONSTRAINT fk_moviegenre_movie FOREIGN KEY (tmdb_id) REFERENCES Movie(tmdb_id) ON DELETE CASCADE,
    CONSTRAINT fk_moviegenre_genre FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) ON DELETE CASCADE,
    INDEX idx_moviegenre_genre_tmdb (genre_id, tmdb_id)
);
```

---

## 📊 3. The 10 Core SQL Analytical Reports

The application executes and renders interactive visualizations for 10 analytical reports:

| Report ID | Name | Objective & SQL Implementation |
| :--- | :--- | :--- |
| **R01** | **Movies released by year** | `SELECT YEAR(release_date) AS release_year, COUNT(*) AS movie_count FROM Movie WHERE release_date IS NOT NULL GROUP BY YEAR(release_date) ORDER BY release_year ASC;` |
| **R02** | **Average rating by genre** | `SELECT g.genre_name, ROUND(AVG(m.vote_average), 2) AS avg_tmdb_rating, COUNT(m.tmdb_id) AS movie_count FROM Genre g JOIN MovieGenre mg ON g.genre_id = mg.genre_id JOIN Movie m ON mg.tmdb_id = m.tmdb_id WHERE m.vote_average IS NOT NULL GROUP BY g.genre_id, g.genre_name ORDER BY avg_tmdb_rating DESC;` |
| **R03** | **Top movies by rating** | `SELECT m.tmdb_id, m.title, YEAR(m.release_date) AS release_year, m.vote_average, m.vote_count, m.revenue, m.budget FROM Movie m WHERE m.vote_average IS NOT NULL AND m.vote_count >= 1000 ORDER BY m.vote_average DESC, m.vote_count DESC LIMIT 25;` |
| **R04** | **Revenue by release year** | `SELECT YEAR(release_date) AS release_year, SUM(revenue) AS total_revenue, COUNT(*) AS movie_count, ROUND(AVG(revenue), 2) AS avg_revenue FROM Movie WHERE release_date IS NOT NULL AND revenue > 0 GROUP BY YEAR(release_date) ORDER BY release_year ASC;` |
| **R05** | **Revenue by genre** | `SELECT g.genre_name, SUM(m.revenue) AS total_revenue, COUNT(m.tmdb_id) AS movie_count, ROUND(AVG(m.revenue), 2) AS avg_revenue FROM Genre g JOIN MovieGenre mg ON g.genre_id = mg.genre_id JOIN Movie m ON mg.tmdb_id = m.tmdb_id WHERE m.revenue > 0 GROUP BY g.genre_id, g.genre_name ORDER BY total_revenue DESC;` |
| **R06** | **Budget compared with revenue** | `SELECT tmdb_id, title, YEAR(release_date) AS release_year, budget, revenue, (revenue - budget) AS gap, CASE WHEN budget > 0 THEN ROUND(((revenue - budget) * 100.0 / budget), 2) ELSE NULL END AS gap_pct FROM Movie WHERE budget > 0 AND revenue > 0 ORDER BY gap DESC;` |
| **R07** | **Rating distribution** | `SELECT CONCAT(FLOOR(vote_average), '.0 - ', FLOOR(vote_average) + 0.9) AS rating_interval, FLOOR(vote_average) AS interval_lower, COUNT(*) AS movie_count FROM Movie WHERE vote_average IS NOT NULL GROUP BY FLOOR(vote_average) ORDER BY interval_lower ASC;` |
| **R08** | **Most-voted movies** | `SELECT tmdb_id, title, YEAR(release_date) AS release_year, vote_count, vote_average, revenue FROM Movie WHERE vote_count IS NOT NULL ORDER BY vote_count DESC LIMIT 10;` |
| **R09** | **Movie count by genre** | `SELECT g.genre_name, COUNT(DISTINCT mg.tmdb_id) AS movie_count FROM Genre g LEFT JOIN MovieGenre mg ON g.genre_id = mg.genre_id GROUP BY g.genre_id, g.genre_name ORDER BY movie_count DESC;` |
| **R10** | **Average runtime by genre** | `SELECT g.genre_name, ROUND(AVG(m.runtime), 2) AS avg_runtime, COUNT(m.tmdb_id) AS movie_count FROM Genre g JOIN MovieGenre mg ON g.genre_id = mg.genre_id JOIN Movie m ON mg.tmdb_id = m.tmdb_id WHERE m.runtime IS NOT NULL AND m.runtime > 0 GROUP BY g.genre_id, g.genre_name ORDER BY avg_runtime DESC;` |

*(Note: In R06, `revenue - budget` represents the financial gap/difference, not net profit, in accordance with project scope).*

---

## 💻 4. Local Installation & Setup Guide

### Step 1: Clone or Navigate to the Project Directory
```bash
cd "C:\Users\ASUS\.gemini\antigravity\scratch\movie_analytics_dashboard"
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure MySQL Database
1. Open your MySQL client (MySQL Workbench, phpMyAdmin, or MySQL CLI):
   ```bash
   mysql -u root -p
   ```
2. Create the database and tables using `schema.sql`:
   ```sql
   SOURCE schema.sql;
   ```
3. Seed the sample dataset using `seed_data.sql`:
   ```sql
   SOURCE seed_data.sql;
   ```

*(Alternative)*: Ingest the full Kaggle dataset (`movies_metadata.csv`):
```bash
python etl_loader.py --csv path/to/movies_metadata.csv --target mysql
```

### Step 4: Configure Database Credentials
Create a `.env` file from `.env.example`:
```ini
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=MovieAnalytics
```
*(You can also configure or test credentials directly from the sidebar in the running Streamlit web application).*

### Step 5: Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🖥️ 5. Dashboard Features & Navigation

- **KPI Header Cards**: Real-time display of **Total Movies**, **Total Genres**, **Mean TMDb Rating**, and **Total Positive Revenue**.
- **Sidebar Dynamic Filtering**:
  - Filter by **Release Year Range** (interactive slider)
  - Filter by **Genre** (multi-select with Select All toggle)
  - Filter by **TMDb Rating Score** (0.0 to 10.0 scale)
  - Quick Search by Movie Title
  - Live Database Connection status checker and instant toggle to Demo Mode
- **Navigation Tabs**:
  1. **📁 Catalogue**: Interactive data grid with search, custom column formatting (currency, ratings, runtimes), and a deep-dive Movie Inspector.
  2. **📊 Reports (R01–R10)**: Dropdown selector for the 10 SQL analytical reports with formatted SQL query code view, Plotly interactive visualizations (including the R02 Average TMDb Rating by Genre bar chart and the R08 Most-Voted Movies leaderboard), and instant report-specific CSV export.
  3. **💾 Export CSV**: Universal export center allowing export of any report or the filtered catalogue with formatted timestamps.
