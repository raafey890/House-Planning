function logoutService() {

    console.log("User Logged Out");

    return {

        status: "success",

        message: "Logout Successful"

    };
}

export default logoutService;