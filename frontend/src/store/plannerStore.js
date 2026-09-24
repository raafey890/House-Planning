import { create } from 'zustand';
import { supabase } from '../lib/supabase';
import useAuthStore from './authStore';
import useProjectStore from './projectStore';

const usePlannerStore = create((set, get) => ({
  // Core Identifiers
  projectId: null,
  projectName: '',

  // Step 1: Plot Details
  plotWidth: 30,
  plotLength: 40,
  facing: 'East',
  floors: 1,
  location: '',
  budget: '',

  // Step 2: Room Requirements (Core)
  bedrooms: 3,
  bathrooms: 2,
  kitchens: 1,
  livingRooms: 1,

  // Step 2: Room Requirements (Additional)
  diningRooms: 0,
  parkingSpaces: 0,
  balconies: 0,
  poojaRoom: false,
  studyRoom: false,
  homeOffice: false, // maps to study_room usually, or new field? Let's map to studyRoom or add it
  utilityRoom: false,
  storeRoom: false, // new
  guestRoom: false, // new

  // Step 3: Design Preferences
  architectureStyle: 'Modern',
  interiorStyle: 'Minimal',
  priorities: [],
  specialRequirements: '',

  // UI State
  loading: false,
  error: null,
  saveSuccess: false,

  setField: (field, value) => {
    set({ [field]: value, saveSuccess: false });
  },

  togglePriority: (priority) => {
    const { priorities } = get();
    if (priorities.includes(priority)) {
      set({ priorities: priorities.filter(p => p !== priority), saveSuccess: false });
    } else {
      set({ priorities: [...priorities, priority], saveSuccess: false });
    }
  },

  loadProjectSettings: (projectData) => {
    if (!projectData) return;
    const reqs = projectData.project_requirements?.[0] || {};
    
    set({
      projectId: projectData.id,
      projectName: projectData.name || '',
      plotLength: projectData.plot_length || 30,
      plotWidth: projectData.plot_width || 40,
      facing: projectData.facing || 'East',
      floors: projectData.floors || 1,
      location: projectData.location || '',
      budget: projectData.budget || '',
      architectureStyle: projectData.design_style || 'Modern',
      interiorStyle: projectData.interior_style || 'Minimal',
      priorities: projectData.priorities || [],
      
      bedrooms: reqs.bedrooms ?? 3,
      bathrooms: reqs.bathrooms ?? 2,
      kitchens: reqs.kitchens ?? 1,
      livingRooms: reqs.living_rooms ?? 1,
      diningRooms: reqs.dining_rooms ?? 0,
      parkingSpaces: reqs.parking_spaces ?? 0,
      balconies: reqs.balconies ?? 0,
      poojaRoom: reqs.pooja_room ?? false,
      studyRoom: reqs.study_room ?? false,
      utilityRoom: reqs.utility_room ?? false,
      guestRoom: reqs.guest_room ?? false,
      specialRequirements: reqs.custom_notes || '',
      saveSuccess: false
    });
  },

  clearPlanner: () => {
    set({
      projectId: null,
      projectName: '',
      plotWidth: 30,
      plotLength: 40,
      facing: 'East',
      floors: 1,
      location: '',
      budget: '',
      bedrooms: 3,
      bathrooms: 2,
      kitchens: 1,
      livingRooms: 1,
      diningRooms: 0,
      parkingSpaces: 0,
      balconies: 0,
      poojaRoom: false,
      studyRoom: false,
      homeOffice: false,
      utilityRoom: false,
      storeRoom: false,
      guestRoom: false,
      architectureStyle: 'Modern',
      interiorStyle: 'Minimal',
      priorities: [],
      specialRequirements: '',
      loading: false,
      error: null,
      saveSuccess: false
    });
  },

  saveToDatabase: async () => {
    const user = useAuthStore.getState().user;
    if (!user) return { error: new Error('User not authenticated') };

    const state = get();
    set({ loading: true, error: null, saveSuccess: false });

    const projectPayload = {
      user_id: user.id,
      name: state.projectName || 'My Dream Home',
      location: state.location,
      plot_length: state.plotLength,
      plot_width: state.plotWidth,
      facing: state.facing,
      floors: state.floors,
      budget: state.budget ? Number(state.budget) : null,
      design_style: state.architectureStyle,
      interior_style: state.interiorStyle,
      priorities: state.priorities,
    };

    let pId = state.projectId;

    if (pId) {
      // Update
      const { error: projError } = await supabase
        .from('projects')
        .update(projectPayload)
        .eq('id', pId)
        .eq('user_id', user.id);

      if (projError) {
        set({ error: projError.message, loading: false });
        return { error: projError };
      }
    } else {
      // Create new
      const { data, error: createError } = await supabase
        .from('projects')
        .insert([projectPayload])
        .select()
        .single();
      
      if (createError) {
        set({ error: createError.message, loading: false });
        return { error: createError };
      }
      pId = data.id;
      set({ projectId: pId });
    }

    // Upsert Project Requirements
    const reqsPayload = {
      project_id: pId,
      user_id: user.id,
      bedrooms: state.bedrooms,
      bathrooms: state.bathrooms,
      kitchens: state.kitchens,
      living_rooms: state.livingRooms,
      dining_rooms: state.diningRooms,
      parking_spaces: state.parkingSpaces,
      balconies: state.balconies,
      pooja_room: state.poojaRoom,
      study_room: state.studyRoom || state.homeOffice,
      utility_room: state.utilityRoom || state.storeRoom,
      guest_room: state.guestRoom,
      custom_notes: state.specialRequirements
    };

    const { error: reqError } = await supabase
      .from('project_requirements')
      .upsert(reqsPayload, { onConflict: 'project_id' });

    if (reqError) {
      set({ error: reqError.message, loading: false });
      return { error: reqError };
    }

    // Refresh current project in ProjectStore to keep synced
    useProjectStore.getState().fetchProjects();
    if (useProjectStore.getState().currentProject?.id === pId) {
      useProjectStore.getState().fetchProject(pId);
    }

    set({ loading: false, saveSuccess: true });
    return { data: { id: pId }, error: null };
  }
}));

export default usePlannerStore;