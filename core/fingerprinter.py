import numpy as np
import config

def spectogram(signal):
    fs = config.SAMPLE_RATE
    window_size = config.FFT_WINDOW_SIZE

    # Calculate the total number of frames
    n = len(signal)
    num_windows = n // (window_size)

    # Initialize the Spectrogram matrix
    S = np.zeros((window_size, num_windows))
    hann_window = np.hanning(window_size)

    for i in range(num_windows):
        start = i * window_size
        end = start + window_size
        window = signal[start:end]
        
        # Apply the Hann windowing function to the current segment
        hanned = np.zeros(window_size)
        for j in range(window_size):
            hanned[j] = window[j] * hann_window[j]
        
        F = np.fft.fft(hanned, n=2 * window_size)
        
        S[:, i] = np.abs(F[:window_size])

    # Generate the frequency vector
    f = np.zeros(window_size)
    for i in range(window_size):
        f[i] = i * fs / (2 * window_size)

    # Generate the time vector
    t = np.zeros(num_windows)
    for i in range(num_windows):
        t[i] = i * window_size / fs

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