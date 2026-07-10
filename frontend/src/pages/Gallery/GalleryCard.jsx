import React from "react";

const GalleryCard = ({ image, title, type }) => {

    return (

        <div className="gallery-card">

            <img
                src={image}
                alt={title}
            />

            <div className="gallery-content">

                <h3>{title}</h3>

                <p>{type}</p>

                <button className="view-btn">

                    View Design

                </button>

            </div>

        </div>

    );

};

export default GalleryCard;