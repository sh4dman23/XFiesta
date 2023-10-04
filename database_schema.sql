CREATE TABLE IF NOT EXISTS users (
    id INTEGER NOT NULL,
    username TEXT NOT NULL,
    fullname TEXT,
    hash TEXT NOT NULL,
    about_me TEXT,
    friends INTEGER DEFAULT 0 NOT NULL,
    posts INTEGER DEFAULT 0 NOT NULL,
    carnival INTEGER DEFAULT 0 NOT NULL,
    creation_time TIMESTAMP NOT NULL,
    pfp_location TEXT NOT NULL DEFAULT 'server_hosted_files/profile_pics/default_profile_pic/user_profile_pic.png',
    timezone_offset INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(id)
);
CREATE UNIQUE INDEX IF NOT EXISTS user_index ON users (id, username);

CREATE TABLE IF NOT EXISTS interests (
    id INTEGER NOT NULL,
    interest TEXT NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS user_interests (
    id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    interest_id INTEGER NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(interest_id) REFERENCES interests(id)
);
CREATE INDEX IF NOT EXISTS interest_index ON user_interests(user_id);

CREATE TABLE IF NOT EXISTS friends (
    id INTEGER NOT NULL,
    user_id1 INTEGER NOT NULL,
    user_id2 INTEGER NOT NULL,
    friends INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id1) REFERENCES users(id),
    FOREIGN KEY(user_id2) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS friend_index ON friends(user_id1);
CREATE INDEX IF NOT EXISTS friend_index2 ON friends(user_id2);

CREATE TABLE IF NOT EXISTS posts (
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
CREATE INDEX IF NOT EXISTS post_index ON posts(user_id);

CREATE TABLE IF NOT EXISTS post_tags (
    id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(post_id) REFERENCES posts(id),
    FOREIGN KEY(tag_id) REFERENCES interests(id)
);
CREATE INDEX IF NOT EXISTS post_tag_index ON post_tags(post_id);
CREATE INDEX IF NOT EXISTS tag_index ON post_tags(tag_id);

CREATE TABLE IF NOT EXISTS user_post_interactions (
    id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status INTEGER CHECK (status IN (0, 1, 2)) DEFAULT 0,
    timestamp INTEGER NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(post_id) REFERENCES posts(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS i_posts_index ON user_post_interactions(post_id);
CREATE INDEX IF NOT EXISTS i_users_index ON user_post_interactions(user_id);

CREATE TABLE IF NOT EXISTS comments (
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
CREATE INDEX IF NOT EXISTS comment_post_index ON comments(post_id);
CREATE INDEX IF NOT EXISTS comment_user_index ON comments(user_id);

CREATE TABLE IF NOT EXISTS user_comment_interactions (
    id INTEGER NOT NULL,
    comment_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status INTEGER CHECK (status IN (0, 1, 2)) DEFAULT 0,
    timestamp INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id),
    FOREIGN KEY(comment_id) REFERENCES comments(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS i_comments_index ON user_comment_interactions(comment_id);
CREATE INDEX IF NOT EXISTS i_c_users_index ON user_comment_interactions(user_id);

CREATE TABLE IF NOT EXISTS inbox (
    id INTEGER NOT NULL,
    user_id1 INTEGER NOT NULL,
    user_id2 INTEGER NOT NULL,
    messages INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id1) REFERENCES users(id)
    FOREIGN KEY(user_id2) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS inbox_user_index1 ON inbox(user_id1);
CREATE INDEX IF NOT EXISTS inbox_user_index2 ON inbox(user_id2);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER NOT NULL,
    inbox_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    contents TEXT NOT NULL,
    message_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_status TEXT NOT NULL CHECK(read_status IN ('read', 'unread')) DEFAULT 'unread',
    PRIMARY KEY(id),
    FOREIGN KEY(inbox_id) REFERENCES inbox(id),
    FOREIGN KEY(sender_id) REFERENCES users(id),
    FOREIGN KEY(recipient_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS message_inbox_index ON messages(inbox_id);

CREATE TABLE IF NOT EXISTS deleted_messages (
    id INTEGER NOT NULL,
    inbox_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(inbox_id) REFERENCES inbox(id),
    FOREIGN KEY(sender_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    href TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('read', 'unread')) DEFAULT 'unread',
    details TEXT NOT NULL,
    n_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS notification_user_index ON notifications(user_id);
