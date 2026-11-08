
-- SQL Schema Creation
-- Candidate Initials: SPS

CREATE TABLE IF NOT EXISTS sps_users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    email TEXT,
    phone TEXT,
    website TEXT,
    address_json TEXT,
    company_json TEXT
);

CREATE TABLE IF NOT EXISTS sps_posts (
    id INTEGER PRIMARY KEY,
    userId INTEGER,
    title TEXT,
    body TEXT,
    status TEXT,
    name TEXT,
    username TEXT,
    email TEXT,
    FOREIGN KEY (userId) REFERENCES sps_users(id)
);
