"""Replay the held-out split as a live stream at a target event rate."""
import argparse
import json
import time

import pandas as pd
from confluent_kafka import Producer

from . import config


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate", type=float, default=2000, help="target events/second")
    ap.add_argument("--limit", type=int, default=20000, help="number of events to send")
    ap.add_argument("--stream", default=config.STREAM_PATH)
    a = ap.parse_args(argv)

    df = pd.read_csv(a.stream, dtype="float32", engine="c")
    labels = df.pop("label").astype(int).to_numpy()
    feats = list(df.columns)
    X = df.to_numpy()
    n = min(a.limit, len(X))

    p = Producer({"bootstrap.servers": config.BOOTSTRAP, "linger.ms": 5, "compression.type": "lz4"})
    tick = 0.01
    per_tick = max(1, int(a.rate * tick))
    t0 = time.perf_counter()
    sent = ticks = 0
    while sent < n:
        for _ in range(min(per_tick, n - sent)):
            msg = {"id": sent, "ts_ns": time.time_ns(), "label": int(labels[sent]),
                   "features": dict(zip(feats, X[sent].tolist()))}
            while True:
                try:
                    p.produce(config.TOPIC_RAW, key=str(sent), value=json.dumps(msg))
                    break
                except BufferError:
                    p.poll(0.1)
            sent += 1
        p.poll(0)
        ticks += 1
        lag = t0 + ticks * tick - time.perf_counter()
        if lag > 0:
            time.sleep(lag)
    p.flush()
    dt = time.perf_counter() - t0
    print(f"sent {sent} events in {dt:.2f}s ({sent / dt:.0f} ev/s achieved, target {a.rate:.0f})")


if __name__ == "__main__":
    main()
