CREATE TABLE users (
    id INTEGER NOT NULL,
    username TEXT NOT NULL,
    fullname TEXT,
    hash TEXT NOT NULL,
    creation_time TIMESTAMP NOT NULL,
    friends INTEGER DEFAULT 0 NOT NULL,
    PRIMARY KEY(id)
);
