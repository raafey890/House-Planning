const interiorMarketplace = {

    designers: [],

    designCategories: [

        "Modern",
        "Luxury",
        "Minimal",

        "Traditional"

    ],

    addDesigner(designer) {

        designer.id = Date.now();

        designer.completedDesigns = 0;

        this.designers.push(designer);

    },

    searchByCategory(category) {

        return this.designers.filter(
            designer =>
            designer.specialization === category
        );

    },

    markFeatured(designerId) {

        const designer =
        this.designers.find(
            item => item.id === designerId
        );

        if(designer) {

            designer.featured = true;

        }

    }

};

export default interiorMarketplace;