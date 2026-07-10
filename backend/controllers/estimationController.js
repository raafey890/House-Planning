const Estimation = require("../models/Estimation");


// CREATE ESTIMATION
const createEstimation = async (req, res) => {

    try {

        const {
            materialCost,
            laborCost,
            electricalCost,
            plumbingCost,
        } = req.body;

        const totalCost =
            materialCost +
            laborCost +
            electricalCost +
            plumbingCost;

        const estimation = await Estimation.create({
            materialCost,
            laborCost,
            electricalCost,
            plumbingCost,
            totalCost,
        });

        res.status(201).json({
            success: true,
            message: "Estimation Created Successfully",
            data: estimation,
        });

    } catch (error) {

        res.status(500).json({
            success: false,
            message: error.message,
        });

    }

};


// GET ALL ESTIMATIONS
const getEstimations = async (req, res) => {

    try {

        const estimations = await Estimation.find();

        res.status(200).json({
            success: true,
            totalEstimations: estimations.length,
            data: estimations,
        });

    } catch (error) {

        res.status(500).json({
            success: false,
            message: error.message,
        });

    }

};


// GET SINGLE ESTIMATION
const getSingleEstimation = async (req, res) => {

    try {

        const estimation = await Estimation.findById(req.params.id);

        if (!estimation) {

            return res.status(404).json({
                success: false,
                message: "Estimation Not Found",
            });

        }

        res.status(200).json({
            success: true,
            data: estimation,
        });

    } catch (error) {

        res.status(500).json({
            success: false,
            message: error.message,
        });

    }

};


// DELETE ESTIMATION
const deleteEstimation = async (req, res) => {

    try {

        const estimation = await Estimation.findById(req.params.id);

        if (!estimation) {

            return res.status(404).json({
                success: false,
                message: "Estimation Not Found",
            });

        }

        await estimation.deleteOne();

        res.status(200).json({
            success: true,
            message: "Estimation Deleted Successfully",
        });

    } catch (error) {

        res.status(500).json({
            success: false,
            message: error.message,
        });

    }

};


module.exports = {
    createEstimation,
    getEstimations,
    getSingleEstimation,
    deleteEstimation,
};