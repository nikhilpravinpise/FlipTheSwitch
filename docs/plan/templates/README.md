# Templates and seed data (drafts)

| File | Use | Verified by |
| --- | --- | --- |
| `labquorum-core.template.yaml` | Solo core: four agents in one room, three HQ roles | Spike S4 |
| `labquorum-lab.template.yaml` | Run once per lab in Switch Console: the five agents (instructions, addressing, directories, `auto_mode: false`), the HQ room, handbook, roles, aliases, kickoff | Optional; separately fund import |
| `labquorum-project.template.yaml` | Run once per project, per demo take and per E2E run: one project room that reuses the lab's agents through `type: agent` params | Optional; separately fund import |
| `seed-data.md` | Demo seed sketch: people, instruments, inventory, protocol, papers, plate CSVs, request ids | Golden tests U-D05, I-09, I-15 |

These started as the Opus planner's drafts ([`../../inputs/opus-5.5/`](../../inputs/opus-5.5/)) and were aligned with the merged plan: bench notes use `bench_log_draft` and `bench_log_confirm` with read-back, documents use `render_document`, and the plate layout uses the inner region with the C5 transcription error. Per-profile settings, `ask` rules and gate-hook installation are requirements in [03-architecture.md](../03-architecture.md#32-the-two-layer-approval-model), not ready-to-install files: implement them and certify their effective behavior before enabling commits. Field names (`aliases`, `roles`, `docs`, `auto_mode`, placeholders inside `directory`) are checked against the pinned Console release in spike S4 before anything depends on them.

S4 must assert the core template creates 4 agents, 1 room, 3 roles, 0 groups and 0 links; inspect kickoff card and server log, and verify `!roles` shows scout/librarian, labops/bench-manager and pi-desk/approver. Apply the bounded fresh-room fallback in [08](../08-build-schedule.md) on kickoff failure. If the optional two-room template configuration is exercised, assert 5 agents, 1 HQ room, 1 project room, 3 HQ roles, 0 groups and 0 links. The project template creates `rao-proj-egcg` and unique take rooms; test imports on the pinned release. Single-room templates use top-level kickoff; grouped templates require room-local kickoff. Per-request consent and actual readable status must be tested after import.

S4 enrollment: create distinct initially unclaimed PI and Maya accounts, enroll both and verify posting. In S1 record the unclaimed helper and owner probes before claiming either; then claim, re-enroll and verify both can post before S3. The YAML lists only the creator. Import and settings behavior remain UNVERIFIED until the pinned runtime passes.

The funded baseline is booking only; the two roadmap templates advertise tools that require separate implementation and tests. Do not install them as the baseline. S4 is the pre-S1 fixture: create the private room, enroll unclaimed local test identities before S1; perform the unclaimed probes, then claim and re-enroll both before S3. These local test users are not event registrations.
