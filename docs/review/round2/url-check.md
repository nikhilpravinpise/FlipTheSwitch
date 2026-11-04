# URL check: 117 unique URLs, 9 not 2xx/3xx

| Status | URL | Files |
| --- | --- | --- |
| 403 | https://doi.org/10.1145/2948992.2948998 | 01-problem-market-usp.md, 05-wispr-flow.md |
| 403 | https://eta.lbl.gov/news/berkeley-lab-leads-effort-build-ai-assistant-energy-materials-discovery | 01-problem-market-usp.md |
| 404 | https://github.com/sandbox-quantum/switch/blob/main/docs/official/deploy/self-hosting.md | 03-architecture.md |
| 403 | https://help.consensus.app/en/articles/10087865-subscription-plans | 01-problem-market-usp.md |
| 403 | https://newsroom.wiley.com/press-releases/press-release-details/2025/AI-Adoption-Jumps-to-84-Among-Researchers-as-Expectations-Undergo-Significant-Reality-Check/default.aspx | 01-problem-market-usp.md |
| 403 | https://phys.org/news/2019-08-results-impact-volumes-workload.html | 01-problem-market-usp.md |
| 403 | https://scispace.com/pricing | 01-problem-market-usp.md |
| 403 | https://scite.ai/pricing | 01-problem-market-usp.md |
| 403 | https://www.labvantage.com/press-release/labvantage-solutions-introduces-labvantage-cortex-advancing-its-lims-platform-for-ai-driven-laboratory-operations/ | 01-problem-market-usp.md |

## Notes (orchestrator)

- The eight 403 responses come from sites that block automated clients (Cloudflare or similar); the round-1 market reviewer fetched those pages successfully in a browser context. Keep them unless a reviewer finds the content changed.
- The 404 is real: `docs/official/deploy/self-hosting.md` does not exist on Switch `main`. Candidates on `main`: `docs/official/deploy/index.md` and `docs/official/deploy/host-remotely.md`. The editor must read both and link the one that actually documents self-hosting a server.
