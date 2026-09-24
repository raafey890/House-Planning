const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");

// Database connection (MongoDB deprecated in Phase 2)
// const connectDB = require("./config/db");
// connectDB();
dotenv.config();

// ROUTES
const aiRoutes = require("./routes/aiRoutes");
const {
    notFound,
    errorHandler,
} = require("./middleware/errorMiddleware");

const app = express();

// MIDDLEWARE
app.use(cors());

app.use(express.json());

app.use(express.urlencoded({
    extended: true,
}));

// API ROUTES
app.use("/api/ai", aiRoutes);


// DEFAULT ROUTE
app.get("/", (req, res) => {

    res.send("AI Property Intelligence System API Running");

});
app.use(notFound);

app.use(errorHandler);


// SERVER
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {

    console.log(`Server running on port ${PORT}`);

});