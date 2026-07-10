const express = require("express");

const router = express.Router();

const {
    createEstimation,
    getEstimations,
    getSingleEstimation,
    deleteEstimation,
} = require("../controllers/estimationController");


// CREATE ESTIMATION
router.post("/", createEstimation);


// GET ALL ESTIMATIONS
router.get("/", getEstimations);


// GET SINGLE ESTIMATION
router.get("/:id", getSingleEstimation);


// DELETE ESTIMATION
router.delete("/:id", deleteEstimation);


module.exports = router;