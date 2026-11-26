import numpy as np
import pandas as pd
import torch


def to_tensor(x: np.ndarray) -> torch.Tensor:
    return torch.tensor(x, dtype=torch.float)

def normalise_volume(x: np.ndarray) -> np.ndarray:
    return x / np.max(np.abs(x))