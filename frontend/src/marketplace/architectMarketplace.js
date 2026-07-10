const architectMarketplace = {

    architects: [],

    premiumArchitects: [],

    addArchitect(architect) {

        architect.id = Date.now();

        architect.portfolio = [];

        architect.rating = 0;

        this.architects.push(architect);

    },

    addPortfolioProject(
        architectId,
        project
    ) {

        const architect =
        this.architects.find(
            item => item.id === architectId
        );

        if(architect) {

            architect.portfolio.push(project);

        }

    },

    getTopArchitects() {

        return this.architects.sort(
            (a, b) => b.rating - a.rating
        );

    }

};

export default architectMarketplace;