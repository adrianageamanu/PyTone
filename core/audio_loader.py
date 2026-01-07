import librosa
import numpy as np
import config

def stereo_to_mono(stereo):
    mono = np.mean(stereo, axis=0)
    mono = mono / np.max(np.abs(mono))

    return mono

def load_audio(path):
    audio, _ = librosa.load(path, sr=config.SAMPLE_RATE, mono=False)
    
    if audio.ndim == 2:
        audio = stereo_to_mono(audio)
    
    return audio