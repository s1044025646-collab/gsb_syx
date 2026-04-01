const Note = require("../models/note");
const asyncHandler = require("../middleware/asyncHandler");

const get_all_notes = asyncHandler(async (req, res) => {
  const notes = await Note.find().sort({ createdAt: -1 }).lean();

  if (notes.length > 0) {
    res.status(200).json({
      msg: "All notes have been fetched successfully!",
      content: notes,
    });
  } else {
    res.status(200).json({ msg: "No notes to show!" });
  }
});

const add_note = asyncHandler(async (req, res) => {
  const note = new Note(req.body);
  const savedNote = await note.save();

  res.status(201).json({
    msg: "Your note was saved successfully!",
    content: savedNote,
  });
});

const get_one_note = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const note = await Note.findById(id).lean();

  if (note) {
    res.status(200).json({
      msg: "The note was fetched successfully!",
      content: note,
    });
  } else {
    res.status(404).json({ msg: "This note doesn't exist!" });
  }
});

const update_note = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const updatedNote = await Note.findByIdAndUpdate(id, req.body, {
    new: true,
    runValidators: true,
  });

  if (updatedNote) {
    res.status(200).json({
      msg: "The note was updated successfully!",
      content: updatedNote,
    });
  } else {
    res.status(404).json({ msg: "This note doesn't exist!" });
  }
});

const delete_note = asyncHandler(async (req, res) => {
  const { id } = req.params;
  const deletedNote = await Note.findByIdAndDelete(id);

  if (deletedNote) {
    res.status(200).json({ msg: "The note was successfully deleted!" });
  } else {
    res.status(404).json({ msg: "This note doesn't exist!" });
  }
});

module.exports = {
  get_all_notes,
  add_note,
  get_one_note,
  update_note,
  delete_note,
};
