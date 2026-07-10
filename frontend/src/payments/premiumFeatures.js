const premiumFeatures = {

    enabledFeatures: [

        "HD Export",
        "Unlimited AI Generation",
        "3D Walkthrough",
        "Cloud Sync"

    ],

    isPremiumUser(user) {

        return user?.premium === true;

    },

    accessFeature(user, featureName) {

        if(
            this.isPremiumUser(user)
        ) {

            return true;

        }

        console.log(
            `${featureName} requires Premium`
        );

        return false;

    }

};

export default premiumFeatures;