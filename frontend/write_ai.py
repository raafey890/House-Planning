content = '''import { useAuthStore } from '../store';

const API_BASE_URL = import.meta.env.VITE_AI_API_BASE_URL || 'http://127.0.0.1:8001/api/v1';

export const aiService = {
    async generateFloorPlan(projectId, optimizationPriority = "balanced") {
        const token = useAuthStore.getState().session?.access_token;
        if (!token) {
            throw new Error("Authentication required");
        }

        const response = await fetch(${API_BASE_URL}/projects//floor-plans/generate, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': Bearer 
            },
            body: JSON.stringify({ optimization_priority: optimizationPriority })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || "Generation failed");
        }
        
        if (data.status === "failed") {
            const errors = data.validation?.errors?.join(" | ") || "AI Generation failed";
            throw new Error(errors);
        }
        
        return data;
    }
};'''

with open('src/services/aiService.js', 'w', encoding='utf-8') as f:
    f.write(content)
