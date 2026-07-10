const express = require("express");

const router = express.Router();

const {
    generateFloorPlan,
} = require("../controllers/aiController");


// GENERATE AI FLOOR PLAN
router.post("/generate", generateFloorPlan);


module.exports = router;