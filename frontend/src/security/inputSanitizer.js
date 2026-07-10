const inputSanitizer = {

    sanitizeText(input) {

        return input
            .replace(/</g, "")
            .replace(/>/g, "")
            .trim();

    },

    validateEmail(email) {

        return email.includes("@");

    },

    validatePhone(phone) {

        return phone.length >= 10;

    },

    preventSQLInjection(input) {

        return input.replace(/['";]/g, "");

    }

};

export default inputSanitizer;