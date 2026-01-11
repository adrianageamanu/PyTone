import numpy as np
import hashlib
import config
from core.audio_loader import load_audio
from scipy.signal import spectrogram as scipy_spectrogram

def spectogram(signal):
    fs = config.SAMPLE_RATE
    window_size = config.FFT_WINDOW_SIZE

    # use scipy c-optimized implementation
    f, t, S = scipy_spectrogram(
        x=signal,
        fs=fs,
        window='hann',
        nperseg=window_size,
        noverlap=0, # no overlap for speed
        nfft=window_size * 2,
        mode='magnitude'
    )

    return S, f, t

def extract_peaks(S, f, t):
    peaks = []
    rows, cols = S.shape
    
    # define 3 frequency bands to capture bass, vocals, and highs
    # structure: (min_freq, max_freq)
    bands = [
        (0, 500),      # bass
        (500, 2000),   # mids/vocals
        (2000, 6000)   # treble
    ]
    
    # iterate through time columns
    for i in range(1, cols - 1):
        # calculate dynamic threshold for this time slice
        col_mean = np.mean(S[:, i])
        
        for min_f, max_f in bands:
            # find indices corresponding to this frequency band
            band_mask = (f >= min_f) & (f < max_f)
            band_indices = np.where(band_mask)[0]
            
            if len(band_indices) == 0:
                continue
                
            # find the strongest frequency in this band at this time
            # get the sub-array for this band
            band_energies = S[band_indices, i]
            
            # find max energy in this band
            local_max_idx = np.argmax(band_energies)
            max_energy = band_energies[local_max_idx]
            
            # global index in the spectrogram
            real_idx = band_indices[local_max_idx]
            
            # check if it's a true local peak (stronger than neighbors in time)
            if max_energy > col_mean * 1.5: # must be significantly above noise
                if max_energy > S[real_idx, i-1] and max_energy > S[real_idx, i+1]:
                    peaks.append((t[i], f[real_idx]))
                
    return peaks

def generate_hashes(peaks):
    hashes = []
    
    # standard shazam value
    FAN_OUT = 10 
    
    num_peaks = len(peaks)
    
    for i in range(num_peaks):
        for j in range(1, FAN_OUT + 1):
            if (i + j) < num_peaks:
                
                anchor = peaks[i]
                t1 = anchor[0]
                f1 = anchor[1]
                
                target = peaks[i + j]
                t2 = target[0]
                f2 = target[1]
                
                t_delta = t2 - t1
                
                # strict timing window (0.1s to 3s)
                if t_delta >= 0.1 and t_delta <= 3.0:
                    
                    f1_int = int(f1)
                    f2_int = int(f2)
                    t_delta_formated = round(t_delta, 2)
                    
                    raw_string = f"{f1_int}|{f2_int}|{t_delta_formated}"
                    
                    encoded_string = raw_string.encode('utf-8')
                    
                    sha1_obj = hashlib.sha1(encoded_string)
                    hash_result = sha1_obj.hexdigest()
                    
                    final_pair = (hash_result, t1)
                    hashes.append(final_pair)
                    
    return hashes

def process_audio(path):
    signal = load_audio(path)
    S, f, t = spectogram(signal)
    peaks = extract_peaks(S, f, t)
    final_hashes = generate_hashes(peaks)
    return final_hashes