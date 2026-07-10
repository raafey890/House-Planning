import "./Navbar.css";

import NavLinks from "./NavLinks";
import MobileMenu from "./MobileMenu";
import UserMenu from "./UserMenu";

function Navbar() {

    return (

        <header className="navbar">

            <div className="navbar-logo">

                <h2>
                    AI House Planner
                </h2>

            </div>

            <nav className="navbar-links">

                <NavLinks />

            </nav>

            <div className="navbar-actions">

                <UserMenu />

                <MobileMenu />

            </div>

        </header>

    );

}

export default Navbar;