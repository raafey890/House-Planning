async function geminiService(prompt) {

    console.log("Connecting To Gemini AI...");

    console.log("Prompt Sent:");

    console.log(prompt);

    const response = {

        status: "success",

        message: "Gemini AI Generated Designs",

        images: [

            "generated_house_001.jpg",
            "generated_house_002.jpg",
            "generated_house_003.jpg"

        ]

    };

    return response;
}

export default geminiService;