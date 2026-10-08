import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://pachangas-backend.onrender.com/api';

const API = axios.create({
  baseURL: API_URL,
});

export default API;