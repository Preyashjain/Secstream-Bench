"""Dataset loading. Synthetic data lets the whole pipeline run with zero downloads;
CICIDS2017 (MachineLearningCVE CSVs) plugs in via the same interface."""
from pathlib import Path

import numpy as np
import pandas as pd

SYN_FEATURES = [
    "Flow Duration", "Total Fwd Packets", "Total Bwd Packets",
    "Fwd Packet Length Mean", "Bwd Packet Length Mean", "Flow Bytes/s",
    "Flow Packets/s", "Flow IAT Mean", "Fwd IAT Mean", "SYN Flag Count",
    "ACK Flag Count", "Avg Packet Size",
]


def synthetic(n: int = 60_000, attack_frac: float = 0.15, seed: int = 0):
    """Imbalanced, overlapping lognormal 'flows'. NOT a security result -- plumbing only."""
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < attack_frac).astype(int)
    k = len(SYN_FEATURES)
    base = rng.uniform(1.0, 6.0, size=k)
    shift = rng.normal(0.0, 0.6, size=k)          # per-feature attack shift
    sigma = np.where(y[:, None] == 1, 1.25, 1.0)
    X = np.exp(base + y[:, None] * shift + rng.normal(size=(n, k)) * sigma).astype(np.float32)
    return pd.DataFrame(X, columns=SYN_FEATURES), pd.Series(y, name="label")


def load_cicids(path: str):
    """Load CICIDS2017 CSVs (a file or a directory of files). Binary label: BENIGN vs attack."""
    p = Path(path)
    files = sorted(p.glob("*.csv")) if p.is_dir() else [p]
    if not files:
        raise FileNotFoundError(f"no CSV files under {path}")
    df = pd.concat((pd.read_csv(f, low_memory=False) for f in files), ignore_index=True)
    df.columns = df.columns.str.strip()
    y = (df["Label"].astype(str).str.strip().str.upper() != "BENIGN").astype(int)
    X = df.drop(columns=["Label"]).select_dtypes(include=[np.number])
    X = X.replace([np.inf, -np.inf], np.nan)
    keep = X.notna().all(axis=1)
    return X[keep].astype(np.float32).reset_index(drop=True), y[keep].reset_index(drop=True).rename("label")


def load(source: str):
    return synthetic() if source == "synthetic" else load_cicids(source)
