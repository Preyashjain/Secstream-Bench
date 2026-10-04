# Decisions

## Phase 0

- **Decision:** Keep the existing root `secstream/` thin slice while introducing the
  required `src/secstream/` namespace.
  **Alternatives:** Move the working slice immediately or rewrite it during the skeleton.
  **Reason:** Phase 0 establishes packaging and tooling; moving behavior would enlarge
  the change before a phase-specific test requires it.

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