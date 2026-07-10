const {
  registerValidator,
  loginValidator,
} = require("../validators/authValidator");

const validate = require("../middleware/validationMiddleware");

const express = require("express");

const router = express.Router();

router.get("/test", (req, res) => {
    res.json({
        message: "Auth Route Working"
    });
});


const {
    registerUser,
    loginUser,
} = require("../controllers/authController");


// REGISTER USER
router.post(
  "/register",
  registerValidator,
  validate,
  registerUser
);


// LOGIN USER
router.post(
  "/login",
  loginValidator,
  validate,
  loginUser
);



module.exports = router;