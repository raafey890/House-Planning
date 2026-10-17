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
      if (error || !session) {
        // Fallback to local stored session (demo, mock, or offline mode)
        try {
          const stored = localStorage.getItem('app_auth_session') || localStorage.getItem('sb-cptjtxjqsyuwrwstcehu-auth-token');
          if (stored) {
            const parsed = JSON.parse(stored);
            if (parsed && (parsed.user || parsed.access_token)) {
              const u = parsed.user || { id: parsed.user_id || 'demo-user', email: 'demo@example.com' };
              set({ session: parsed, user: u, loading: false, initialized: true });
              return;
            }
          }
        } catch (_) {}
        set({ error: error?.message || null, session: null, user: null, loading: false, initialized: true });
        return;
      }
      set({ session, user: session?.user || null, loading: false, initialized: true });
      if (session?.user) {
        get().fetchProfile(session.user.id);
      }
    });

    supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        set({ session, user: session?.user || null });
        get().fetchProfile(session.user.id);
      } else {
        const fallback = localStorage.getItem('app_auth_session');
        if (fallback) {
          try {
            const parsed = JSON.parse(fallback);
            if (parsed && (parsed.user || parsed.access_token)) {
              return;
            }
          } catch (_) {}
        }
        set({ session: null, user: null, profile: null });
      }
    });
  },

  signUp: async (email, password, fullName) => {
    set({ loading: true, error: null });
    if (supabase.supabaseUrl === 'https://invalid-config.supabase.co') {
      const msg = 'Supabase is not configured. Please add VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY to frontend/.env.local';
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
      const msg = 'Supabase is not configured. Please add VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY to frontend/.env.local';
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

  resendConfirmation: async (email) => {
    if (!email) return { error: new Error('Please enter your email address.') };
    const { data, error } = await supabase.auth.resend({
      type: 'signup',
      email,
    });
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

if (typeof window !== 'undefined') {
  window.useAuthStore = useAuthStore;
}

export default useAuthStore;