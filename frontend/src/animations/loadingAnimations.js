const loadingAnimations = {

    loadingStates: {

        aiGeneration: false,

        imageUpload: false,

        floorPlanLoading: false

    },

    startLoading(type) {

        this.loadingStates[type] = true;

        console.log(`${type} loading started`);

    },

    stopLoading(type) {

        this.loadingStates[type] = false;

        console.log(`${type} loading stopped`);

    },

    getLoadingStatus(type) {

        return this.loadingStates[type];

    },

    showSkeletonLoader() {

        console.log("Displaying Skeleton Loader");

    },

    showProgressBar(progress) {

        console.log(`Progress: ${progress}%`);

    }

};

export default loadingAnimations;