const authMiddleware = {

    isAuthenticated(user) {

        if(user && user.token) {

            return true;

        }

        return false;

    },

    validateSession(session) {

        if(session.expired) {

            console.log("Session Expired");

            return false;

        }

        return true;

    },

    requireLogin(user) {

        if(!this.isAuthenticated(user)) {

            throw new Error(
                "Authentication Required"
            );

        }

    }

};

export default authMiddleware;