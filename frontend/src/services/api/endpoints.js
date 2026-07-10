const endpoints = {

    auth: {

        login: "/auth/login",

        signup: "/auth/signup",

        profile: "/auth/profile"

    },

    planner: {

        generatePlan: "/planner/generate",

        savePlan: "/planner/save"

    },

    ai: {

        generateDesign: "/ai/design",

        generateInterior: "/ai/interior"

    },

    payment: {

        createOrder: "/payment/create-order"

    }

};

export default endpoints;