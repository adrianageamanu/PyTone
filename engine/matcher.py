import mysql.connector
from collections import Counter

def find_potential_matches(sample_hashes, db_cursor):
    matches_found = {}

    for hash_value, t_sample in sample_hashes:
        # Search for the hash in the database to find song ID and original timestamp
        query = "SELECT song_id, offset_time FROM Hash WHERE hash_value = %s"
        
        try:
            db_cursor.execute(query, (hash_value,))
            database_hits = db_cursor.fetchall()
            
            if not database_hits:
                continue

            for song_id, t_db in database_hits:
                time_diff = t_db - t_sample
                
                # Round to 1 decimal to handle slight recording variations
                time_diff = round(time_diff, 1)
                
                # Group time differences by song_id for histogram analysis
                if song_id not in matches_found:
                    matches_found[song_id] = []
                
                matches_found[song_id].append(time_diff)
                
        except mysql.connector.Error:
            # Skip if there is a database communication error
            continue

    return matches_found