import { useAuthStore } from '../store';
import { supabase } from '../lib/supabase';

const API_BASE_URL = import.meta.env.VITE_AI_API_BASE_URL || 'http://127.0.0.1:8001/api/v1';

/**
 * Custom error class for generation failures.
 * Contains structured fields from the backend.
 */
class GenerationError extends Error {
    constructor(message, { code = 'UNKNOWN', retryable = false, generationId = null } = {}) {
        super(message);
        this.name = 'GenerationError';
        this.code = code;
        this.retryable = retryable;
        this.generationId = generationId;
    }
}

export const aiService = {
    /**
     * Calls the FastAPI backend to generate a new floor plan.
     * Returns { generation_id, status, floor_plan_id, layout_data, validation, message }
     *
     * status can be:
     *   "completed"       — fresh AI plan generated successfully
     *   "fallback_saved"  — AI failed, returning most recent saved plan
     *   "failed"          — all attempts failed, no saved plan available
     */
    async generateFloorPlan(projectId, optimizationPriority = "balanced") {
        const token = useAuthStore.getState().session?.access_token;
        if (!token) {
            throw new GenerationError("Authentication required", { code: 'AUTH_REQUIRED', retryable: false });
        }

        let response;
        try {
            response = await fetch(`${API_BASE_URL}/projects/${projectId}/floor-plans/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ optimization_priority: optimizationPriority })
            });
        } catch (networkErr) {
            // Network-level failure (backend down, DNS, CORS, etc.)
            throw new GenerationError(
                "Could not reach the AI server. Please check your connection and try again.",
                { code: 'NETWORK_ERROR', retryable: true }
            );
        }

        const data = await response.json();

        if (!response.ok) {
            // Backend returned a structured error (Phase 6C.3 / 6M.1 format)
            if (data.code) {
                const errorMsg = data.message || "Floor plan generation couldn't complete right now.";
                const suggestionsText = data.suggestions && data.suggestions.length > 0
                    ? ` Suggestions: ${data.suggestions.join(", ")}`
                    : "";
                throw new GenerationError(
                    `${errorMsg}${suggestionsText}`,
                    {
                        code: data.code,
                        retryable: data.retryable ?? true,
                        generationId: data.generation_id || null
                    }
                );
            }
            // Detail format fallback (including FastAPI Pydantic 422 errors)
            let detailMsg = "Generation couldn't complete right now. Please retry.";
            if (typeof data.detail === 'string') {
                detailMsg = data.detail;
            } else if (Array.isArray(data.detail)) {
                detailMsg = data.detail.map(d => d.msg || JSON.stringify(d)).join("; ");
            } else if (data.detail && typeof data.detail === 'object') {
                detailMsg = JSON.stringify(data.detail);
            }

            throw new GenerationError(
                detailMsg,
                { code: 'VALIDATION_ERROR', retryable: false }
            );
        }

        // Check for validation failures in a successful response
        if (data.status === "failed") {
            const errors = data.validation?.errors?.join(" | ") || "AI generation failed";
            throw new GenerationError(errors, { code: 'VALIDATION_FAILED', retryable: true });
        }

        return data;
    },

    /**
     * Fetches all saved floor plans for a project from Supabase.
     * Returns array of { id, version_name, layout_data, created_at, is_selected }
     * ordered newest first.
     */
    async getFloorPlans(projectId) {
        const { data, error } = await supabase
            .from('floor_plans')
            .select('id, version_name, layout_data, created_at, is_selected')
            .eq('project_id', projectId)
            .order('created_at', { ascending: false });

        if (error) {
            throw new Error(error.message || 'Failed to fetch floor plans');
        }

        return data || [];
    }
};

export { GenerationError };