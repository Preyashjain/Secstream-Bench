"""Train the detector and write the HELD-OUT split that the producer will replay.
Never replay training rows through the stream -- it would inflate every metric."""
import argparse
from pathlib import Path

import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import train_test_split

from .. import config
from ..data.loader import load


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="synthetic", help="'synthetic' or path to CICIDS2017 CSV(s)")
    ap.add_argument("--test-size", type=float, default=0.3)
    ap.add_argument("--model-out", default=config.MODEL_PATH)
    ap.add_argument("--stream-out", default=config.STREAM_PATH)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)

    X, y = load(a.source)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=a.test_size, stratify=y, random_state=a.seed)
    clf = HistGradientBoostingClassifier(max_iter=200, class_weight="balanced", random_state=a.seed)
    clf.fit(Xtr, ytr)

    s = clf.predict_proba(Xte)[:, 1]
    p, r, f1, _ = precision_recall_fscore_support(yte, s >= 0.5, average="binary", zero_division=0)
    print(f"train={len(Xtr)} test={len(Xte)} attack_frac={y.mean():.3f}")
    print(f"AUC={roc_auc_score(yte, s):.4f} precision={p:.4f} recall={r:.4f} f1={f1:.4f}")

    Path(a.model_out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": clf, "features": list(X.columns), "threshold": 0.5}, a.model_out)
    out = Xte.copy()
    out["label"] = yte.values
    Path(a.stream_out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.stream_out, index=False)
    print(f"wrote {a.model_out} and {a.stream_out}")


if __name__ == "__main__":
    main()
