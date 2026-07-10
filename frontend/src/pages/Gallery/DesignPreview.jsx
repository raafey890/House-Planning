import React from "react";

const DesignPreview = () => {

    return (

        <div className="design-preview">

            <div className="preview-overlay">

                <div className="preview-modal">

                    <img
                        src="https://images.unsplash.com/photo-1600585154526-990dced4db0d"
                        alt="Preview"
                    />

                    <div className="preview-info">

                        <h2>
                            Modern Luxury Villa
                        </h2>

                        <p>
                            AI generated futuristic
                            architectural concept.
                        </p>

                        <button className="close-btn">

                            Close

                        </button>

                    </div>

                </div>

            </div>

        </div>

    );

};

export default DesignPreview;