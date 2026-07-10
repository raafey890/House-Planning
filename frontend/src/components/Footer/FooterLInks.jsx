import { Link } from "react-router-dom";

function FooterLinks() {

    return (

        <div className="footer-links">

            <div className="footer-column">

                <h4>
                    Company
                </h4>

                <Link to="/">
                    Home
                </Link>

                <Link to="/dashboard">
                    Dashboard
                </Link>

                <Link to="/premium">
                    Premium
                </Link>

            </div>

            <div className="footer-column">

                <h4>
                    Services
                </h4>

                <Link to="/planner">
                    Planner
                </Link>

                <Link to="/gallery">
                    Gallery
                </Link>

                <Link to="/estimator">
                    Estimator
                </Link>

            </div>

        </div>

    );

}

export default FooterLinks;