PY ?= python3
PARTITIONS ?= 8
WORKERS ?= 4
RATE ?= 2000
N ?= 20000
COMPOSE ?= docker compose

setup:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e '.[dev]'
install: setup

shell:
	$(COMPOSE) run --rm dev bash

lint:
	$(PY) -m ruff check .

up:
	$(COMPOSE) up -d redpanda
down:
	$(COMPOSE) down
train:            ## synthetic data; for real data: make train SOURCE=/path/to/CICIDS2017_csvs
	$(PY) -m secstream.train --source $(or $(SOURCE),synthetic)
topics:
	$(PY) -m secstream.setup_topics --partitions $(PARTITIONS) --reset
consume:          ## one worker; run in N terminals, or use `make run-workers`
	$(PY) -m secstream.consumer
run-workers:
	@for i in $$(seq 1 $(WORKERS)); do $(PY) -m secstream.consumer --max-idle-s 15 & done; wait
produce:
	$(PY) -m secstream.producer --rate $(RATE) --limit $(N)
collect:
	$(PY) -m secstream.collector --expect $(N) --csv results/runs.csv --tag workers=$(WORKERS) --tag rate=$(RATE) --tag partitions=$(PARTITIONS)
test:
	$(PY) -m pytest -q

verify: lint test smoke
	@printf 'PASS: lint, unit tests, and smoke checks\n'

smoke: test

bench-smoke:
	@printf 'Phase 0: benchmark smoke is not yet measured\n'

fl-smoke:
	@printf 'Phase 0: federated smoke is not yet measured\n'

bench:
	@printf 'Phase 2 benchmark is not yet implemented\n'

fl:
	@printf 'Phase 4 federated sweep is not yet implemented\n'

c-build:
	@printf 'Phase 3 C ingest is not yet implemented\n'

fuzz:
	@printf 'Phase 3 fuzzing is not yet implemented\n'

broker-check:
	$(PY) scripts/broker_check.py
