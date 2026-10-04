import os

BOOTSTRAP = os.getenv("SECSTREAM_BOOTSTRAP", "localhost:19092")
TOPIC_RAW = os.getenv("SECSTREAM_TOPIC_RAW", "flows.raw")
TOPIC_VERDICTS = os.getenv("SECSTREAM_TOPIC_VERDICTS", "flows.verdicts")
GROUP_ID = os.getenv("SECSTREAM_GROUP", "detector")
MODEL_PATH = os.getenv("SECSTREAM_MODEL", "artifacts/model.joblib")
STREAM_PATH = os.getenv("SECSTREAM_STREAM", "artifacts/stream_test.csv")
