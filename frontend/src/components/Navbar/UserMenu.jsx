import { Link } from "react-router-dom";

function UserMenu() {

    return (

        <div className="user-menu">

            <Link to="/login">

                <button className="login-button">
                    Login
                </button>

            </Link>

            <Link to="/premium">

                <button className="premium-button">
                    Go Premium
                </button>

            </Link>

        </div>

    );

}

export default UserMenu;