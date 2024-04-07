CREATE TABLE IF NOT EXISTS task_results (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL,
    state TEXT,
    result TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
);