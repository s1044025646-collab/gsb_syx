import axios from 'axios';

const DEFAULT_API_URL = 'https://mern-notes-backend-5z2j.onrender.com';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || DEFAULT_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
