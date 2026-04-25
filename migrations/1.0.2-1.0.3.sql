-- Migration 1.0.2 to 1.0.3
-- Add proxies configuration
INSERT OR IGNORE INTO configuration (key, value) VALUES ('proxies', '');
UPDATE configuration SET value = '1.0.3' WHERE key = 'version';
