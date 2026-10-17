-- ============================================================================
-- MIGRATION: 20261016000000_cost_estimation_details.sql
-- DESCRIPTION: Non-destructive addition of estimation details, snapshots,
--              breakdowns, and rate snapshots for Phase 6D Cost Estimation Engine.
-- ============================================================================

ALTER TABLE public.estimations
ADD COLUMN IF NOT EXISTS floor_plan_id UUID REFERENCES public.floor_plans(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS area_schedule JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS quantity_breakdown JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS line_items JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS rates_snapshot JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS assumptions JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS contingency_cost NUMERIC NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS tax_cost NUMERIC NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS overhead_cost NUMERIC NOT NULL DEFAULT 0;

COMMENT ON COLUMN public.estimations.floor_plan_id IS 'Reference to the specific floor plan layout version used to calculate this estimate';
COMMENT ON COLUMN public.estimations.area_schedule IS 'Geometry-derived area schedule (BUA, indoor room area, site areas, terraces)';
COMMENT ON COLUMN public.estimations.quantity_breakdown IS 'Key material and structural quantity totals';
COMMENT ON COLUMN public.estimations.line_items IS 'Complete itemized list of material, labor and fixture lines with formulas';
COMMENT ON COLUMN public.estimations.rates_snapshot IS 'Immutable snapshot of unit rates and sources applied during calculation';
