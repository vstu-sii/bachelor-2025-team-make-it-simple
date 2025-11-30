<script setup>
import { ref } from "vue";
import api from "../api/axios";
import { useRouter } from "vue-router";

const router = useRouter();

const step = ref(1);
const form = ref({
  last_name: "",
  first_name: "",
  middle_name: "",
  birth_date: "",
  phone: "",
  email: "",
  telegram: "",
  vk: "",
  interests: "",
  role: "Ученик",
  password: "",
  password_repeat: "",
});

function nextStep() {
  step.value++;
}

function prevStep() {
  step.value--;
}

function goToLogin() {
  router.push("/login");
}

async function submit() {
  if (form.value.password !== form.value.password_repeat) {
    alert("Пароли не совпадают");
    return;
  }

  const payload = {
    last_name: form.value.last_name,
    first_name: form.value.first_name,
    middle_name: form.value.middle_name,
    birth_date: form.value.birth_date,
    phone: form.value.phone,
    telegram: form.value.telegram || null,
    vk: form.value.vk || null,
    avatar_path: null,
    role: form.value.role,
    email: form.value.email,
    password: form.value.password,
  };

  try {
    await api.post("/auth/register", payload);

    alert("Регистрация прошла — подтвердите email");
    router.push("/login");
  } catch (err) {
    console.error("ERR FULL:", err);
    alert("Ошибка: " + (err.response?.data?.detail || err.message));
  }
}
</script>

<template>
  <div class="auth-page">

    <!-- Левая половина -->
    <div class="left-side">
      <img src="/src/assets/left-bg.svg" alt="background" class="left-bg">

      <div class="welcome-text">
        <h1>Добро<br>пожаловать!</h1>

        <p class="lead-paragraph">
          Получите готовый план персонализированного урока за минуты!
        </p>

        <p class="info-paragraph">
          Наш сервис изучает интересы ученика, анализируя информацию из открытых источников. 
          На основе этих данных мы создаем персонализированный учебный план. Репетитор подбирает задания 
          по темам и предлагает идеи для уроков, что помогает вовлечь учеников, экономит время на подготовку 
          и сохраняет индивидуальный подход даже при высокой нагрузке.
        </p>
      </div>

      <img src="/src/assets/logo.svg" class="logo" alt="Make It SIMpLe">
    </div>

    <!-- Правая половина -->
    <div class="right-side">

      <div class="auth-card">
        <h2 class="auth-title">Создание аккаунта</h2>
        <p class="subtitle">Введите данные для создания аккаунта</p>

        <div class="divider"></div>

        <!-- Формы -->
        <form class="auth-form" @submit.prevent="nextStep">

          <!-- Шаг 1 -->
          <template v-if="step === 1">
            <label>Фамилия</label>
            <input v-model="form.last_name" type="text" placeholder=" ">

            <label>Имя</label>
            <input v-model="form.first_name" type="text" placeholder=" ">

            <label>Отчество</label>
            <input v-model="form.middle_name" type="text" placeholder=" ">

            <label>Дата рождения</label>
            <input v-model="form.birth_date" type="date">

            <label>Телефон</label>
            <input v-model="form.phone" type="text" placeholder="+7">

            <label>Email</label>
            <input v-model="form.email" type="email" placeholder=" ">
          </template>

          <!-- Шаг 2 -->
          <template v-if="step === 2">
            <label>Telegram</label>
            <input v-model="form.telegram" type="text">

            <label>VK</label>
            <input v-model="form.vk" type="text">

            <label>Роль</label>
            <div class="role-selector">
              <label class="role-item">
                <input type="radio" value="Ученик" v-model="form.role">
                Ученик
              </label>

              <label class="role-item">
                <input type="radio" value="Репетитор" v-model="form.role">
                Репетитор
              </label>
            </div>

            <label>Пароль</label>
            <input v-model="form.password" type="password">

            <label>Повторите пароль</label>
            <input v-model="form.password_repeat" type="password">
          </template>

          <div class="divider"></div>

          <div class="buttons">
            <!-- Кнопка "Авторизоваться" на первом шаге -->
            <button
              type="button"
              class="btn-register"
              v-if="step === 1"
              @click.prevent="goToLogin"
            >
              Авторизоваться
            </button>

            <!-- Кнопка "Назад" на втором шаге -->
            <button
              type="button"
              class="btn-register"
              v-if="step > 1"
              @click.prevent="prevStep"
            >
              Назад
            </button>

            <!-- Кнопки для перехода/регистрации -->
            <button
              v-if="step < 2"
              type="submit"
              class="btn-login"
            >
              Далее
            </button>

            <button
              v-if="step === 2"
              type="button"
              class="btn-login"
              @click="submit"
            >
              Зарегистрироваться
            </button>
          </div>

        </form>
      </div>

    </div>

  </div>
</template>

<style scoped>
@import url('https://fonts.cdnfonts.com/css/kyivtype-titling');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap');

/* Контейнер страницы */
.auth-page {
  display: flex;
  width: 100vw;
  height: 100vh;
  background: #071446;
  margin: 0;
  padding: 0;
  position: relative;
}

/* ЛЕВАЯ ЧАСТЬ */
.left-side {
  position: relative;
  width: 50%;
  height: 100%;
  overflow: hidden;
  background: #071446; /* Запасной фон на случай проблем с изображением */
}

/* Картинка гарантированно заполняет блок */
.left-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: left center;
  display: block;
  min-width: 100%; /* Гарантирует минимальную ширину */
  min-height: 100%; /* Гарантирует минимальную высоту */
}

/* Текст */
.welcome-text {
  position: absolute;
  top: 8%;
  left: 10%;
  width: 72%;
  font-family: 'KyivType Titling', serif;
  color: white;
  z-index: 2; /* Чтобы текст был поверх изображения */
}

.welcome-text h1 {
  font-size: 100px;
  line-height: 1.05;
  font-weight: 400;
  margin-bottom: 50px;
}

.welcome-text p {
  text-align: justify;
  text-indent: 2em;
  margin-top: 18px;
  max-width: 480px;
  font-family: Inter, sans-serif;
  font-size: 18px;
}

.lead-paragraph {
  color: #F9C2A2;
}

.info-paragraph {
  color: #FFE4D1;
  opacity: 0.92;
}

/* Логотип */
.logo {
  position: absolute;
  bottom: 40px;
  right: 40px;
  width: 260px;
  opacity: 0.95;
  z-index: 2;
}

/* ПРАВАЯ ЧАСТЬ */
.right-side {
  width: 50%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgb(8, 21, 80);
  overflow: hidden;
  position: relative;
}

/* Форма */
.auth-card {
  background: rgb(6, 15, 48);
  padding: 50px 60px;
  border-radius: 28px;
  width: 460px;
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.40);
  text-align: center;
  font-family: 'KyivType Titling', serif;
  z-index: 1;
}

/* Заголовок с JetBrains Mono */
.auth-title {
  font-family: "JetBrains Mono", monospace;
  font-optical-sizing: auto;
  font-weight: 600;
  font-style: normal;
  font-size: 32px;
  color: white;
  margin-bottom: 10px;
}

/* Подзаголовок с KyivType Titling 15px */
.subtitle {
  font-family: 'KyivType Titling', serif;
  font-size: 15px;
  color: #c7c7c7;
  margin-bottom: 20px;
}

.divider {
  width: 100%;
  height: 1px;
  background: rgba(200, 200, 200, 0.2);
  margin: 20px 0;
}

.auth-form {
  text-align: left;
}

/* Метки полей ввода с KyivType Titling 15px */
.auth-form label {
  font-family: 'KyivType Titling', serif;
  font-size: 15px;
  margin-bottom: 6px;
  display: block;
  color: #dcdcdc;
}

.auth-form input {
  width: 100%;
  padding: 12px 14px;
  background: #fff9d6;
  border: none;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 15px;
  outline: none;
  font-family: 'KyivType Titling', serif;
}

/* Кнопки с JetBrains Mono */
.buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.btn-login,
.btn-register {
  font-family: "JetBrains Mono", monospace;
  font-optical-sizing: auto;
  font-weight: 600;
  font-style: normal;
  border: none;
  color: white;
  padding: 12px 26px;
  font-size: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.2s;
}

.btn-login {
  background: #ff2a6d;
}

.btn-register {
  background: #6b7591;
}

.btn-login:hover,
.btn-register:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}

/* Стили для выбора роли */
.role-selector {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.role-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-family: 'KyivType Titling', serif;
  font-size: 15px;
  color: #dcdcdc;
}

.role-item input[type="radio"] {
  width: auto;
  margin: 0;
}
</style>