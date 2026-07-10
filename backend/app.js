const express = require("express");

const cors = require("cors");

const app = express();

/* MIDDLEWARE */

app.use(cors());

app.use(express.json());

app.use(express.urlencoded({ extended: true }));

/* TEST ROUTE */

app.get("/", (req, res) => {

    res.send("AI House Planner Backend Running");

});

module.exports = app;