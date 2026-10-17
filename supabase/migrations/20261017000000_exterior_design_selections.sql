-- ============================================================================
-- MIGRATION: 20261017000000_exterior_design_selections.sql
-- DESCRIPTION: Table and RLS policies for Phase 6F.1 Exterior Design Studio.
--              Stores user exterior design selections, color customization palettes,
--              materials, lighting, architectural elements, landscaping, and cost breakdowns.
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.project_exterior_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    design_id TEXT NOT NULL,
    design_name TEXT,
    category TEXT,
    style TEXT,
    colors JSONB DEFAULT '{}'::jsonb,
    materials JSONB DEFAULT '{}'::jsonb,
    architectural_elements JSONB DEFAULT '{}'::jsonb,
    lighting JSONB DEFAULT '{}'::jsonb,
    landscaping JSONB DEFAULT '{}'::jsonb,
    boundary_wall JSONB DEFAULT '{}'::jsonb,
    compatibility_status TEXT DEFAULT 'compatible',
    compatibility_notes JSONB DEFAULT '[]'::jsonb,
    additional_cost NUMERIC(12,2) DEFAULT 0,
    cost_breakdown JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_project_exterior UNIQUE (project_id)
);

CREATE INDEX IF NOT EXISTS idx_exterior_selections_project ON public.project_exterior_selections(project_id);

ALTER TABLE public.project_exterior_selections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own project exterior selections" ON public.project_exterior_selections
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.projects
            WHERE public.projects.id = public.project_exterior_selections.project_id
            AND public.projects.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.projects
            WHERE public.projects.id = public.project_exterior_selections.project_id
            AND public.projects.user_id = auth.uid()
        )
    );

COMMENT ON TABLE public.project_exterior_selections IS 'Stores project-level exterior design selections, facade finish upgrades, and computed costs for Phase 6F.1';
COMMENT ON COLUMN public.project_exterior_selections.design_id IS 'Unique catalog identifier from the 32 distinct exterior designs (e.g., ext_mod_01, ext_min_02)';
COMMENT ON COLUMN public.project_exterior_selections.additional_cost IS 'Incremental exterior elevation cost over standard civil finishes (INR)';
