import librosa
import numpy as np
import config

def stereo_to_mono(stereo):
    mono = np.mean(stereo, axis=0)
    mono = mono / np.max(np.abs(mono))

    return mono