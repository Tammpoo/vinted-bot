-- Migration 1.0.1 to 1.0.2
-- Add banwords configuration
INSERT OR IGNORE INTO configuration (key, value) VALUES ('banwords', '');
UPDATE configuration SET value = '1.0.2' WHERE key = 'version';
