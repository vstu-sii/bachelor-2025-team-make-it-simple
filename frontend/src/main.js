import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "./router";
import './assets/css/global.css'
import App from "./App.vue";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount("#app");


import { useAuthStore } from "./stores/auth";

setTimeout(async () => {
  const authStore = useAuthStore();
  console.log("Проверка авторизации при старте...");
  await authStore.checkAndRestoreAuth();
}, 100);