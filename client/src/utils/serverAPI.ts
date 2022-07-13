import axios from "axios";

const API_URL = 'http://localhost:8000';  // local django server

export const serverAPI = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
});