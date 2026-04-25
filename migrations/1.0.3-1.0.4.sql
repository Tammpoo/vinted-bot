-- Migration 1.0.3 to 1.0.4
-- No schema changes
UPDATE configuration SET value = '1.0.4' WHERE key = 'version';
