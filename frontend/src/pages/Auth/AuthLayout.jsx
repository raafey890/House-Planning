import React from "react";

import "../../styles/pages/auth.css";

const AuthLayout = ({ children }) => {

    return (

        <div className="auth-layout">

            <div className="auth-left">

                <h1>
                    AI House Planner
                </h1>

                <p>
                    Design futuristic homes,
                    estimate construction costs,
                    and generate AI architecture
                    concepts professionally.
                </p>

            </div>

            <div className="auth-right">

                {children}

            </div>

        </div>

    );

};

export default AuthLayout;