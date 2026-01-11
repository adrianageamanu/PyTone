from database import db_handler
from core.fingerprinter import process_audio
from collections import Counter

def find_potential_matches(sample_hashes):
    matches_found = {}

    for hash_value, t_sample in sample_hashes:
        # get hits from db handler
        database_hits = db_handler.get_matches_from_hash(hash_value)
            
        if not database_hits:
            continue

        for song_id, t_db in database_hits:
            time_diff = t_db - t_sample
            
            # round to 1 decimal
            time_diff = round(time_diff, 1)
            
            # group by song id
            if song_id not in matches_found:
                matches_found[song_id] = []
            
            matches_found[song_id].append(time_diff)

    return matches_found

def rank_matches(matches_found):
    final_results = []

    for song_id, offsets in matches_found.items():
        # Use Counter to create a histogram of the time differences
        offset_counts = Counter(offsets)
        
        # Get the most frequent offset and its count
        best_offset, peak_score = offset_counts.most_common(1)[0]
        
        # fetch song info using db handler
        song_info = db_handler.get_song_by_id(song_id)
        
        if song_info:
            final_results.append({
                "title": song_info[0],
                "artist": song_info[1],
                "dur": song_info[2],
                "img": song_info[3],
                "url": song_info[4],
                "score": peak_score,
                "offset": best_offset
            })

    # Sort results so the highest score is at the top
    final_results.sort(key=lambda x: x['score'], reverse=True)
    
    return final_results

def identify_song(file_path):
    # Get hashes from the audio file
    sample_hashes = process_audio(file_path)
    
    if not sample_hashes:
        print("No hashes generated. Check audio file.")
        return None

    # Find matches in database
    matches = find_potential_matches(sample_hashes)
    
    if not matches:
        print("No matches found in database.")
        return None

    # Rank them
    ranked_list = rank_matches(matches)

    # Return the top match
    if ranked_list:
        return ranked_list[0]
    
    return None