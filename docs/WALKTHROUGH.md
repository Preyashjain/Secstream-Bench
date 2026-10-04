# Walkthrough

## Phase 0

- `pyproject.toml` defines the Python 3.11 package, pinned runtime and development
  dependencies, Ruff settings, and pytest markers.
- `requirements.txt` mirrors the pinned dependencies used by the development image.
- `docker/Dockerfile` supplies Python, C build tools, Clang, Make, and Git in one image.
- `docker-compose.yml` runs the pinned single-node Redpanda broker and the development
  container, with a health-gated dependency between them.
- `Makefile` exposes setup, lint, test, verify, broker, and future phase commands.
- `scripts/broker_check.py` creates one topic, sends 1,000 local messages, and verifies
  that all 1,000 can be consumed.
- `src/secstream/` contains the package layout reserved for the phase modules.
- `.github/workflows/ci.yml` runs only lint and broker-free unit tests on Python 3.11.
- `.gitignore` prevents raw data, generated results, caches, and build artifacts from
  entering the repository.

### Reused existing code

- The root `secstream/` package remains the existing replay, consumer, model, training,
  topic setup, and collector implementation for later phases.
- `tests/test_pipeline_offline.py` remains the broker-free regression test for the
  existing train, score, and metric path.
- `README.md`, `artifacts/`, and `results/` remain in place; Phase 0 only adds the
  project scaffolding around them.

### Verification status

Python syntax and Makefile expansion were checked locally. The required container
commands could not run because Docker was not installed on the host, so broker health
and the 1,000-message check remain unverified.