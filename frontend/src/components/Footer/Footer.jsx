import "./Footer.css";

import FooterLinks from "./FooterLinks";
import SocialLinks from "./SocialLinks";

function Footer() {

    return (

        <footer className="footer">

            <div className="footer-top">

                <div className="footer-brand">

                    <h2>
                        AI House Planner
                    </h2>

                    <p>
                        Build your dream home using AI-powered
                        planning, estimation, and visualization.
                    </p>

                </div>

                <FooterLinks />

            </div>

            <div className="footer-bottom">

                <SocialLinks />

                <p>
                    © 2026 AI House Planner. All rights reserved.
                </p>

            </div>

        </footer>

    );

}

export default Footer;