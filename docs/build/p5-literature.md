# P5 literature verification

Build notes for the `p5-lit` literature expansion. This adds public-metadata lookup and deterministic citation identity checks for the `librarian` MCP profile used by `scout`.

## API policy checked 2026-11-05

The client uses a shared SQLite host limiter, a 10-second HTTP timeout, at most three safe-GET attempts, exponential backoff with jitter, and the larger of the backoff delay or `Retry-After`. Each attempt counts against the 50-request budget for its MCP tool call. Five consecutive HTTP 5xx responses open that host's circuit for 60 seconds and return `UNREACHABLE`.

Crossref's current public guidance distinguishes single-record requests from list requests. Its polite pool allows 10 requests per second and three concurrent requests for a single DOI record, and 3 requests per second and three concurrent requests for list requests. The client uses DOI lookups only, sends `mailto` from `CONTACT_EMAIL`, and paces them at 8 requests per second with at most three in flight. Crossref asks for a functioning contact address and warns that repeated use of an invalid address could result in blocking. [Crossref rate-limit update](https://community.crossref.org/t/refining-rest-api-limits-for-improved-stability-and-reliability/16137), [Crossref REST guidance](https://www.crossref.org/blog/announcing-changes-to-rest-api-rate-limits/).

OpenAlex allows basic API queries without a key. Current published per-second limits are 10 requests without a key, 30 with a free key or prepaid use, and 50 for an annual plan. A verified free key increases the daily budget and is required to use cursor paging after the first page. The client supports an optional `OPENALEX_API_KEY` bearer token and conservatively paces requests at 8 per second. It does not use cursor paging. OpenAlex recommends exponential backoff and honors `Retry-After` on rate-limit responses. [OpenAlex authentication and rate limits](https://help.openalex.org/api/authentication/), [OpenAlex error handling](https://help.openalex.org/api/errors/).

The 8 requests-per-second setting is below each applicable published limit. These API policies can change, so recheck the linked official pages before changing the pacing or authentication behavior.

## HTTP, cache, and limits

`src/labquorum/scholarly/http.py` provides Crossref and OpenAlex GET clients. The host limiter stores the next allowed time, active leases, consecutive server failures, and circuit expiry in SQLite under the scholarly cache directory. Processes sharing that cache directory therefore share the same per-host rate and concurrency policy. HTTPX supplies the per-request timeout and transport boundary used by the mocked tests. [HTTPX timeout documentation](https://www.python-httpx.org/advanced/timeouts/), [HTTPX transport documentation](https://www.python-httpx.org/advanced/transports/).

JSON response files are stored in the platform cache directory: `%LOCALAPPDATA%/LabQuorum/cache/scholarly` on Windows, `$XDG_CACHE_HOME/labquorum/scholarly` when configured, otherwise `~/.cache/labquorum/scholarly`. Cache keys are SHA-256 digests. The configured TTLs are 7 days for search results, 30 days for DOI metadata, and 1 day for retraction status. Responses expose a `checked_at` timestamp and an age label such as `fresh` or `cached, 1h old`. A DOI response tagged for both DOI metadata and retraction status is reused only while both tagged entries are within TTL; the daily retraction TTL therefore prompts a fresh combined lookup after it expires.

The 50-request budget counts outbound attempts, including retry attempts and requests to both providers. Search text over 300 characters and result counts above 8 are rejected before an OpenAlex request. Empty search text returns an empty result without making an HTTP request. The MCP profile also has the existing 30-calls-per-minute tool guard.

## Deterministic verifier

`src/labquorum/scholarly/verify.py` applies the algorithm in architecture section 3.5:

1. Normalize DOI values to lowercase, decode URL-encoded characters, remove DOI URL and `doi:` prefixes, and trim trailing punctuation.
2. For a DOI, query Crossref `works/{doi}`. On 404, query OpenAlex by DOI, which covers DataCite records. If both sources miss, return `UNRESOLVED`.
3. Without a DOI, search OpenAlex for at most eight candidates. RapidFuzz `token_set_ratio` ranks candidates for retrieval only. The library documents that token-set scoring can return 100 when one string is a subset of another, so this score never verifies a citation. [RapidFuzz token-set ratio](https://rapidfuzz.github.io/RapidFuzz/Usage/fuzz.html).
4. Normalize titles by unescaping HTML, stripping HTML and LaTeX markup, applying Unicode NFKC, folding accents, case-folding, and normalizing punctuation and whitespace. Automatic identity requires an exact normalized full-title match. A missing or non-exact title returns `NEEDS_REVIEW`. First-author surname differences and year differences greater than one return `MISMATCH` with field-level diffs.
5. Crossref `update-to` entries of type retraction and OpenAlex `is_retracted=true` return `RETRACTED`. Crossref correction and expression-of-concern entries produce `VERIFIED_WITH_NOTE`. Crossref's `update-to` data identifies the notice DOI; an OpenAlex boolean signal does not itself supply one. [Crossref Retraction Watch metadata](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/), [OpenAlex work attributes](https://help.openalex.org/data/works/attributes/).
6. Crossref `is-preprint-of` relations and OpenAlex published-version locations produce `VERIFIED_WITH_NOTE` and include a version-of-record DOI when available. [Crossref preprint relations](https://www.crossref.org/documentation/schema-library/markup-guide-record-types/posted-content-includes-preprints/).
7. A required provider that remains unreachable after retries yields `UNREACHABLE`, never a verified verdict.

The success message is exactly `metadata matched; no retraction signal found in checked sources as of DATE; claim support not established`, with `DATE` filled from the check timestamp. Results separately expose matched metadata, checked sources, cache age, and `claim_support: not established`. Metadata lookup does not inspect source text and does not establish support for a scientific claim.

Bibliography verification deduplicates entries by normalized DOI, or by normalized title, first-author surname, and year when the DOI is absent. The MCP tool accepts up to 50 entries. Search results are metadata candidates only. This implementation does not parse free-form bibliography syntax or publish draft sections.

## MCP profile

`librarian` exposes exactly `verify_citation`, `verify_bibliography`, and `search_literature`; `scout` maps to this profile. The JSON schemas are snapshotted with the installed MCP SDK `Tool.from_function` at `.venv/Lib/site-packages/mcp/server/fastmcp/tools/base.py:46` and compared with the configured FastMCP server's `list_tools` implementation at `.venv/Lib/site-packages/mcp/server/fastmcp/server.py:331`. `search_literature` sends OpenAlex at most 8 results for a query of at most 300 characters. Tool errors use the shared error enum, and results are compacted to the configured response size limit.

## Tests and recorded data

Pytest configures `--record-mode=none` and `--block-network` in `pyproject.toml`; the installed `pytest-recording` plugin defaults to `none` and applies the network blocker at `.venv/Lib/site-packages/pytest_recording/plugin.py:74-161`. Unit and fault-injection tests use HTTPX mock transports or `respx`. The cassette tests cover a verified DOI, the pinned retraction DOI, and the deliberately unresolved negative DOI. Cassette headers and identifying request parameters are filtered: `authorization`, `user-agent`, `mailto`, and `api_key`.

The three cassette episodes were recorded on 2026-11-05 with `CONTACT_EMAIL=labquorum-dev@example.invalid`, as specified for this build run. This placeholder was used only for cassette capture; set a functioning address in `CONTACT_EMAIL` before live Crossref use. The positive control DOI `10.1038/s41586-021-03819-2` is an additional public metadata fixture because the seed-data template pins a retraction and an unresolved negative DOI but does not pin a positive verified DOI. A miss for the negative DOI is recorded as `UNRESOLVED`, not as proof that a source is fabricated.

The current repository's phase registry has P1, P2, and P3 IDs only. `docs/build/evidence/p5.json` records this builder's red-test evidence for later phase-gate registration; it does not add or alter a gate. The P1 and P2 gates remain the only gate scripts requested for this build.

## Current limitations

- Retraction signals are limited to the checked Crossref and OpenAlex metadata. A `VERIFIED` verdict means no signal was found in those checked records as of the check date, not that the work is unretracted everywhere.
- OpenAlex's `is_retracted` signal is boolean and does not provide a notice DOI. The result identifies OpenAlex as the signal source and leaves `retraction_doi` empty for that case.
- Search recall and the general false-positive rate are not measured. The seed-derived set has three explicitly labeled examples, not the planned 40-citation regression set or the 24-source holdout evaluation.
- A DOI and metadata match do not establish claim support. These tools accept user-supplied query and citation strings, so callers must send only public bibliographic data; the query-length limit is not a privacy control.
