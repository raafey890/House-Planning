const contractorMarketplace = {

    contractors: [],

    featuredContractors: [],

    addContractor(contractor) {

        contractor.id = Date.now();

        contractor.rating = 0;

        contractor.projectsCompleted = 0;

        this.contractors.push(contractor);

    },

    featureContractor(contractorId) {

        const contractor =
        this.contractors.find(
            item => item.id === contractorId
        );

        if(contractor) {

            this.featuredContractors.push(
                contractor
            );

        }

    },

    searchContractor(location) {

        return this.contractors.filter(
            contractor =>
            contractor.location === location
        );

    },

    updateRating(contractorId, rating) {

        const contractor =
        this.contractors.find(
            item => item.id === contractorId
        );

        if(contractor) {

            contractor.rating = rating;

        }

    }

};

export default contractorMarketplace;