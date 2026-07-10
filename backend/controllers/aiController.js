const {
    generateAIResponse,
} = require("../services/openaiService");


// GENERATE AI FLOOR PLAN
const generateFloorPlan = async (req, res) => {

    try {

        const {
            bedrooms,
            bathrooms,
            floors,
            budget,
            plotSize,
            designStyle,
        } = req.body;


        // VALIDATION
        if (
            !bedrooms ||
            !bathrooms ||
            !floors ||
            !budget
        ) {

            return res.status(400).json({

                success: false,

                message:
                    "Please Fill All Required Fields",

            });

        }


        // AI SERVICE RESPONSE
        const aiResult = await generateAIResponse(
            req.body
        );


        res.status(200).json({

            success: true,

            message:
                "AI Floor Plan Generated Successfully",

            data: aiResult,

        });

    } catch (error) {

        res.status(500).json({

            success: false,

            message: error.message,

        });

    }

};


module.exports = {
    generateFloorPlan,
};