/**
 * Cost Estimation Service — Phase 6D.
 * Connects frontend React components to FastAPI cost estimation endpoints and Supabase.
 */

import { useAuthStore } from '../store';
import { supabase } from '../lib/supabase';

const API_BASE_URL = import.meta.env.VITE_AI_API_BASE_URL || 'http://127.0.0.1:8001/api/v1';

export const costEstimationService = {
    /**
     * Generates a new cost estimate from the layout or floor_plan_id.
     */
    async generateEstimate(projectId, floorPlanId = null, layoutData = null, customRates = null, customSpecs = null) {
        const token = useAuthStore.getState().session?.access_token;
        if (!token) {
            throw new Error("Authentication required");
        }

        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/cost-estimate/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                floor_plan_id: floorPlanId,
                layout_data: layoutData,
                custom_rates: customRates,
                custom_specifications: customSpecs
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || data.message || "Failed to generate cost estimate");
        }
        return data;
    },

    /**
     * Fetches the latest saved estimate for the project.
     */
    async getLatestEstimate(projectId) {
        const token = useAuthStore.getState().session?.access_token;
        if (!token) {
            throw new Error("Authentication required");
        }

        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/cost-estimate`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || data.message || "Failed to fetch cost estimate");
        }
        return data;
    },

    /**
     * Recalculates an estimate with updated rates without re-running the layout engine.
     */
    async recalculateEstimate(projectId, estimateId, customRates, layoutData = null, floorPlanId = null, customSpecs = null) {
        const token = useAuthStore.getState().session?.access_token;
        if (!token) {
            throw new Error("Authentication required");
        }

        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/cost-estimate/recalculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                current_estimate_id: estimateId,
                floor_plan_id: floorPlanId,
                layout_data: layoutData,
                custom_rates: customRates,
                custom_specifications: customSpecs
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || data.message || "Failed to recalculate cost estimate");
        }
        return data;
    },

    /**
     * Fetches the baseline regional benchmark rates profile.
     */
    async getBenchmarkRates(projectId) {
        const token = useAuthStore.getState().session?.access_token;
        if (!token) {
            throw new Error("Authentication required");
        }

        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/cost-estimate/rates`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || data.message || "Failed to fetch benchmark rates");
        }
        return data;
    },

    /**
     * Downloads CSV export of the estimate.
     */
    async downloadCsv(projectId) {
        const token = useAuthStore.getState().session?.access_token;
        if (!token) {
            throw new Error("Authentication required");
        }

        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/cost-estimate/export-csv`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error("Failed to export CSV");
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cost_estimate_${projectId.slice(0, 8)}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    }
};
