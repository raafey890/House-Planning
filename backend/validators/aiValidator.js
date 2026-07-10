const { body } = require("express-validator");

exports.aiValidator = [
  body("plotLength")
    .isNumeric()
    .withMessage("Plot length must be numeric"),

  body("plotWidth")
    .isNumeric()
    .withMessage("Plot width must be numeric"),

  body("bedrooms")
    .isNumeric()
    .withMessage("Bedrooms must be numeric"),

  body("bathrooms")
    .isNumeric()
    .withMessage("Bathrooms must be numeric"),
];