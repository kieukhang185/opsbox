
-- Enable the uuid-ossp extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the tasks status enum type
CREATE TYPE task_status AS ENUM ('NEW', 'PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED');

-- Create the tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    status task_status NOT NULL DEFAULT 'NEW',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    result TEXT
);

-- Trigger function to update the updated_at column on row modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger to call the function before any update on the tasks table
CREATE TRIGGER update_task_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Index on the status column for faster queries based on task status
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
-- Index on the created_at column for faster queries based on creation time
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
-- Index on the updated_at column for faster queries based on update time
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at);

-- Sample data insertion (optional)
INSERT INTO tasks (title, status) VALUES
('Sample Task 1', 'NEW'),
('Sample Task 2', 'PENDING'),
('Sample Task 3', 'RUNNING');
-- Commit the transaction
COMMIT;
