const featureFlags = {

    enableVoiceInput: true,

    enable3DWalkthrough: true,

    enableARView: false,

    enablePremiumFeatures: false,

    enableMarketplace: true,

    enableLiveMaterialRates: true,

    enableOfflineMode: false,

    enableCloudSync: true,

    enableAIRegeneration: true,

    toggleFeature(featureName, status) {

        if(this.hasOwnProperty(featureName)) {

            this[featureName] = status;

        }

    }

};

export default featureFlags;