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
            # calculate offset: t_db = t_sample + offset
            # so offset = t_db - t_sample
            time_diff = t_db - t_sample
            
            # quantize to 0.1s to allow slight timing errors
            time_diff = round(time_diff, 1)
            
            if song_id not in matches_found:
                matches_found[song_id] = []
            
            matches_found[song_id].append(time_diff)

    return matches_found

def rank_matches(matches_found):
    final_results = []

    for song_id, offsets in matches_found.items():
        # find the most common time offset
        offset_counts = Counter(offsets)
        best_offset, peak_score = offset_counts.most_common(1)[0]
        
        # basic threshold to avoid noise
        if peak_score < 3:
            continue
        
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

    # sort by highest score
    final_results.sort(key=lambda x: x['score'], reverse=True)
    
    return final_results

def identify_song(file_path):
    sample_hashes = process_audio(file_path)
    
    if not sample_hashes:
        print("no hashes generated.")
        return None

    matches = find_potential_matches(sample_hashes)
    
    if not matches:
        print("no matches found.")
        return None

    ranked_list = rank_matches(matches)

    if ranked_list:
        return ranked_list[0]
    
    return None