import axios from 'axios';

// Detectar si estamos en producción (Render) o desarrollo (localhost)
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';

const API = axios.create({
  baseURL: isProduction 
    ? 'https://pachangas-backend.onrender.com/api'
    : 'http://127.0.0.1:8000/api',
});

console.log('API Base URL:', API.defaults.baseURL);

export default API;
