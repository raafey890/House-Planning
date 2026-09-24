-- 001_initial_schema.sql
-- Core Platform Schema for AI House Planning

-- Enable UUID extension if not present
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 1. PROFILES
-- ==========================================
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Trigger to automatically create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, avatar_url)
  VALUES (new.id, COALESCE(new.raw_user_meta_data->>'full_name', 'New User'), new.raw_user_meta_data->>'avatar_url');
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- ==========================================
-- 2. PROJECTS
-- ==========================================
CREATE TABLE public.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    project_type TEXT,
    location TEXT,
    plot_length NUMERIC,
    plot_width NUMERIC,
    total_area NUMERIC GENERATED ALWAYS AS (plot_length * plot_width) STORED,
    facing TEXT,
    floors INTEGER DEFAULT 1,
    budget NUMERIC,
    design_style TEXT DEFAULT 'Modern',
    status TEXT DEFAULT 'Draft',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_projects_user_id ON public.projects(user_id);

ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own projects" ON public.projects
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ==========================================
-- 3. PROJECT REQUIREMENTS
-- ==========================================
CREATE TABLE public.project_requirements (
    project_id UUID PRIMARY KEY REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    bedrooms INTEGER DEFAULT 1,
    bathrooms INTEGER DEFAULT 1,
    kitchens INTEGER DEFAULT 1,
    living_rooms INTEGER DEFAULT 1,
    dining_rooms INTEGER DEFAULT 0,
    parking_spaces INTEGER DEFAULT 0,
    balconies INTEGER DEFAULT 0,
    pooja_room BOOLEAN DEFAULT false,
    study_room BOOLEAN DEFAULT false,
    utility_room BOOLEAN DEFAULT false,
    custom_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.project_requirements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own project requirements" ON public.project_requirements
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ==========================================
-- 4. AI GENERATIONS
-- ==========================================
CREATE TABLE public.ai_generations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE SET NULL,
    generation_type TEXT NOT NULL,
    provider TEXT NOT NULL,
    model_used TEXT NOT NULL,
    prompt_payload JSONB NOT NULL,
    response_payload JSONB,
    status TEXT NOT NULL CHECK (status IN ('Processing', 'Completed', 'Failed')),
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.ai_generations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users read own generations" ON public.ai_generations
    FOR SELECT USING (auth.uid() = user_id);

-- ==========================================
-- 5. FLOOR PLANS
-- ==========================================
CREATE TABLE public.floor_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    version_name TEXT NOT NULL,
    layout_data JSONB NOT NULL,
    image_path TEXT,
    model_3d_path TEXT,
    is_selected BOOLEAN DEFAULT false,
    ai_generation_id UUID REFERENCES public.ai_generations(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.floor_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own floor plans" ON public.floor_plans
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ==========================================
-- 6. DESIGNS (Interior/Exterior)
-- ==========================================
CREATE TABLE public.designs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    design_type TEXT NOT NULL CHECK (design_type IN ('Interior', 'Exterior')),
    room_type TEXT,
    image_path TEXT NOT NULL,
    ai_generation_id UUID REFERENCES public.ai_generations(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.designs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own designs" ON public.designs
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ==========================================
-- 7. ESTIMATIONS
-- ==========================================
CREATE TABLE public.estimations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE UNIQUE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    material_cost NUMERIC NOT NULL DEFAULT 0,
    labor_cost NUMERIC NOT NULL DEFAULT 0,
    electrical_cost NUMERIC NOT NULL DEFAULT 0,
    plumbing_cost NUMERIC NOT NULL DEFAULT 0,
    interior_cost NUMERIC NOT NULL DEFAULT 0,
    exterior_cost NUMERIC NOT NULL DEFAULT 0,
    total_cost NUMERIC NOT NULL DEFAULT 0,
    estimated_duration_weeks INTEGER,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.estimations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own estimations" ON public.estimations
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ==========================================
-- 8. UTILITIES (Updated_at Trigger)
-- ==========================================
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON public.projects FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_project_reqs_updated_at BEFORE UPDATE ON public.project_requirements FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_floor_plans_updated_at BEFORE UPDATE ON public.floor_plans FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_estimations_updated_at BEFORE UPDATE ON public.estimations FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- ==========================================
-- 9. STORAGE SETUP
-- ==========================================
-- Note: Storage buckets and policies are typically inserted into storage.buckets and storage.objects
INSERT INTO storage.buckets (id, name, public) VALUES ('avatars', 'avatars', true) ON CONFLICT DO NOTHING;
INSERT INTO storage.buckets (id, name, public) VALUES ('project-assets', 'project-assets', false) ON CONFLICT DO NOTHING;

CREATE POLICY "Avatar images are publicly accessible" ON storage.objects
    FOR SELECT USING (bucket_id = 'avatars');

CREATE POLICY "Users can upload their own avatar" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'avatars' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can update their own avatar" ON storage.objects
    FOR UPDATE USING (bucket_id = 'avatars' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can manage own project assets" ON storage.objects
    FOR ALL USING (bucket_id = 'project-assets' AND auth.uid()::text = (storage.foldername(name))[1])
    WITH CHECK (bucket_id = 'project-assets' AND auth.uid()::text = (storage.foldername(name))[1]);
