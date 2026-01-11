from core.fingerprinter import process_audio
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

def rank_matches(matches_found, db_cursor):
    final_results = []

    for song_id, offsets in matches_found.items():
        # Use Counter to create a histogram of the time differences
        offset_counts = Counter(offsets)
        
        # Get the most frequent offset and its count
        best_offset, peak_score = offset_counts.most_common(1)[0]
        
        # Fetch song details from the database
        query = "SELECT name, artist FROM Song WHERE id = %s"
        db_cursor.execute(query, (song_id,))
        song_info = db_cursor.fetchone()
        
        if song_info:
            final_results.append({
                "name": song_info[0],
                "artist": song_info[1],
                "score": peak_score,
                "offset": best_offset
            })

    # Sort results so the highest score is at the top
    final_results.sort(key=lambda x: x['score'], reverse=True)
    
    return final_results

def identify_song(file_path, db_cursor):
    # Get hashes from the audio file
    sample_hashes = process_audio(file_path)
    
    if not sample_hashes:
        print("No hashes generated. Check audio file.")
        return []

    # Find matches in database
    matches = find_potential_matches(sample_hashes, db_cursor)
    
    if not matches:
        print("No matches found in database.")
        return []

    # Rank them
    ranked_list = rank_matches(matches, db_cursor)

    # Return the top match
    if ranked_list:
        return ranked_list[0]
    
    return None