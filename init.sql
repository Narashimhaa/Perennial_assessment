-- Initialize the database schema for the Employee Search API
-- This script sets up the complete database structure and populates it with sample data

-- ============================================================================
-- 1. CREATE TABLES
-- ============================================================================

-- Create employees table
CREATE TABLE IF NOT EXISTS public.employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    department VARCHAR(100),
    "position" VARCHAR(100),
    "location" VARCHAR(255),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    org_id INTEGER
);

-- Create org_column_config table
CREATE TABLE IF NOT EXISTS public.org_column_config (
    org_id SERIAL PRIMARY KEY,
    visible_columns TEXT[]
);

-- ============================================================================
-- 2. CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Primary indexes
CREATE INDEX IF NOT EXISTS ix_employees_id ON public.employees USING btree (id);
CREATE INDEX IF NOT EXISTS ix_employees_org_id ON public.employees USING btree (org_id);
CREATE INDEX IF NOT EXISTS ix_org_column_config_org_id ON public.org_column_config USING btree (org_id);

-- Search and filter indexes
CREATE INDEX IF NOT EXISTS idx_employees_status ON public.employees(status);
CREATE INDEX IF NOT EXISTS idx_employees_department ON public.employees(department);
CREATE INDEX IF NOT EXISTS idx_employees_location ON public.employees("location");
CREATE INDEX IF NOT EXISTS idx_employees_position ON public.employees("position");

-- Text search indexes for better performance
CREATE INDEX IF NOT EXISTS idx_employees_first_name_lower ON public.employees(LOWER(first_name));
CREATE INDEX IF NOT EXISTS idx_employees_last_name_lower ON public.employees(LOWER(last_name));
CREATE INDEX IF NOT EXISTS idx_employees_email_lower ON public.employees(LOWER(email));

-- ============================================================================
-- 3. INSERT ORGANIZATION CONFIGURATION
-- ============================================================================

-- Insert organization column configurations
INSERT INTO public.org_column_config (org_id, visible_columns) VALUES
(1, ARRAY['first_name', 'last_name', 'department', 'position']),
(2, ARRAY['first_name', 'email', 'phone', 'location']),
(3, ARRAY['first_name', 'last_name', 'department', 'location', 'position'])
ON CONFLICT (org_id) DO NOTHING;

-- ============================================================================
-- 4. GENERATE SAMPLE EMPLOYEE DATA (500 records)
-- ============================================================================

-- Insert 500 sample employees with realistic data distribution
INSERT INTO public.employees (
    first_name,
    last_name,
    email,
    phone,
    department,
    "position",
    "location",
    status,
    avatar_url,
    created_at,
    updated_at,
    org_id
)
SELECT
    INITCAP(SUBSTRING(md5(random()::text), 1, 8)) AS first_name,
    INITCAP(SUBSTRING(md5(random()::text), 9, 8)) AS last_name,
    SUBSTRING(md5(random()::text), 1, 10) || '@example.com' AS email,
    '+1-555-' || LPAD((trunc(random() * 10000))::text, 4, '0') AS phone,
    dept.val AS department,
    pos.val AS "position",
    loc.val AS "location",
    CASE floor(random() * 3)::int
        WHEN 0 THEN 'ACTIVE'
        WHEN 1 THEN 'NOT_STARTED'
        ELSE 'TERMINATED'
    END AS status,
    'https://api.dicebear.com/6.x/thumbs/svg?seed=' || SUBSTRING(md5(random()::text), 1, 10) AS avatar_url,
    CURRENT_TIMESTAMP - (random() * interval '365 days') AS created_at,
    CURRENT_TIMESTAMP - (random() * interval '30 days') AS updated_at,
    (floor(random() * 3) + 1)::int AS org_id
FROM generate_series(1, 500)
CROSS JOIN LATERAL (
    SELECT val FROM unnest(ARRAY['Engineering', 'Marketing', 'Sales', 'HR', 'Support']) val
    OFFSET floor(random() * 5)
) AS dept
CROSS JOIN LATERAL (
    SELECT val FROM unnest(ARRAY['Manager', 'Developer', 'Analyst', 'Intern', 'Executive']) val
    OFFSET floor(random() * 5)
) AS pos
CROSS JOIN LATERAL (
    SELECT val FROM unnest(ARRAY['New York', 'San Francisco', 'Berlin', 'London', 'Chennai']) val
    OFFSET floor(random() * 5)
) AS loc;

-- ============================================================================
-- 5. INSERT ADDITIONAL TEST DATA (Known records for testing)
-- ============================================================================

-- Insert some known test records for easier testing and validation
INSERT INTO public.employees (first_name, last_name, email, phone, department, "position", "location", status, avatar_url, org_id) VALUES
('Alice', 'Smith', 'alice.smith@example.com', '+1-555-0101', 'Engineering', 'Manager', 'New York', 'ACTIVE', 'https://api.dicebear.com/6.x/thumbs/svg?seed=alice', 1),
('Bob', 'Johnson', 'bob.johnson@example.com', '+1-555-0102', 'Engineering', 'Developer', 'San Francisco', 'ACTIVE', 'https://api.dicebear.com/6.x/thumbs/svg?seed=bob', 1),
('Carol', 'Williams', 'carol.williams@example.com', '+1-555-0103', 'Marketing', 'Analyst', 'Berlin', 'NOT_STARTED', 'https://api.dicebear.com/6.x/thumbs/svg?seed=carol', 1),
('David', 'Brown', 'david.brown@example.com', '+1-555-0104', 'Sales', 'Executive', 'London', 'ACTIVE', 'https://api.dicebear.com/6.x/thumbs/svg?seed=david', 2),
('Emma', 'Davis', 'emma.davis@example.com', '+1-555-0105', 'HR', 'Manager', 'Chennai', 'ACTIVE', 'https://api.dicebear.com/6.x/thumbs/svg?seed=emma', 2),
('Frank', 'Miller', 'frank.miller@example.com', '+1-555-0106', 'Support', 'Analyst', 'New York', 'TERMINATED', 'https://api.dicebear.com/6.x/thumbs/svg?seed=frank', 3),
('Grace', 'Wilson', 'grace.wilson@example.com', '+1-555-0107', 'Engineering', 'Intern', 'San Francisco', 'ACTIVE', 'https://api.dicebear.com/6.x/thumbs/svg?seed=grace', 3)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 6. UPDATE STATISTICS AND ANALYZE TABLES
-- ============================================================================

-- Update table statistics for better query planning
ANALYZE public.employees;
ANALYZE public.org_column_config;

-- ============================================================================
-- 7. VERIFICATION QUERIES (for logging/debugging)
-- ============================================================================

-- Log the data distribution for verification
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully!';
    RAISE NOTICE 'Total employees created: %', (SELECT COUNT(*) FROM public.employees);
    RAISE NOTICE 'Employees by organization: Org 1: %, Org 2: %, Org 3: %',
        (SELECT COUNT(*) FROM public.employees WHERE org_id = 1),
        (SELECT COUNT(*) FROM public.employees WHERE org_id = 2),
        (SELECT COUNT(*) FROM public.employees WHERE org_id = 3);
    RAISE NOTICE 'Active employees: %', (SELECT COUNT(*) FROM public.employees WHERE status = 'ACTIVE');
    RAISE NOTICE 'Organizations configured: %', (SELECT COUNT(*) FROM public.org_column_config);
END $$;
