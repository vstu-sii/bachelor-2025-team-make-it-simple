<script setup>
import { onMounted, onUnmounted, reactive, ref, computed } from "vue";
import { useAuthStore } from "../stores/auth";
import api from "../api/axios";
import { useRouter } from "vue-router";
import StudentProfileComponents from "./StudentProfileComponents.vue";
import TutorProfileComponents from "./TutorProfileComponents.vue";

onMounted(() => {
  // Добавляем класс к body при входе на страницу профиля
  document.body.classList.add('profile-page')
})

onUnmounted(() => {
  // Убираем класс при выходе со страницы профиля
  document.body.classList.remove('profile-page')
})


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

// Определяем роль пользователя
const userRole = computed(() => auth.user?.role || "");
const isStudent = computed(() => userRole.value === "Ученик");
const isTutor = computed(() => userRole.value === "Репетитор");

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

        <!-- Основной контейнер с основной информацией -->
        <div class="main-info-outer-container">
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
              <!-- ФИО и дата рождения -->
              <div class="right-top inner-box">
                <div class="field-column-group">
                  <div class="field-row">
                    <label>Фамилия</label>
                    <div v-if="editing" class="field-input-container">
                      <input v-model="form.last_name" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.last_name }}</div>
                  </div>

                  <div class="field-row">
                    <label>Имя</label>
                    <div v-if="editing" class="field-input-container">
                      <input v-model="form.first_name" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.first_name }}</div>
                  </div>

                  <div class="field-row">
                    <label>Отчество</label>
                    <div v-if="editing" class="field-input-container">
                      <input v-model="form.middle_name" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.middle_name }}</div>
                  </div>

                  <div class="field-row">
                    <label>Дата рождения</label>
                    <div v-if="editing" class="field-input-container">
                      <input type="date" v-model="form.birth_date" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.birth_date }}</div>
                  </div>
                </div>
              </div>

              <!-- Контакты -->
              <div class="right-bottom inner-box">
                <div class="field-column-group">
                  <div class="field-row">
                    <label>Электронная почта</label>
                    <div class="field-value-box disabled">{{ form.email }}</div>
                  </div>

                  <div class="field-row">
                    <label>Телефон</label>
                    <div v-if="editing" class="field-input-container">
                      <input v-model="form.phone" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.phone }}</div>
                  </div>

                  <div class="field-row">
                    <label>ВКонтакте</label>
                    <div v-if="editing" class="field-input-container">
                      <input v-model="form.vk" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.vk }}</div>
                  </div>

                  <div class="field-row">
                    <label>Telegram</label>
                    <div v-if="editing" class="field-input-container">
                      <input v-model="form.telegram" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.telegram }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Контейнер интересов -->
          <div class="extra-box inner-box">
            <div class="interests-column-box">
              <label>Интересы</label>
              <div v-if="editing" class="field-input-container">
                <textarea v-model="form.interests" class="interests-textarea"></textarea>
              </div>
              <div v-else class="interests-value">{{ form.interests }}</div>
            </div>
          </div>
        </div>

        <!-- Динамическая часть в зависимости от роли -->
        <component :is="isStudent ? StudentProfileComponents : TutorProfileComponents" 
                   :user="auth.user" 
                   v-if="userRole" />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ====== Общие настройки ====== */
.profile-page-container {
  background-color: #F4886D;
  border-radius: 14%;
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  width: 100%;
  /* ИЗМЕНИТЬ: убрать height: 100% */
  min-height: 100vh; /* ВМЕСТО height: 100% */
  max-width: 1100px;
  margin: 0 auto;
}

.profile-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: 'KyivType Titling', serif;
  width: 100%;
  /* ДОБАВИТЬ: разрешить рост */
  flex-grow: 1;
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
  /* ДОБАВИТЬ: разрешить прокрутку если нужно */
  overflow-y: visible;
}

/* ====== ЦВЕТ ТЕКСТА ====== */
.profile-content {
  color: #592012;
}

.profile-content label,
.profile-content h2,
.profile-content p,
.profile-content span,
.profile-content .role-text,
.profile-content .course-label,
.profile-content .course-value {
  color: #592012;
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

.header-left {
  display: flex;
  align-items: center;
}

.header-logo {
  height: 38px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
  height: 100%;
}

.user-name {
  font-family: 'JetBrains Mono', monospace;
  color: #ff0044;
  font-weight: 700;
  font-size: 20px;
  display: flex;
  align-items: center;
  height: 100%;
}

.user-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2px solid #ff0044;
  object-fit: cover;
  display: flex;
  align-items: center;
}

.menu-icon {
  width: 32px;
  height: 32px;
  cursor: pointer;
  transition: opacity 0.3s;
  display: flex;
  align-items: center;
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

/* ====== НОВЫЕ КОНТЕЙНЕРЫ ====== */

/* Внешний контейнер для основной информации */
.main-info-outer-container {
  background: #fbb599;
  border-radius: 25px;
  padding: 30px;
  width: 1000px;
  box-shadow: 0 0 20px rgba(0,0,0,0.25);
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Внешний контейнер для информации о курсе */
.course-outer-container {
  background: #fbb599;
  border-radius: 25px;
  padding: 30px;
  width: 1000px;
  box-shadow: 0 0 20px rgba(0,0,0,0.25);
}

.course-outer-container .course-card {
  background: #fedac4;
  border-radius: 20px;
  padding: 30px 40px;
  text-align: center;
  box-shadow: 0 0 15px rgba(0,0,0,0.2);
  width: 100%;
  margin: 0;
}

/* ====== Основная карточка профиля ====== */
.main-info-container {
  display: flex;
  gap: 30px;
  width: 100%;
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
}

/* Правая часть */
.right-info {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ===== КНОПКИ ===== */
.btn-edit {
  background: #f4886d !important;
  color: #411616 !important;
}

.btn-save {
  background: #b24c3e !important;
}

.btn-edit:hover {
  background: #cf7058 !important;
}

.btn-save:hover {
  background: #983e32 !important;
}

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
  font-weight: bold;
  cursor: pointer;
  transition: 0.25s;
  margin-bottom: 10px;
  font-family: 'KyivType Titling', serif;
}

.btn-save,
.btn-cancel {
  color: #fff;
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

/* ===== КОЛОНОЧНЫЕ ПОЛЯ (ФИО / Контакты) ===== */
.field-column-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* ЖИРНЫЙ ШРИФТ ДЛЯ ЗНАЧЕНИЙ */
.field-value-box {
  background: #d8b9a7;
  padding: 6px 12px;
  border-radius: 8px;
  min-width: 180px;
  text-align: left;
  font-weight: bold !important;
}

.field-value-box.disabled {
  opacity: 0.7;
}

.field-input-container {
  min-width: 180px;
}

.field-input {
  width: 100%;
  border: none;
  border-radius: 8px;
  background: #ffe8d5;
  padding: 6px 12px;
  font-size: 15px;
  font-family: 'KyivType Titling', serif;
  transition: background 0.25s;
  color: #592012;
  font-weight: bold;
}

.field-input:focus {
  outline: none;
  background: #fff9de;
}

/* ===== ИНТЕРЕСЫ ===== */
.interests-column-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.interests-value {
  background: #d8b9a7;
  padding: 10px 14px;
  border-radius: 8px;
  min-height: 60px;
  font-weight: normal;
}

.interests-textarea {
  width: 100%;
  border: none;
  border-radius: 8px;
  background: #ffe8d5;
  padding: 10px 14px;
  font-size: 15px;
  font-family: 'KyivType Titling', serif;
  min-height: 60px;
  resize: vertical;
  transition: background 0.25s;
  color: #592012;
  font-weight: normal;
}

.interests-textarea:focus {
  outline: none;
  background: #fff9de;
}

/* Контейнер под основной частью */
.extra-box {
  width: 100%;
  margin-top: 0;
}

/* ===== Адаптив ====== */
@media (max-width: 1024px) {
  .main-info-outer-container {
    width: 95%;
    padding: 20px;
  }

  .main-info-container {
    flex-direction: column;
    align-items: center;
    width: 100%;
  }

  .right-info {
    width: 100%;
  }

  .extra-box {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .main-header {
    padding: 0 20px;
  }

  .user-name {
    font-size: 16px;
  }

  .profile-page-container {
    padding: 20px;
  }

  .field-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }

  .field-value-box,
  .field-input-container {
    min-width: 100%;
    width: 100%;
  }
}
</style>