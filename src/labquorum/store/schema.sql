CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS person (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL,
    timezone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS instrument (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    aliases_json TEXT NOT NULL,
    location TEXT NOT NULL,
    timezone TEXT NOT NULL,
    requires_training INTEGER NOT NULL CHECK (requires_training IN (0, 1)),
    max_block_minutes INTEGER NOT NULL CHECK (max_block_minutes > 0),
    min_gap_minutes INTEGER NOT NULL CHECK (min_gap_minutes >= 0),
    booking_window_days INTEGER NOT NULL CHECK (booking_window_days >= 0),
    opening_hours_json TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ok', 'down', 'down_until')),
    down_until_utc TEXT
);

CREATE TABLE IF NOT EXISTS training (
    person_id TEXT NOT NULL REFERENCES person(id),
    instrument_id TEXT NOT NULL REFERENCES instrument(id),
    granted_at_utc TEXT NOT NULL,
    expires_at_utc TEXT NOT NULL,
    PRIMARY KEY (person_id, instrument_id)
);

CREATE TABLE IF NOT EXISTS counter (
    name TEXT PRIMARY KEY,
    value INTEGER NOT NULL CHECK (value >= 0)
);

CREATE TABLE IF NOT EXISTS approval_request (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL CHECK (kind = 'booking'),
    requester TEXT NOT NULL REFERENCES person(id),
    resource TEXT NOT NULL REFERENCES instrument(id),
    start_utc TEXT NOT NULL,
    end_utc TEXT NOT NULL,
    project TEXT NOT NULL,
    revision INTEGER NOT NULL CHECK (revision > 0),
    content_hash TEXT NOT NULL,
    decision_json TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'committed', 'declined', 'expired')),
    created_utc TEXT NOT NULL,
    expires_utc TEXT NOT NULL,
    decided_utc TEXT,
    decline_reason TEXT
);

CREATE TABLE IF NOT EXISTS booking (
    id TEXT PRIMARY KEY,
    instrument_id TEXT NOT NULL REFERENCES instrument(id),
    person_id TEXT NOT NULL REFERENCES person(id),
    project_id TEXT NOT NULL,
    start_utc TEXT NOT NULL,
    end_utc TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('proposed', 'committed', 'cancelled', 'expired', 'declined')),
    request_id TEXT NOT NULL UNIQUE REFERENCES approval_request(id),
    CHECK (end_utc > start_utc)
);

CREATE INDEX IF NOT EXISTS booking_instrument_start
    ON booking(instrument_id, status, start_utc, end_utc);
CREATE INDEX IF NOT EXISTS approval_request_expiry
    ON approval_request(status, expires_utc);

CREATE TABLE IF NOT EXISTS app_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_event (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    ts_utc TEXT NOT NULL,
    actor_agent TEXT NOT NULL,
    tool TEXT NOT NULL,
    args_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    hash TEXT NOT NULL
);
