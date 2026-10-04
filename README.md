# secstream-bench

A benchmarkable streaming intrusion-detection pipeline. Research question for the full project:
**what does security cost a streaming ML pipeline?** (throughput/latency overhead of memory-safety
hardening, privacy mechanisms, and robust aggregation -- plus how robust the detector is.)

This repo is the **thin vertical slice**: replay -> Redpanda -> parallel detector workers -> verdicts -> metrics.

```
producer (rate-controlled replay of held-out data)
   -> Redpanda topic flows.raw (N partitions)
   -> M detector workers (same consumer group; M <= N)
   -> topic flows.verdicts
   -> collector (throughput, p50/p95/p99 latency, precision/recall -> results/runs.csv)
```

## Quickstart (all free, runs on a laptop)

```bash
python -m venv .venv && source .venv/bin/activate
make install
make test                 # offline tests, no Kafka needed
make train                # synthetic data; real data: make train SOURCE=/path/to/CICIDS2017_csvs
make up                   # starts Redpanda in Docker (wait ~10s)
make topics PARTITIONS=8  # recreate topics clean for each run
```

One benchmark run (workers in the background, then produce, then collect):

```bash
make run-workers WORKERS=4 &      # exits itself after 15s idle
sleep 5
make produce RATE=2000 N=20000
make collect WORKERS=4 RATE=2000 PARTITIONS=8
```

Each `collect` appends one row to `results/runs.csv`. Sweep WORKERS x RATE x PARTITIONS and you have your
first parallelism benchmark.

## Things to know (methodology)

- **Parallelism = consumer processes**, capped by partition count. Workers > partitions gives idle workers.
- **Recreate topics between runs** (`make topics`), otherwise old messages and committed offsets contaminate results.
- **The stream replays the held-out split only**, never training rows.
- Producer and workers share one machine, so they compete for CPU. Report that, and keep the producer's
  *achieved* rate (it prints it) rather than assuming the target was hit.
- Latency = verdict time - produce time (same machine clock). It includes batching and Kafka time, by design.
- Synthetic data is for plumbing only. Quote no detection numbers from it.
- Messages are JSON for simplicity; serialization cost is a known overhead worth isolating later.

## Roadmap (one module per research group)

1. **Stream benchmark + performance model**: sweep configs, fit a small latency predictor, test on unseen configs. Try PyFlink for real operator parallelism.
2. **Federated backdoors**: split data over 3-5 simulated sites (Flower), implement poisoning/backdoor attacks, robust aggregation, DP; plot attack success vs clean accuracy.
3. **Fuzzed C ingest stage**: your own C flow-feature parser, fuzzed with AFL++ + ASan/UBSan; measure the hardening cost in the same benchmark.
