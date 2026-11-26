from typing import NamedTuple, TypedDict

from sklearn.preprocessing import StandardScaler
from torch import nn as nn

class SharedCollection(NamedTuple):
    model: nn.Module
    loss: nn.modules.loss._Loss
    scaler: StandardScaler

class AmpSetting(TypedDict):
    gain: float
    low: float
    mid: float
    treble: float
