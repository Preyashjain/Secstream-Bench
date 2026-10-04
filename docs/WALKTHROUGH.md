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
- `src/secstream/` is the only importable package and contains the moved stream,
  detector, data, and configuration modules.
- `.github/workflows/ci.yml` runs only lint and broker-free unit tests on Python 3.11.
- `.gitignore` prevents raw data, generated results, caches, and build artifacts from
  entering the repository.

### Reused and moved existing code

- The former root `secstream/` replay, consumer, model, training, topic setup, collector,
  data, and configuration implementations were moved into `src/secstream/` unchanged
  except for package-relative imports.
- `tests/test_pipeline_offline.py` remains the broker-free regression test for the
  existing train, score, and metric path.
- `README.md`, `artifacts/`, and `results/` remain in place; the two tracked `.gitkeep`
  files were not removed.

### Verification status

Python syntax and Makefile expansion were checked locally. The required container
commands could not run because Docker was not installed on the host, so broker health
and the 1,000-message check remain unverified.