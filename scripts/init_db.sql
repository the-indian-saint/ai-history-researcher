-- PostgreSQL initialization script for AI Research Framework
-- This script runs automatically when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "unaccent";  -- For accent-insensitive search

-- Set default timezone
SET timezone = 'UTC';

-- Create custom types if needed
DO $$ BEGIN
    CREATE TYPE source_type AS ENUM (
        'academic',
        'primary',
        'archaeological',
        'manuscript',
        'inscription',
        'literary',
        'digital_archive'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE processing_status AS ENUM (
        'pending',
        'processing',
        'completed',
        'failed',
        'archived'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Grant necessary permissions to the application user
GRANT ALL PRIVILEGES ON DATABASE research_db TO research_user;
GRANT ALL ON SCHEMA public TO research_user;

-- Create indexes for better performance (will be created by SQLAlchemy, but good to have)
-- These will be skipped if tables don't exist yet

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully';
END $$;
