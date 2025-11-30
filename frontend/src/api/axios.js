import axios from "axios";
import { config } from "../config.js";

const api = axios.create({
  baseURL: config.apiUrl,
});

const token = localStorage.getItem("token");
if (token) {
  api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
}

export default api;