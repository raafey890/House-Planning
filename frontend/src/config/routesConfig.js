const routesConfig = {

    home: "/",

    planner: "/planner",

    gallery: "/gallery",

    estimator: "/estimator",

    floorplan: "/floorplan",

    viewer3D: "/viewer3d",

    login: "/login",

    signup: "/signup",

    dashboard: "/dashboard",

    premium: "/premium",

    settings: "/settings",

    profile: "/profile",

    admin: "/admin",

    notFound: "/404",

    getRoute(pageName) {

        return this[pageName];

    }

};

export default routesConfig;