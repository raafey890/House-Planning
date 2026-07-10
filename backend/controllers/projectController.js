const Project = require("../models/Project");


// CREATE PROJECT
const createProject = async (req, res) => {

    try {

        const {
            projectName,
            projectType,
            location,
            budget,
            floorPlanImage,
            description,
        } = req.body;

        // VALIDATION
        if (!projectName || !projectType) {

            return res.status(400).json({
                success: false,
                message: "Project Name and Type are required",
            });

        }

        // CREATE PROJECT
        const project = await Project.create({

    user: req.user._id,
            projectName,
            projectType,
            location,
            budget,
            floorPlanImage,
            description,
        });

        res.status(201).json({
            success: true,
            message: "Project Created Successfully",
            data: project,
        });

    } catch (error) {

        res.status(500).json({
            success: false,
            message: error.message,
        });

    }

};


// GET ALL PROJECTS
const getProjects = async (req, res) => {

    try {

        const projects = await Project.find().sort({
            createdAt: -1,
        });

        res.status(200).json({
            success: true,
            totalProjects: projects.length,
            data: projects,
        });

    } catch (error) {

        res.status(500).json({
            success: false,
            message: error.message,
        });

    }

};


// GET SINGLE PROJECT
const getSingleProject = async (req, res) => {

    try {

        const project = await Project.findById(req.params.id);

        if (!project) {

            return res.status(404).json({
                success: false,
                message: "Project Not Found",
            });

        }

        res.status(200).json({
            success: true,
            data: project,
        });

    } catch (error) {

        res.status(500).json({
            success: false,
            message: error.message,
        });

    }

};


// UPDATE PROJECT
const updateProject = async (req, res) => {

    try {

        const project = await Project.findById(req.params.id);

        if (!project) {

            return res.status(404).json({
                success: false,
                message: "Project Not Found",
            });

        }

        const updatedProject = await Project.findByIdAndUpdate(
            req.params.id,
            req.body,
            {
                new: true,
            }
        );

        res.status(200).json({
            success: true,
            message: "Project Updated Successfully",
            data: updatedProject,
        });

    } catch (error) {

        res.status(500).json({
            success: false,
            message: error.message,
        });

    }

};


// DELETE PROJECT
const deleteProject = async (req, res) => {

    try {

        const project = await Project.findById(req.params.id);

        if (!project) {

            return res.status(404).json({
                success: false,
                message: "Project Not Found",
            });

        }

        await project.deleteOne();

        res.status(200).json({
            success: true,
            message: "Project Deleted Successfully",
        });

    } catch (error) {

        res.status(500).json({
            success: false,
            message: error.message,
        });

    }

};


module.exports = {
    createProject,
    getProjects,
    getSingleProject,
    updateProject,
    deleteProject,
};