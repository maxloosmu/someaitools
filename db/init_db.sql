CREATE TABLE users (
    email VARCHAR(255) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    has_taken_free_summary BOOLEAN NOT NULL DEFAULT FALSE,
    last_free_summary_time TIMESTAMP NULL DEFAULT NULL,
    email_authenticated BOOLEAN NOT NULL DEFAULT FALSE,
    login_authenticated BOOLEAN NOT NULL DEFAULT FALSE,
    confirmation_code INTEGER,
    confirmation_code_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE access_logs (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(255) NOT NULL,
    client_info TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_email VARCHAR(255) REFERENCES users(email)
);

CREATE TABLE file_uploads (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INT,
    page_count INT,
    user_email VARCHAR(255) REFERENCES users(email)
);
