"""
Movie Catalogue, Ratings & Revenue Dashboard
Full-Stack Streamlit Web Application backed by MySQL (MovieAnalytics) / 3NF Relational Architecture
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
from datetime import datetime
from config import DBConfig
from database import DatabaseManager

# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Styling (Preserved exactly from 1st version)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Movie Catalogue, Ratings & Revenue Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom modern CSS styling matching the 1st version
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .summary-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .summary-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1);
    }
    .badge-pk { background-color: #FEF08A; color: #854D0E; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 0.75rem; }
    .badge-fk { background-color: #BAE6FD; color: #0369A1; font-weight: bold; border-radius: 4px; padding: 2px 6px; font-size: 0.75rem; }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Database Connection State & Initialization
# -----------------------------------------------------------------------------
if "db_config" not in st.session_state:
    st.session_state["db_config"] = DBConfig()

if "use_sqlite_demo" not in st.session_state:
    # Auto-detect if MySQL is reachable; if not, gracefully default to Demo Mode
    initial_mgr = DatabaseManager(config=st.session_state["db_config"], use_sqlite_demo=False)
    can_connect_mysql, _ = initial_mgr.test_connection()
    st.session_state["use_sqlite_demo"] = not can_connect_mysql


@st.cache_resource(show_spinner=False)
def get_db_manager(host, port, user, password, database, use_sqlite_demo):
    cfg = DBConfig(host=host, port=port, user=user, password=password, database=database)
    return DatabaseManager(config=cfg, use_sqlite_demo=use_sqlite_demo)


# =============================================================================
# TOP OF LEFT SIDEBAR: Database Settings, Design, Visualization, SQL Commands
# =============================================================================
st.sidebar.markdown("## 🎬 Movie Analytics")
st.sidebar.caption("Relational DBMS Architecture • 3NF Normalized")

# 1. Navigation Menu right at the TOP of the left sidebar
st.sidebar.markdown("### 🧭 Dashboard Navigation")
sidebar_nav = st.sidebar.radio(
    "Choose View:",
    [
        "📁 Catalogue",
        "📐 Design (ER Diagram)",
        "📊 Visualization (10 Graph Types)",
        "💻 SQL Commands (Queries)",
        "🔌 Database Settings",
        "💾 Export CSV"
    ],
    index=0
)

st.sidebar.markdown("---")

# 2. Database Connection Settings (Collapsible drawer accessible in left sidebar)
with st.sidebar.expander("🔌 Database Settings", expanded=(sidebar_nav == "🔌 Database Settings")):
    db_mode = st.radio(
        "Backend Connection:",
        ["MySQL (MovieAnalytics)", "Demo Mode (Local SQLite)"],
        index=1 if st.session_state["use_sqlite_demo"] else 0
    )
    is_sqlite = (db_mode == "Demo Mode (Local SQLite)")
    st.session_state["use_sqlite_demo"] = is_sqlite

    mysql_host = st.text_input("MySQL Host", value=st.session_state["db_config"].host, disabled=is_sqlite)
    mysql_port = st.number_input("MySQL Port", value=st.session_state["db_config"].port, step=1, disabled=is_sqlite)
    mysql_user = st.text_input("MySQL User", value=st.session_state["db_config"].user, disabled=is_sqlite)
    mysql_pass = st.text_input("MySQL Password", value=st.session_state["db_config"].password, type="password", disabled=is_sqlite)
    mysql_db = st.text_input("Database Name", value=st.session_state["db_config"].database, disabled=is_sqlite)

    if st.button("🔄 Test Connection"):
        test_mgr = DatabaseManager(
            config=DBConfig(host=mysql_host, port=int(mysql_port), user=mysql_user, password=mysql_pass, database=mysql_db),
            use_sqlite_demo=is_sqlite
        )
        ok, msg = test_mgr.test_connection()
        if ok:
            st.success(msg)
        else:
            st.error(msg)

# Active Database Manager
db = get_db_manager(
    mysql_host if not is_sqlite else "localhost",
    int(mysql_port) if not is_sqlite else 3306,
    mysql_user if not is_sqlite else "root",
    mysql_pass if not is_sqlite else "",
    mysql_db if not is_sqlite else "MovieAnalytics",
    is_sqlite
)

# Test live connection status
connected, conn_status = db.test_connection()
if connected:
    st.sidebar.success(f"🟢 {conn_status}")
else:
    st.sidebar.error(f"🔴 {conn_status}")
    st.sidebar.info("💡 Running seamlessly in SQLite Demo Mode.")

st.sidebar.markdown("---")

# 3. Universal Filter Controls (from the first version)
st.sidebar.subheader("🔍 Filters")

try:
    filter_meta = db.get_filter_options()
    all_genres = filter_meta["genres"]
    min_db_year = filter_meta["min_year"]
    max_db_year = filter_meta["max_year"]
except Exception:
    all_genres = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Drama", "Fantasy", "Horror", "Romance", "Science Fiction", "Thriller"]
    min_db_year, max_db_year = 1970, 2024

year_range = st.sidebar.slider(
    "Release Year Range",
    min_value=int(min_db_year),
    max_value=int(max_db_year),
    value=(int(min_db_year), int(max_db_year))
)

select_all_genres = st.sidebar.checkbox("Select All Genres", value=True)
if select_all_genres:
    selected_genres = all_genres
else:
    selected_genres = st.sidebar.multiselect(
        "Select Genres",
        options=all_genres,
        default=all_genres[:5] if all_genres else []
    )

st.sidebar.markdown("**⭐ Rating Source: TMDb**")
min_rating = st.sidebar.slider("Minimum TMDb Rating (0-10)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
title_search = st.sidebar.text_input("Search Title", placeholder="e.g. Inception, Avatar...")


# -----------------------------------------------------------------------------
# Main Header & Global KPI Metrics Cards (Preserved exactly from 1st version)
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">🎬 Movie Catalogue, Ratings & Revenue Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Relational DBMS Analytics platform for Kaggle\'s <i>The Movies Dataset</i> (MySQL / 3NF Architecture)</div>',
    unsafe_allow_html=True
)

kpis = db.get_kpis(year_range[0], year_range[1], selected_genres)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🎥 Total Movies</div>
        <div class="metric-value">{kpis['total_movies']:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🎭 Total Genres</div>
        <div class="metric-value">{kpis['total_genres']}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">⭐ Mean TMDb Rating</div>
        <div class="metric-value">{kpis['mean_rating']:.1f} <span style="font-size: 1rem; color: #F59E0B;">/ 10</span></div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    rev_billions = kpis['total_revenue'] / 1e9
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💰 Positive Revenue</div>
        <div class="metric-value">${rev_billions:.2f}B</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# =============================================================================
# OPTION 1: 📁 CATALOGUE & DEEP DIVE (WITH EXACT SPECIFIC SQL QUERY)
# =============================================================================
if sidebar_nav.startswith("📁"):
    st.subheader("📚 Movie Catalogue Explorer")
    st.caption("Browse, search, and inspect the normalized movie dataset with live filters.")

    catalogue_df = db.get_catalogue(
        min_year=year_range[0],
        max_year=year_range[1],
        selected_genres=selected_genres,
        min_rating=min_rating,
        search_title=title_search
    )

    if catalogue_df.empty:
        st.warning("No movies matched your filter criteria. Try adjusting the sidebar filters.")
    else:
        st.write(f"Showing **{len(catalogue_df)}** matching movies:")

        display_df = catalogue_df.copy()
        display_df["Financial Gap ($)"] = display_df["gap"].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "$0")
        display_df["Revenue ($)"] = display_df["revenue"].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "$0")
        display_df["Budget ($)"] = display_df["budget"].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "$0")
        display_df["Runtime (min)"] = display_df["runtime"].apply(lambda x: f"{x:.0f}m" if pd.notnull(x) else "N/A")
        display_df["Rating"] = display_df["vote_average"].apply(lambda x: f"⭐ {x:.1f}" if pd.notnull(x) else "N/A")
        display_df["Votes"] = display_df["vote_count"].apply(lambda x: f"{x:,}" if pd.notnull(x) else "0")

        cols_to_show = ["tmdb_id", "title", "release_year", "genres", "Rating", "Votes", "Budget ($)", "Revenue ($)", "Financial Gap ($)", "Runtime (min)"]
        st.dataframe(
            display_df[cols_to_show].rename(columns={
                "tmdb_id": "TMDb ID",
                "title": "Title",
                "release_year": "Year",
                "genres": "Genres"
            }),
            use_container_width=True,
            height=380
        )

        # ---------------------------------------------------------------------
        # Deep Dive: Movie Inspector with Specific Relational SQL Query
        # ---------------------------------------------------------------------
        st.markdown("---")
        with st.expander("🔍 Deep Dive: Movie Inspector", expanded=True):
            selected_movie_title = st.selectbox("Select a movie to inspect:", catalogue_df["title"].tolist())
            movie_row = catalogue_df[catalogue_df["title"] == selected_movie_title].iloc[0]

            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.write(f"**Title**: {movie_row['title']}")
                st.write(f"**TMDb ID**: `{movie_row['tmdb_id']}`")
                st.write(f"**Release Date**: {movie_row['release_date']}")
                st.write(f"**Genres**: {movie_row['genres']}")
            with mcol2:
                st.write(f"**Budget**: ${movie_row['budget']:,.0f}")
                st.write(f"**Revenue**: ${movie_row['revenue']:,.0f}")
                gap_val = movie_row['revenue'] - movie_row['budget']
                color = "green" if gap_val >= 0 else "red"
                st.markdown(f"**Financial Gap**: <span style='color:{color}; font-weight:bold;'>${gap_val:,.0f}</span> *(revenue − budget)*", unsafe_allow_html=True)
            with mcol3:
                st.write(f"**Runtime**: {movie_row['runtime']} minutes")
                st.write(f"**TMDb Score**: ⭐ {movie_row['vote_average']} / 10")
                st.write(f"**Vote Count**: {movie_row['vote_count']:,} votes")

            # Dedicated Specific SQL Query requested by user
            st.markdown("---")
            st.markdown(f"#### 📜 Exact SQL Query Used for '{movie_row['title']}':")
            st.caption("Here is the exact multi-table relational SQL query executed to retrieve this movie and its normalized genres:")
            
            specific_movie_sql = f"""SELECT 
    m.tmdb_id,
    m.title,
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
WHERE m.tmdb_id = {movie_row['tmdb_id']}  -- Filter by TMDb ID for '{movie_row['title']}'
GROUP BY m.tmdb_id, m.title, m.release_date, m.budget, m.revenue, m.runtime, m.vote_average, m.vote_count;"""
            st.code(specific_movie_sql, language="sql")

            st.markdown("**Underlying Normalized Relational Queries:**")
            st.code(f"""-- 1. Primary Movie Entity Query:
SELECT * FROM Movie WHERE tmdb_id = {movie_row['tmdb_id']};

-- 2. Many-to-Many Genre Query via MovieGenre bridge table:
SELECT g.genre_id, g.genre_name 
FROM Genre g
JOIN MovieGenre mg ON g.genre_id = mg.genre_id
WHERE mg.tmdb_id = {movie_row['tmdb_id']};""", language="sql")


# =============================================================================
# OPTION 2: 📐 DESIGN (ER DIAGRAM OF ALL COLUMNS - NEAR DATABASE SETTINGS)
# =============================================================================
elif sidebar_nav.startswith("📐"):
    st.subheader("📐 Relational Database Schema Design & ER Diagram")
    st.caption("Entity-Relationship (ER) diagram showing all columns, data types, primary keys, foreign keys, and 1NF, 2NF, 3NF normalization rules.")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.info("🔹 **1NF Compliant**: Atomic attributes. Repeating JSON genre arrays decomposed into distinct atomic tuples.")
    with m2:
        st.success("🔹 **2NF Compliant**: No partial dependencies. Bridge table `MovieGenre` uses composite primary key `(tmdb_id, genre_id)`.")
    with m3:
        st.warning("🔹 **3NF Compliant**: No transitive dependencies. Genre metadata separated into distinct `Genre` entity.")

    st.markdown("### 🗺️ Visual Entity-Relationship (ER) Diagram")

    # ER Diagram — load pre-generated SVG file and display as base64 image
    # (st.html strips SVG in Streamlit 1.67+; base64 img tag is the reliable fix)
    _er_svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er_diagram.svg")
    try:
        with open(_er_svg_path, "rb") as _f:
            _svg_b64 = base64.b64encode(_f.read()).decode("utf-8")
        st.markdown(
            f'<div style="border:1px solid #CBD5E1; border-radius:12px; padding:16px; background:#F8FAFC;">'
            f'<img src="data:image/svg+xml;base64,{_svg_b64}" '
            f'style="width:100%; height:auto; border-radius:8px;" alt="ER Diagram"/>'
            f'</div>',
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        st.error(f"ER diagram SVG not found at: `{_er_svg_path}`. Run `python generate_er.py` once in the project folder.")

    # Complete Column Schema & Data Dictionary Table — stacked vertically (no overlap)
    st.markdown("### 📋 Complete Column Schema & Data Dictionary")
    st.caption("Each table is shown in full below — scroll down to see all three.")

    # ── Table 1: Movie ──────────────────────────────────────────────────────────
    with st.expander("🎬 Table 1: Movie  (10 columns)", expanded=True):
        st.markdown("""
| Column | Data Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- |
| `tmdb_id` | `INT` | 🔑 **PK · NOT NULL** | TMDb movie unique ID |
| `title` | `VARCHAR(255)` | NOT NULL | Movie title |
| `release_date` | `DATE` | NULL | Official theatrical release date |
| `budget` | `BIGINT` | NULL | Production cost in USD |
| `revenue` | `BIGINT` | NULL | Box office gross in USD |
| `runtime` | `DECIMAL(6,2)` | NULL | Movie duration in minutes |
| `vote_average` | `DECIMAL(3,1)` | NULL | TMDb score (0.0 – 10.0 scale) |
| `vote_count` | `INT` | NULL | Total user votes submitted |
| `popularity` | `DECIMAL(10,4)` | NULL | TMDb popularity score |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | Record creation timestamp |
""")
        st.info("**Primary Key**: `tmdb_id`  •  **Engine**: InnoDB  •  **3NF Compliant** ✅")

    st.markdown("")  # spacer

    # ── Table 2: Genre ───────────────────────────────────────────────────────────
    with st.expander("🎭 Table 2: Genre  (3 columns)", expanded=True):
        st.markdown("""
| Column | Data Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- |
| `genre_id` | `INT` | 🔑 **PK · AUTO_INCREMENT** | TMDb genre unique ID |
| `genre_name` | `VARCHAR(100)` | **UNIQUE · NOT NULL** | Unique genre label |
| `created_at` | `TIMESTAMP` | DEFAULT NOW() | Record creation timestamp |
""")
        st.success("**Purpose**: Master lookup table — eliminates redundant genre strings and preserves 3NF integrity.")

    st.markdown("")  # spacer

    # ── Table 3: MovieGenre (Bridge) ─────────────────────────────────────────────
    with st.expander("🔗 Table 3: MovieGenre — Bridge / Junction Table  (2 columns)", expanded=True):
        st.markdown("""
| Column | Data Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- |
| `tmdb_id` | `INT` | 🔑 **PK · FK → Movie(tmdb_id)** | Links to Movie record |
| `genre_id` | `INT` | 🔑 **PK · FK → Genre(genre_id)** | Links to Genre record |
""")
        st.warning(
            "**Composite Primary Key**: `(tmdb_id, genre_id)`  \n"
            "**FK1**: `tmdb_id` → `Movie(tmdb_id)`  ON DELETE CASCADE · ON UPDATE CASCADE  \n"
            "**FK2**: `genre_id` → `Genre(genre_id)` ON DELETE CASCADE · ON UPDATE CASCADE  \n"
            "**Purpose**: Resolves the Many-to-Many (M:N) relationship between Movie and Genre."
        )


# =============================================================================
# OPTION 3: 📊 VISUALIZATION (10 GRAPH TYPES & DATABASE SUMMARY STATS - BELOW DESIGN)
# =============================================================================
elif sidebar_nav.startswith("📊"):
    st.subheader("📊 Visualizations – 10 Distinct Graph Types")
    st.caption("Includes 10 different types of charts (Bar, Line, Area, Scatter, Pie, Histogram, Horizontal Bar, Box Plot, Bubble, Heatmap), followed by total database table metrics and summary statistics.")

    # 1. Bar Graph (Vertical)
    st.markdown("#### 1️⃣ Bar Graph (Vertical): Average TMDb Rating by Genre")
    st.caption("Calculates and compares the mean TMDb rating for each film genre on a 0–10 scale.")
    df_r02, _ = db.get_report_r02()
    if not df_r02.empty:
        fig1 = px.bar(
            df_r02,
            x="genre_name",
            y="avg_tmdb_rating",
            color="avg_tmdb_rating",
            color_continuous_scale="Viridis",
            labels={"genre_name": "Genre", "avg_tmdb_rating": "Mean TMDb Score"},
            text="avg_tmdb_rating",
            title="Average TMDb Rating by Genre"
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(yaxis_range=[0, 10], height=400, template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)

    c_g1, c_g2 = st.columns(2)

    # 2. Line Graph
    with c_g1:
        st.markdown("#### 2️⃣ Line Graph: Annual Movie Production Trend")
        st.caption("Tracks the total count of recorded movie releases per year over time.")
        df_r01, _ = db.get_report_r01()
        if not df_r01.empty:
            fig2 = px.line(
                df_r01,
                x="release_year",
                y="movie_count",
                markers=True,
                labels={"release_year": "Release Year", "movie_count": "Number of Movies"},
                title="Year-over-Year Movie Release Trend"
            )
            fig2.update_traces(line=dict(color="#2563EB", width=3))
            fig2.update_layout(height=380, template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)

    # 3. Area Graph
    with c_g2:
        st.markdown("#### 3️⃣ Area Graph: Cumulative Box Office Revenue Growth")
        st.caption("Visualizes cumulative revenue accumulation over release years.")
        df_r04, _ = db.get_report_r04()
        if not df_r04.empty:
            df_r04_sorted = df_r04.sort_values("release_year").copy()
            df_r04_sorted["cum_revenue_billions"] = df_r04_sorted["total_revenue"].cumsum() / 1e9
            fig3 = px.area(
                df_r04_sorted,
                x="release_year",
                y="cum_revenue_billions",
                labels={"release_year": "Release Year", "cum_revenue_billions": "Cumulative Revenue ($B)"},
                title="Cumulative Box Office Revenue Growth ($ Billions)"
            )
            fig3.update_traces(line=dict(color="#059669"), fillcolor="rgba(16, 185, 129, 0.25)")
            fig3.update_layout(height=380, template="plotly_white")
            st.plotly_chart(fig3, use_container_width=True)

    # 4. Scatter Plot
    st.markdown("#### 4️⃣ Scatter Plot: Production Budget vs. Box Office Revenue")
    st.caption("Compares recorded production budget against revenue, with point size denoting financial gap (`revenue - budget`).")
    df_r06, _ = db.get_report_r06()
    if not df_r06.empty:
        fig4 = px.scatter(
            df_r06,
            x="budget",
            y="revenue",
            size="gap",
            color="gap",
            hover_name="title",
            labels={"budget": "Budget ($)", "revenue": "Revenue ($)", "gap": "Financial Gap ($)"},
            title="Budget vs. Revenue Scatter (Dashed Line = Break-Even)",
            color_continuous_scale="Spectral"
        )
        max_limit = max(df_r06["budget"].max(), df_r06["revenue"].max())
        fig4.add_trace(go.Scatter(
            x=[0, max_limit],
            y=[0, max_limit],
            mode="lines",
            name="Break-even (Revenue = Budget)",
            line=dict(color="black", dash="dash")
        ))
        fig4.update_layout(height=420, template="plotly_white")
        st.plotly_chart(fig4, use_container_width=True)

    c_g3, c_g4 = st.columns(2)

    # 5. Pie / Donut Chart
    with c_g3:
        st.markdown("#### 5️⃣ Pie / Donut Chart: Revenue Contribution by Genre")
        st.caption("Displays relative gross revenue share across movie genres.")
        df_r05, _ = db.get_report_r05()
        if not df_r05.empty:
            fig5 = px.pie(
                df_r05,
                names="genre_name",
                values="total_revenue",
                hole=0.45,
                title="Gross Revenue Distribution by Genre",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig5.update_traces(textposition="inside", textinfo="percent+label")
            fig5.update_layout(height=380)
            st.plotly_chart(fig5, use_container_width=True)

    # 6. Histogram
    with c_g4:
        st.markdown("#### 6️⃣ Histogram: TMDb Movie Score Distribution")
        st.caption("Distribution of movie ratings grouped into frequency score bins.")
        cat_df_all = db.get_catalogue(min_db_year, max_db_year)
        if not cat_df_all.empty:
            fig6 = px.histogram(
                cat_df_all,
                x="vote_average",
                nbins=12,
                title="TMDb Movie Rating Frequency Bins",
                labels={"vote_average": "TMDb Rating Score"},
                color_discrete_sequence=["#6366F1"]
            )
            fig6.update_layout(height=380, template="plotly_white", bargap=0.1)
            st.plotly_chart(fig6, use_container_width=True)

    # 7. Horizontal Bar Graph
    st.markdown("#### 7️⃣ Horizontal Bar Graph: Top 10 Most-Voted Movies (Popularity Leaderboard)")
    st.caption("Ranks movies with the highest number of recorded user votes on TMDb.")
    df_r08, _ = db.get_report_r08(10)
    if not df_r08.empty:
        fig7 = px.bar(
            df_r08,
            x="vote_count",
            y="title",
            orientation="h",
            labels={"vote_count": "Total Votes", "title": "Movie Title"},
            color="vote_count",
            color_continuous_scale="Sunset",
            title="Top 10 Most-Voted Titles"
        )
        fig7.update_layout(yaxis={"categoryorder": "total ascending"}, height=380, template="plotly_white")
        st.plotly_chart(fig7, use_container_width=True)

    c_g5, c_g6 = st.columns(2)

    # 8. Box Plot
    with c_g5:
        st.markdown("#### 8️⃣ Box Plot: Movie Runtime Distribution by Genre")
        st.caption("Shows duration distribution, medians, quartiles, and outliers per genre.")
        df_runtime = db.get_runtime_distribution_by_genre()
        if not df_runtime.empty:
            fig8 = px.box(
                df_runtime,
                x="genre_name",
                y="runtime",
                color="genre_name",
                title="Runtime Spread Across Genres (Minutes)",
                labels={"genre_name": "Genre", "runtime": "Runtime (min)"}
            )
            fig8.update_layout(height=400, showlegend=False, template="plotly_white")
            st.plotly_chart(fig8, use_container_width=True)

    # 9. Bubble Chart
    with c_g6:
        st.markdown("#### 9️⃣ Bubble Chart: Financial Gap vs. TMDb Rating")
        st.caption("Bubble Size = Vote Count, Bubble Color = Production Budget.")
        if not cat_df_all.empty:
            fig9 = px.scatter(
                cat_df_all,
                x="vote_average",
                y="gap",
                size="vote_count",
                color="budget",
                hover_name="title",
                labels={"vote_average": "TMDb Rating", "gap": "Financial Gap ($)", "budget": "Budget ($)"},
                title="Financial Difference vs. Rating (Size = Popularity)",
                color_continuous_scale="Turbo"
            )
            fig9.update_layout(height=400, template="plotly_white")
            st.plotly_chart(fig9, use_container_width=True)

    # 10. Heatmap
    st.markdown("#### 🔟 Heatmap: Numerical Feature Correlation Matrix")
    st.caption("Calculates Pearson correlation coefficients across budget, revenue, runtime, rating, votes, and financial gap.")
    if not cat_df_all.empty:
        numeric_cols = ["budget", "revenue", "gap", "runtime", "vote_average", "vote_count"]
        corr_matrix = cat_df_all[numeric_cols].corr()
        fig10 = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Feature Correlation Matrix Heatmap",
            labels=dict(color="Correlation")
        )
        fig10.update_layout(height=380)
        st.plotly_chart(fig10, use_container_width=True)

    # -------------------------------------------------------------------------
    # Comprehensive Summary Statistics (Below All Graphs as Requested)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🗄️ Database Tables & Global Summary Statistics")
    st.caption("Direct aggregate metrics across all relational tables and entities stored in the MySQL / SQLite database.")

    stats = db.get_database_summary_stats()

    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        st.markdown(f"""
        <div class="summary-card">
            <div class="metric-label">🗄️ Total Tables & Views</div>
            <div style="font-size:1.5rem; font-weight:700; color:#1E293B;">{stats['total_tables']} Tables + {stats['total_views']} View</div>
            <small style="color:#64748B;">Movie, Genre, MovieGenre, v_movie_full_catalogue</small>
        </div>
        """, unsafe_allow_html=True)
    with s_col2:
        st.markdown(f"""
        <div class="summary-card">
            <div class="metric-label">🎥 Total Movies In DB</div>
            <div style="font-size:1.5rem; font-weight:700; color:#1E293B;">{stats['total_movies']:,}</div>
            <small style="color:#64748B;">Unique primary movie records</small>
        </div>
        """, unsafe_allow_html=True)
    with s_col3:
        st.markdown(f"""
        <div class="summary-card">
            <div class="metric-label">🎭 Total Registered Genres</div>
            <div style="font-size:1.5rem; font-weight:700; color:#1E293B;">{stats['total_genres']}</div>
            <small style="color:#64748B;">Master genre categories</small>
        </div>
        """, unsafe_allow_html=True)
    with s_col4:
        st.markdown(f"""
        <div class="summary-card">
            <div class="metric-label">🔗 Total Bridge Mappings</div>
            <div style="font-size:1.5rem; font-weight:700; color:#1E293B;">{stats['total_mappings']:,}</div>
            <small style="color:#64748B;">MovieGenre bridge records</small>
        </div>
        """, unsafe_allow_html=True)

    s_col5, s_col6, s_col7, s_col8 = st.columns(4)
    with s_col5:
        st.markdown(f"""
        <div class="summary-card">
            <div class="metric-label">💰 Total Box Office Revenue</div>
            <div style="font-size:1.5rem; font-weight:700; color:#059669;">${stats['total_revenue']/1e9:.2f}B</div>
            <small style="color:#64748B;">Sum of all recorded revenues</small>
        </div>
        """, unsafe_allow_html=True)
    with s_col6:
        st.markdown(f"""
        <div class="summary-card">
            <div class="metric-label">💸 Total Production Budget</div>
            <div style="font-size:1.5rem; font-weight:700; color:#DC2626;">${stats['total_budget']/1e9:.2f}B</div>
            <small style="color:#64748B;">Sum of all recorded budgets</small>
        </div>
        """, unsafe_allow_html=True)
    with s_col7:
        st.markdown(f"""
        <div class="summary-card">
            <div class="metric-label">⚖️ Total Financial Difference</div>
            <div style="font-size:1.5rem; font-weight:700; color:#2563EB;">${stats['total_gap']/1e9:.2f}B</div>
            <small style="color:#64748B;">Cumulative revenue − budget</small>
        </div>
        """, unsafe_allow_html=True)
    with s_col8:
        st.markdown(f"""
        <div class="summary-card">
            <div class="metric-label">🗳️ Total Votes Counted</div>
            <div style="font-size:1.5rem; font-weight:700; color:#7C3AED;">{stats['total_votes']:,}</div>
            <small style="color:#64748B;">User votes submitted on TMDb</small>
        </div>
        """, unsafe_allow_html=True)

    # Hall of fame record cards
    h1, h2, h3 = st.columns(3)
    with h1:
        st.markdown(f"🏆 **Highest Grossing Movie**: `{stats['top_revenue_movie']}`")
    with h2:
        st.markdown(f"🥇 **Most Voted Movie**: `{stats['top_voted_movie']}`")
    with h3:
        st.markdown(f"👑 **Highest Rated Movie (≥1000 votes)**: `{stats['top_rated_movie']}`")


# =============================================================================
# OPTION 4: 💻 SQL COMMANDS (BELOW VISUALIZATION AS REQUESTED)
# =============================================================================
elif sidebar_nav.startswith("💻"):
    st.subheader("💻 SQL Commands & Schema Architecture")
    st.caption("Complete reference of all SQL DDL, DML, and analytical queries powering the database and dashboard.")

    sql_tab1, sql_tab2, sql_tab3, sql_tab4 = st.tabs([
        "📜 Analytical Report Queries (R01–R10)",
        "🏗️ Schema DDL & Table Definitions",
        "📥 ETL Insertion Queries",
        "⚡ Interactive Live SQL Runner"
    ])

    with sql_tab1:
        st.markdown("### 📊 The 10 Core Analytical SQL Queries")
        report_names = [
            "R01 – Movies Released by Year",
            "R02 – Average Rating by Genre",
            "R03 – Top Movies by Rating",
            "R04 – Revenue by Release Year",
            "R05 – Revenue by Genre",
            "R06 – Budget Compared with Revenue (Financial Gap)",
            "R07 – Rating Distribution",
            "R08 – Most-Voted Movies",
            "R09 – Movie Count by Genre",
            "R10 – Average Runtime by Genre"
        ]
        sel_rep = st.selectbox("Select Report to inspect SQL syntax:", report_names)

        queries_map = {
            "R01": (
                "R01 – Movies released by year",
                """SELECT 
    YEAR(release_date) AS release_year, 
    COUNT(*) AS movie_count 
FROM Movie 
WHERE release_date IS NOT NULL 
GROUP BY YEAR(release_date) 
ORDER BY release_year ASC;"""
            ),
            "R02": (
                "R02 – Average rating by genre",
                """SELECT 
    g.genre_name, 
    ROUND(AVG(m.vote_average), 2) AS avg_tmdb_rating,
    COUNT(m.tmdb_id) AS movie_count
FROM Genre g
JOIN MovieGenre mg ON g.genre_id = mg.genre_id
JOIN Movie m ON mg.tmdb_id = m.tmdb_id
WHERE m.vote_average IS NOT NULL
GROUP BY g.genre_id, g.genre_name
ORDER BY avg_tmdb_rating DESC;"""
            ),
            "R03": (
                "R03 – Top movies by rating",
                """SELECT 
    m.tmdb_id, 
    m.title, 
    YEAR(m.release_date) AS release_year,
    m.vote_average, 
    m.vote_count,
    m.revenue,
    m.budget
FROM Movie m
WHERE m.vote_average IS NOT NULL 
  AND m.vote_count >= 1000
ORDER BY m.vote_average DESC, m.vote_count DESC
LIMIT 25;"""
            ),
            "R04": (
                "R04 – Revenue by release year",
                """SELECT 
    YEAR(release_date) AS release_year, 
    SUM(revenue) AS total_revenue,
    COUNT(*) AS movie_count,
    ROUND(AVG(revenue), 2) AS avg_revenue
FROM Movie 
WHERE release_date IS NOT NULL AND revenue > 0
GROUP BY YEAR(release_date) 
ORDER BY release_year ASC;"""
            ),
            "R05": (
                "R05 – Revenue by genre",
                """SELECT 
    g.genre_name, 
    SUM(m.revenue) AS total_revenue,
    COUNT(m.tmdb_id) AS movie_count,
    ROUND(AVG(m.revenue), 2) AS avg_revenue
FROM Genre g
JOIN MovieGenre mg ON g.genre_id = mg.genre_id
JOIN Movie m ON mg.tmdb_id = m.tmdb_id
WHERE m.revenue > 0
GROUP BY g.genre_id, g.genre_name
ORDER BY total_revenue DESC;"""
            ),
            "R06": (
                "R06 – Budget compared with revenue",
                """SELECT 
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
ORDER BY gap DESC;"""
            ),
            "R07": (
                "R07 – Rating distribution",
                """SELECT 
    CONCAT(FLOOR(vote_average), '.0 - ', FLOOR(vote_average) + 0.9) AS rating_interval,
    FLOOR(vote_average) AS interval_lower,
    COUNT(*) AS movie_count
FROM Movie 
WHERE vote_average IS NOT NULL
GROUP BY FLOOR(vote_average)
ORDER BY interval_lower ASC;"""
            ),
            "R08": (
                "R08 – Most-voted movies",
                """SELECT 
    tmdb_id, 
    title, 
    YEAR(release_date) AS release_year,
    vote_count, 
    vote_average,
    revenue
FROM Movie 
WHERE vote_count IS NOT NULL
ORDER BY vote_count DESC 
LIMIT 10;"""
            ),
            "R09": (
                "R09 – Movie count by genre",
                """SELECT 
    g.genre_name, 
    COUNT(DISTINCT mg.tmdb_id) AS movie_count
FROM Genre g
LEFT JOIN MovieGenre mg ON g.genre_id = mg.genre_id
GROUP BY g.genre_id, g.genre_name
ORDER BY movie_count DESC;"""
            ),
            "R10": (
                "R10 – Average runtime by genre",
                """SELECT 
    g.genre_name, 
    ROUND(AVG(m.runtime), 2) AS avg_runtime,
    COUNT(m.tmdb_id) AS movie_count
FROM Genre g
JOIN MovieGenre mg ON g.genre_id = mg.genre_id
JOIN Movie m ON mg.tmdb_id = m.tmdb_id
WHERE m.runtime IS NOT NULL AND m.runtime > 0
GROUP BY g.genre_id, g.genre_name
ORDER BY avg_runtime DESC;"""
            )
        }

        code_key = sel_rep[:3]
        title_text, query_text = queries_map[code_key]
        st.write(f"**{title_text}**")
        st.code(query_text, language="sql")

        # Live Execution preview of this query
        st.write("**Live Query Result Preview:**")
        preview_df = db.execute_query(query_text)
        st.dataframe(preview_df, use_container_width=True)

    with sql_tab2:
        st.markdown("### 🏗️ Data Definition Language (DDL) Schema Scripts")
        st.code("""
-- 1. Create Database
CREATE DATABASE IF NOT EXISTS MovieAnalytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE MovieAnalytics;

-- 2. Create Movie Table
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

-- 3. Create Genre Table
CREATE TABLE Genre (
    genre_id    INT PRIMARY KEY,
    genre_name  VARCHAR(100) UNIQUE NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Create MovieGenre Many-to-Many Bridge Table
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

-- 5. Analytical Full Catalogue View
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
        """, language="sql")

    with sql_tab3:
        st.markdown("### 📥 ETL Insertion Queries")
        st.code("""
-- Insert Genres with Duplicate Key Conflict Resolution
INSERT INTO Genre (genre_id, genre_name)
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE genre_name = VALUES(genre_name);

-- Insert Cleaned Movie Records
INSERT INTO Movie (tmdb_id, title, release_date, budget, revenue, runtime, vote_average, vote_count)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    release_date = VALUES(release_date),
    budget = VALUES(budget),
    revenue = VALUES(revenue),
    runtime = VALUES(runtime),
    vote_average = VALUES(vote_average),
    vote_count = VALUES(vote_count);

-- Insert Bridge Table Many-to-Many Relationships
INSERT IGNORE INTO MovieGenre (tmdb_id, genre_id)
VALUES (%s, %s);
        """, language="sql")

    with sql_tab4:
        st.markdown("### ⚡ Live Interactive SQL Console")
        st.caption("Execute custom `SELECT` queries directly against the database and view instantaneous results.")

        default_custom_query = "SELECT title, release_date, budget, revenue, (revenue - budget) AS gap FROM Movie WHERE revenue > 0 ORDER BY gap DESC LIMIT 5;"
        user_query = st.text_area("Enter SQL SELECT Query:", value=default_custom_query, height=120)

        if st.button("🚀 Execute Query"):
            # Security guard: Allow only SELECT queries
            cleaned_query = user_query.strip()
            if not cleaned_query.upper().startswith("SELECT"):
                st.error("⚠️ For security reasons, only SELECT queries are permitted in this console.")
            else:
                try:
                    res_df = db.execute_query(cleaned_query)
                    st.success(f"Query returned {len(res_df)} rows:")
                    st.dataframe(res_df, use_container_width=True)
                except Exception as ex:
                    st.error(f"SQL Execution Error: {str(ex)}")


# =============================================================================
# OPTION 5: 🔌 DATABASE SETTINGS VIEW
# =============================================================================
elif sidebar_nav.startswith("🔌"):
    st.subheader("🔌 MySQL Database Configuration & Status")
    st.caption("Inspect live connection status and configure connection parameters.")

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.markdown("#### Connection Status")
        if connected:
            st.success(f"🟢 {conn_status}")
        else:
            st.error(f"🔴 {conn_status}")
            st.info("💡 Running in pre-seeded SQLite Demo Mode.")

        st.markdown("""
        **Database Schema Details:**
        - **Target Database**: `MovieAnalytics`
        - **Relational Tables**: `Movie`, `Genre`, `MovieGenre`
        - **Normalization Standard**: 1NF, 2NF, 3NF compliant
        """)

    with d_col2:
        st.markdown("#### Database Quick Actions")
        st.write("To switch to your live MySQL server, update your credentials in the left sidebar drawer and click **'Test Connection'**.")
        st.code(f"""MYSQL_HOST = "{mysql_host}"
MYSQL_PORT = {mysql_port}
MYSQL_USER = "{mysql_user}"
MYSQL_DATABASE = "{mysql_db}"
""", language="ini")


# =============================================================================
# OPTION 6: 💾 EXPORT CSV
# =============================================================================
elif sidebar_nav.startswith("💾"):
    st.subheader("💾 Universal Data Export Center")
    st.caption("Select any analytical report, database summary table, or the filtered catalogue to preview and export as CSV.")

    export_target = st.selectbox(
        "Choose Dataset / Report to Export:",
        [
            "Full Filtered Catalogue",
            "R01 – Movies Released by Year",
            "R02 – Average Rating by Genre",
            "R03 – Top Movies by Rating",
            "R04 – Revenue by Release Year",
            "R05 – Revenue by Genre",
            "R06 – Budget Compared with Revenue (Gap)",
            "R07 – Rating Distribution",
            "R08 – Most-Voted Movies",
            "R09 – Movie Count by Genre",
            "R10 – Average Runtime by Genre"
        ]
    )

    if export_target == "Full Filtered Catalogue":
        export_df = catalogue_df
        export_filename = f"movie_catalogue_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    elif "R01" in export_target:
        export_df, _ = db.get_report_r01()
        export_filename = "R01_movies_by_year.csv"
    elif "R02" in export_target:
        export_df, _ = db.get_report_r02()
        export_filename = "R02_avg_rating_by_genre.csv"
    elif "R03" in export_target:
        export_df, _ = db.get_report_r03(min_votes=100, limit=50)
        export_filename = "R03_top_movies_by_rating.csv"
    elif "R04" in export_target:
        export_df, _ = db.get_report_r04()
        export_filename = "R04_revenue_by_year.csv"
    elif "R05" in export_target:
        export_df, _ = db.get_report_r05()
        export_filename = "R05_revenue_by_genre.csv"
    elif "R06" in export_target:
        export_df, _ = db.get_report_r06()
        export_filename = "R06_budget_vs_revenue_gap.csv"
    elif "R07" in export_target:
        export_df, _ = db.get_report_r07()
        export_filename = "R07_rating_distribution.csv"
    elif "R08" in export_target:
        export_df, _ = db.get_report_r08(limit=25)
        export_filename = "R08_most_voted_movies.csv"
    elif "R09" in export_target:
        export_df, _ = db.get_report_r09()
        export_filename = "R09_movie_count_by_genre.csv"
    elif "R10" in export_target:
        export_df, _ = db.get_report_r10()
        export_filename = "R10_avg_runtime_by_genre.csv"

    st.write(f"**Dataset Preview** ({len(export_df)} records):")
    st.dataframe(export_df, use_container_width=True, height=350)

    csv_bytes = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download '{export_filename}'",
        data=csv_bytes,
        file_name=export_filename,
        mime="text/csv",
        type="primary"
    )
