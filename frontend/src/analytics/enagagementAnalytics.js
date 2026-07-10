const engagementAnalytics = {

    likes: 0,

    shares: 0,

    downloads: 0,

    savedProjects: 0,

    increaseLikes() {

        this.likes++;

    },

    increaseShares() {

        this.shares++;

    },

    increaseDownloads() {

        this.downloads++;

    },

    increaseSavedProjects() {

        this.savedProjects++;

    }

};

export default engagementAnalytics;