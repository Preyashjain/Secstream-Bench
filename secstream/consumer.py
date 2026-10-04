"""Detector worker. Run several processes with the same group id: Kafka splits the
partitions between them. That's the parallelism knob (workers <= partitions)."""
import argparse
import json
import os
import time

from confluent_kafka import Consumer, Producer

from . import config
from .model import load_bundle, score_batch


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=config.MODEL_PATH)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--max-idle-s", type=float, default=0, help="exit after this long with no messages (0 = run forever)")
    a = ap.parse_args(argv)

    bundle = load_bundle(a.model)
    thr = bundle.get("threshold", 0.5)
    c = Consumer({"bootstrap.servers": config.BOOTSTRAP, "group.id": config.GROUP_ID,
                  "auto.offset.reset": "earliest", "enable.auto.commit": True})
    c.subscribe([config.TOPIC_RAW])
    out = Producer({"bootstrap.servers": config.BOOTSTRAP, "linger.ms": 5})
    pid, done, last = os.getpid(), 0, time.time()
    try:
        while True:
            msgs = c.consume(num_messages=a.batch, timeout=0.5)
            good = [json.loads(m.value()) for m in msgs if m.error() is None]
            if not good:
                if a.max_idle_s and time.time() - last > a.max_idle_s:
                    break
                continue
            last = time.time()
            scores = score_batch(bundle, [g["features"] for g in good])
            now = time.time_ns()
            for g, s in zip(good, scores):
                v = {"id": g["id"], "ts_in_ns": g["ts_ns"], "ts_out_ns": now, "label": g["label"],
                     "score": float(s), "pred": int(s >= thr), "worker": pid}
                out.produce(config.TOPIC_VERDICTS, key=str(g["id"]), value=json.dumps(v))
            out.poll(0)
            done += len(good)
    except KeyboardInterrupt:
        pass
    finally:
        out.flush()
        c.close()
        print(f"worker {pid}: processed {done} events")


if __name__ == "__main__":
    main()
