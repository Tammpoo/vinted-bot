-- Migration 1.0.4 to 1.0.5
-- No schema changes
UPDATE configuration SET value = '1.0.5' WHERE key = 'version';
