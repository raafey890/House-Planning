function useAuth() {

    const login = () => {

        console.log("User Logged In");

    };

    const logout = () => {

        console.log("User Logged Out");

    };

    return {

        login,
        logout

    };
}

export default useAuth;