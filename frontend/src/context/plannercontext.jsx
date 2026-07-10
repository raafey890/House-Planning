const PlannerContext = {

    plotSize: "",

    facing: "",

    floors: 1,

    rooms: 0,

    budget: 0,

    style: "",

    generatedDesigns: [],

    updatePlannerData(data) {

        this.plotSize = data.plotSize;

        this.facing = data.facing;

        this.floors = data.floors;

        this.rooms = data.rooms;

        this.budget = data.budget;

        this.style = data.style;

    },

    resetPlanner() {

        this.plotSize = "";

        this.facing = "";

        this.floors = 1;

        this.rooms = 0;

        this.budget = 0;

        this.style = "";

    }

};

export default PlannerContext;