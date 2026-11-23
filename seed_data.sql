-- ============================================================================
-- Seed Data for MovieAnalytics
-- Based on Kaggle's The Movies Dataset (movies_metadata.csv)
-- ============================================================================

USE MovieAnalytics;

-- ----------------------------------------------------------------------------
-- 1. Insert Standard TMDb Genres
-- ----------------------------------------------------------------------------
INSERT INTO Genre (genre_id, genre_name) VALUES
(28, 'Action'),
(12, 'Adventure'),
(16, 'Animation'),
(35, 'Comedy'),
(80, 'Crime'),
(99, 'Documentary'),
(18, 'Drama'),
(10751, 'Family'),
(14, 'Fantasy'),
(36, 'History'),
(27, 'Horror'),
(10402, 'Music'),
(9648, 'Mystery'),
(10749, 'Romance'),
(878, 'Science Fiction'),
(10770, 'TV Movie'),
(53, 'Thriller'),
(10752, 'War'),
(37, 'Western')
ON DUPLICATE KEY UPDATE genre_name = VALUES(genre_name);

-- ----------------------------------------------------------------------------
-- 2. Insert Representative Movie Records
-- ----------------------------------------------------------------------------
INSERT INTO Movie (tmdb_id, title, release_date, budget, revenue, runtime, vote_average, vote_count) VALUES
(19995, 'Avatar', '2009-12-10', 237000000, 2787965087, 162.00, 7.2, 11800),
(597, 'Titanic', '1997-11-18', 200000000, 1845034188, 194.00, 7.5, 7562),
(27205, 'Inception', '2010-07-14', 160000000, 825532764, 148.00, 8.1, 13752),
(155, 'The Dark Knight', '2008-07-16', 185000000, 1004558444, 152.00, 8.2, 12002),
(680, 'Pulp Fiction', '1994-09-10', 8000000, 213928762, 154.00, 8.3, 8428),
(238, 'The Godfather', '1972-03-14', 6000000, 245066411, 175.00, 8.5, 5893),
(278, 'The Shawshank Redemption', '1994-09-23', 25000000, 28341469, 142.00, 8.5, 8205),
(157336, 'Interstellar', '2014-11-05', 165000000, 675120017, 169.00, 8.1, 10867),
(24428, 'The Avengers', '2012-04-25', 220000000, 1519557910, 143.00, 7.4, 11776),
(862, 'Toy Story', '1995-10-30', 30000000, 373554033, 81.00, 7.7, 5269),
(329, 'Jurassic Park', '1993-06-11', 63000000, 920100000, 127.00, 7.6, 4856),
(13, 'Forrest Gump', '1994-07-06', 55000000, 677945399, 142.00, 8.2, 7927),
(603, 'The Matrix', '1999-03-30', 63000000, 463517383, 136.00, 7.9, 8907),
(550, 'Fight Club', '1999-10-15', 63000000, 100853753, 139.00, 8.3, 9413),
(129, 'Spirited Away', '2001-07-20', 15000000, 274925095, 125.00, 8.3, 3840),
(354912, 'Coco', '2017-10-27', 175000000, 807082196, 105.00, 8.2, 17000),
(496243, 'Parasite', '2019-05-30', 11400000, 258773045, 132.00, 8.5, 16000),
(98, 'Gladiator', '2000-05-01', 103000000, 457640427, 155.00, 7.9, 5439),
(105, 'Back to the Future', '1985-07-03', 19000000, 381109762, 116.00, 8.0, 6079),
(120, 'The Lord of the Rings: The Fellowship of the Ring', '2001-12-18', 93000000, 871368364, 178.00, 8.0, 8770),
(122, 'The Lord of the Rings: The Return of the King', '2003-12-01', 94000000, 1118888979, 201.00, 8.1, 8064),
(299536, 'Avengers: Infinity War', '2018-04-25', 300000000, 2048359754, 149.00, 8.3, 27000),
(299534, 'Avengers: Endgame', '2019-04-24', 356000000, 2797800564, 181.00, 8.3, 23000),
(49026, 'The Dark Knight Rises', '2012-07-16', 250000000, 1084939099, 165.00, 7.6, 9106),
(77, 'Memento', '2000-10-11', 9000000, 39723096, 113.00, 8.1, 4028),
(11, 'Star Wars', '1977-05-25', 11000000, 775398007, 121.00, 8.1, 6624),
(1891, 'The Empire Strikes Back', '1980-05-17', 18000000, 538400000, 124.00, 8.2, 5879),
(598, 'City of God', '2002-02-05', 3300000, 30595293, 130.00, 8.1, 1814),
(694, 'The Shining', '1980-05-22', 19000000, 44017374, 144.00, 8.1, 3790),
(424, 'Schindler''s List', '1993-11-29', 22000000, 321365567, 195.00, 8.3, 4329),
(8587, 'The Lion King', '1994-06-23', 45000000, 788241776, 89.00, 8.0, 5376),
(807, 'Se7en', '1995-09-22', 33000000, 327311859, 127.00, 8.1, 5782),
(274, 'The Silence of the Lambs', '1991-02-01', 19000000, 272742922, 118.00, 8.1, 4443),
(289, 'Casablanca', '1942-11-26', 1000000, 10462500, 102.00, 8.2, 2410),
(637, 'Life Is Beautiful', '1997-12-20', 20000000, 229400000, 116.00, 8.3, 3569),
(19404, 'Dilwale Dulhania Le Jayenge', '1995-10-20', 4000000, 100000000, 190.00, 8.7, 3800),
(24, 'Whiplash', '2014-10-10', 3300000, 48982041, 107.00, 8.3, 4256),
(389, '12 Angry Men', '1957-03-25', 1000000, 4360000, 96.00, 8.5, 6500),
(1422, 'The Departed', '2006-10-05', 90000000, 289847354, 151.00, 7.9, 4339),
(1124, 'The Prestige', '2006-10-19', 40000000, 109676311, 130.00, 8.0, 4391),
(37799, 'The Social Network', '2010-10-01', 40000000, 224920315, 120.00, 7.7, 5123),
(106646, 'The Wolf of Wall Street', '2013-12-25', 100000000, 392000694, 180.00, 7.9, 6571),
(10195, 'Thor', '2011-04-21', 150000000, 449326618, 115.00, 6.7, 7022),
(68718, 'Django Unchained', '2012-12-25', 100000000, 425368238, 165.00, 7.8, 10098),
(335984, 'Blade Runner 2049', '2017-10-04', 150000000, 259239658, 164.00, 7.9, 11500),
(14160, 'Up', '2009-05-28', 175000000, 735099082, 96.00, 7.7, 6870),
(12, 'Finding Nemo', '2003-05-30', 94000000, 940335536, 100.00, 7.6, 6122),
(10681, 'WALL·E', '2008-06-22', 180000000, 521311860, 98.00, 7.8, 6296),
(490132, 'Green Book', '2018-11-16', 23000000, 321752656, 130.00, 8.2, 10200),
(372058, 'Your Name.', '2016-08-26', 5000000, 357986087, 106.00, 8.5, 9800)
ON DUPLICATE KEY UPDATE 
    title = VALUES(title),
    release_date = VALUES(release_date),
    budget = VALUES(budget),
    revenue = VALUES(revenue),
    runtime = VALUES(runtime),
    vote_average = VALUES(vote_average),
    vote_count = VALUES(vote_count);

-- ----------------------------------------------------------------------------
-- 3. Link Movies and Genres (MovieGenre Bridge Table)
-- ----------------------------------------------------------------------------
INSERT INTO MovieGenre (tmdb_id, genre_id) VALUES
-- Avatar: Action(28), Adventure(12), Fantasy(14), Sci-Fi(878)
(19995, 28), (19995, 12), (19995, 14), (19995, 878),
-- Titanic: Drama(18), Romance(10749)
(597, 18), (597, 10749),
-- Inception: Action(28), Sci-Fi(878), Adventure(12)
(27205, 28), (27205, 878), (27205, 12),
-- The Dark Knight: Drama(18), Action(28), Crime(80), Thriller(53)
(155, 18), (155, 28), (155, 80), (155, 53),
-- Pulp Fiction: Thriller(53), Crime(80)
(680, 53), (680, 80),
-- The Godfather: Drama(18), Crime(80)
(238, 18), (238, 80),
-- The Shawshank Redemption: Drama(18), Crime(80)
(278, 18), (278, 80),
-- Interstellar: Adventure(12), Drama(18), Sci-Fi(878)
(157336, 12), (157336, 18), (157336, 878),
-- The Avengers: Action(28), Adventure(12), Sci-Fi(878)
(24428, 28), (24428, 12), (24428, 878),
-- Toy Story: Animation(16), Comedy(35), Family(10751)
(862, 16), (862, 35), (862, 10751),
-- Jurassic Park: Adventure(12), Sci-Fi(878)
(329, 12), (329, 878),
-- Forrest Gump: Comedy(35), Drama(18), Romance(10749)
(13, 35), (13, 18), (13, 10749),
-- The Matrix: Action(28), Sci-Fi(878)
(603, 28), (603, 878),
-- Fight Club: Drama(18)
(550, 18),
-- Spirited Away: Animation(16), Family(10751), Fantasy(14)
(129, 16), (129, 10751), (129, 14),
-- Coco: Animation(16), Family(10751), Music(10402), Adventure(12)
(354912, 16), (354912, 10751), (354912, 10402), (354912, 12),
-- Parasite: Comedy(35), Thriller(53), Drama(18)
(496243, 35), (496243, 53), (496243, 18),
-- Gladiator: Action(28), Drama(18), Adventure(12)
(98, 28), (98, 18), (98, 12),
-- Back to the Future: Adventure(12), Comedy(35), Sci-Fi(878), Family(10751)
(105, 12), (105, 35), (105, 878), (105, 10751),
-- The Lord of the Rings 1: Adventure(12), Fantasy(14), Action(28)
(120, 12), (120, 14), (120, 28),
-- The Lord of the Rings 3: Adventure(12), Fantasy(14), Action(28)
(122, 12), (122, 14), (122, 28),
-- Avengers: Infinity War: Action(28), Adventure(12), Sci-Fi(878)
(299536, 28), (299536, 12), (299536, 878),
-- Avengers: Endgame: Action(28), Adventure(12), Sci-Fi(878)
(299534, 28), (299534, 12), (299534, 878),
-- The Dark Knight Rises: Action(28), Crime(80), Drama(18), Thriller(53)
(49026, 28), (49026, 80), (49026, 18), (49026, 53),
-- Memento: Mystery(9648), Thriller(53)
(77, 9648), (77, 53),
-- Star Wars: Adventure(12), Action(28), Sci-Fi(878)
(11, 12), (11, 28), (11, 878),
-- The Empire Strikes Back: Adventure(12), Action(28), Sci-Fi(878)
(1891, 12), (1891, 28), (1891, 878),
-- City of God: Drama(18), Crime(80)
(598, 18), (598, 80),
-- The Shining: Horror(27), Thriller(53)
(694, 27), (694, 53),
-- Schindler's List: Drama(18), History(36), War(10752)
(424, 18), (424, 36), (424, 10752),
-- The Lion King: Animation(16), Drama(18), Family(10751)
(8587, 16), (8587, 18), (8587, 10751),
-- Se7en: Crime(80), Mystery(9648), Thriller(53)
(807, 80), (807, 9648), (807, 53),
-- The Silence of the Lambs: Crime(80), Drama(18), Thriller(53)
(274, 80), (274, 18), (274, 53),
-- Casablanca: Drama(18), Romance(10749)
(289, 18), (289, 10749),
-- Life Is Beautiful: Comedy(35), Drama(18)
(637, 35), (637, 18),
-- Dilwale Dulhania Le Jayenge: Comedy(35), Drama(18), Romance(10749)
(19404, 35), (19404, 18), (19404, 10749),
-- Whiplash: Drama(18), Music(10402)
(24, 18), (24, 10402),
-- 12 Angry Men: Drama(18)
(389, 18),
-- The Departed: Drama(18), Thriller(53), Crime(80)
(1422, 18), (1422, 53), (1422, 80),
-- The Prestige: Drama(18), Mystery(9648), Thriller(53)
(1124, 18), (1124, 9648), (1124, 53),
-- The Social Network: Drama(18)
(37799, 18),
-- The Wolf of Wall Street: Crime(80), Drama(18), Comedy(35)
(106646, 80), (106646, 18), (106646, 35),
-- Thor: Adventure(12), Fantasy(14), Action(28)
(10195, 12), (10195, 14), (10195, 28),
-- Django Unchained: Drama(18), Western(37)
(68718, 18), (68718, 37),
-- Blade Runner 2049: Sci-Fi(878), Drama(18)
(335984, 878), (335984, 18),
-- Up: Animation(16), Comedy(35), Family(10751), Adventure(12)
(14160, 16), (14160, 35), (14160, 10751), (14160, 12),
-- Finding Nemo: Animation(16), Family(10751)
(12, 16), (12, 10751),
-- WALL·E: Animation(16), Family(10751), Sci-Fi(878)
(10681, 16), (10681, 10751), (10681, 878),
-- Green Book: Drama(18), Comedy(35)
(490132, 18), (490132, 35),
-- Your Name.: Animation(16), Romance(10749), Drama(18)
(372058, 16), (372058, 10749), (372058, 18)
ON DUPLICATE KEY UPDATE tmdb_id = VALUES(tmdb_id);
