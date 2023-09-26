CREATE TABLE users (
    id INTEGER NOT NULL,
    username TEXT NOT NULL,
    fullname TEXT,
    hash TEXT NOT NULL,
    about_me TEXT,
    friends INTEGER DEFAULT 0 NOT NULL,
    posts INTEGER DEFAULT 0 NOT NULL,
    carnival INTEGER DEFAULT 0 NOT NULL,
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

CREATE TABLE posts (
    id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    likes INTEGER NOT NULL DEFAULT 0,
    comments INTEGER NOT NULL DEFAULT 0,
    title TEXT NOT NULL,
    contents TEXT NOT NULL,
    imagelocation TEXT DEFAULT NULL,
    post_time TIMESTAMP NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE post_tags (
    id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(post_id) REFERENCES posts(id),
    FOREIGN KEY(tag_id) REFERENCES interests(id)
);

CREATE TABLE user_post_interactions (
    id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status INTEGER CHECK (status IN (0, 1, 2)) DEFAULT 0,
    timestamp INTEGER NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(post_id) REFERENCES posts(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE comments (
    id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    contents TEXT NOT NULL,
    likes INTEGER NOT NULL DEFAULT 0,
    replies INTEGER NOT NULL DEFAULT 0,
    comment_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id),
    FOREIGN KEY(post_id) REFERENCES posts(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE user_comment_interactions (
    id INTEGER NOT NULL,
    comment_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status INTEGER CHECK (status IN (0, 1, 2)) DEFAULT 0,
    timestamp INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id),
    FOREIGN KEY(comment_id) REFERENCES comments(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
