import { Link } from "react-router-dom";

function NavLinks() {

    return (

        <ul className="nav-links">

            <li>
                <Link to="/">
                    Home
                </Link>
            </li>

            <li>
                <Link to="/planner">
                    Planner
                </Link>
            </li>

            <li>
                <Link to="/gallery">
                    Gallery
                </Link>
            </li>

            <li>
                <Link to="/floorplan">
                    Floor Plan
                </Link>
            </li>

            <li>
                <Link to="/estimator">
                    Estimator
                </Link>
            </li>

            <li>
                <Link to="/dashboard">
                    Dashboard
                </Link>
            </li>

        </ul>

    );

}

export default NavLinks;