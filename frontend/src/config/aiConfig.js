const aiConfig = {

    geminiAPIKey: "YOUR_GEMINI_API_KEY",

    openAIAPIKey: "YOUR_OPENAI_API_KEY",

    imageGenerationLimit: 36,

    supportedStyles: [

        "Modern",
        "Luxury",
        "Minimal",
        "Traditional",
        "Village"

    ],

    generationTimeout: 30000,

    retryAttempts: 2,

    enableSmartRecommendations: true,

    AIModels: {

        imageGeneration: "gemini-pro",

        textRecommendations: "gpt-4"

    }

};

export default aiConfig;