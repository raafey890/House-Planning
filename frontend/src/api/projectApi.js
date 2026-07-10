import apiClient from "./apiClient";

export const createProject = async (data) => {
    const response = await apiClient.post(
        "/projects",
        data
    );

    return response.data;
};

export const getProjects = async () => {
    const response = await apiClient.get(
        "/projects"
    );

    return response.data;
};