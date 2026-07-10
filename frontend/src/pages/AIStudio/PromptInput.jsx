import React from "react";

const PromptInput = () => {

    return (

        <div className="prompt-box">

            <textarea

                placeholder="
Generate a modern luxury villa with
3 floors, glass exterior, swimming pool,
and futuristic lighting...
                "

            />

            <div className="prompt-actions">

                <button className="primary-btn">

                    Generate Design

                </button>

            </div>

        </div>

    );

};

export default PromptInput;