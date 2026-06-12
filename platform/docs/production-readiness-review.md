# Production Readiness Review — Notes API

**Reviewer:** Platform / DevOps
**Date:** 2026-06-12
**Application:** Notes API (FastAPI + Postgres)
**Verdict:** Not yet production-ready — blockers must be closed before deploy.

A Production Readiness Review (PRR) is the checkpoint where the team that will
operate an application audits it against production standards before agreeing to
run it. It is the contract between the developer who built it and the DevOps
engineer who will run it: it states what is ready, what is missing, and who owns
each fix.

## What the developer delivered well

- A working REST API with full CRUD on notes.
- A passing unit test.
- A clear README with local run instructions.
- A reproducible local database via Docker Compose.

## Findings

| # | Area | Current state | Status | Owner | Action before production |
|---|------|---------------|--------|-------|--------------------------|
| 1 | Configuration & secrets | DB URL and password hardcoded in `src/main.py` | Gap (blocker) | DevOps | Move config to env vars; store secrets in AWS Secrets Manager / SSM |
| 2 | Health checks | No `/health` endpoint | Gap | Dev + DevOps | Add `/health` that verifies DB connectivity; wire to the load balancer |
| 3 | Packaging | No Dockerfile; runs via `uvicorn` on the dev's machine | Gap (blocker) | DevOps | Add Dockerfile, build image, push to ECR |
| 4 | Dependencies | `requirements.txt` unpinned; test tools mixed with runtime deps | Gap | DevOps | Pin versions; split prod vs dev dependencies |
| 5 | Database | Tables created at import via `create_all`; local Postgres only | Gap | DevOps | Use managed Postgres (RDS); review schema-management approach |
| 6 | Logging & monitoring | Default stdout logs; no metrics | Partial | DevOps | Ship stdout to CloudWatch (native on Fargate, no extra stack) |
| 7 | Security | Secrets in source; no `.gitignore`; no image or code scanning | Gap | DevOps | Add `.gitignore`; remove secrets; Trivy + Semgrep scans in CI |
| 8 | Deployment & CI/CD | None — manual local run | Gap (blocker) | DevOps | GitHub Actions: test, scan, build, push, deploy to ECS |
| 9 | Scaling & resilience | Single local process; no restart or load balancing | Gap | DevOps | ECS service behind an ALB with health-based task replacement |
| 10 | Tests | One unit test, requires a live database | Partial | Dev | Keep and run in CI; isolate from the live DB later |

## Conditions for production sign-off

- **Blockers (must fix):** items 1, 3, 5, 8 — plus item 2, which makes 8 and 9 work.
- **Should fix:** items 4, 6, 7.
- **Accepted for this release:** authentication is out of scope; test isolation is deferred.

Each finding above becomes a task in Act 3, where the DevOps engineer closes the
gaps and brings the application to production on AWS.