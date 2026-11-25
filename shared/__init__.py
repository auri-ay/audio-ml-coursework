from typing import NamedTuple, TypedDict

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
from torch import nn as nn

DEFAULT_SAMPLE_RATE = 22050


def to_tensor(x: np.ndarray) -> torch.Tensor:
    return torch.tensor(x, dtype=torch.float)


class SharedCollection(NamedTuple):
    model: nn.Module
    loss: nn.modules.loss._Loss
    scaler: StandardScaler


def flatten(x: pd.DataFrame) -> np.ndarray:
    x = x.apply(lambda row: row.to_numpy(), axis=1)
    # pyrefly: ignore[no-matching-overload]
    return np.vstack(x.to_numpy()).astype(np.float32)


class AmpSetting(TypedDict):
    gain: float
    low: float
    mid: float
    treble: float
