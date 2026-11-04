# Templates and seed data (drafts)

| File | Use | Verified by |
| --- | --- | --- |
| `labquorum-lab.template.yaml` | Run once per lab in Switch Console: the five agents (instructions, addressing, directories, `auto_mode: false`), the HQ room, handbook, roles, aliases, kickoff | Spike S4 |
| `labquorum-project.template.yaml` | Run once per project, per demo take and per E2E run: one project room that reuses the lab's agents through `type: agent` params | Spike S4 |
| `seed-data.md` | Demo seed sketch: people, instruments, inventory, protocol, papers, plate CSVs, request ids | Golden tests U-D05, I-09, I-15 |

These started as the Opus planner's drafts ([`../../inputs/opus-5.5/`](../../inputs/opus-5.5/)) and were aligned with the merged plan: bench notes use `bench_log_draft` and `bench_log_confirm` with read-back, documents use `render_document`, and the plate layout uses the inner region with the C5 transcription error. The agent folder settings for `@pi-desk`, with the `ask` rules and the gate hook, are in [03-architecture.md](../03-architecture.md#example-agentspi-deskclaudesettingsjson-draft). Field names (`aliases`, `roles`, `docs`, `auto_mode`, placeholders inside `directory`) are checked against the pinned Console release in spike S4 before anything depends on them.
