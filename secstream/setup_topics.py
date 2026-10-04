"""Create topics. #partitions is the ceiling on useful consumer parallelism."""
import argparse
import time

from confluent_kafka.admin import AdminClient, NewTopic

from . import config


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--partitions", type=int, default=8)
    ap.add_argument("--reset", action="store_true", help="delete topics first (clean benchmark run)")
    a = ap.parse_args(argv)

    admin = AdminClient({"bootstrap.servers": config.BOOTSTRAP})
    topics = [config.TOPIC_RAW, config.TOPIC_VERDICTS]

    if a.reset:
        for t, f in admin.delete_topics(topics, operation_timeout=30).items():
            try:
                f.result()
            except Exception as e:  # topic may not exist yet
                print(f"delete {t}: {e}")
        time.sleep(3)

    new = [NewTopic(t, num_partitions=a.partitions, replication_factor=1) for t in topics]
    pending = {}
    for _ in range(10):
        pending = {}
        for t, f in admin.create_topics(new).items():
            try:
                f.result()
                print(f"created {t} ({a.partitions} partitions)")
            except Exception as e:
                if "ALREADY_EXISTS" in str(e) and not a.reset:
                    print(f"{t} already exists")
                else:
                    pending[t] = e
        if not pending:
            return
        new = [n for n in new if n.topic in pending]
        time.sleep(2)
    raise SystemExit(f"could not create topics: {pending}")


if __name__ == "__main__":
    main()
