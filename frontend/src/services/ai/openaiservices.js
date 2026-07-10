async function openaiService(prompt) {

    console.log("Connecting To OpenAI...");

    console.log(prompt);

    const response = {

        status: "success",

        message: "OpenAI Generated Results"

    };

    return response;
}

export default openaiService;