# Templates and seed data (drafts)

| File | Use | Verified by |
| --- | --- | --- |
| `labquorum-core.template.yaml` | Solo core: four agents in one room, three HQ roles | Spike S4 |
| `labquorum-lab.template.yaml` | Run once per lab in Switch Console: the five agents (instructions, addressing, directories, `auto_mode: false`), the HQ room, handbook, roles, aliases, kickoff | Optional; separately fund import |
| `labquorum-project.template.yaml` | Run once per project, per demo take and per E2E run: one project room that reuses the lab's agents through `type: agent` params | Spike S4 |
| `seed-data.md` | Demo seed sketch: people, instruments, inventory, protocol, papers, plate CSVs, request ids | Golden tests U-D05, I-09, I-15 |

These started as the Opus planner's drafts ([`../../inputs/opus-5.5/`](../../inputs/opus-5.5/)) and were aligned with the merged plan: bench notes use `bench_log_draft` and `bench_log_confirm` with read-back, documents use `render_document`, and the plate layout uses the inner region with the C5 transcription error. Per-profile settings, `ask` rules and gate-hook installation are requirements in [03-architecture.md](../03-architecture.md#32-the-two-layer-approval-model), not ready-to-install files: implement them and certify their effective behavior before enabling commits. Field names (`aliases`, `roles`, `docs`, `auto_mode`, placeholders inside `directory`) are checked against the pinned Console release in spike S4 before anything depends on them.

S4 must assert the core template creates 4 agents, 1 room, 3 roles, 0 groups and 0 links. If the optional two-room template configuration is exercised, assert 5 agents, 1 HQ room, 1 project room, 3 HQ roles, 0 groups and 0 links. The project template creates `rao-proj-egcg` and unique take rooms; test imports on the pinned release. Single-room templates use top-level kickoff; grouped templates require room-local kickoff. Per-request consent and actual readable status must be tested after import.

S4 enrollment: create distinct PI and Maya accounts, explicitly add Maya to the private core room and verify she can post. Verify identity claiming separately before the negative card tests. The YAML lists only the creator. Import and settings behavior remain UNVERIFIED until the pinned runtime passes.

The funded baseline is booking only; the two roadmap templates advertise tools that require separate implementation and tests. Do not install them as the baseline. Before S1/S3, allocate and create a disposable private room, claim both local test identities, enroll both and prove each can post. S4 must not be the first provisioning step because the earlier identity and wrong-person tests depend on this fixture. These local test users are not event registrations.
