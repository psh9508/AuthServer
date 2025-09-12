CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login_id VARCHAR(255) NOT NULL UNIQUE,
    password BYTEA NOT NULL,
    salt VARCHAR(32) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO users (login_id, password, salt)
VALUES (
    'admin',
    digest('admin' || 'random_salt', 'sha256'),
    'random_salt'
);