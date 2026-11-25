from typing import NamedTuple, Callable, overload

import librosa
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
import torch.nn.functional as F
from librosa.feature import rms, spectral_centroid, zero_crossing_rate

default_sample_rate = 22050

def to_tensor(x: np.ndarray) -> torch.Tensor:
    return torch.tensor(x, dtype=torch.float)

class SharedCollection(NamedTuple):
    model: nn.Module
    loss: nn.modules.loss._Loss
    scaler: StandardScaler


class NaiveModel(nn.Module):
    def __init__(self, input_n: int = 3, h1_n: int = 70, h2_n: int = 50, h3_n=20):
        super(NaiveModel, self).__init__()
        self.fc1 = nn.Linear(input_n, h1_n)
        self.fc2 = nn.Linear(h1_n, h2_n)
        self.fc3 = nn.Linear(h2_n, h3_n)
        self.fc4 = nn.Linear(h3_n, 4)

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)

        x = self.fc2(x)
        x = F.relu(x)

        x = self.fc3(x)
        x = F.relu(x)

        x = self.fc4(x)

        return x

@overload
def calculate_classical_features(row: pd.Series) -> pd.Series: ...
@overload
def calculate_classical_features(row: np.ndarray, sample_rate: int) -> pd.Series: ...

def calculate_classical_features(row: pd.Series | np.ndarray | None = None, sample_rate: None | int = None) -> pd.Series:

    expected_len = 5 * default_sample_rate

    if isinstance(row, pd.Series):
        x, sr = librosa.load(row.processed_file)
    elif isinstance(row, np.ndarray):
        assert sample_rate == default_sample_rate
        x = row
        sr = sample_rate
    else:
        raise TypeError(f"Row should be Series or ndarray, got {type(row)}")

    assert sr is not None

    x = x[:min(len(x), expected_len)]
    if expected_len - len(x) > 0:
        x = np.pad(x, (0, expected_len - len(x)))
    S = np.abs(librosa.stft(x))

    r = rms(S=S)[0]
    sc = spectral_centroid(y=x, sr=sr)[0]
    zcr = zero_crossing_rate(x)[0]

    if isinstance(row, pd.Series):
        new_row = row
    else:
        new_row = pd.Series()

    new_row["root_mean_square_mean"] = np.mean(r)
    new_row["root_mean_square_variance"] = np.var(r)
    new_row["spectral_centroid_mean"] = np.mean(sc)
    new_row["spectral_centroid_variance"] = np.var(sc)
    new_row["zero_crossing_rate_mean"] = np.mean(zcr)
    new_row["zero_crossing_rate_variance"] = np.var(zcr)

    return new_row


def flatten(x: pd.DataFrame) -> np.ndarray:
    x = x.apply(lambda row: row.to_numpy(), axis=1)
    # pyrefly: ignore[no-matching-overload]
    return np.vstack(x.to_numpy()).astype(np.float32)
