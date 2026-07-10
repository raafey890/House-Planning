const subscriptionPlans = {

    plans: [

        {
            id: 1,

            name: "Free",

            price: 0,

            features: [

                "5 AI Designs",
                "Basic Floorplans",
                "Low Quality Images"

            ]

        },

        {
            id: 2,

            name: "Premium",

            price: 999,

            features: [

                "Unlimited AI Designs",
                "HD Images",
                "3D Walkthrough",
                "Priority AI Generation",
                "Cloud Save"

            ]

        },

        {
            id: 3,

            name: "Enterprise",

            price: 4999,

            features: [

                "Team Collaboration",
                "Architect Support",
                "Marketplace Access",
                "Advanced Analytics"

            ]

        }

    ],

    getPlan(planName) {

        return this.plans.find(
            plan => plan.name === planName
        );

    }

};

export default subscriptionPlans;