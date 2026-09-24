import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey || supabaseUrl.includes('your-project-id')) {
  console.error(
    "Missing or invalid Supabase environment variables!\n\n" +
    "Please create a `.env` file in the `frontend` folder with:\n" +
    "VITE_SUPABASE_URL=your_project_url\n" +
    "VITE_SUPABASE_ANON_KEY=your_anon_key\n\n" +
    "You can find these in your Supabase Dashboard -> Project Settings -> API."
  );
}

// Fallback to prevent immediate crash, but will fail with a clear message on use if invalid
export const supabase = createClient(
  supabaseUrl && !supabaseUrl.includes('your-project-id') ? supabaseUrl : 'https://invalid-config.supabase.co',
  supabaseAnonKey && !supabaseAnonKey.includes('your-anon-key') ? supabaseAnonKey : 'invalid-key'
);
