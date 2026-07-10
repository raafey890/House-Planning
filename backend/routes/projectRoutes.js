const express = require("express");

const router = express.Router();

const {
    createProject,
    getProjects,
    getSingleProject,
    updateProject,
    deleteProject,
} = require("../controllers/projectController");




const {
    protect,
} = require("../middleware/authMiddleware");
router.get(
  "/protected",
  protect,
  (req, res) => {
    res.json({
      success: true,
      message: "Protected Route Accessed"
    });
  }
);



// CREATE PROJECT
router.post(
    "/",
    protect,
    createProject
);


// GET ALL PROJECTS
router.get(
    "/",
    protect,
    getProjects
);


// GET SINGLE PROJECT
router.get("/:id", getSingleProject);


// UPDATE PROJECT
router.put("/:id", updateProject);


// DELETE PROJECT
router.delete("/:id", deleteProject);


module.exports = router;