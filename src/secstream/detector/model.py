import joblib
import numpy as np
import pandas as pd


def load_bundle(path: str) -> dict:
    return joblib.load(path)


def to_matrix(bundle: dict, records: list[dict]) -> pd.DataFrame:
    feats = bundle["features"]
    return pd.DataFrame(np.asarray([[r[f] for f in feats] for r in records], dtype=np.float32), columns=feats)


def score_batch(bundle: dict, records: list[dict]) -> np.ndarray:
    """Attack probability for each record (records = {feature_name: value})."""
    return bundle["model"].predict_proba(to_matrix(bundle, records))[:, 1]
