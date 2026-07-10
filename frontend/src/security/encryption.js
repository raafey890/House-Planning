const encryption = {

    encryptData(data) {

        console.log("Encrypting Data");

        return btoa(JSON.stringify(data));

    },

    decryptData(encryptedData) {

        console.log("Decrypting Data");

        return JSON.parse(
            atob(encryptedData)
        );

    },

    generateToken() {

        return Math.random()
            .toString(36)
            .substring(2);

    },

    hashPassword(password) {

        return btoa(password);

    }

};

export default encryption;