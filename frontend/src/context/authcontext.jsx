const AuthContext = {

    isLoggedIn: false,

    user: null,

    loading: false,

    error: null,

    login(userData) {

        this.isLoggedIn = true;

        this.user = userData;

        console.log("User Logged In");

    },

    logout() {

        this.isLoggedIn = false;

        this.user = null;

        console.log("User Logged Out");

    },

    setLoading(status) {

        this.loading = status;

    },

    setError(message) {

        this.error = message;

    }

};

export default AuthContext;