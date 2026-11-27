import librosa
import numpy as np
import matplotlib.pyplot as plt

melfb = librosa.filters.mel(sr=44100, n_fft=2048, n_mels=26, fmin=0, fmax=22050)

def calc_stft(x, sr=44100, window_ms = 25, shift_ms = 10):
    window_length = int(sr*window_ms/1000)
    shift_length = int(sr* shift_ms/1000)

    d = librosa.stft(
        x,
        win_length=window_length,
        hop_length=shift_length,
        window="hann"
    )
    

    return np.abs(d)

def calc_mel(x, sr=44100, window_ms=25, shift_ms=10):
    magnitude = calc_stft(x, sr, window_ms, shift_ms)
    power = magnitude**2

    return melfb @ power

def calc_mfcc(x, sr=44100, window_ms = 25, shift_ms = 10, width=99, height=26):
    mfcc = librosa.feature.mfcc(
        y=x,
        sr=sr,
        S=None,
        n_mfcc=width,
        n_mels=height,
        lifter = 0,
        n_fft = 2048,
        win_length = window_ms,
        hop_length = shift_ms,
        window="hann",
        )
    return mfcc

