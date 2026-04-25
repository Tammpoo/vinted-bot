-- Initial database schema
CREATE TABLE IF NOT EXISTS configuration (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    price REAL NOT NULL,
    title TEXT NOT NULL,
    photo_url TEXT,
    query_id INTEGER,
    currency TEXT,
    FOREIGN KEY (query_id) REFERENCES queries(id)
);

CREATE TABLE IF NOT EXISTS query_timestamps (
    query_id INTEGER PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    FOREIGN KEY (query_id) REFERENCES queries(id)
);

CREATE TABLE IF NOT EXISTS allowlist (
    country_code TEXT PRIMARY KEY
);

-- Default configuration
INSERT OR IGNORE INTO configuration (key, value) VALUES ('version', '1.0.0');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('telegram_enabled', 'False');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('telegram_token', '');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('telegram_chat_id', '');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('telegram_process_running', 'False');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('rss_enabled', 'False');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('rss_process_running', 'False');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('query_refresh_delay', '30');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('items_per_query', '20');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('github_url', 'https://github.com/Fuyucch1/Vinted-Notifications');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('message_template', '🆕 <b>{title}</b>\n💶 Price: {price}\n🛍️ Brand: {brand}');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('banwords', '');
INSERT OR IGNORE INTO configuration (key, value) VALUES ('proxies', '');
