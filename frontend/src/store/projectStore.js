import { create } from 'zustand';
import { supabase } from '../lib/supabase';
import useAuthStore from './authStore';

const useProjectStore = create((set, get) => ({
  projects: [],
  currentProject: null,
  loading: false,
  error: null,

  fetchProjects: async () => {
    const user = useAuthStore.getState().user;
    if (!user) return { error: new Error('User not authenticated') };

    set({ loading: true, error: null });
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false });

    if (error) set({ error: error.message, loading: false });
    else set({ projects: data || [], loading: false });
    
    return { data, error };
  },

  fetchProject: async (id) => {
    set({ loading: true, error: null });
    const { data, error } = await supabase
      .from('projects')
      .select('*, project_requirements(*)')
      .eq('id', id)
      .single();

    if (error) set({ error: error.message, loading: false });
    else set({ currentProject: data, loading: false });

    return { data, error };
  },

  createProject: async (projectData) => {
    const user = useAuthStore.getState().user;
    if (!user) return { error: new Error('User not authenticated') };

    set({ loading: true, error: null });
    const { data, error } = await supabase
      .from('projects')
      .insert([{ ...projectData, user_id: user.id }])
      .select()
      .single();

    if (error) {
      set({ error: error.message, loading: false });
    } else {
      set((state) => ({ 
        projects: [data, ...state.projects],
        currentProject: data, 
        loading: false 
      }));
    }
    return { data, error };
  },

  updateProject: async (id, projectData) => {
    set({ loading: true, error: null });
    const { data, error } = await supabase
      .from('projects')
      .update(projectData)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      set({ error: error.message, loading: false });
    } else {
      set((state) => ({
        projects: state.projects.map((p) => p.id === id ? data : p),
        currentProject: state.currentProject?.id === id ? data : state.currentProject,
        loading: false
      }));
    }
    return { data, error };
  },

  deleteProject: async (id) => {
    set({ loading: true, error: null });
    const { error } = await supabase
      .from('projects')
      .delete()
      .eq('id', id);

    if (error) {
      set({ error: error.message, loading: false });
    } else {
      set((state) => ({
        projects: state.projects.filter((p) => p.id !== id),
        currentProject: state.currentProject?.id === id ? null : state.currentProject,
        loading: false
      }));
    }
    return { error };
  },

  clearCurrentProject: () => set({ currentProject: null })
}));

export default useProjectStore;
