import React from 'react';
import { PenTool, Layout, Image as ImageIcon, Box, Calculator } from 'lucide-react';

const TrustStrip = () => {
    return (
        <div className="trust-strip">
            <div className="trust-container">
                <div className="trust-item"><PenTool size={20} /> AI Planning</div>
                <div className="trust-item"><Layout size={20} /> Floor Plans</div>
                <div className="trust-item"><ImageIcon size={20} /> Interior Design</div>
                <div className="trust-item"><Box size={20} /> 3D Visualization</div>
                <div className="trust-item"><Calculator size={20} /> Cost Estimation</div>
            </div>
        </div>
    );
};

export default TrustStrip;
