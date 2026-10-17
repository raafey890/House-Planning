/**
 * Interior Design Service — Phase 6E.1.
 * Connects frontend components to FastAPI interior design catalog,
 * calculation endpoints, and Supabase project selections persistence.
 */

import { useAuthStore } from '../store';

const API_BASE_URL = import.meta.env.VITE_AI_API_BASE_URL || 'http://127.0.0.1:8001/api/v1';

export const interiorDesignService = {
    /**
     * Retrieves the 32 distinct interior design options from catalog,
     * with optional category, room_type, budget_tier, and style filters.
     */
    async getCatalog(filters = {}) {
        const params = new URLSearchParams();
        if (filters.category && filters.category !== 'all') params.append('category', filters.category);
        if (filters.room_type) params.append('room_type', filters.room_type);
        if (filters.budget_tier && filters.budget_tier !== 'all') params.append('budget_tier', filters.budget_tier);
        if (filters.style && filters.style !== 'all') params.append('style', filters.style);

        const url = `${API_BASE_URL}/interior/catalog${params.toString() ? `?${params.toString()}` : ''}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch interior design catalog');
        }
        return await response.json();
    },

    /**
     * Retrieves a single interior design option by ID.
     */
    async getDesignById(designId) {
        const response = await fetch(`${API_BASE_URL}/interior/catalog/${designId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch design '${designId}'`);
        }
        return await response.json();
    },

    /**
     * Validates compatibility of a design with specific room dimensions.
     */
    async validateCompatibility(designId, roomType, roomWidth = 0, roomLength = 0, roomArea = 0) {
        const response = await fetch(`${API_BASE_URL}/interior/validate-compatibility`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                design_id: designId,
                room_type: roomType,
                room_width: roomWidth,
                room_length: roomLength,
                room_area: roomArea
            })
        });
        if (!response.ok) {
            throw new Error('Compatibility check failed');
        }
        return await response.json();
    },

    /**
     * Requests a personalized, geometry-grounded 2D architectural room preview.
     */
    async generatePersonalizedPreview(params) {
        const response = await fetch(`${API_BASE_URL}/interior/generate-preview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        if (!response.ok) {
            throw new Error('Failed to generate personalized room preview');
        }
        return await response.json();
    },

    /**
     * Calculates costs for a batch of room selections using exact room geometry.
     */
    async calculateCosts(projectId, selections, layoutData = null, floorPlanId = null) {
        const response = await fetch(`${API_BASE_URL}/interior/calculate-cost`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project_id: projectId,
                floor_plan_id: floorPlanId,
                layout_data: layoutData,
                selections: selections
            })
        });
        if (!response.ok) {
            throw new Error('Failed to calculate interior costs');
        }
        return await response.json();
    },

    /**
     * Fetches saved project interior selections.
     */
    async getProjectSelections(projectId) {
        // First check local storage for instantaneous load
        const cached = localStorage.getItem(`interior_selections_${projectId}`);
        let initialData = null;
        if (cached) {
            try { initialData = JSON.parse(cached); } catch (_) {}
        }

        const token = useAuthStore.getState().session?.access_token;
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/interior-selections`, {
                headers
            });
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem(`interior_selections_${projectId}`, JSON.stringify(data));
                return data;
            }
        } catch (e) {
            console.warn('[interiorDesignService] Network request failed, using cache:', e);
        }

        return initialData || { selections: {}, total_interior_cost: 0 };
    },

    /**
     * Saves/updates room interior selections for a project.
     */
    async saveProjectSelections(projectId, payload) {
        // Cache locally first for reliability
        localStorage.setItem(`interior_selections_${projectId}`, JSON.stringify(payload));

        const token = useAuthStore.getState().session?.access_token;
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/interior-selections`, {
                method: 'POST',
                headers,
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                return await response.json();
            }
        } catch (e) {
            console.warn('[interiorDesignService] Network error saving to backend, saved locally:', e);
        }

        return payload;
    },

    /**
     * Deletes a room selection from a project.
     */
    async deleteRoomSelection(projectId, roomId) {
        const cached = localStorage.getItem(`interior_selections_${projectId}`);
        if (cached) {
            try {
                const data = JSON.parse(cached);
                if (data.selections && data.selections[roomId]) {
                    delete data.selections[roomId];
                    localStorage.setItem(`interior_selections_${projectId}`, JSON.stringify(data));
                }
            } catch (_) {}
        }

        const token = useAuthStore.getState().session?.access_token;
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}/interior-selections/${roomId}`, {
                method: 'DELETE',
                headers
            });
            if (response.ok) {
                return await response.json();
            }
        } catch (e) {
            console.warn('[interiorDesignService] Network delete failed, removed locally:', e);
        }

        return { success: true };
    }
};
