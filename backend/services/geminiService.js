const axios = require("axios");

const generateGeminiResponse = async (prompt) => {
    try {
        return {
            success: true,
            message: "Gemini service placeholder",
            data: prompt
        };
    } catch (error) {
        throw new Error(error.message);
    }
};

module.exports = {
    generateGeminiResponse,
};