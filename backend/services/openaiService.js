const axios = require("axios");


// GENERATE AI FLOOR PLAN RESPONSE
const generateAIResponse = async (userData) => {

    try {

        const {
            bedrooms,
            bathrooms,
            floors,
            budget,
            plotSize,
            designStyle,
        } = userData;


        // MOCK AI RESPONSE
        // LATER WE CONNECT REAL OPENAI API

        const aiResult = {

            projectSummary: {
                bedrooms,
                bathrooms,
                floors,
                plotSize,
                designStyle,
                budget,
            },

            recommendedRooms: [

                {
                    room: "Living Room",
                    size: "18x20",
                },

                {
                    room: "Master Bedroom",
                    size: "14x16",
                },

                {
                    room: "Kitchen",
                    size: "12x14",
                },

                {
                    room: "Dining Area",
                    size: "10x12",
                },

            ],

            aiSuggestions: [

                "Use natural lighting for energy efficiency",

                "Modern open kitchen recommended",

                "Add balcony for ventilation",

                "Use premium tiles for luxury appearance",

            ],

            estimatedConstructionTime:
                "8-12 Months",

            estimatedCostAnalysis:
                `Approximate budget utilization around ₹${budget}`,

            sustainabilityScore: "85/100",

        };


        return aiResult;

    } catch (error) {

        throw new Error(error.message);

    }

};


module.exports = {
    generateAIResponse,
};