const { body } = require("express-validator");

exports.projectValidator = [
  body("projectName")
    .notEmpty()
    .withMessage("Project name is required"),

  body("plotLength")
    .isNumeric()
    .withMessage("Plot length must be a number"),

  body("plotWidth")
    .isNumeric()
    .withMessage("Plot width must be a number"),

  body("floors")
    .isNumeric()
    .withMessage("Floors must be a number"),
];