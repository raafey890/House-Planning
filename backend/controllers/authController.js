const User = require("../models/User");

const bcrypt = require("bcryptjs");

const jwt = require("jsonwebtoken");


// GENERATE TOKEN
const generateToken = (id) => {

    return jwt.sign(

        { id },

        process.env.JWT_SECRET,

        {
            expiresIn: "30d",
        }

    );

};


// REGISTER USER
const registerUser = async (req, res) => {

    try {

        const {
            name,
            email,
            password,
        } = req.body;


        // VALIDATION
        if (
            !name ||
            !email ||
            !password
        ) {

            return res.status(400).json({

                success: false,

                message: "Please Fill All Fields",

            });

        }


        // CHECK USER
        const userExists = await User.findOne({
            email,
        });

        if (userExists) {

            return res.status(400).json({

                success: false,

                message: "User Already Exists",

            });

        }


        // HASH PASSWORD
        const salt = await bcrypt.genSalt(10);

        const hashedPassword = await bcrypt.hash(
            password,
            salt
        );


        // CREATE USER
        const user = await User.create({

            name,
            email,
            password: hashedPassword,

        });


        res.status(201).json({

            success: true,

            _id: user._id,

            name: user.name,

            email: user.email,

            role: user.role,

            token: generateToken(user._id),

        });

    } catch (error) {

        res.status(500).json({

            success: false,

            message: error.message,

        });

    }

};


// LOGIN USER
const loginUser = async (req, res) => {

    try {

        const {
            email,
            password,
        } = req.body;


        // FIND USER
        const user = await User.findOne({
            email,
        });


        if (!user) {

            return res.status(401).json({

                success: false,

                message: "Invalid Email",

            });

        }


        // PASSWORD MATCH
        const isMatch = await bcrypt.compare(
            password,
            user.password
        );


        if (!isMatch) {

            return res.status(401).json({

                success: false,

                message: "Invalid Password",

            });

        }


        res.status(200).json({

            success: true,

            _id: user._id,

            name: user.name,

            email: user.email,

            role: user.role,

            token: generateToken(user._id),

        });

    } catch (error) {

        res.status(500).json({

            success: false,

            message: error.message,

        });

    }

};


module.exports = {
    registerUser,
    loginUser,
};