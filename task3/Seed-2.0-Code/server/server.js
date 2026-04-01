// Importing Modules
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

// Inititating Express
const app = express();

// Environment Variables
require("dotenv").config();

// Validate dbURL
if (!process.env.dbURL) {
  console.error("Error: dbURL is not defined in environment variables");
  process.exit(1);
}

// Connecting to Database
mongoose
  .connect(process.env.dbURL)
  .then((result) =>
    app.listen(process.env.PORT || 3000, () => {
      console.log("Connection to the Database was established!");
    })
  )
  .catch((error) => console.log(error));

// Middlewares
app.use(express.json()); // JSON Parser
app.use(express.urlencoded({ extended: true })); // URL Body Parser

// CORS
app.use(
  cors({
    origin: "*",
  })
);

// Routes
const routes = require("./routes/routes");
app.use(routes);

// Error Handling Middleware
const errorHandler = require("./middleware/errorHandler");
app.use(errorHandler);
