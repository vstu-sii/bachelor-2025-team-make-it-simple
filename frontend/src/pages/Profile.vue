<script setup>
import { onMounted, reactive, ref } from "vue";
import { useAuthStore } from "../stores/auth";
import api from "../api/axios";
import { useRouter } from "vue-router";

const router = useRouter();
const auth = useAuthStore();
const editing = ref(false);
const fileInput = ref(null);

const form = reactive({
  last_name: "",
  first_name: "",
  middle_name: "",
  birth_date: "",
  phone: "",
  telegram: "",
  vk: "",
  interests: "",
  avatar_path: "",
  role: "",
  email: "",
});

// Аватарка по умолчанию
const defaultAvatar = "/src/assets/avatars/default_avatar.svg";

onMounted(async () => {
  if (!auth.token) {
    router.push("/login");
    return;
  }

  await auth.fetchMe();

  if (!auth.user) {
    router.push("/login");
    return;
  }

  Object.assign(form, auth.user);
});

async function save() {
  if (!auth.user) return;

  try {
    const res = await api.put(`/auth/${auth.user.user_id}`, form);
    auth.user = res.data;

    editing.value = false;
    alert("Профиль обновлён");
  } catch (err) {
    console.error(err);
    alert("Ошибка обновления");
  }
}

function triggerFileInput() {
  fileInput.value?.click();
}

async function handleAvatarUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  if (!file.type.startsWith('image/')) {
    alert('Пожалуйста, выберите изображение');
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    alert('Размер файла не должен превышать 5MB');
    return;
  }

  try {
    const formData = new FormData();
    formData.append('avatar', file);

    const response = await api.post('/auth/upload-avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    form.avatar_path = response.data.avatar_path;
    alert('Аватар успешно обновлен!');

  } catch (err) {
    console.error('Ошибка загрузки аватарки:', err);
    alert('Ошибка загрузки аватарки');
  }
}

function cancelEdit() {
  editing.value = false;
  Object.assign(form, auth.user);
}
</script>

<template>
  <div class="profile-page-container">
    <div class="profile-page">

      <header class="main-header fixed-header">
        <div class="header-left">
          <img src="/src/assets/logo.svg" alt="Make It Simple" class="header-logo" />
        </div>
        <div class="header-right">
          <span class="user-name">
            {{ form.first_name }} {{ form.last_name?.charAt(0) }}.
          </span>
          <img :src="form.avatar_path || defaultAvatar" alt="avatar" class="user-avatar" />
          <img src="/src/assets/menu.svg" alt="menu" class="menu-icon" />
        </div>
      </header>

      <div class="profile-content">

        <!-- Основная информация -->
        <div class="main-info-container">

          <!-- Левая часть -->
          <div class="left-info">
            <div class="inner-box">
              <h2>Основная информация</h2>
              <img :src="form.avatar_path || defaultAvatar" class="avatar" alt="avatar" />
              <p class="role-text">{{ form.role }}</p>

              <div class="action-buttons">
                <button v-if="!editing" class="btn-edit" @click="editing = true">Редактировать</button>

                <div v-else class="edit-buttons">
                  <button class="btn-save" @click="save">Сохранить</button>
                  <button class="btn-cancel" @click="cancelEdit">Отмена</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Правая часть -->
          <div class="right-info">
            <!-- Первый контейнер -->
            <div class="right-top inner-box">
              <div class="field-group">
                <label>Фамилия</label>
                <input v-if="editing" v-model="form.last_name" class="field-input" />
                <span v-else>{{ form.last_name }}</span>
              </div>

              <div class="field-group">
                <label>Имя</label>
                <input v-if="editing" v-model="form.first_name" class="field-input" />
                <span v-else>{{ form.first_name }}</span>
              </div>

              <div class="field-group">
                <label>Отчество</label>
                <input v-if="editing" v-model="form.middle_name" class="field-input" />
                <span v-else>{{ form.middle_name }}</span>
              </div>

              <div class="field-group">
                <label>День рождения</label>
                <input v-if="editing" type="date" v-model="form.birth_date" class="field-input" />
                <span v-else>{{ form.birth_date }}</span>
              </div>
            </div>

            <!-- Второй контейнер -->
            <div class="right-bottom inner-box">
              <div class="field-group">
                <label>Почта</label>
                <span class="disabled">{{ form.email }}</span>
              </div>

              <div class="field-group">
                <label>Телефон</label>
                <input v-if="editing" v-model="form.phone" class="field-input" />
                <span v-else>{{ form.phone }}</span>
              </div>

              <div class="field-group">
                <label>ВКонтакте</label>
                <input v-if="editing" v-model="form.vk" class="field-input" />
                <span v-else>{{ form.vk }}</span>
              </div>

              <div class="field-group">
                <label>Телеграм</label>
                <input v-if="editing" v-model="form.telegram" class="field-input" />
                <span v-else>{{ form.telegram }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Контейнер интересов -->
        <div class="extra-box inner-box">
          <label>Интересы</label>
          <textarea v-if="editing" v-model="form.interests" class="interests-textarea"></textarea>
          <p v-else>{{ form.interests }}</p>
        </div>

        <!-- Информация о курсе -->
        <div class="course-card inner-box">
          <h2>Информация о курсе</h2>
          <div class="course-row">
            <label>Твой репетитор</label>
            <p>{{ auth.user?.tutor_full_name || "Не назначен" }}</p>
          </div>
          <div class="course-row">
            <label>Название курса</label>
            <p>{{ auth.user?.course_name || "—" }}</p>
          </div>
          <button class="btn-details">Подробности курса</button>
        </div>

      </div>
    </div>
  </div>
</template>



<style scoped>
/* ====== Общие настройки ====== */
/* Новый контейнер для страницы с фоном */
.profile-page-container {
  background-color: #F4886D;
  border-radius: 14%;
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  width: 100%;
  height: 100%;
  max-width: 1100px; /* Ограничиваем ширину, чтобы фон не растягивался слишком сильно */
  margin: 0 auto; /* Центрируем */
}

/* Обновим внешний контейнер profile-page */
.profile-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: 'KyivType Titling', serif;
  width: 100%; /* Это позволяет контейнеру быть гибким */
}

/* ====== Хедер ====== */
.main-header.fixed-header {
  position: fixed;
  top: 0;
  width: 100%;
  height: 80px;
  background: #01072c;
  border-bottom: 2px solid #ff0044;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  z-index: 999;
}

.header-logo {
  height: 38px;
}

.user-name {
  font-family: 'JetBrains Mono', monospace;
  color: #ff0044;
  font-weight: 700;
  font-size: 20px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #ff0044;
  object-fit: cover;
}

.menu-icon {
  width: 32px;
  height: 32px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.menu-icon:hover {
  opacity: 0.7;
}

/* ====== Контейнер контента ====== */
.profile-content {
  margin-top: 120px;
  width: 100%;
  max-width: 1050px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}

/* ====== Основная карточка профиля ====== */
.profile-card {
  display: flex;
  justify-content: center;
  background: #fbb599;
  border-radius: 28px;
  padding: 40px 50px;
  width: 950px;
  gap: 30px;
  box-shadow: 0 0 25px rgba(0, 0, 0, 0.35);
}

/* Левая колонка */
.left-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 230px;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 180px;
  height: 180px;
  object-fit: cover;
  border-radius: 20px;
  border: 3px solid #fff;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.25);
}

.role-text {
  font-size: 18px;
  color: #3b1d10;
  margin: 10px 0;
}

.btn-change-avatar {
  background: #8a3f30;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: 0.25s;
}

.btn-change-avatar:hover {
  background: #703428;
}

/* Кнопки */
.action-buttons {
  margin-top: 20px;
  width: 100%;
}

.btn-edit,
.btn-save,
.btn-cancel {
  width: 100%;
  border: none;
  padding: 10px 14px;
  border-radius: 12px;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
  transition: 0.25s;
  margin-bottom: 10px;
}

.btn-edit,
.btn-save {
  background: #b24c3e;
}

.btn-edit:hover,
.btn-save:hover {
  background: #983e32;
}

.btn-cancel {
  background: #6d718b;
}

.btn-cancel:hover {
  background: #585c74;
}

/* ====== Правая колонка ====== */
.right-column {
  flex: 1;
  background: #fbb599;
  border-radius: 20px;
  padding: 25px 30px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.1);
}

.fields-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px 30px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field-label {
  font-weight: bold;
  font-size: 16px;
  color: #2f1b10;
}

.field-input,
.interests-textarea {
  width: 100%;
  border: none;
  border-radius: 10px;
  background: #ffe8d5;
  padding: 8px 10px;
  font-size: 15px;
  font-family: 'KyivType Titling', serif;
  transition: background 0.25s;
}

.field-input:focus,
.interests-textarea:focus {
  outline: none;
  background: #fff9de;
}

.field-text {
  font-size: 15px;
  color: #2a2420;
}

.field-text.disabled {
  opacity: 0.6;
}

.interests-group {
  grid-column: 1 / -1;
}

.interests-textarea {
  min-height: 70px;
  resize: vertical;
}

/* ====== Карточка курса ====== */
.course-card {
  width: 850px;
  background: #fbc4a4;
  border-radius: 22px;
  padding: 30px 40px;
  box-shadow: 0 0 25px rgba(0, 0, 0, 0.35);
  text-align: center;
}

.course-card h2 {
  font-size: 26px;
  color: #361a10;
  margin-bottom: 15px;
}

.course-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 40px;
  font-size: 16px;
}

.course-row label {
  font-weight: bold;
  color: #2f1b10;
}

.course-row p {
  color: #50392f;
}

.btn-details {
  background: #b24c3e;
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 15px;
  padding: 10px 20px;
  margin-top: 20px;
  cursor: pointer;
  transition: 0.25s;
}

.btn-details:hover {
  background: #983e32;
}

/* ====== Адаптив ====== */
@media (max-width: 1024px) {
  .profile-card {
    flex-direction: column;
    align-items: center;
    width: 95%;
  }

  .right-column {
    width: 100%;
  }

  .fields-grid {
    grid-template-columns: 1fr;
  }

  .course-card {
    width: 95%;
  }
}

@media (max-width: 768px) {
  .main-header {
    padding: 0 20px;
  }

  .user-name {
    font-size: 16px;
  }

  .profile-card,
  .course-card {
    padding: 20px;
  }

  .course-row {
    flex-direction: column;
    text-align: left;
    gap: 5px;
  }
}

.main-info-container {
  display: flex;
  gap: 30px;
  width: 950px;
}

.inner-box {
  background: #fedac4;
  border-radius: 20px;
  padding: 20px 25px;
  box-shadow: 0 0 10px rgba(0,0,0,0.15);
}

/* Левая часть */
.left-info {
  flex: 1;
  display: flex;
  justify-content: center;
}

.left-info .inner-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.left-info h2 {
  font-size: 20px;
  font-weight: bold;
}

.avatar {
  width: 150px;
  height: 150px;
  border-radius: 15px;
  border: 3px solid #fff;
  object-fit: cover;
}

.role-text {
  font-size: 16px;
  color: #3b1d10;
}

/* Правая часть */
.right-info {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-info .inner-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-group {
  display: flex;
  justify-content: space-between;
  font-size: 15px;
}

/* Контейнер под основной частью */
.extra-box {
  width: 950px;
  margin-top: 20px;
}

/* Курс */
.course-card {
  width: 950px;
  text-align: center;
  margin-top: 20px;
}

/* Кнопки */
.btn-edit,
.btn-save,
.btn-cancel,
.btn-details {
  border: none;
  border-radius: 10px;
  padding: 10px 20px;
  background: #b24c3e;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
  transition: 0.25s;
}

.btn-edit:hover,
.btn-save:hover,
.btn-details:hover {
  background: #983e32;
}

.btn-cancel {
  background: #6d718b;
}

.btn-cancel:hover {
  background: #585c74;
}

.edit-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}


</style>
