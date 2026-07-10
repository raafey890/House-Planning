const mongoose = require("mongoose");


const projectSchema = new mongoose.Schema(

    {

        user: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "User",
        },

        projectName: {
            type: String,
            required: true,
        },

        projectType: {
            type: String,
            required: true,
        },

        location: {
            type: String,
            default: "",
        },

        budget: {
            type: Number,
            default: 0,
        },

        plotSize: {
            type: String,
            default: "",
        },

        floors: {
            type: Number,
            default: 1,
        },

        bedrooms: {
            type: Number,
            default: 1,
        },

        bathrooms: {
            type: Number,
            default: 1,
        },

        designStyle: {
            type: String,
            default: "Modern",
        },

        floorPlanImage: {
            type: String,
            default: "",
        },

        description: {
            type: String,
            default: "",
        },

        aiGenerated: {
            type: Boolean,
            default: false,
        },

        status: {
            type: String,
            enum: [
                "Pending",
                "In Progress",
                "Completed",
            ],
            default: "Pending",
        },

    },

    {
        timestamps: true,
    }

);


module.exports = mongoose.model(
    "Project",
    projectSchema
);