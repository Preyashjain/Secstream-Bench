"""Kafka-free tests: data -> train -> bundle -> scoring -> metrics."""
import json

import pandas as pd

from secstream.detector import train
from secstream.detector.model import load_bundle, score_batch
from secstream.stream.collector import summarize


def test_train_score_roundtrip(tmp_path):
    m, s = tmp_path / "m.joblib", tmp_path / "s.csv"
    train.main(["--source", "synthetic", "--model-out", str(m), "--stream-out", str(s)])
    bundle = load_bundle(str(m))
    df = pd.read_csv(s)
    df.pop("label")
    assert list(df.columns) == bundle["features"]
    recs = json.loads(json.dumps(df.head(200).to_dict("records")))   # same JSON round-trip as the wire
    scores = score_batch(bundle, recs)
    assert len(scores) == 200 and ((scores >= 0) & (scores <= 1)).all()


def test_summarize():
    rows = [{"ts_in_ns": 0, "ts_out_ns": 10_000_000, "label": 1, "pred": 1, "worker": 1},
            {"ts_in_ns": 5_000_000, "ts_out_ns": 25_000_000, "label": 0, "pred": 1, "worker": 2}]
    r = summarize(rows)
    assert r["events"] == 2 and r["workers_seen"] == 2
    assert r["recall"] == 1.0 and r["precision"] == 0.5
