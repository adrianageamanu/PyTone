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
