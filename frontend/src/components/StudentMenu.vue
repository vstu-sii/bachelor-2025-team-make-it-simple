<template>
    <div class="student-menu">
      <!-- Информация о пользователе -->
      <UserInfo :user="auth.user" />
      
      <!-- Разделитель -->
      <div class="menu-divider"></div>
      
      <!-- Пункты меню -->
      <div class="menu-item" @click="goToProfile">
        <span class="menu-text">Профиль</span>
      </div>
      
      <!-- Показываем "Мой курс" только если есть информация о курсе -->
      <div 
        v-if="hasCourse"
        class="menu-item" 
        @click="goToCourse" 
        :title="`Перейти к моему курсу: ${courseInfo?.course_name || 'Без названия'}`"
      >
        <span class="menu-text">Мой курс</span>
        <span class="course-name">
          {{ courseInfo?.course_name || 'Без названия' }}
        </span>
      </div>
      
      <!-- Если курса нет, показываем не кликаемый элемент -->
      <div 
        v-else
        class="menu-item disabled"
        :title="'У вас пока нет курса'"
      >
        <span class="menu-text">Мой курс</span>
        <span class="no-course">—</span>
      </div>
      
      <div class="menu-divider"></div>
      
      <div class="menu-item logout" @click="logout">
        <span class="menu-text">Выйти</span>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed, onMounted } from "vue";
  import { useAuthStore } from "../stores/auth";
  import { useRouter } from "vue-router";
  import api from "../api/axios";
  import UserInfo from "./UserInfoForHeader.vue";
  
  const auth = useAuthStore();
  const router = useRouter();
  const emit = defineEmits(['close']);
  
  // Получаем информацию о курсе ученика
  const courseInfo = computed(() => {
    return auth.user?.course_info || {};
  });
  
  const hasCourse = computed(() => {
    return courseInfo.value && courseInfo.value.course_id;
  });
  
  // При монтировании проверяем, есть ли данные о курсе
  onMounted(async () => {
    // Если нет данных о курсе, но пользователь авторизован - загружаем
    if (auth.user && !auth.user.course_info && auth.user.user_id) {
      try {
        await auth.fetchUserWithCourseInfo();
      } catch (error) {
        console.error("Ошибка загрузки информации о курсе:", error);
      }
    }
  });
  
  function goToProfile() {
    emit('close');
    router.push('/profile');
  }
  
  async function goToCourse() {
    emit('close');
    
    // Дополнительная проверка на всякий случай
    if (!hasCourse.value) {
      // Если нет курса, перенаправляем на страницу поиска курсов
      router.push('/courses');
      return;
    }
  
    if (auth.user?.user_id && courseInfo.value?.course_id) {
      try {
        router.push(`/course/${courseInfo.value.course_id}`);
      } catch (error) {
        console.error("Ошибка при переходе к курсу:", error);
        router.push('/courses');
      }
    }
  }
  
  // Альтернатива: если нужно сделать возможность записи на курс при клике на отключенную кнопку
  function goToCoursesCatalog() {
    emit('close');
    router.push('/courses');
  }
  
  function logout() {
    emit('close');
    auth.logout();
    router.push('/login');
  }
  </script>
  
  <style scoped>
  .student-menu {
    min-width: 250px;
  }
  
  .menu-item {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    cursor: pointer;
    transition: background-color 0.3s;
    color: white;
    font-family: 'Arial', serif;
    font-size: 14px;
  }
  
  .menu-item:hover:not(.disabled) {
    background-color: rgba(255, 0, 68, 0.2);
  }
  
  .menu-item.disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }
  
  .menu-text {
    flex-grow: 1;
  }
  
  .course-name {
    font-size: 12px;
    color: #ff0044;
    margin-left: 10px;
    opacity: 0.9;
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-weight: bold;
  }
  
  .no-course {
    font-size: 12px;
    color: #888;
    margin-left: 10px;
    font-style: italic;
  }
  
  .menu-divider {
    height: 1px;
    background-color: rgba(255, 0, 68, 0.3);
    margin: 0;
  }
  
  .logout {
    color: #ff6b6b;
  }
  
  .logout:hover {
    background-color: rgba(255, 107, 107, 0.2);
  }
  </style>