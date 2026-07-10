const marketplaceReviews = {

    reviews: [],

    addReview(reviewData) {

        const review = {

            id: Date.now(),

            ...reviewData,

            createdAt: new Date()

        };

        this.reviews.push(review);

    },

    getReviews(serviceId) {

        return this.reviews.filter(
            review =>
            review.serviceId === serviceId
        );

    },

    calculateAverageRating(serviceId) {

        const serviceReviews =
        this.getReviews(serviceId);

        if(serviceReviews.length === 0) {

            return 0;

        }

        const total =
        serviceReviews.reduce(
            (sum, review) =>
            sum + review.rating,
            0
        );

        return total /
        serviceReviews.length;

    }

};

export default marketplaceReviews;