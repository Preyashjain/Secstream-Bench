# secstream-bench specification

## Research question

Measure the separate runtime cost of ingest hardening and the separate model-quality
and training-time cost of privacy noise and robust aggregation in a streaming ML
intrusion-detection pipeline. The performance model predicts pipeline latency from
configuration. Costs remain in their native units and are never collapsed into one score.

## Phases

0. Skeleton: pinned project tooling, Docker Compose Redpanda, CI, and documentation.
1. M1 thin slice: replay, consumer-group detector, trained models, and raw run results.
2. M1 benchmark: factorial sweeps, saturation analysis, and held-out performance model.
3. M3 ingest: C parser, hardened build variants, differential tests, and bounded fuzzing.
4. M2 federated security: poisoning, defenses, privacy knob, and reproducible sweeps.
5. Combine: deploy M2 models in M1 and generate the cost-of-security write-up.

## Stack and data rules

Python 3.11+, pinned open-source dependencies, a pinned Redpanda image, and one
development image are required. CICIDS2017 is manually supplied by the owner under
`data/raw/`; synthetic data is used for tests and smoke runs. No credentials, cloud
services, or committed datasets are allowed.

## Testing contract

`make test` is fast and broker-free. Integration tests require Redpanda and slow tests
are never run by the agent. `make verify` runs lint, unit tests, and the current phase's
smoke target. Every completed phase updates `docs/DECISIONS.md` and
`docs/WALKTHROUGH.md`.

## Phase 0 acceptance

From a fresh clone, `make setup && make verify` passes, Redpanda starts healthy, and
`make broker-check` produces and consumes 1,000 messages. Later-phase targets may report
that they are not yet implemented until their phase begins.