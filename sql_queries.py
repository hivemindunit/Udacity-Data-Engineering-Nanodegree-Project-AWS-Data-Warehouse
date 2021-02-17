import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs;"
songplay_table_drop = "DROP TABLE IF EXISTS songplays;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS songs;"
artist_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = "DROP TABLE IF EXISTS time;"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE staging_events (
    artist TEXT,
    auth TEXT,
    first_name TEXT,
    gender CHAR(1),
    item_in_session INTEGER,
    last_name TEXT,
    length NUMERIC,
    level TEXT,
    location TEXT,
    method TEXT,
    page TEXT,
    registration NUMERIC,
    session_id INTEGER,
    song TEXT,
    status SMALLINT,
    ts BIGINT,
    user_agent TEXT,
    user_id INTEGER
);
""")

staging_songs_table_create = ("""
CREATE TABLE staging_songs (
    num_songs SMALLINT,
    artist_id TEXT,
    artist_latitude NUMERIC,
    artist_longitude NUMERIC,
    artist_location TEXT,
    artist_name TEXT,
    song_id TEXT,
    title TEXT,
    duration NUMERIC,
    year SMALLINT
);
""")

songplay_table_create = ("""
CREATE TABLE songplays (
    songplay_id INTEGER IDENTITY(0,1) NOT NULL,
    start_time TIMESTAMP,
    user_id INTEGER NOT NULL,
    level TEXT,
    song_id TEXT,
    artist_id TEXT,
    session_id INTEGER,
    location TEXT,
    user_agent TEXT,
    primary key(songplay_id)
);
""")

user_table_create = ("""
CREATE TABLE users (
    user_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gender CHAR(1),
    level TEXT,
    primary key(user_id)
);
""")

song_table_create = ("""
CREATE TABLE songs (
    song_id TEXT,
    title TEXT,
    artist_id TEXT,
    year SMALLINT,
    duration SMALLINT,
    primary key(song_id)
);
""")

artist_table_create = ("""
CREATE TABLE artists (
    artist_id TEXT,
    name TEXT,
    location TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    primary key(artist_id)
);
""")

time_table_create = ("""
CREATE TABLE time (
    start_time timestamp NOT NULL,
    hour SMALLINT,
    day SMALLINT,
    week SMALLINT,
    month SMALLINT,
    year SMALLINT,
    weekday SMALLINT,
    primary key(start_time)
);
""")

# STAGING TABLES

staging_events_copy = ("""
    copy staging_events from {}
    credentials 'aws_iam_role={}' 
    compupdate off region 'us-west-2'
    timeformat as 'epochmillisecs'
    truncatecolumns blanksasnull emptyasnull
    format as json {};
""").format(config.get("S3","LOG_DATA"), 
config.get("IAM_ROLE","ARN"), config.get("S3","LOG_JSONPATH"))

staging_songs_copy = ("""
    copy staging_songs from {}
    credentials 'aws_iam_role={}' 
    compupdate off region 'us-west-2'
    truncatecolumns blanksasnull emptyasnull
    format as json 'auto';
""").format(config.get("S3","SONG_DATA"), config.get("IAM_ROLE","ARN"))

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays(
start_time, user_id, level, song_id, 
artist_id, session_id, location, user_agent)
SELECT timestamp 'epoch' + e.ts/1000 * interval '1 second' as start_time, 
e.user_id, e.level, s.song_id, s.artist_id, 
e.session_id, e.location, e.user_agent
FROM staging_events e, staging_songs s
WHERE e.page = 'NextSong' 
AND e.song = s.title 
AND e.artist = s.artist_name 
AND e.length = s.duration
""")

user_table_insert = ("""
INSERT INTO users(user_id, first_name, last_name, gender, level)
SELECT distinct  user_id, first_name, last_name, gender, level
FROM staging_events
WHERE page = 'NextSong'
""")

song_table_insert = ("""
INSERT INTO songs(song_id, title, artist_id, year, duration)
SELECT song_id, title, artist_id, year, duration
FROM staging_songs
WHERE song_id IS NOT NULL
""")

artist_table_insert = ("""
INSERT INTO artists(artist_id, name, location, latitude, longitude)
SELECT distinct artist_id, artist_name, artist_location, 
artist_latitude, artist_longitude 
FROM staging_songs
WHERE artist_id IS NOT NULL
""")

time_table_insert = ("""
INSERT INTO time(start_time, hour, day, week, month, year, weekDay)
SELECT start_time, extract(hour from start_time), extract(day from start_time),
extract(week from start_time), extract(month from start_time), 
extract(year from start_time), extract(dayofweek from start_time)
FROM songplays
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
