import axiosInstance from './axiosInstance';

export const notesAPI = {
  getAllNotes: async () => {
    const response = await axiosInstance.get('/allNotes');
    return response.data;
  },

  addNote: async (note) => {
    const response = await axiosInstance.post('/addNote', note);
    return response.data;
  },

  getNoteById: async (id) => {
    const response = await axiosInstance.get(`/noteDetails/${id}`);
    return response.data;
  },

  updateNote: async (id, note) => {
    const response = await axiosInstance.patch(`/updateNote/${id}`, note);
    return response.data;
  },

  deleteNote: async (id) => {
    const response = await axiosInstance.delete(`/deleteNote/${id}`);
    return response.data;
  },

  submitFeedback: async (feedback) => {
    const response = await axiosInstance.post('/submitFeedback', feedback);
    return response.data;
  },
};
