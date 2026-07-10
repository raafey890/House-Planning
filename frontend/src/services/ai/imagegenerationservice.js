async function imageGenerationService(prompt) {

    console.log("Generating AI Images...");

    console.log(prompt);

    const generatedImages = [

        "generated_house_001.jpg",
        "generated_house_002.jpg",
        "generated_house_003.jpg",
        "generated_house_004.jpg"

    ];

    return generatedImages;
}

export default imageGenerationService;