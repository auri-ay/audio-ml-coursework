from typing import Callable, overload

import librosa
import numpy as np
import pandas as pd
from librosa.feature import rms, spectral_centroid, zero_crossing_rate

from shared import DEFAULT_SAMPLE_RATE


def calculate_features(f: Callable[[pd.Series, np.ndarray, int], pd.Series], row: pd.Series | np.ndarray | None = None,
                       sample_rate: None | int = None) -> pd.Series:
    expected_len = 5 * DEFAULT_SAMPLE_RATE

    if isinstance(row, pd.Series):
        x, sr = librosa.load(row.processed_file)
        assert isinstance(sr, int)
    elif isinstance(row, np.ndarray):
        assert sample_rate == DEFAULT_SAMPLE_RATE
        x = row
        sr = sample_rate
    else:
        raise TypeError(f"Row should be Series or ndarray, got {type(row)}")

    assert sr is not None

    x = x[:min(len(x), expected_len)]
    if expected_len - len(x) > 0:
        x = np.pad(x, (0, expected_len - len(x)))

    if isinstance(row, pd.Series):
        new_row = row
    else:
        new_row = pd.Series()

    return f(new_row, x, sr)


@overload
def calculate_classical_features(row: pd.Series) -> pd.Series: ...


@overload
def calculate_classical_features(row: np.ndarray, sample_rate: int) -> pd.Series: ...


def calculate_classical_features(row: pd.Series | np.ndarray | None = None,
                                 sample_rate: None | int = None) -> pd.Series:
    def _inner(new_row, x, sr):
        S = np.abs(librosa.stft(x))

        r = rms(S=S)[0]
        sc = spectral_centroid(y=x, sr=sr)[0]
        zcr = zero_crossing_rate(x)[0]
        new_row["root_mean_square_mean"] = np.mean(r)
        new_row["root_mean_square_variance"] = np.var(r)
        new_row["spectral_centroid_mean"] = np.mean(sc)
        new_row["spectral_centroid_variance"] = np.var(sc)
        new_row["zero_crossing_rate_mean"] = np.mean(zcr)
        new_row["zero_crossing_rate_variance"] = np.var(zcr)

        return new_row

    return calculate_features(_inner, row, sample_rate)


@overload
def calculate_cnn_features(row: pd.Series) -> pd.Series: ...


@overload
def calculate_cnn_features(row: np.ndarray, sample_rate: int) -> pd.Series: ...


def calculate_cnn_features(row: pd.Series | np.ndarray | None = None, sample_rate: None | int = None) -> pd.Series:
    def _inner(new_row, x, sr):
        return new_row

    return calculate_features(_inner, row, sample_rate)
