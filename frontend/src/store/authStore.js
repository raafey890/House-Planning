import { create } from 'zustand';
import { supabase } from '../lib/supabase';

const useAuthStore = create((set, get) => ({
  user: null,
  session: null,
  profile: null,
  loading: true,
  initialized: false,
  error: null,

  initializeAuth: () => {
    supabase.auth.getSession().then(({ data: { session }, error }) => {
      if (error) {
        set({ error: error.message, loading: false, initialized: true });
        return;
      }
      set({ session, user: session?.user || null, loading: false, initialized: true });
      if (session?.user) {
        get().fetchProfile(session.user.id);
      }
    });

    supabase.auth.onAuthStateChange((_event, session) => {
      set({ session, user: session?.user || null });
      if (session?.user) {
        get().fetchProfile(session.user.id);
      } else {
        set({ profile: null });
      }
    });
  },

  signUp: async (email, password, fullName) => {
    set({ loading: true, error: null });
    if (supabase.supabaseUrl === 'https://invalid-config.supabase.co') {
      const msg = 'Supabase is not configured. Please add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to frontend/.env';
      set({ error: msg, loading: false });
      return { error: new Error(msg) };
    }
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
        },
      },
    });
    if (error) set({ error: error.message, loading: false });
    else set({ loading: false });
    return { data, error };
  },

  signIn: async (email, password) => {
    set({ loading: true, error: null });
    if (supabase.supabaseUrl === 'https://invalid-config.supabase.co') {
      const msg = 'Supabase is not configured. Please add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to frontend/.env';
      set({ error: msg, loading: false });
      return { error: new Error(msg) };
    }
    
    let data, error;
    try {
      const res = await supabase.auth.signInWithPassword({ email, password });
      data = res.data;
      error = res.error;
    } catch (err) {
      error = err;
    }
    if (error) set({ error: error.message, loading: false });
    else set({ loading: false });
    return { data, error };
  },

  signOut: async () => {
    set({ loading: true, error: null });
    const { error } = await supabase.auth.signOut();
    if (error) set({ error: error.message, loading: false });
    else set({ user: null, session: null, profile: null, loading: false });
    return { error };
  },

  fetchProfile: async (userId) => {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .single();
    if (!error && data) {
      set({ profile: data });
    }
  },

  updateProfile: async (updates) => {
    const { user } = get();
    if (!user) return { error: new Error('No authenticated user') };

    set({ loading: true, error: null });
    const { data, error } = await supabase
      .from('profiles')
      .update(updates)
      .eq('id', user.id)
      .select()
      .single();

    if (error) {
      set({ error: error.message, loading: false });
    } else {
      set({ profile: data, loading: false });
    }
    return { data, error };
  },

  clearError: () => set({ error: null }),
}));

export default useAuthStore;