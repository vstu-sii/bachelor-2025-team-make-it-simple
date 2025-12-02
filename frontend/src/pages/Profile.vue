<script setup>
import { onMounted, onUnmounted, reactive, ref, computed, watch } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRoute, useRouter } from "vue-router";
import api from "../api/axios";
import StudentProfileComponents from "./StudentProfileComponents.vue";
import TutorProfileComponents from "./TutorProfileComponents.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

// Добавляем состояние загрузки аутентификации
const authLoading = ref(true);

// Определяем, чей профиль загружать
const profileUserId = computed(() => {
  return route.params.id ? parseInt(route.params.id) : auth.user?.user_id;
});

const isOwnProfile = computed(() => {
  return !route.params.id || parseInt(route.params.id) === auth.user?.user_id;
});

const editing = ref(false);
const fileInput = ref(null);
const loading = ref(true);
const error = ref(null);

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
  course_info: null,
  tutor_full_name: null,
  courses_count: null,
  students_count: null
});

// Аватарка по умолчанию
const defaultAvatar = "/src/assets/avatars/default_avatar.svg";

// Определяем роль пользователя
const userRole = computed(() => form.role || "");
const isStudent = computed(() => userRole.value === "Ученик");
const isTutor = computed(() => userRole.value === "Репетитор");

onMounted(async () => {
  document.body.classList.add('profile-page');
  
  // Загружаем данные пользователя если есть токен
  const token = localStorage.getItem("token");
  if (token && !auth.user) {
    try {
      await auth.fetchMe();
    } catch (err) {
      console.error("Ошибка загрузки данных пользователя:", err);
    }
  }
  authLoading.value = false;
});

onUnmounted(() => {
  document.body.classList.remove('profile-page');
});

// Функция загрузки профиля
async function loadProfile(userId) {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await api.get(`/auth/${userId}/with_course`);
    Object.assign(form, response.data);
    loading.value = false;
  } catch (err) {
    console.error("Ошибка загрузки профиля:", err);
    error.value = "Не удалось загрузить профиль пользователя";
    loading.value = false;
    
    if (!isOwnProfile.value && err.response?.status === 404) {
      router.push("/profile");
    }
  }
}

// Следим за изменением параметра маршрута
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadProfile(parseInt(newId));
  } else if (auth.user) {
    loadProfile(auth.user.user_id);
  }
}, { immediate: true });

// Следим за изменением текущего пользователя
watch(() => auth.user, (newUser) => {
  if (newUser && !route.params.id) {
    loadProfile(newUser.user_id);
  }
});

async function save() {
  if (!isOwnProfile.value) {
    alert("Вы не можете редактировать чужой профиль");
    return;
  }

  if (!auth.user) return;

  try {
    const res = await api.put(`/auth/${auth.user.user_id}`, {
      last_name: form.last_name,
      first_name: form.first_name,
      middle_name: form.middle_name,
      birth_date: form.birth_date,
      phone: form.phone,
      telegram: form.telegram,
      vk: form.vk,
      interests: form.interests
    });
    
    // Обновляем данные текущего пользователя
    auth.user = { ...auth.user, ...res.data };
    
    // Перезагружаем профиль
    await loadProfile(auth.user.user_id);
    
    editing.value = false;
    alert("Профиль обновлён");
  } catch (err) {
    console.error(err);
    alert("Ошибка обновления");
  }
}

function triggerFileInput() {
  if (!isOwnProfile.value) {
    alert("Вы не можете менять аватар чужого профиля");
    return;
  }
  fileInput.value?.click();
}

async function handleAvatarUpload(event) {
  if (!isOwnProfile.value) {
    alert("Вы не можете менять аватар чужого профиля");
    return;
  }
  
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
    
    // Обновляем аватар в store текущего пользователя
    if (isOwnProfile.value && auth.user) {
      auth.user.avatar_path = response.data.avatar_path;
    }
    
    alert('Аватар успешно обновлен!');

  } catch (err) {
    console.error('Ошибка загрузки аватарки:', err);
    alert('Ошибка загрузки аватарки');
  }
}

function cancelEdit() {
  editing.value = false;
  loadProfile(profileUserId.value);
}
</script>

<template>
  <div class="profile-page-container">
    <div class="profile-page">
      
      <!-- Хедер (всегда показываем) -->
      <header class="main-header fixed-header">
        <div class="header-left">
          <img src="/src/assets/logo.svg" alt="Make It Simple" class="header-logo" @click="router.push('/profile')" style="cursor: pointer;" />
          <!-- Кнопка "Вернуться" в хедере для чужих профилей -->
          <button v-if="!isOwnProfile && auth.user" @click="router.push('/profile')" class="back-to-profile-header-btn">
            ← Мой профиль
          </button>
        </div>
        
        <!-- Правая часть хедера - всегда показываем данные авторизованного пользователя или ничего -->
        <div class="header-right" v-if="auth.user">
          <span class="user-name" @click="router.push('/profile')" style="cursor: pointer;">
            {{ auth.user.first_name }} {{ auth.user.last_name?.charAt(0) }}.
          </span>
          <img :src="auth.user.avatar_path || defaultAvatar" alt="avatar" class="user-avatar" @click="router.push('/profile')" style="cursor: pointer;" />
        </div>
        
        <!-- Если пользователь не авторизован, ничего не показываем в правой части -->
        <!-- Убираем кнопку "Войти" -->
      </header>

      <!-- Показываем индикатор загрузки аутентификации -->
      <div v-if="authLoading" class="auth-loading">
        <p>Проверка авторизации...</p>
      </div>

      <div v-else class="profile-content" v-if="!loading && !error">
        
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

                <!-- Для репетитора показываем статистику -->
                <div v-if="isTutor && form.courses_count !== null" class="tutor-stats">
                  <div class="stat-item">
                    <span class="stat-value">{{ form.courses_count }}</span>
                    <span class="stat-label">курсов</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ form.students_count }}</span>
                    <span class="stat-label">учеников</span>
                  </div>
                </div>

                <!-- Кнопки редактирования только для своего профиля -->
                <div class="action-buttons" v-if="isOwnProfile && auth.user">
                  <button v-if="!editing" class="btn-edit" @click="editing = true">Редактировать</button>

                  <div v-else class="edit-buttons">
                    <button class="btn-save" @click="save">Сохранить</button>
                    <button class="btn-cancel" @click="cancelEdit">Отмена</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Правая часть с данными -->
            <div class="right-info">
              <!-- ФИО и дата рождения -->
              <div class="right-top inner-box">
                <div class="field-column-group">
                  <div class="field-row">
                    <label>Фамилия</label>
                    <div v-if="editing && isOwnProfile && auth.user" class="field-input-container">
                      <input v-model="form.last_name" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.last_name }}</div>
                  </div>

                  <div class="field-row">
                    <label>Имя</label>
                    <div v-if="editing && isOwnProfile && auth.user" class="field-input-container">
                      <input v-model="form.first_name" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.first_name }}</div>
                  </div>

                  <div class="field-row">
                    <label>Отчество</label>
                    <div v-if="editing && isOwnProfile && auth.user" class="field-input-container">
                      <input v-model="form.middle_name" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.middle_name }}</div>
                  </div>

                  <div class="field-row">
                    <label>Дата рождения</label>
                    <div v-if="editing && isOwnProfile && auth.user" class="field-input-container">
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
                    <div v-if="editing && isOwnProfile && auth.user" class="field-input-container">
                      <input v-model="form.phone" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.phone }}</div>
                  </div>

                  <div class="field-row">
                    <label>ВКонтакте</label>
                    <div v-if="editing && isOwnProfile && auth.user" class="field-input-container">
                      <input v-model="form.vk" class="field-input" />
                    </div>
                    <div v-else class="field-value-box">{{ form.vk }}</div>
                  </div>

                  <div class="field-row">
                    <label>Telegram</label>
                    <div v-if="editing && isOwnProfile && auth.user" class="field-input-container">
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
              <div v-if="editing && isOwnProfile && auth.user" class="field-input-container">
                <textarea v-model="form.interests" class="interests-textarea"></textarea>
              </div>
              <div v-else class="interests-value">{{ form.interests || "Интересы не указаны" }}</div>
            </div>
          </div>
        </div>

        <!-- Динамическая часть в зависимости от роли -->
        <component 
          v-if="userRole" 
          :is="isStudent ? StudentProfileComponents : TutorProfileComponents" 
          :user="form"
          :is-own-profile="isOwnProfile"
        />

      </div>

      <!-- Индикатор загрузки профиля -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Загрузка профиля...</p>
      </div>

      <!-- Сообщение об ошибке -->
      <div v-if="error" class="error-container">
        <p>{{ error }}</p>
        <button v-if="auth.user" @click="router.push('/profile')" class="btn-back">Вернуться в свой профиль</button>
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
  min-height: 100vh;
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
  flex-grow: 1;
}

/* Индикатор загрузки аутентификации */
.auth-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  color: #592012;
  font-size: 18px;
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
  gap: 20px;
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

/* Кнопка "Вернуться" в хедере */
.back-to-profile-header-btn {
  background: #6d718b;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'KyivType Titling', serif;
  font-size: 14px;
  transition: background 0.3s;
}

.back-to-profile-header-btn:hover {
  background: #585c74;
}

/* Убираем стили для кнопки "Войти" */
.login-btn {
  display: none;
}

/* Статистика репетитора */
.tutor-stats {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #592012;
}

.stat-label {
  font-size: 12px;
  color: #592012;
  opacity: 0.8;
}

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

/* Индикатор загрузки */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 50vh;
  color: #592012;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #f4886d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Сообщение об ошибке */
.error-container {
  text-align: center;
  padding: 40px;
  color: #592012;
  background: #ffe8d5;
  border-radius: 20px;
  margin: 20px auto;
  max-width: 600px;
}

.error-container p {
  margin-bottom: 20px;
  font-size: 18px;
}

.btn-back {
  background: #f4886d;
  color: #592012;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  font-family: 'KyivType Titling', serif;
}

/* ===== Адаптив ====== */
@media (max-width: 1024px) {
  .main-info-outer-container,
  .course-outer-container {
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
  
  .main-header.fixed-header {
    padding: 0 20px;
  }
}

@media (max-width: 768px) {
  .main-header.fixed-header {
    padding: 0 15px;
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
  
  .tutor-stats {
    flex-direction: column;
    gap: 10px;
  }
  
  .header-left {
    gap: 10px;
  }
  
  .back-to-profile-header-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>