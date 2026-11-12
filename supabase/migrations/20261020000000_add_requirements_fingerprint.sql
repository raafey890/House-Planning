-- Phase 6M.1: Add requirements_fingerprint column to floor_plans table.
-- Stores a JSONB snapshot of the planning requirements used to generate
-- each plan, enabling the fallback system to only reuse plans whose
-- requirements match the current request.

ALTER TABLE public.floor_plans
    ADD COLUMN IF NOT EXISTS requirements_fingerprint JSONB;

COMMENT ON COLUMN public.floor_plans.requirements_fingerprint IS
    'JSONB snapshot of planning requirements (plot dims, facing, floors, room counts) used to generate this plan. Used for fallback matching.';
