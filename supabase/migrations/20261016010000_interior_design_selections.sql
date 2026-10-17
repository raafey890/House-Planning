-- ============================================================================
-- MIGRATION: 20261016010000_interior_design_selections.sql
-- DESCRIPTION: Table and RLS policies for Phase 6E.1 Interactive Interior Design Studio.
--              Stores user design selections, material upgrade choices,
--              false ceiling and lighting selections, and cost breakdowns per room.
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.project_interior_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    room_id TEXT NOT NULL,
    room_type TEXT NOT NULL,
    room_name TEXT,
    room_area_sqft NUMERIC(10,2) DEFAULT 0,
    design_id TEXT NOT NULL,
    design_name TEXT,
    wall_finish_choice TEXT,
    flooring_choice TEXT,
    ceiling_option_id TEXT,
    lighting_points_count INTEGER DEFAULT 0,
    customizations JSONB DEFAULT '{}'::jsonb,
    additional_cost NUMERIC(12,2) DEFAULT 0,
    cost_breakdown JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_project_room UNIQUE (project_id, room_id)
);

CREATE INDEX IF NOT EXISTS idx_interior_selections_project ON public.project_interior_selections(project_id);

ALTER TABLE public.project_interior_selections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own project interior selections" ON public.project_interior_selections
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.projects
            WHERE public.projects.id = public.project_interior_selections.project_id
            AND public.projects.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.projects
            WHERE public.projects.id = public.project_interior_selections.project_id
            AND public.projects.user_id = auth.uid()
        )
    );

COMMENT ON TABLE public.project_interior_selections IS 'Stores room-specific interior design selections, finish upgrades, and computed costs for Phase 6E.1';
COMMENT ON COLUMN public.project_interior_selections.design_id IS 'Unique catalog identifier from the 32 distinct interior designs (e.g., int_lr_01, int_kit_02)';
COMMENT ON COLUMN public.project_interior_selections.additional_cost IS 'Incremental interior cost over baseline civil finishes (INR)';
