const threeDAnimations = {

    rotateModel(modelId) {

        console.log(
            `Rotating 3D Model ${modelId}`
        );

    },

    zoomModel(level) {

        console.log(
            `Zoom Level: ${level}`
        );

    },

    changeLighting(mode) {

        console.log(
            `Lighting Changed To ${mode}`
        );

    },

    startWalkthrough() {

        console.log(
            "3D Walkthrough Started"
        );

    }

};

export default threeDAnimations;