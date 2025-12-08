import { defineStore } from "pinia";
import api from "../api/axios";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || null,
    user: null,
    isLoading: false, // Добавляем флаг загрузки
  }),

  actions: {
    setToken(token) {
      this.token = token;
      if (token) {
        localStorage.setItem("token", token);
        api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      } else {
        localStorage.removeItem("token");
        delete api.defaults.headers.common["Authorization"];
      }
    },

    async login(email, password) {
      this.isLoading = true;
      try {
        const res = await api.post("/auth/login", { email, password });
        const { access_token } = res.data;

        this.setToken(access_token);

        const me = await api.get("/auth/me");
        this.user = me.data;

        // Загружаем дополнительную информацию о курсе после входа
        await this.fetchUserWithCourseInfo();
        
        return this.user;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchMe() {
      if (!this.token) {
        console.log("Нет токена, пропускаем fetchMe");
        return null;
      }
      
      this.isLoading = true;
      try {
        console.log("Загрузка данных пользователя...");
        api.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
        const res = await api.get("/auth/me");
        this.user = res.data;
        
        console.log("Данные пользователя загружены:", this.user);
        
        // Загружаем дополнительную информацию о курсе
        await this.fetchUserWithCourseInfo();
        
        return this.user;
      } catch (error) {
        console.error("Ошибка загрузки данных пользователя:", error);
        // Если токен невалидный, очищаем его
        if (error.response?.status === 401) {
          this.setToken(null);
          this.user = null;
        }
        return null;
      } finally {
        this.isLoading = false;
      }
    },

    // НОВЫЙ МЕТОД: Загружает информацию о пользователе с данными о курсе
    async fetchUserWithCourseInfo() {
      if (!this.user?.user_id) {
        console.log("Не могу загрузить информацию о курсе: нет user_id");
        return;
      }
      
      try {
        console.log(`Загрузка информации о курсе для пользователя ${this.user.user_id}...`);
        const response = await api.get(`/auth/${this.user.user_id}/with_course`);
        
        // Обновляем информацию о пользователе, включая данные о курсе
        this.user = { ...this.user, ...response.data };
        
        console.log("Информация о курсе загружена:", {
          user_id: this.user.user_id,
          role: this.user.role,
          course_info: this.user.course_info,
          courses_count: this.user.courses_count
        });
        
      } catch (error) {
        console.error('Ошибка загрузки информации о курсе:', error);
        // Не выбрасываем ошибку, чтобы не ломать работу приложения
      }
    },

    logout() {
      this.isLoading = false;
      this.setToken(null);
      this.user = null;
    },

    // Дополнительный метод для обновления данных пользователя
    updateUserData(newData) {
      if (this.user) {
        this.user = { ...this.user, ...newData };
      }
    },
    
    // Новый метод: проверка и восстановление состояния
    async checkAndRestoreAuth() {
      if (this.token && !this.user) {
        console.log("Токен есть, но пользователь не загружен. Восстанавливаем...");
        await this.fetchMe();
      }
    },
  },
});