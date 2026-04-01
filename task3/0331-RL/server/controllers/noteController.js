// Importing Models
const Note = require("../models/note");
const asyncHandler = require("../middleware/asyncHandler");

// Controllers

// To retrieve all notes from the database
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

// To add a new note to the database
const add_note = asyncHandler(async (req, res) => {
  const note = new Note(req.body);
  const savedNote = await note.save();

  res.status(201).json({
    msg: "Your note was saved successfully!",
    content: savedNote,
  });
});

// To retrieve a single note by its ID
const get_one_note = asyncHandler(async (req, res) => {
  const id = req.params.id;
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

// To edit an existing note
const update_note = asyncHandler(async (req, res) => {
  const id = req.params.id;
  const updatedNote = await Note.findByIdAndUpdate(id, req.body, { new: true }).lean();

  if (updatedNote) {
    res.status(200).json({
      msg: "The note was updated successfully!",
      content: updatedNote,
    });
  } else {
    res.status(404).json({ msg: "This note doesn't exist!" });
  }
});

// To delete a note from the database
const delete_note = asyncHandler(async (req, res) => {
  const id = req.params.id;
  const deletedNote = await Note.findByIdAndDelete(id);

  if (deletedNote) {
    res.status(200).json({ msg: "The note was successfully deleted!" });
  } else {
    res.status(404).json({ msg: "This note doesn't exist!" });
  }
});

// Exports
module.exports = {
  get_all_notes,
  add_note,
  get_one_note,
  update_note,
  delete_note,
};
