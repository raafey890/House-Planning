const storageConfig = {

    maxUploadSizeMB: 25,

    supportedImageFormats: [

        "jpg",
        "jpeg",
        "png",
        "webp"

    ],

    supportedDocumentFormats: [

        "pdf",
        "docx"

    ],

    cloudProvider: "Firebase",

    enableCompression: true,

    autoBackup: true,

    uploadPaths: {

        generatedImages: "/generated",

        userProjects: "/projects",

        floorPlans: "/floorplans"

    }

};

export default storageConfig;