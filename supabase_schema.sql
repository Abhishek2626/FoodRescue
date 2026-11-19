-- ====================================================================
-- FoodRescue Cloud: Production Supabase PostgreSQL Schema DDL
-- Platform: Supabase PostgreSQL (Cloud Database Extension)
-- ====================================================================

-- 1. Enable UUID Extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create Donations Table
CREATE TABLE IF NOT EXISTS public.donations (
    id VARCHAR(32) PRIMARY KEY,
    donor_name VARCHAR(255) NOT NULL,
    food_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity NUMERIC(10, 2) NOT NULL CHECK (quantity > 0),
    unit VARCHAR(50) NOT NULL,
    expiry DATE NOT NULL,
    location VARCHAR(255) NOT NULL,
    pickup_window VARCHAR(100) DEFAULT 'Flexible',
    contact VARCHAR(255),
    description TEXT,
    storage_conditions VARCHAR(100) DEFAULT 'Ambient / Room Temperature',
    allergens VARCHAR(255) DEFAULT 'None / Pure Vegetarian',
    status VARCHAR(50) NOT NULL DEFAULT 'Available',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    claimed_by VARCHAR(255) DEFAULT '',
    claim_note TEXT DEFAULT '',
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Performance Indexes for fast filtering and matching
CREATE INDEX IF NOT EXISTS idx_donations_status ON public.donations(status);
CREATE INDEX IF NOT EXISTS idx_donations_category ON public.donations(category);
CREATE INDEX IF NOT EXISTS idx_donations_expiry ON public.donations(expiry);
CREATE INDEX IF NOT EXISTS idx_donations_created_at ON public.donations(created_at DESC);

-- 3. Create Audit Events Log Table (Immutable append-only ledger)
CREATE TABLE IF NOT EXISTS public.events (
    id VARCHAR(64) PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    donation_id VARCHAR(32) REFERENCES public.donations(id) ON DELETE CASCADE,
    food_name VARCHAR(255),
    event VARCHAR(100) NOT NULL,
    actor VARCHAR(255) NOT NULL,
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_donation ON public.events(donation_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON public.events(timestamp DESC);

-- 4. Row Level Security (RLS) Configuration
ALTER TABLE public.donations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;

-- Educational / Demonstration Policies
-- Allows read and write for the Streamlit web client via Supabase anon key
CREATE POLICY "Public Read Access on Donations" ON public.donations FOR SELECT USING (true);
CREATE POLICY "Public Insert on Donations" ON public.donations FOR INSERT WITH CHECK (true);
CREATE POLICY "Public Update on Donations" ON public.donations FOR UPDATE USING (true);

CREATE POLICY "Public Read on Events" ON public.events FOR SELECT USING (true);
CREATE POLICY "Public Insert on Events" ON public.events FOR INSERT WITH CHECK (true);

-- 5. Seed Initial Demonstration Records
INSERT INTO public.donations (
    id, donor_name, food_name, category, quantity, unit, expiry, location, 
    pickup_window, contact, description, storage_conditions, allergens, status, 
    created_at, claimed_by, claim_note
) VALUES
(
    'FR-2026-1001', 
    'Green Leaf Organic Cafe', 
    'Nutritious Veg Meal Trays', 
    'Cooked Meals', 
    35.0, 
    'meals', 
    CURRENT_DATE + INTERVAL '1 day', 
    'Indiranagar, Bengaluru', 
    'Within 2 hours', 
    'mgr.indiranagar@greenleaf.demo', 
    'Steamed brown rice, mixed dal, and roasted seasonal vegetables packed in bio-trays.', 
    'Hot Hold (> 60°C)', 
    'None / Pure Vegetarian', 
    'Available', 
    NOW() - INTERVAL '3 hours', 
    '', 
    ''
),
(
    'FR-2026-1002', 
    'Sunrise Artisan Bakery', 
    'Sourdough & Multigrain Loaves', 
    'Bakery & Bread', 
    14.0, 
    'kg', 
    CURRENT_DATE + INTERVAL '2 days', 
    'Koramangala 4th Block, Bengaluru', 
    'Today evening', 
    'contact@sunrisebakery.demo', 
    'Day-end artisan loaves and dinner rolls, paper bagged and sealed.', 
    'Ambient / Room Temperature', 
    'Contains Gluten / Wheat', 
    'Available', 
    NOW() - INTERVAL '5 hours', 
    '', 
    ''
),
(
    'FR-2026-1003', 
    'Campus Dining Hall - Tech University', 
    'Fresh Apple & Orange Crates', 
    'Fresh Produce', 
    25.0, 
    'boxes', 
    CURRENT_DATE + INTERVAL '4 days', 
    'Jayanagar 7th Block, Bengaluru', 
    'Tomorrow morning', 
    'catering.lead@techuniv.demo', 
    'Whole seasonal fresh fruits in ventilated wooden crates. High quality.', 
    'Keep in dry, cool place', 
    'None / Pure Vegetarian', 
    'Accepted', 
    NOW() - INTERVAL '8 hours', 
    'Hope Community Kitchen', 
    'Scheduled volunteer van pickup for tomorrow breakfast program.'
)
ON CONFLICT (id) DO NOTHING;

-- Initial audit events
INSERT INTO public.events (id, timestamp, donation_id, food_name, event, actor, details) VALUES
('EVT-101', NOW() - INTERVAL '8 hours', 'FR-2026-1003', 'Fresh Apple & Orange Crates', 'Created', 'Campus Dining Hall (Donor)', 'Published 25 boxes of fresh produce.'),
('EVT-102', NOW() - INTERVAL '5 hours', 'FR-2026-1003', 'Fresh Apple & Orange Crates', 'Accepted', 'Hope Community Kitchen (NGO)', 'Accepted for morning breakfast distribution.')
ON CONFLICT (id) DO NOTHING;
