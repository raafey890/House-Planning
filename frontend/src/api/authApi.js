import apiClient from "./apiClient";

export const signupUser = async (userData) => {
    const response = await apiClient.post(
        "/auth/register",
        userData
    );

    return response.data;
};

export const loginUser = async (userData) => {
    const response = await apiClient.post(
        "/auth/login",
        userData
    );

    return response.data;
};