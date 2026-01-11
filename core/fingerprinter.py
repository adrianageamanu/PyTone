import numpy as np
import hashlib
import config
from core.audio_loader import load_audio
from scipy.signal import spectrogram as scipy_spectrogram

# def spectogram(signal):
#     fs = config.SAMPLE_RATE
#     window_size = config.FFT_WINDOW_SIZE

#     # Calculate the total number of frames
#     n = len(signal)
#     num_windows = n // (window_size)

#     # Initialize the Spectrogram matrix
#     S = np.zeros((window_size, num_windows))
#     hann_window = np.hanning(window_size)

#     for i in range(num_windows):
#         start = i * window_size
#         end = start + window_size
#         window = signal[start:end]
        
#         # Apply the Hann windowing function to the current segment
#         hanned = np.zeros(window_size)
#         for j in range(window_size):
#             hanned[j] = window[j] * hann_window[j]
        
#         F = np.fft.fft(hanned, n=2 * window_size)
        
#         S[:, i] = np.abs(F[:window_size])

#     # Generate the frequency vector
#     f = np.zeros(window_size)
#     for i in range(window_size):
#         f[i] = i * fs / (2 * window_size)

#     # Generate the time vector
#     t = np.zeros(num_windows)
#     for i in range(num_windows):
#         t[i] = i * window_size / fs

#     return S, f, t

def spectogram(signal):
    fs = config.SAMPLE_RATE
    window_size = config.FFT_WINDOW_SIZE

    # use scipy c-optimized implementation instead of python loop
    f, t, S = scipy_spectrogram(
        x=signal,
        fs=fs,
        window='hann',
        nperseg=window_size,
        noverlap=0,
        nfft=window_size * 2,
        mode='magnitude'
    )

    return S, f, t

def extract_peaks(S, f, t):
    peaks = []
    rows, cols = S.shape
    
    # Iterate from 1 to cols-1 to always have left/right neighbors
    for i in range(1, cols - 1):
        column = S[:, i]
        
        # Local threshold for the current time window
        threshold = np.mean(column) + 0.5 * np.std(column)
        
        # Define 3 frequency bands with clear names
        low_mask = (f < 500)
        mid_mask = (f >= 500) & (f < 2000)
        high_mask = (f >= 2000)
        
        # Extract the strongest local peak from each band
        for mask in [low_mask, mid_mask, high_mask]:
            band_indices = np.where(mask)[0]
            
            max_val = -1
            max_idx = -1
            
            for idx in band_indices:
                if idx <= 0 or idx >= rows - 1:
                    continue
                
                current_energy = S[idx, i]
                
                if current_energy > threshold:
                    # Point must be greater than its 4 direct neighbors
                    if current_energy > S[idx-1, i] and current_energy > S[idx+1, i] and \
                       current_energy > S[idx, i-1] and current_energy > S[idx, i+1]:
                        
                        if current_energy > max_val:
                            max_val = current_energy
                            max_idx = idx

            # Store the identified peak (timestamp and frequency)
            if max_idx != -1:
                peaks.append((t[i], f[max_idx]))
                
    return peaks

def generate_hashes(peaks):
    hashes = []
    
    # Value recommended in Shazam paper
    FAN_OUT = 10 
    
    num_peaks = len(peaks)
    
    for i in range(num_peaks):
        for j in range(1, FAN_OUT + 1):
            if (i + j) < num_peaks:
                
                # Extract data for the Anchor peak
                anchor = peaks[i]
                t1 = anchor[0]
                f1 = anchor[1]
                
                # Extract data for the Target peak
                target = peaks[i + j]
                t2 = target[0]
                f2 = target[1]
                
                t_delta = t2 - t1
                
                if t_delta > 0 and t_delta <= 3.0:
                    
                    # Round frequencies to integers to handle small recording errors
                    f1_int = int(f1)
                    f2_int = int(f2)
                    
                    # Format the time delta to 2 decimal places
                    t_delta_formated = round(t_delta, 2)
                    
                    # Format: Frequency1 | Frequency2 | Time_Delta
                    raw_string = str(f1_int) + "|" + str(f2_int) + "|" + str(t_delta_formated)
                    
                    # Encode the string to bytes so it can be hashed
                    encoded_string = raw_string.encode('utf-8')
                    
                    # Apply the SHA-1 algorithm to create a unique signature
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