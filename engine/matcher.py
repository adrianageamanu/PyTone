from database import db_handler
from collections import Counter

def find_potential_matches(sample_hashes):
    matches_found = {}

    for hash_value, t_sample in sample_hashes:
        # fetch all occurrences of this hash from db
        database_hits = db_handler.get_matches_from_hash(hash_value)
        
        if not database_hits:
            continue
            
        for song_id, t_db in database_hits:
            # calculate the relative offset
            # if the song matches, (t_db - t_sample) should be constant
            offset = t_db - t_sample
            
            # quantize offset to 0.1s to handle float inaccuracies
            offset_bin = round(offset, 1)
            
            if song_id not in matches_found:
                matches_found[song_id] = []
            
            matches_found[song_id].append(offset_bin)

    return matches_found

def rank_matches(matches_found):
    final_results = []

    for song_id, offsets in matches_found.items():
        # count the occurences of the most common offset
        # this is the 'score' of the match
        offset_counts = Counter(offsets)
        best_offset, peak_score = offset_counts.most_common(1)[0]
        
        # increased threshold: with ~3000 hashes, a real match should have >10 hits
        if peak_score < 10:
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

    # sort by highest score first
    final_results.sort(key=lambda x: x['score'], reverse=True)
    
    return final_results

def identify_song(file_path):
    # local import
    from core.fingerprinter import process_audio
    
    sample_hashes = process_audio(file_path)
    
    if not sample_hashes:
        return None

    matches = find_potential_matches(sample_hashes)
    
    if not matches:
        return None

    ranked_list = rank_matches(matches)

    if ranked_list:
        return ranked_list[0]
    
    return None