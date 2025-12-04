<template>
    <div class="tutor-menu">
      <!-- Информация о пользователе -->
      <UserInfo :user="auth.user" />
      
      <!-- Разделитель -->
      <div class="menu-divider"></div>
      
      <!-- Пункты меню -->
      <div class="menu-item" @click="goToProfile">
        <span class="menu-text">Профиль</span>
      </div>
      
      <div class="menu-item" @click="goToCreateCourse">
        <span class="menu-text">Создать курс</span>
      </div>
      
      <div class="menu-item" @click="scrollToCoursesSection">
        <span class="menu-text">Мои курсы</span>
        <span v-if="coursesCount > 0" class="badge">{{ coursesCount }}</span>
        <span v-else class="no-courses">—</span>
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
  import UserInfo from "./UserInfoForHeader.vue";
  
  const auth = useAuthStore();
  const router = useRouter();
  const emit = defineEmits(['close']);
  
  // Получаем количество курсов репетитора
  const coursesCount = computed(() => {
    return auth.user?.courses_count || 0;
  });
  
  // При монтировании проверяем, есть ли данные о курсах
  onMounted(async () => {
    // Если нет данных о курсах, но пользователь авторизован - загружаем
    if (auth.user && auth.user.user_id && !auth.user.courses_count) {
      try {
        await auth.fetchUserWithCourseInfo();
      } catch (error) {
        console.error("Ошибка загрузки информации о курсах:", error);
      }
    }
  });
  
  function goToProfile() {
    emit('close');
    // Если мы уже на странице профиля, просто прокручиваем к началу
    if (router.currentRoute.value.path === '/profile') {
      scrollToTop();
    } else {
      router.push('/profile');
    }
  }
  
  function goToCreateCourse() {
    emit('close');
    router.push('/courses/create');
  }
  
  function scrollToCoursesSection() {
    emit('close');
    
    // Если мы уже на странице профиля
    if (router.currentRoute.value.path === '/profile' || 
        router.currentRoute.value.path.startsWith('/profile/')) {
      
      // Прокручиваем к разделу с курсами
      setTimeout(() => {
        const coursesSection = document.querySelector('.course-outer-container');
        if (coursesSection) {
          // Прокручиваем с небольшим отступом сверху (учитывая высоту хедера)
          const headerHeight = 80; // Высота хедера
          const elementPosition = coursesSection.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.pageYOffset - headerHeight - 20;
          
          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });
          
          // Добавляем подсветку секции курсов
          highlightCoursesSection();
        } else {
          // Если секция не найдена, возможно профиль еще загружается
          console.log('Секция курсов не найдена. Попробуйте позже.');
          
          // Можно попробовать перейти на профиль и потом прокрутить
          router.push('/profile');
          setTimeout(() => {
            const retrySection = document.querySelector('.course-outer-container');
            if (retrySection) {
              const retryPosition = retrySection.getBoundingClientRect().top + window.pageYOffset - 100;
              window.scrollTo({
                top: retryPosition,
                behavior: 'smooth'
              });
              highlightCoursesSection();
            }
          }, 500);
        }
      }, 100);
    } else {
      // Если мы не на странице профиля, переходим на профиль и потом прокручиваем
      router.push('/profile');
      
      // Используем setTimeout чтобы дождаться загрузки страницы
      setTimeout(() => {
        const coursesSection = document.querySelector('.course-outer-container');
        if (coursesSection) {
          const elementPosition = coursesSection.getBoundingClientRect().top + window.pageYOffset - 100;
          window.scrollTo({
            top: elementPosition,
            behavior: 'smooth'
          });
          highlightCoursesSection();
        }
      }, 500);
    }
  }
  
  // Функция для подсветки секции курсов
  function highlightCoursesSection() {
    const coursesSection = document.querySelector('.course-outer-container');
    if (coursesSection) {
      // Добавляем класс для анимации подсветки
      coursesSection.classList.add('highlighted');
      
      // Убираем класс через 2 секунды
      setTimeout(() => {
        coursesSection.classList.remove('highlighted');
      }, 2000);
    }
  }
  
  // Функция для прокрутки к началу страницы
  function scrollToTop() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
  
  function logout() {
    emit('close');
    auth.logout();
    router.push('/login');
  }
  </script>
  
  <style scoped>
  .tutor-menu {
    min-width: 250px;
  }
  
  .menu-item {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    cursor: pointer;
    transition: background-color 0.3s;
    color: white;
    font-family: 'KyivType Titling', serif;
    font-size: 14px;
  }
  
  .menu-item:hover {
    background-color: rgba(255, 0, 68, 0.2);
  }
  
  .menu-text {
    flex-grow: 1;
  }
  
  .badge {
    background-color: #ff0044;
    color: white;
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: bold;
    min-width: 20px;
    text-align: center;
  }
  
  .no-courses {
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