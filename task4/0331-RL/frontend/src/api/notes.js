import api from "./axios";

export const getAllNotes = async () => {
  const response = await api.get("/allNotes");
  return response.data;
};

export const addNote = async (note) => {
  const response = await api.post("/addNote", note);
  return response.data;
};

export const getNoteById = async (id) => {
  const response = await api.get(`/noteDetails/${id}`);
  return response.data;
};

export const updateNote = async (id, note) => {
  const response = await api.patch(`/updateNote/${id}`, note);
  return response.data;
};

export const deleteNote = async (id) => {
  const response = await api.delete(`/deleteNote/${id}`);
  return response.data;
};

export const submitFeedback = async (feedback) => {
  const response = await api.post("/submitFeedback", feedback);
  return response.data;
};
