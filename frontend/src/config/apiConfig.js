const apiConfig = {

    baseURL: "https://api.houseplanner.com",

    timeout: 10000,

    retryAttempts: 3,

    endpoints: {

        generateDesign: "/ai/generate",

        uploadImage: "/storage/upload",

        login: "/auth/login",

        signup: "/auth/signup",

        materialRates: "/pricing/materials",

        saveProject: "/projects/save"

    },

    headers: {

        "Content-Type": "application/json"

    },

    getEndpoint(serviceName) {

        return this.baseURL + this.endpoints[serviceName];

    }

};

export default apiConfig;