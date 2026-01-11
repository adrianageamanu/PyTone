import numpy as np
import hashlib
import config
from core.audio_loader import load_audio
from scipy.signal import spectrogram as scipy_spectrogram
from scipy.ndimage import maximum_filter

def spectogram(signal):
    # standard shazam settings
    fs = config.SAMPLE_RATE
    window_size = config.FFT_WINDOW_SIZE
    
    # create spectrogram
    f, t, S = scipy_spectrogram(
        x=signal,
        fs=fs,
        window='hann',
        nperseg=window_size,
        noverlap=int(window_size * config.OVERLAP_RATIO),
        nfft=window_size * 2,
        mode='magnitude'
    )
    
    # use log-magnitude (decibels) for better handling of dynamic range
    # this matches the Shazam logic
    S = np.log(S + 1e-10)
    
    return S, f, t

def extract_peaks(S, f, t):
    # these parameters determine the density of peaks
    # (20, 20) is the standard Dejavu value for good collision resistance
    struct_size = (20, 20) 
    
    # find local maxima in 2D (time and frequency)
    # this is much faster than iterating manually
    local_max = maximum_filter(S, size=struct_size) == S
    
    # dynamic threshold: only keep peaks that are significant relative to the background
    # using 'mean' ensures we get peaks even in quiet songs
    background = (S > np.mean(S))
    
    # intersection of local maxima and background threshold
    peaks_mask = local_max & background
    
    # extract indices
    freq_idx, time_idx = np.where(peaks_mask)
    
    # zip and sort by time (required for hashing loop)
    peaks = list(zip(t[time_idx], f[freq_idx]))
    peaks.sort(key=lambda x: x[0])
    
    return peaks

def generate_hashes(peaks):
    hashes = []
    # fan_out determines how many pairs we make per peak
    # 15 is the standard value to get ~3000 hashes per song
    FAN_OUT = config.FAN_VALUE 
    
    num_peaks = len(peaks)
    
    for i in range(num_peaks):
        for j in range(1, FAN_OUT):
            if (i + j) < num_peaks:
                
                t1, f1 = peaks[i]
                t2, f2 = peaks[i + j]
                
                t_delta = t2 - t1
                
                # strict window between 0s and 10s (standard is often 0-4s)
                if 0 <= t_delta <= 10.0: 
                    
                    # use binning for frequencies to improve match accuracy
                    # round t_delta to 2 decimals to allow slight timing jitter
                    h_str = f"{int(f1)}|{int(f2)}|{round(t_delta, 2)}"
                    
                    h_val = hashlib.sha1(h_str.encode('utf-8')).hexdigest()
                    
                    # add to list
                    hashes.append((h_val, t1))
                    
    return hashes

def process_audio(path):
    signal = load_audio(path)
    S, f, t = spectogram(signal)
    peaks = extract_peaks(S, f, t)
    final_hashes = generate_hashes(peaks)
    return final_hashes