const UserContext = {

    userName: "",

    email: "",

    phoneNumber: "",

    profileImage: "",

    savedProjects: [],

    favoriteDesigns: [],

    premiumUser: false,

    recentlyViewed: [],

    updateUserProfile(userData) {

        this.userName = userData.userName;

        this.email = userData.email;

        this.phoneNumber = userData.phoneNumber;

        this.profileImage = userData.profileImage;

    },

    addSavedProject(project) {

        this.savedProjects.push(project);

    },

    addFavoriteDesign(design) {

        this.favoriteDesigns.push(design);

    },

    clearUserData() {

        this.userName = "";

        this.email = "";

        this.phoneNumber = "";

        this.profileImage = "";

        this.savedProjects = [];

        this.favoriteDesigns = [];

    }

};

export default UserContext;