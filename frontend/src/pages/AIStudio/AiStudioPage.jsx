import React from "react";
import AIRecommendations from "./AIRecommendations";
import GenerationHistory from "./GenerationHistory";

import PromptInput from "./PromptInput";
import AIOptions from "./AIOptions";
import AIHistory from "./AIHistory";
import AIResultCard from "./AIResultCard";

import "../../styles/pages/aistudio.css";

const AIStudioPage = () => {

    return (

        <div className="ai-studio-page">

            <div className="ai-studio-header">

                <h1>
                    AI Design Studio
                </h1>

                <p>
                    Generate futuristic house plans,
                    interiors, exteriors and smart
                    architecture concepts with AI.
                </p>

            </div>

            <AIOptions />

            <PromptInput />

            <div className="ai-results-grid">

                <AIResultCard />

                <AIResultCard />

                <AIResultCard />

            </div>

            <AIHistory />
            <AIRecommendations />

<GenerationHistory />

        </div>

    );

};

export default AIStudioPage;