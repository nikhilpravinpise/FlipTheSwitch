# Final submission status

Submitted 7 Nov 2026 at 22:30 IST for Best Business Workflow.

- [Repository](https://github.com/nikhilpravinpise/FlipTheSwitch)
- [Demo video](https://youtu.be/GbRepWsmOqk), unlisted, 1:50
- [Published blog](https://dev.to/darshan_ved_9ca4564654404/a-proposal-is-not-a-reservation-what-we-learned-putting-ai-agents-in-a-labs-booking-chat-3cee)
- Wispr cards: [Nikhil's Share card](evidence/wispr/nikhil-wispr-share-card-2026-11-07.png) and [Darshan's 20:43 card](evidence/wispr/insights-2026-11-07-2043.png).
- Main contained v1.0.3 plus PRs #21, #22 and #23 at submission close-out.

## Certification

The deployment is proposal-only; binding is not certified. The recorded smoke test named a conflict and proposed a slot without a commit. An isolated test-ledger approval for AR-0043 produced one matching booking and one commit event. Decline, refusal, student card response, and injection probes I-36 and I-37 also have passing observations. See [test evidence](../test-evidence.md) and [certification summary](evidence/p4/certification.json).

E2E-11 was not run because a current Console session ID could not be verified. I-38 to I-40 failed before recording a request or card. The live model and effort trace is not proven: no readable `turn_context` was captured.

## Known limitations

- Darshan's [accessibility review](https://github.com/nikhilpravinpise/FlipTheSwitch/issues/4) found repeated conflict text, a crowded Mattermost layout at simulated 200 percent CSS zoom, and system posts announced as "Someone wrote". A real screen-reader pass and true browser-level 200 percent zoom are UNVERIFIED.
- Tools accept a caller-supplied `requester_handle` and do not authenticate it against the platform sender.
- `tests/contract/p2_probe_args.json` and `scripts/gates/p2_stdio_probe.py` use a fixed 9 Nov date with the real clock and are not run in CI.
- The live deployment ran on one laptop over Tailscale; it is not a public instance.

## Next steps, in priority order

1. Authenticate the requester against the platform sender.
2. Certify E2E-11 and I-38 to I-40.
3. Capture the live model and effort trace.
4. Fix repeated conflict text.
