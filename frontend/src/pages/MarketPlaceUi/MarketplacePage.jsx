import Contractors from "./Contractors.jsx";
import Architects from "./Architects.jsx";
import InteriorDesigners from "./InteriorDesigner.jsx";

function MarketplacePage() {

    return (

        <div className="marketplace-page">

            <h1>
                Marketplace
            </h1>

            <Contractors />

            <Architects />

            <InteriorDesigners />

        </div>

    );

}

export default MarketplacePage;