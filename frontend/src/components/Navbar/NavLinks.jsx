import { Link } from "react-router-dom";

function NavLinks() {
    return (
        <ul className="nav-links">
            <li><Link to="/">Home</Link></li>
            <li><a href="/#how-it-works">How It Works</a></li>
            <li><Link to="/gallery">Gallery</Link></li>
            <li><Link to="/pricing">Pricing</Link></li>
        </ul>
    );
}

export default NavLinks;