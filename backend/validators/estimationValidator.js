const { body } = require("express-validator");

exports.estimationValidator = [
  body("area")
    .isNumeric()
    .withMessage("Area must be numeric"),

  body("constructionType")
    .notEmpty()
    .withMessage("Construction type is required"),

  body("location")
    .notEmpty()
    .withMessage("Location is required"),
];