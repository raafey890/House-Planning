import Navbar from "../../components/Navbar/Navbar";
import Footer from "../../components/Footer/Footer";
import HeroSection from "./HeroSection";
import TrustStrip from "./TrustStrip";
import HowItWorks from "./HowItWorks";
import FeaturesSection from "./FeaturesSection";
import FloorPlanShowcase from "./FloorPlanShowcase";
import DesignShowcase from "./DesignShowcase";
import ThreeDSection from "./ThreeDSection";
import EstimatorSection from "./EstimatorSection";
import ProjectWorkspaceSection from "./ProjectWorkspaceSection";
import GalleryPreview from "./GalleryPreview";
import CTASection from "./CTASection";

import "../../styles/pages/home.css"; // Ensure this applies home layout styles if needed

const HomePage = () => {
    return (
        <div className="home-page">
            <Navbar />
            <main>
                <HeroSection />
                <HowItWorks />
                <FeaturesSection />
                <FloorPlanShowcase />
                <DesignShowcase />
                <ThreeDSection />
                <EstimatorSection />
                <GalleryPreview />
                <CTASection />
            </main>
            <Footer />
        </div>
    );
};

export default HomePage;