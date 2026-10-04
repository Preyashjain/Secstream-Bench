"""Read verdicts, report throughput / latency / detection quality, optionally append to a CSV."""
import argparse
import csv
import json
import time
import uuid
from pathlib import Path

import numpy as np
from confluent_kafka import Consumer

from . import config


def summarize(rows: list[dict]) -> dict:
    lat = np.array([(r["ts_out_ns"] - r["ts_in_ns"]) / 1e6 for r in rows])
    t_start = min(r["ts_in_ns"] for r in rows)
    t_end = max(r["ts_out_ns"] for r in rows)
    y = np.array([r["label"] for r in rows])
    p = np.array([r["pred"] for r in rows])
    tp = int(((p == 1) & (y == 1)).sum())
    return {
        "events": len(rows),
        "throughput_eps": round(len(rows) / ((t_end - t_start) / 1e9), 1),
        "lat_p50_ms": round(float(np.percentile(lat, 50)), 1),
        "lat_p95_ms": round(float(np.percentile(lat, 95)), 1),
        "lat_p99_ms": round(float(np.percentile(lat, 99)), 1),
        "precision": round(tp / max(int((p == 1).sum()), 1), 4),
        "recall": round(tp / max(int((y == 1).sum()), 1), 4),
        "workers_seen": len({r["worker"] for r in rows}),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect", type=int, required=True, help="stop after this many verdicts")
    ap.add_argument("--timeout-s", type=float, default=120)
    ap.add_argument("--csv", default=None)
    ap.add_argument("--tag", action="append", default=[], help="key=value, repeatable")
    a = ap.parse_args(argv)

    c = Consumer({"bootstrap.servers": config.BOOTSTRAP, "group.id": f"collector-{uuid.uuid4().hex[:8]}",
                  "auto.offset.reset": "earliest"})
    c.subscribe([config.TOPIC_VERDICTS])
    rows, deadline = {}, time.time() + a.timeout_s
    while len(rows) < a.expect and time.time() < deadline:
        for m in c.consume(num_messages=500, timeout=0.5):
            if m.error() is None:
                v = json.loads(m.value())
                rows[v["id"]] = v          # dedupe on id
    c.close()
    if not rows:
        raise SystemExit("no verdicts received -- are consumers running?")

    res = summarize(list(rows.values()))
    res.update(dict(t.split("=", 1) for t in a.tag))
    if len(rows) < a.expect:
        print(f"WARNING: only {len(rows)}/{a.expect} verdicts before timeout")
    print(json.dumps(res, indent=2))
    if a.csv:
        path = Path(a.csv)
        path.parent.mkdir(parents=True, exist_ok=True)
        new = not path.exists()
        with path.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(res))
            if new:
                w.writeheader()
            w.writerow(res)


if __name__ == "__main__":
    main()
