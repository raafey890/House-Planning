import React from "react";

const favorites = [

    "Luxury Villa",
    "Modern Duplex",
    "Minimal Interior"

];

const FavoriteDesigns = () => {

    return (

        <div className="favorite-designs">

            <h2>Favorite Designs</h2>

            <div className="favorite-grid">

                {
                    favorites.map((item, index) => (

                        <div
                            className="favorite-card"
                            key={index}
                        >

                            ❤️ {item}

                        </div>

                    ))
                }

            </div>

        </div>

    );

};

export default FavoriteDesigns;