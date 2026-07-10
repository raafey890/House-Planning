const rateLimiter = {

    requests: {},

    limit: 100,

    interval: 60000,

    checkLimit(userId) {

        if(!this.requests[userId]) {

            this.requests[userId] = 1;

            return true;

        }

        this.requests[userId]++;

        if(
            this.requests[userId] > this.limit
        ) {

            return false;

        }

        return true;

    },

    resetLimits() {

        this.requests = {};

    }

};

export default rateLimiter;