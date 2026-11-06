# Security policy

## Supported use and data

LabQuorum is an early release candidate for local lab booking workflows. Use synthetic data only. Do not store unpublished research, personal information, or human-subjects data in the ledger, agent folders, logs, or backups. Such data needs separately designed operating-system or container isolation and institutional review.

The `.env` file can hold optional API credentials. Keep it out of version control and restrict access to it. SQLite ledgers and backups are not encrypted by LabQuorum, so protect their files and parent directories with operating-system permissions. Model and dictation service calls can leave the local machine.

## Threat model and limits

The approval boundary depends on Switch resolving the actual human identity, applying the configured addressing policy, and presenting the exact booking decision for review. A decision hash binds the request data to a ledger operation; it does not authenticate a person. Session-wide approval can weaken per-request review. Binding commits must remain disabled unless the installed Switch and Codex configuration has passed the project's P4 certification for identity, profile exposure, card contents, and one-decision behavior. If that evidence is absent or does not match the installed versions, use proposal-only mode.

All agents and the ledger currently run as the same operating-system user. Agent folder instructions and configuration are policy, not an operating-system security boundary. A malicious process running as that user, or a compromised administrator, can read or change the ledger, configuration, and backups. This threat is out of scope for the current design.

The audit hash chain detects edits that are not re-hashed. A writer with access to the database can truncate the tail or recompute the chain. Without an external checkpoint, `lq audit verify` cannot detect those changes. A successful backup integrity check and audit verification do not provide encryption or an external tamper-proof record.

## Reporting a vulnerability

Report suspected vulnerabilities privately through [GitHub's private vulnerability reporting page](https://github.com/nikhilpravinpise/FlipTheSwitch/security/advisories/new). Include the affected version, impact, and steps to reproduce. Do not post credentials, personal data, or an exploit in a public issue. If private reporting is unavailable, contact a maintainer through GitHub and ask for a private channel. There is no guaranteed response or remediation time.
