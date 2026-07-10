const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");

const connectDB = require("./config/db");


// ROUTES
const authRoutes = require("./routes/authRoutes");
const projectRoutes = require("./routes/projectRoutes");
const estimationRoutes = require("./routes/estimationRoutes");
const aiRoutes = require("./routes/aiRoutes");
const {
    notFound,
    errorHandler,
} = require("./middleware/errorMiddleware");


dotenv.config();

connectDB();

const app = express();


// MIDDLEWARE
app.use(cors());

app.use(express.json());

app.use(express.urlencoded({
    extended: true,
}));


// API ROUTES
app.use("/api/auth", authRoutes);

app.use("/api/projects", projectRoutes);

app.use("/api/estimations", estimationRoutes);

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