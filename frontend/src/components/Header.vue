<template>
  <header class="main-header fixed-header">
    <div class="header-left">
      <img src="/src/assets/logo.svg" alt="Make It Simple" class="header-logo" @click="goHome" style="cursor: pointer;" />
      <!-- Кнопка "Вернуться" в хедере для чужих профилей -->
      <button v-if="showBackButton" @click="goToMyProfile" class="back-to-profile-header-btn">
        ← Мой профиль
      </button>
    </div>
    
    <!-- Правая часть хедера -->
    <div class="header-right" v-if="auth.user">
      <span class="user-name" @click="goToProfile" style="cursor: pointer;">
        {{ auth.user.first_name }} {{ auth.user.last_name?.charAt(0) }}.
      </span>
      <img :src="auth.user.avatar_path || defaultAvatar" alt="avatar" class="user-avatar" @click="goToProfile" style="cursor: pointer;" />
      
      <!-- Контейнер для меню -->
      <div class="menu-container" @click="toggleMenu">
        <img src="/src/assets/menu.svg" alt="Меню" class="menu-icon" style="cursor: pointer;"/>
        
        <!-- Выпадающее меню -->
        <div v-if="showMenu" class="dropdown-menu" @click.stop>
          <!-- Динамический компонент меню в зависимости от роли -->
          <component :is="menuComponent" @close="showMenu = false" />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import StudentMenu from "./StudentMenu.vue";
import TutorMenu from "./TutorMenu.vue";

const auth = useAuthStore();
const router = useRouter();
const defaultAvatar = "/src/assets/avatars/default_avatar.svg";

const showMenu = ref(false);

// Пропсы
const props = defineProps({
  showBackButton: {
    type: Boolean,
    default: false
  }
});

// Определяем, какой компонент меню показывать
const menuComponent = computed(() => {
  if (!auth.user) return null;
  return auth.user.role === "Ученик" ? StudentMenu : TutorMenu;
});

// Навигационные функции
function goHome() {
  router.push('/profile');
}

function goToProfile() {
  router.push('/profile');
}

function goToMyProfile() {
  router.push('/profile');
}

// Функция для открытия/закрытия меню
function toggleMenu() {
  showMenu.value = !showMenu.value;
}

// Закрытие меню при клике вне его
function handleClickOutside(event) {
  const menuContainer = document.querySelector('.menu-container');
  if (menuContainer && !menuContainer.contains(event.target)) {
    showMenu.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
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
  position: relative;
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

/* Контейнер для меню */
.menu-container {
  position: relative;
  display: flex;
  align-items: center;
}

/* Иконка меню с уменьшенным размером */
.menu-icon {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

/* ВЫПАДАЮЩЕЕ МЕНЮ - ОСНОВНОЕ ИЗМЕНЕНИЕ */
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  background: #01072c;
  border: 2px solid #ff0044;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
  min-width: 280px; /* УВЕЛИЧЕНО с 200px для отображения информации о пользователе */
  z-index: 1000;
  overflow: hidden;
}

/* Кнопка "Вернуться" в хедере */
.back-to-profile-header-btn {
  background: #6d718b;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Arial', serif;
  font-size: 14px;
  transition: background 0.3s;
}

.back-to-profile-header-btn:hover {
  background: #585c74;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .main-header.fixed-header {
    padding: 0 20px;
  }
  
  .dropdown-menu {
    min-width: 260px; /* АДАПТИВНОЕ значение для планшетов */
  }
}

@media (max-width: 768px) {
  .main-header.fixed-header {
    padding: 0 15px;
  }

  .user-name {
    font-size: 16px;
  }
  
  .menu-icon {
    width: 18px;
    height: 18px;
  }
  
  .header-left {
    gap: 10px;
  }
  
  .back-to-profile-header-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
  
  .header-right {
    gap: 12px;
  }
  
  .dropdown-menu {
    min-width: 240px; /* АДАПТИВНОЕ значение для мобильных */
    right: -10px; /* СДВИГ вправо для лучшего позиционирования на мобильных */
  }
}
</style>