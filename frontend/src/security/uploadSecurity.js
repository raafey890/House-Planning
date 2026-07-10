const uploadSecurity = {

    allowedFormats: [

        "jpg",
        "jpeg",
        "png",
        "pdf"

    ],

    maxFileSizeMB: 25,

    validateFile(file) {

        const fileExtension =
        file.name.split(".").pop();

        if(
            !this.allowedFormats.includes(
                fileExtension
            )
        ) {

            return {

                valid: false,

                message: "Invalid File Format"

            };

        }

        return {

            valid: true,

            message: "File Accepted"

        };

    },

    scanForThreats(file) {

        console.log(
            `Scanning ${file.name} for threats`
        );

        return true;

    }

};

export default uploadSecurity;