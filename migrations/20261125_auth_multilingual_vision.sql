-- Apply once to an existing PostgreSQL database before starting the updated app.
-- New installations can use SQLAlchemy create_all.

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'customer',
    customer_id INTEGER NULL REFERENCES customers(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);

ALTER TABLE tickets ADD COLUMN IF NOT EXISTS normalized_subject VARCHAR(200);
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS normalized_description TEXT;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(16) NOT NULL DEFAULT 'en';
