import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://mern-notes-backend-5z2j.onrender.com';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default axiosInstance;
