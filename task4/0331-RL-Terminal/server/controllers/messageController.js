const Message = require("../models/message");
const asyncHandler = require("../middleware/asyncHandler");

const submit_feedback = asyncHandler(async (req, res) => {
  const message = new Message(req.body);
  await message.save();

  res.status(201).json({ msg: "Thank you for your feedback!" });
});

module.exports = { submit_feedback };
