const apiSecurity = {

    validateAPIKey(apiKey) {

        if(!apiKey) {

            return false;

        }

        return true;

    },

    secureHeaders() {

        return {

            "X-Frame-Options": "DENY",

            "X-Content-Type-Options":
            "nosniff"

        };

    },

    blockSuspiciousRequest(request) {

        console.log(
            "Checking Suspicious Activity"
        );

        return false;

    }

};

export default apiSecurity;