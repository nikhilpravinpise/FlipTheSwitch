# Laptop load plan

Decided Thu 5 Nov 2026, 14:35 IST. Goal: keep both laptops responsive while the full product runs, without a migration that would cost testing time.

## Measured baseline (Nikhil's laptop, 14:30 IST)

AMD Ryzen 7 260 (8 cores, 16 threads), 23.3 GB RAM, 7.8 GB free with Docker/WSL (1.6 GB), Switch Console (0.9 GB), Switch PostgreSQL (0.5 GB), Wispr Flow (1.3 GB), Chrome (1.0 GB), Codex and Claude Code running.

## Decisions

| Decision | Why | How |
| --- | --- | --- |
| Stay local; remote host is a documented fallback only | Every free remote option needs re-onboarding and retesting (1.5-3 h for AWS, 8-16 h+ for Modal); local fits in RAM. See `remote-host.md`, `modal-hosting.md` | Move to AWS Free plan EC2 only if the Windows agent smoke test fails or measured RAM headroom drops below 20% |
| Cap the WSL2 VM that hosts Docker/Mattermost | WSL2 defaults to 50% of RAM (about 11.6 GB here) | `%USERPROFILE%\.wslconfig`: `memory=5GB`, `processors=4`, `swap=2GB`, `autoMemoryReclaim=gradual` ([WSL config docs](https://learn.microsoft.com/windows/wsl/wsl-config)); applied at the next WSL restart |
| Baseline room runs only the agents that do real work | Two agents that only say "unavailable" cost two Claude sessions and weaken the demo | Booking baseline: `@labops` and `@pi-desk`. `@scout` and `@analyst` join only in P5 when their tools are built and gated |
| Agent sessions start on demand and are stopped after test batches | Each Claude Code session is a separate process tree | Switch Console starts sessions only when addressed; harness resets or interrupts sessions after each batch (`!reset`, `!interrupt`) |
| At most two concurrent Codex build runs plus one research run | Builds run tests locally (race tests spawn processes) | Orchestrator policy |
| Heavy test suites run serially | I-01 and I-25 spawn worker processes | Integration tests are marked `race` and run without xdist |
| No sleep on AC power | A sleeping laptop ends agent sessions | `powercfg /change standby-timeout-ac 0` and `hibernate-timeout-ac 0` applied |
| Darshan's laptop stays light | He needs only a browser, Tailscale and Wispr Flow | No Docker, Console or agents on his machine; his work is QA, accessibility, video and blog |

## Capacity check (S6)

Before filming, measure peak RAM and CPU with both rooms' sessions active and after three takes; require at least 20% RAM headroom. Record in `docs/build/adr/000-spikes.md`.
