import { createRouter, createWebHistory } from "vue-router";

import Login from "../pages/Login.vue";
import Register from "../pages/Register.vue";
import Profile from "../pages/Profile.vue";
import CoursePage from "../pages/CoursePage.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "login", component: Login },
  { path: "/register", name: "register", component: Register },
  { 
    path: "/profile", 
    name: "profile-self", 
    component: Profile,
    meta: { requiresAuth: true }
  },
  { 
    path: "/profile/:id(\\d+)", // только цифры
    name: "profile", 
    component: Profile,
    meta: { requiresAuth: true },
    props: true  // передаем параметр как props
  },
  { 
    path: "/course/:id(\\d+)", 
    name: "course", 
    component: CoursePage,
    meta: { requiresAuth: true },
    props: true
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Навигационный гард для проверки аутентификации
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const token = localStorage.getItem("token");
  
  if (requiresAuth && !token) {
    next("/login");
  } else {
    next();
  }
});

export default router;