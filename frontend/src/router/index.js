import { createRouter, createWebHistory } from "vue-router";

import Login from "../pages/Login.vue";
import Register from "../pages/Register.vue";
import Profile from "../pages/Profile.vue";

const routes = [
  { path: "/login", name: "login", component: Login },
  { path: "/register", name: "register", component: Register },
  { path: "/profile", name: "profile", component: Profile }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
