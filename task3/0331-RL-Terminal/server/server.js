const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const { errorHandler, notFound } = require("./middleware/errorMiddleware");

require("dotenv").config();

if (!process.env.dbURL) {
  console.error("Error: dbURL is not configured in environment variables!");
  process.exit(1);
}

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(
  cors({
    origin: "*",
  })
);

const routes = require("./routes/routes");
app.use(routes);

app.use(notFound);
app.use(errorHandler);

mongoose
  .connect(process.env.dbURL)
  .then(() => {
    const PORT = process.env.PORT || 3002;
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
      console.log("Connection to the Database was established!");
    });
  })
  .catch((error) => {
    console.error("Database connection failed:", error.message);
    process.exit(1);
  });
