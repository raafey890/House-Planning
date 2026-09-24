const express = require("express");

const router = express.Router();

const {
    generateFloorPlan,
} = require("../controllers/aiController");


const { protect } = require("../middleware/supabaseAuth");

// GENERATE AI FLOOR PLAN
router.post("/generate", protect, generateFloorPlan);


module.exports = router;