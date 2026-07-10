import apiClient from "./apiClient";

export const calculateEstimate = async (
    estimationData
) => {

    const response = await apiClient.post(
        "/estimation/calculate",
        estimationData
    );

    return response.data;
};