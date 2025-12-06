<template>
    <div class="lesson-page">
      <!-- Хедер -->
      <AppHeader :show-back-button="true" />
      
      <!-- Кнопка "назад" -->
      <button class="back-btn" @click="goBack">
        <img src="/src/assets/arrow-back.svg" alt="back" />
      </button>
  
      <!-- Название урока -->
      <div class="lesson-title-container">
        <h1 class="lesson-title">Урок №{{ lessonId }} курса {{ courseTitle }}</h1>
        <div class="lesson-title-divider"></div>
      </div>
  
      <!-- Основной контейнер -->
      <div class="main-container">
        <div class="inner-container">
          <!-- Простая информация об уроке -->
          <div class="lesson-info">
            <h2>Информация об уроке</h2>
            <p><strong>ID урока:</strong> {{ lessonId }}</p>
            <p><strong>ID курса:</strong> {{ courseId }}</p>
            <p><strong>ID ученика:</strong> {{ studentId }}</p>
            <p><strong>URL:</strong> /course/{{ courseId }}/lesson/{{ lessonId }}</p>
            <p>Здесь будет содержимое урока...</p>
          </div>
  
          <!-- Кнопки навигации -->
          <div class="navigation-buttons">
            <button class="nav-btn prev-btn" @click="goToPrevLesson">
              ← Предыдущий урок
            </button>
            <button class="nav-btn next-btn" @click="goToNextLesson">
              Следующий урок →
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useAuthStore } from "../stores/auth";
  import api from "../api/axios";
  import AppHeader from "../components/Header.vue";
  
  const route = useRoute();
  const router = useRouter();
  const auth = useAuthStore();
  
  // Получаем параметры из URL
  const lessonId = ref(parseInt(route.params.id));
  const courseId = ref(route.query.courseId ? parseInt(route.query.courseId) : null);
  const studentId = ref(route.query.studentId ? parseInt(route.query.studentId) : null);
  
  // Состояния
  const courseTitle = ref("...");
  const lessonData = ref(null);
  const loading = ref(false);
  
  // Навигация
  function goBack() {
    if (courseId.value) {
      router.push(`/course/${courseId.value}`);
    } else {
      router.back();
    }
  }
  
  function goToPrevLesson() {
    if (lessonId.value > 1) {
      const prevLessonId = lessonId.value - 1;
      router.push(`/lesson/${prevLessonId}?courseId=${courseId.value}&studentId=${studentId.value}`);
    }
  }
  
  function goToNextLesson() {
    const nextLessonId = lessonId.value + 1;
    router.push(`/lesson/${nextLessonId}?courseId=${courseId.value}&studentId=${studentId.value}`);
  }
  
  // Загрузка данных урока
  async function loadLessonData() {
    if (!lessonId.value) return;
    
    try {
      loading.value = true;
      
      // Загружаем информацию об уроке
      // const response = await api.get(`/lessons/${lessonId.value}`);
      // lessonData.value = response.data;
      
      // Загружаем информацию о курсе
      if (courseId.value) {
        const courseResponse = await api.get(`/courses/${courseId.value}`);
        courseTitle.value = courseResponse.data.title || `Курс ${courseId.value}`;
      } else {
        courseTitle.value = "Неизвестный курс";
      }
      
    } catch (error) {
      console.error("Ошибка загрузки данных урока:", error);
      courseTitle.value = "Ошибка загрузки";
    } finally {
      loading.value = false;
    }
  }
  
  // Инициализация
  onMounted(() => {
    loadLessonData();
    console.log("LessonPage загружена:", {
      lessonId: lessonId.value,
      courseId: courseId.value,
      studentId: studentId.value,
      query: route.query
    });
  });
  </script>
  
  <style scoped>
  .lesson-page {
    width: 100%;
    min-height: 100vh;
    background: #0b1444;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-bottom: 40px;
    position: relative;
  }
  
  /* Кнопка "назад" */
  .back-btn {
    position: absolute;
    left: 50%;
    transform: translateX(calc(-50% - 535px));
    top: 190px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 10px;
    transition: transform 0.3s;
    z-index: 10;
  }
  
  .back-btn:hover {
    transform: translateX(calc(-50% - 535px - 5px));
  }
  
  .back-btn img {
    width: 80px;
    height: 80px;
  }
  
  /* Название урока */
  .lesson-title-container {
    position: relative;
    margin-top: 130px;
    margin-bottom: 20px;
    text-align: center;
    width: 95%;
    max-width: 1100px;
  }
  
  .lesson-title {
    font-family: 'Arial', Georgia, serif;
    font-size: 32px;
    font-weight: bold;
    color: #fbb599;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    margin: 0;
    padding: 0 20px;
    letter-spacing: 1px;
  }
  
  .lesson-title-divider {
    height: 3px;
    background: linear-gradient(to right, transparent, #fbb599, transparent);
    width: 100%;
    max-width: 500px;
    margin: 10px auto 0 auto;
    border-radius: 2px;
  }
  
  /* Основной контейнер */
  .main-container {
    width: 95%;
    max-width: 1100px;
    background: #F4886D;
    border-radius: 25px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    position: relative;
    margin-top: 10px;
  }
  
  /* Внутренний контейнер */
  .inner-container {
    background: #fbb599;
    border-radius: 20px;
    padding: 30px;
    display: flex;
    flex-direction: column;
    gap: 25px;
  }
  
  /* Информация об уроке */
  .lesson-info {
    background: #fedac4;
    border-radius: 15px;
    padding: 25px;
    border: 2px solid #F4886D;
  }
  
  .lesson-info h2 {
    font-family: 'Arial', Georgia, serif;
    font-size: 24px;
    font-weight: bold;
    color: #592012;
    margin-bottom: 20px;
    text-align: center;
  }
  
  .lesson-info p {
    font-family: 'Arial', Georgia, serif;
    font-size: 16px;
    color: #592012;
    margin-bottom: 10px;
    line-height: 1.6;
  }
  
  /* Кнопки навигации */
  .navigation-buttons {
    display: flex;
    justify-content: space-between;
    gap: 20px;
  }
  
  .nav-btn {
    background: #F4886D;
    color: #592012;
    border: none;
    border-radius: 10px;
    padding: 15px 25px;
    cursor: pointer;
    font-family: 'Arial', Georgia, serif;
    font-weight: bold;
    transition: all 0.3s;
    font-size: 16px;
    flex: 1;
  }
  
  .nav-btn:hover:not(:disabled) {
    background: #E0785D;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(244, 136, 109, 0.3);
  }
  
  .nav-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .prev-btn {
    text-align: left;
  }
  
  .next-btn {
    text-align: right;
  }
  
  /* Адаптивность */
  @media (max-width: 1200px) {
    .back-btn {
      left: 10px;
      transform: none;
    }
    
    .back-btn:hover {
      transform: translateX(-5px);
    }
    
    .lesson-title {
      font-size: 28px;
    }
  }
  
  @media (max-width: 1024px) {
    .main-container {
      width: 98%;
      padding: 25px;
    }
    
    .back-btn {
      left: 30px;
      top: 90px;
    }
    
    .inner-container {
      padding: 25px;
    }
    
    .lesson-title-container {
      margin-top: 120px;
      margin-bottom: 15px;
    }
    
    .lesson-title {
      font-size: 24px;
    }
  }
  
  @media (max-width: 768px) {
    .back-btn {
      left: 20px;
      top: 80px;
    }
    
    .back-btn img {
      width: 60px;
      height: 60px;
    }
    
    .main-container {
      margin-top: 5px;
      padding: 20px;
    }
    
    .inner-container {
      padding: 20px;
      gap: 20px;
    }
    
    .lesson-title-container {
      margin-top: 110px;
      margin-bottom: 10px;
    }
    
    .lesson-title {
      font-size: 20px;
      padding: 0 15px;
    }
    
    .navigation-buttons {
      flex-direction: column;
    }
    
    .nav-btn {
      width: 100%;
      text-align: center;
    }
  }
  
  @media (max-width: 480px) {
    .back-btn {
      left: 15px;
      top: 70px;
    }
    
    .back-btn img {
      width: 50px;
      height: 50px;
    }
    
    .main-container {
      padding: 15px;
    }
    
    .inner-container {
      padding: 15px;
    }
    
    .lesson-title-container {
      margin-top: 100px;
      margin-bottom: 10px;
    }
    
    .lesson-title {
      font-size: 18px;
      padding: 0 10px;
    }
    
    .lesson-title-divider {
      max-width: 300px;
    }
    
    .lesson-info {
      padding: 15px;
    }
    
    .lesson-info h2 {
      font-size: 20px;
    }
    
    .lesson-info p {
      font-size: 14px;
    }
    
    .nav-btn {
      padding: 12px 20px;
      font-size: 14px;
    }
  }
  </style>