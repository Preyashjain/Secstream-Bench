# Decisions

## Phase 0

- **Decision:** Move the existing root modules into the required `src/secstream/`
  subpackages without rewriting their behavior.
  **Alternatives:** Keep two importable packages or rewrite the thin slice during cleanup.
  **Reason:** Two packages made test imports depend on the working directory; one source
  package makes the import path deterministic. No competing implementation existed in
  `src/`, so no same-purpose file had to be discarded.

- **Decision:** Store the moved `data.py` implementation as `src/secstream/data/loader.py`.
  **Alternatives:** Flatten it beside the package or replace the existing data package.
  **Reason:** `data/` is part of the required layout and already had its package marker;
  the loader name avoids a module/package collision.

- **Decision:** Keep runtime and development dependencies in the pinned
  `requirements.txt`; `make setup` only imports them and does not install into a
  throwaway container.
  **Alternatives:** Install the development extra during every setup invocation.
  **Reason:** The Docker image is self-contained and setup remains a deterministic
  environment check.

- **Decision:** Use a pinned Redpanda `v24.2.18` image and a Python 3.11 slim base.
  **Alternatives:** Floating `latest` tags or a host-only setup.
  **Reason:** Reproducible local Linux runs are part of the acceptance contract.

- **Decision:** Make later-phase Make targets explicit no-op notices until implemented.
  **Alternatives:** Omit targets or make them silently succeed.
  **Reason:** The command surface is stable from Phase 0, and an explicit message avoids
  presenting unmeasured work as completed.

- **Verification note:** The current Redpanda quickstart URL returned HTTP 404 during
  this session, so the image tag and healthcheck have not been independently reverified
  against that page. The pinned values remain an explicit Phase 0 assumption to verify
  inside the dev environment before claiming broker acceptance.

- **Verification deviation:** Container acceptance checks could not run in this session
  because the host has neither `docker` nor `docker compose`. No Docker-based result is
  claimed; the owner must run the documented compose commands on a Docker-enabled host.

- **Artifact inventory:** `artifacts/.gitkeep` and `results/.gitkeep` are the only files
  in those directories. They are placeholders with no producing script or test (`unknown`);
  no artifact or result files were deleted.