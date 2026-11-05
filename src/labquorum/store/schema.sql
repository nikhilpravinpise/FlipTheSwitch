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
    down_until_utc TEXT CHECK (
        down_until_utc IS NULL OR (
            length(down_until_utc) = 27
            AND down_until_utc GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'
        )
    )
);

CREATE TABLE IF NOT EXISTS training (
    person_id TEXT NOT NULL REFERENCES person(id),
    instrument_id TEXT NOT NULL REFERENCES instrument(id),
    granted_at_utc TEXT NOT NULL CHECK (
        length(granted_at_utc) = 27
        AND granted_at_utc GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'
    ),
    expires_at_utc TEXT NOT NULL CHECK (
        length(expires_at_utc) = 27
        AND expires_at_utc GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'
    ),
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
    start_utc TEXT NOT NULL CHECK (
        length(start_utc) = 27
        AND start_utc GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'
    ),
    end_utc TEXT NOT NULL CHECK (
        length(end_utc) = 27
        AND end_utc GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'
    ),
    project TEXT NOT NULL,
    revision INTEGER NOT NULL CHECK (revision > 0),
    content_hash TEXT NOT NULL,
    decision_json TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'committed', 'declined', 'expired')),
    created_utc TEXT NOT NULL CHECK (
        length(created_utc) = 27
        AND created_utc GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'
    ),
    expires_utc TEXT NOT NULL CHECK (
        length(expires_utc) = 27
        AND expires_utc GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'
    ),
    decided_utc TEXT CHECK (
        decided_utc IS NULL OR (
            length(decided_utc) = 27
            AND decided_utc GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'
        )
    ),
    decline_reason TEXT,
    CHECK (end_utc > start_utc)
);

CREATE TABLE IF NOT EXISTS booking (
    id TEXT PRIMARY KEY,
    instrument_id TEXT NOT NULL REFERENCES instrument(id),
    person_id TEXT NOT NULL REFERENCES person(id),
    project_id TEXT NOT NULL,
    start_utc TEXT NOT NULL CHECK (
        length(start_utc) = 27
        AND start_utc GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'
    ),
    end_utc TEXT NOT NULL CHECK (
        length(end_utc) = 27
        AND end_utc GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'
    ),
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
    ts_utc TEXT NOT NULL CHECK (
        length(ts_utc) = 27
        AND ts_utc GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]Z'
    ),
    actor_agent TEXT NOT NULL,
    tool TEXT NOT NULL,
    args_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    hash TEXT NOT NULL
);
