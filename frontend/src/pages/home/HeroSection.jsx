const HeroSection = () => {

    return (

        <section className="hero-section fade-in">

            <div className="hero-content">

                <span className="hero-badge">

                    AI Powered House Planning
                </span>

                <h1>

                    Design Your Dream Home
                    With Artificial Intelligence

                </h1>

                <p>

                    Generate smart floor plans,
                    modern interiors, construction
                    estimates, and stunning house
                    visualizations instantly.

                </p>

                <div className="hero-buttons">

                    <button className="primary-btn">

                        Start Planning

                    </button>

                    <button className="secondary-btn">

                        Explore Designs

                    </button>

                </div>

            </div>

            <div className="hero-image-container">

                <div className="hero-glow"></div>

                <img
                    src="https://images.unsplash.com/photo-1600585154526-990dced4db0d"
                    alt="AI House"
                    className="hero-image"
                />

            </div>

        </section>

    );

};

export default HeroSection;