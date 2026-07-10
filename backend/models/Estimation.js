const mongoose = require("mongoose");


const estimationSchema = new mongoose.Schema(

    {

        user: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "User",
        },

        materialCost: {
            type: Number,
            required: true,
        },

        laborCost: {
            type: Number,
            required: true,
        },

        electricalCost: {
            type: Number,
            required: true,
        },

        plumbingCost: {
            type: Number,
            required: true,
        },

        interiorCost: {
            type: Number,
            default: 0,
        },

        exteriorCost: {
            type: Number,
            default: 0,
        },

        totalCost: {
            type: Number,
            required: true,
        },

        estimatedDuration: {
            type: String,
            default: "6 Months",
        },

        projectType: {
            type: String,
            default: "Residential",
        },

    },

    {
        timestamps: true,
    }

);


module.exports = mongoose.model(
    "Estimation",
    estimationSchema
);