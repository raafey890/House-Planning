/**
 * Exterior Design Service — Phase 6F.1.
 * Connects frontend components to FastAPI exterior design catalog,
 * plan-aware compatibility evaluator, incremental cost derivation endpoints,
 * and Supabase / local persistence.
 */

import { useAuthStore } from '../store';

const API_BASE_URL = import.meta.env.VITE_AI_API_BASE_URL || 'http://127.0.0.1:8001/api/v1';

export const exteriorDesignService = {
  /**
   * Retrieves the 32 distinct exterior design options from the catalog,
   * with optional category, budget_tier, style, and house_type filters.
   */
  async getCatalog(filters = {}) {
    const params = new URLSearchParams();
    if (filters.category && filters.category !== 'all') params.append('category', filters.category);
    if (filters.budget_tier && filters.budget_tier !== 'all') params.append('budget_tier', filters.budget_tier);
    if (filters.style && filters.style !== 'all') params.append('style', filters.style);
    if (filters.house_type && filters.house_type !== 'all') params.append('house_type', filters.house_type);
    if (filters.search && filters.search.trim()) params.append('search', filters.search.trim());

    const url = `${API_BASE_URL}/exterior/catalog${params.toString() ? `?${params.toString()}` : ''}`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Failed to fetch exterior design catalog');
    }
    return await response.json();
  },

  /**
   * Retrieves a single exterior design option by ID.
   */
  async getDesignById(designId) {
    const response = await fetch(`${API_BASE_URL}/exterior/catalog/${designId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch exterior design '${designId}'`);
    }
    return await response.json();
  },

  /**
   * Validates compatibility of an exterior design with specific plot and floor geometry.
   */
  async validateCompatibility(params) {
    const response = await fetch(`${API_BASE_URL}/exterior/validate-compatibility`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!response.ok) {
      throw new Error('Compatibility check failed');
    }
    return await response.json();
  },

  /**
   * Calculates detailed cost breakdown based on perimeter, floor height, finishes, lighting, etc.
   */
  async calculateCost(params) {
    const response = await fetch(`${API_BASE_URL}/exterior/calculate-cost`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!response.ok) {
      throw new Error('Failed to calculate exterior costs');
    }
    return await response.json();
  },

  /**
   * Generates a personalized vector elevation preview (SVG) grounded in exact plot dimensions,
   * floor count, custom paint/materials, perspective angle, and day/night lighting.
   */
  async generatePersonalizedPreview(params) {
    const response = await fetch(`${API_BASE_URL}/exterior/generate-preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to generate exterior preview');
    }
    return await response.json();
  },

  /**
   * Generates a photorealistic AI exterior rendering via Gemini Imagen or returns transparent diagnostics.
   */
  async generateExteriorImage(params) {
    const response = await fetch(`${API_BASE_URL}/exterior/generate-image`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to generate exterior image');
    }
    return await response.json();
  },

  /**
   * Validates canonical exterior configuration against architectural and dimension bounds.
   */
  async validateCanonicalConfig(params) {
    const response = await fetch(`${API_BASE_URL}/exterior/validate-config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!response.ok) {
      throw new Error('Canonical config validation failed');
    }
    return await response.json();
  },

  /**
   * Fetches all 32 catalog designs evaluated in real-time against this specific project's
   * plot dimensions and floor count, with compatibility badges and clear architectural reasons.
   */
  async getProjectExteriorOptions(projectId) {
    const token = useAuthStore.getState().session?.access_token;
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/exterior-selections/options`, {
      headers
    });
    if (!response.ok) {
      throw new Error('Failed to fetch evaluated exterior options for project');
    }
    return await response.json();
  },

  /**
   * Fetches saved project exterior selection.
   */
  async getProjectSelection(projectId) {
    // Check local storage first for instantaneous load
    const cached = localStorage.getItem(`exterior_selection_${projectId}`);
    let initialData = null;
    if (cached) {
      try { initialData = JSON.parse(cached); } catch (_) {}
    }

    const token = useAuthStore.getState().session?.access_token;
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}/exterior-selections`, {
        headers
      });
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem(`exterior_selection_${projectId}`, JSON.stringify(data));
        return data;
      }
    } catch (e) {
      console.warn('[exteriorDesignService] Network request failed, using cache:', e);
    }

    return initialData || { project_id: projectId, selection: null, total_exterior_cost: 0 };
  },

  /**
   * Saves/updates exterior selection for a project.
   */
  async saveProjectSelection(projectId, payload) {
    // Cache locally first for reliability
    localStorage.setItem(`exterior_selection_${projectId}`, JSON.stringify(payload));

    const token = useAuthStore.getState().session?.access_token;
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}/exterior-selections`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload)
      });
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem(`exterior_selection_${projectId}`, JSON.stringify(data));
        return data;
      }
    } catch (e) {
      console.warn('[exteriorDesignService] Network error saving to backend, saved locally:', e);
    }

    return payload;
  },

  /**
   * Clears exterior selection for a project.
   */
  async deleteProjectSelection(projectId) {
    localStorage.removeItem(`exterior_selection_${projectId}`);

    const token = useAuthStore.getState().session?.access_token;
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}/exterior-selections`, {
        method: 'DELETE',
        headers
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (e) {
      console.warn('[exteriorDesignService] Network error deleting exterior selection:', e);
    }

    return { project_id: projectId, selection: null, total_exterior_cost: 0 };
  }
};
