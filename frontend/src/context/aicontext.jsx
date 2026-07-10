const AIContext = {

    generatedImages: [],

    selectedDesign: null,

    generationStatus: "idle",

    AIRecommendations: [],

    generationProgress: 0,

    lastPrompt: "",

    error: null,

    setPrompt(prompt) {

        this.lastPrompt = prompt;

    },

    setGenerationStatus(status) {

        this.generationStatus = status;

    },

    addGeneratedImage(image) {

        this.generatedImages.push(image);

    },

    setSelectedDesign(design) {

        this.selectedDesign = design;

    },

    addRecommendation(recommendation) {

        this.AIRecommendations.push(
            recommendation
        );

    },

    updateProgress(progress) {

        this.generationProgress = progress;

    },

    setError(errorMessage) {

        this.error = errorMessage;

    },

    resetAIData() {

        this.generatedImages = [];

        this.selectedDesign = null;

        this.generationStatus = "idle";

        this.AIRecommendations = [];

        this.generationProgress = 0;

        this.error = null;

    }

};

export default AIContext;