CREATE TABLE users (
    id INTEGER NOT NULL,
    username TEXT NOT NULL,
    fullname TEXT,
    hash TEXT NOT NULL,
    about_me TEXT,
    friends INTEGER DEFAULT 0 NOT NULL,
    posts INTEGER DEFAULT 0 NOT NULL,
    creation_time TIMESTAMP NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE interests (
    id INTEGER NOT NULL,
    interest TEXT NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE user_interests (
    id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    interest_id INTEGER NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(interest_id) REFERENCES interests(id)
);

CREATE TABLE friends (
    id INTEGER NOT NULL,
    user_id1 INTEGER NOT NULL,
    user_id2 INTEGER NOT NULL,
    friends INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id1) REFERENCES users(id),
    FOREIGN KEY(user_id2) REFERENCES users(id)
);
