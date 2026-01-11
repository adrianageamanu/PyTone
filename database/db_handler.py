import os
import mysql.connector
from dotenv import load_dotenv

# initialize global variables
mydb = None
mycursor = None

def prepare_db_handler():
    # access global variables to update them
    global mydb, mycursor
    
    # load environment variables from .env
    load_dotenv()
    # read environment variables
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # connect to mysql database
    mydb = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )

    # create a cursor object
    mycursor = mydb.cursor()

def setup_database():
    # reset db if exists
    mycursor.execute("DROP DATABASE IF EXISTS pytone")
    # create new db
    mycursor.execute("CREATE DATABASE pytone")
    # select the db
    mycursor.execute("USE pytone") 

    # create song table
    mycursor.execute("""
        CREATE TABLE Song (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            artist VARCHAR(255),
            duration INT,
            thumbnail_url VARCHAR(500),
            youtube_url VARCHAR(500)
        )
    """)

    # create hash table with song as foreign key
    mycursor.execute("""
        CREATE TABLE Hash (
            id INT AUTO_INCREMENT PRIMARY KEY,
            hash_value VARCHAR(255),
            song_id INT,
            offset_time FLOAT,
            FOREIGN KEY (song_id) REFERENCES Song(id),
            INDEX (hash_value)
        )
    """)

    # save changes
    mydb.commit()

def show_db_tables():
    # retrieve table list
    mycursor.execute("SHOW TABLES")
    for x in mycursor:
        print(x)

def get_all_songs():
    try:
        sql = "SELECT name, artist, duration, thumbnail_url FROM Song ORDER BY id DESC"

        mycursor.execute(sql)

        return mycursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching the library: {err}")
        return []

def add_song(name, artist, duration, thumbnail_url, youtube_url):
    try:
        # check for duplicate with limit to prevent unread result errors
        check_sql = "SELECT id FROM Song WHERE name = %s AND artist = %s LIMIT 1"
        # values to check
        check_val = (name, artist)

        # execute check
        mycursor.execute(check_sql, check_val)

        # if we already stored that song, return its id
        result = mycursor.fetchone()
        if result:
            # return existing id
            return result[0]

        # insert command
        sql = "INSERT INTO Song (name, artist, duration, thumbnail_url, youtube_url) VALUES (%s, %s, %s, %s, %s)"
        # values to insert
        val = (name, artist, duration, thumbnail_url, youtube_url)

        # execute insert
        mycursor.execute(sql, val)

        # save changes
        mydb.commit()

        # return new song id
        return mycursor.lastrowid

    except mysql.connector.Error as err:
        # print error message
        print(f"Error: failed to add song: {err}")
    
        # return none
        return None
    
def add_hash_to_song(song_id, hash_val, offset_time):
    try:
        # insert command
        sql = "INSERT INTO Hash (hash_value, song_id, offset_time) VALUES (%s, %s, %s)"
        # values to insert
        val = (hash_val, song_id, offset_time)

        # execute insert
        mycursor.execute(sql, val)

        # save changes
        mydb.commit()

    except mysql.connector.Error:
        # print error message
        print("Error: Song id likely does not exist.")

def get_hashes_by_song(song_id):
    try:
        # select command
        sql = "SELECT hash_value FROM Hash WHERE song_id = %s"
        # value to select
        val = (song_id,)

        # execute select
        mycursor.execute(sql, val)

        # return list of hashes
        return mycursor.fetchall()

    except mysql.connector.Error:
        # print error message
        print("Error: Failed to retrieve hashes.")
    
        # return empty list
        return []

def get_song_via_hash(hash_val):
    try:
        # join tables to find song details
        # with limit to prevent unread result errors
        sql = """
            SELECT s.name, s.artist, s.duration, s.thumbnail_url, s.youtube_url 
            FROM Song s 
            JOIN Hash h ON s.id = h.song_id 
            WHERE h.hash_value = %s
            LIMIT 1
        """
        # value to search for
        val = (hash_val,)

        # execute command
        mycursor.execute(sql, val)

        # return first match or none
        return mycursor.fetchone()

    except mysql.connector.Error as err:
        # print error message
        print(f"Error: Failed to find song: {err}")

        # return none
        return None