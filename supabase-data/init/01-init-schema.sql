-- IGN Scripts Supabase Database Initialization
-- This script creates the initial schema for the IGN Scripts knowledge system
-- Author: IGN Scripts Data Integration System
-- Created: 2025-01-28

-- Enable UUID extension for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom schemas
CREATE SCHEMA IF NOT EXISTS ignition;
CREATE SCHEMA IF NOT EXISTS auth;

-- Set search path
SET search_path TO ignition, public;

-- ============================================================================
-- IGNITION CONTEXTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS ignition_contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    context_type VARCHAR(50) NOT NULL CHECK (context_type IN ('Gateway', 'Vision', 'Perspective', 'Designer')),
    is_active BOOLEAN DEFAULT true,
    capabilities JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- IGNITION FUNCTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS ignition_functions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    module VARCHAR(100) NOT NULL,
    full_name VARCHAR(300) NOT NULL UNIQUE,
    description TEXT,
    function_type VARCHAR(50) NOT NULL,
    return_type VARCHAR(100),
    parameters JSONB DEFAULT '[]',
    examples JSONB DEFAULT '[]',
    contexts JSONB DEFAULT '[]',
    script_types JSONB DEFAULT '[]',
    complexity_level INTEGER DEFAULT 1 CHECK (complexity_level BETWEEN 1 AND 5),
    usage_frequency INTEGER DEFAULT 0,
    documentation_url TEXT,
    is_deprecated BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- IGNITION SCRIPTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS ignition_scripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    script_type VARCHAR(50) NOT NULL,
    context VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    language VARCHAR(20) DEFAULT 'python',
    functions_used JSONB DEFAULT '[]',
    parameters JSONB DEFAULT '{}',
    quality_score DECIMAL(3,2) DEFAULT 0.0,
    version VARCHAR(20) DEFAULT '1.0.0',
    status VARCHAR(20) DEFAULT 'draft',
    created_by VARCHAR(100) DEFAULT 'system',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_ignition_contexts_type ON ignition_contexts(context_type);
CREATE INDEX IF NOT EXISTS idx_ignition_functions_module ON ignition_functions(module);
CREATE INDEX IF NOT EXISTS idx_ignition_functions_type ON ignition_functions(function_type);
CREATE INDEX IF NOT EXISTS idx_ignition_scripts_type ON ignition_scripts(script_type);
CREATE INDEX IF NOT EXISTS idx_ignition_scripts_context ON ignition_scripts(context);

-- ============================================================================
-- INITIAL DATA SEEDING
-- ============================================================================
INSERT INTO ignition_contexts (name, description, context_type, capabilities) VALUES
('Gateway', 'Ignition Gateway context for server-side operations', 'Gateway', '{"database": true, "tags": true, "alarms": true, "scheduling": true}'),
('Vision', 'Ignition Vision context for desktop client applications', 'Vision', '{"gui": true, "client_tags": true, "windows": true, "components": true}'),
('Perspective', 'Ignition Perspective context for web-based applications', 'Perspective', '{"web_gui": true, "mobile": true, "views": true, "sessions": true}'),
('Designer', 'Ignition Designer context for development environment', 'Designer', '{"development": true, "testing": true, "debugging": true}')
ON CONFLICT (name) DO NOTHING;

-- Sample functions
INSERT INTO ignition_functions (name, module, full_name, description, function_type, return_type, contexts, script_types) VALUES
('runQuery', 'system.db', 'system.db.runQuery', 'Execute a SQL query against a database connection', 'database', 'Dataset', '["Gateway", "Vision", "Perspective"]', '["startup", "timer", "tag_change"]'),
('writeToTag', 'system.tag', 'system.tag.writeToTag', 'Write a value to a tag', 'tag', 'QualityCode', '["Gateway", "Vision", "Perspective"]', '["startup", "timer", "tag_change", "client_event"]'),
('readFromTag', 'system.tag', 'system.tag.readFromTag', 'Read a value from a tag', 'tag', 'QualifiedValue', '["Gateway", "Vision", "Perspective"]', '["startup", "timer", "tag_change", "client_event"]'),
('messageBox', 'system.gui', 'system.gui.messageBox', 'Display a message box to the user', 'gui', 'String', '["Vision", "Perspective"]', '["client_event"]'),
('getLogger', 'system.util', 'system.util.getLogger', 'Get a logger instance for logging', 'utility', 'Logger', '["Gateway", "Vision", "Perspective"]', '["startup", "shutdown", "timer", "tag_change"]')
ON CONFLICT (full_name) DO NOTHING;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'IGN Scripts Supabase database initialization completed successfully!';
    RAISE NOTICE 'Created schemas: ignition, auth';
    RAISE NOTICE 'Created tables: contexts, functions, scripts';
    RAISE NOTICE 'Created indexes and seeded initial data';
END $$;
