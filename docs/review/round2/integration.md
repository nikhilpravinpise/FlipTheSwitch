# Integration log

## Applied changes

## Checks

- Verified the Switch self-host source describes a separately deployed server; host-remotely describes onboarding a host. The architecture and schedule already point to self-host.md and keep fallback unavailable pending preflight (3 primary-source opens attempted).
- Rewrote the master plan around the booking-only forecast, conditional gate and novelty, evidence limits, current counts and scenario scores. Corrected product scope and the AR-0042 seeded end time; labeled the assay demo as optional.
- Aligned the OD unit rule in product and the roadmap template, and made the server fallback edge case conditional on its recorded preflight. Updated the docs index to include both review rounds.
- Initial `python %TEMP%\lq-doc-check.py`: 38 Markdown files, 0 broken relative links or anchors, 187 unique test definitions with 0 duplicates and 0 undefined explicit test IDs, 120 unique edge cases, 0 files containing U+2014.
- Checked the four editor logs against their target sections: decision payload and failure handling, structured evidence, title and protocol tests, enrollment, optional packet reproduction, booking scenario, fallback preflight, Wispr and submission timing are reflected in their target files. S0 now calls the main-branch guide a guide, not a pinned artifact.
- Source check: Switch self-host.md describes deploying a server independently; host-remotely.md describes Console onboarding through SSH. Both candidate index.md fetches failed with cache misses; the correct self-host page itself was available. Five web opens attempted, within the search budget. Installed images, endpoints and runtime behavior remain unverified.
- Historical reviews and change logs preserve their original counts (including 173 and 186) as snapshots, not current catalogue claims. The raw background inputs are likewise historical and outside the editable plan scope; their old numbers are not current assertions.
- The decision record was left untouched for the separate editor. The first and final checks report repository content as found; they do not prove real application behavior or execution of planned tests.
- `python %TEMP%\lq-extra-check.py`: 0 undefined edge-shaped identifiers in plan Markdown/YAML (excluding market labels); 2,290 scheduled minutes = 38 h 10 min; all 3 template YAML files parsed.
- `rg -n "\x{2014}" docs`: no matches. `python %TEMP%\lq-doc-check.py`: 38 Markdown files; 0 broken relative links or anchors; 187 unique definitions, 0 duplicates, 0 undefined explicit test IDs; 120 distinct edge cases (22/12/16/14/10/12/8/6/12/8); 0 files with U+2014.

