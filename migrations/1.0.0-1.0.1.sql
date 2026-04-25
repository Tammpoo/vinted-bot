-- Migration 1.0.0 to 1.0.1
ALTER TABLE queries ADD COLUMN name TEXT;
UPDATE configuration SET value = '1.0.1' WHERE key = 'version';
