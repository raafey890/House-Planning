import apiClient from "./apiClient";

export const generateFloorPlan = async (
    promptData
) => {

    const response = await apiClient.post(
        "/ai/floorplan",
        promptData
    );

    return response.data;
};