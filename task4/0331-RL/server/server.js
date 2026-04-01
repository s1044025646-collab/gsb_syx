// Importing Modules
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const { errorHandler, notFound } = require("./middleware/errorMiddleware");

// Initiating Express
const app = express();

// Environment Variables
require("dotenv").config();

// Validate environment variables
if (!process.env.dbURL) {
  console.error("ERROR: dbURL is not defined in environment variables!");
  process.exit(1);
}

// Connecting to Database
mongoose
  .connect(process.env.dbURL)
  .then(() => {
    const PORT = process.env.PORT || 3001;
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
      console.log("Connection to the Database was established!");
    });
  })
  .catch((error) => {
    console.error("Database connection failed:", error.message);
    process.exit(1);
  });

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

// Error Middlewares
app.use(notFound);
app.use(errorHandler);
