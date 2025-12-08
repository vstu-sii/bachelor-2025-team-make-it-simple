<template>
    <div class="test-page">
      <AppHeader :show-back-button="true" />
      
      <button class="back-btn" @click="goBack">
        <img src="/src/assets/arrow-back.svg" alt="back" />
      </button>
  
      <div class="test-title-container">
        <h1 class="test-title">Тест урока</h1>
        <div class="test-title-divider"></div>
        <p class="lesson-info">{{ lessonTitle }}</p>
      </div>
  
      <div class="main-container">
        <div class="inner-container">
          <div class="test-info">
            <h2>Информация о тесте урока</h2>
            <div class="info-content">
              <p><strong>Урок:</strong> {{ lessonTitle }}</p>
              <p><strong>Количество вопросов:</strong> {{ questions?.length || 0 }}</p>
              <p><strong>Курс:</strong> {{ courseTitle }}</p>
            </div>
          </div>
  
          <div class="test-content">
            <h2>Вопросы теста</h2>
            <div class="questions-placeholder">
              <p>Здесь будет отображаться содержимое теста урока</p>
              <p>Lesson ID: {{ lessonId }}</p>
              <p>Course ID: {{ courseId }}</p>
              <div v-if="questions && questions.length > 0">
                <h3>Вопросы:</h3>
                <ul>
                  <li v-for="(question, index) in questions" :key="index">
                    {{ question }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
  
          <button class="submit-btn" @click="submitTest">
            Завершить тест
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import AppHeader from "../components/Header.vue";
  
  const route = useRoute();
  const router = useRouter();
  
  const lessonId = ref(null);
  const courseId = ref(null);
  const lessonTitle = ref("");
  const courseTitle = ref("");
  const questions = ref([]);
  
  onMounted(() => {
    lessonId.value = route.params.lessonId;
    courseId.value = route.query.courseId;
    
    // Здесь можно загрузить данные теста урока
    // Для демонстрации используем query параметры
    lessonTitle.value = route.query.lessonTitle || `Урок ${lessonId.value}`;
    courseTitle.value = route.query.courseTitle || `Курс ${courseId.value}`;
    
    // Пример вопросов из testData
    if (route.query.testData) {
      try {
        const testData = JSON.parse(route.query.testData);
        questions.value = testData.questions || [];
      } catch (e) {
        console.error("Ошибка парсинга testData:", e);
      }
    }
  });
  
  function goBack() {
    if (courseId.value && lessonId.value) {
      router.push({
        path: `/lesson/${lessonId.value}`,
        query: { courseId: courseId.value }
      });
    } else {
      router.back();
    }
  }
  
  function submitTest() {
    alert("Тест урока завершен!");
    goBack();
  }
  </script>
  
  <style scoped>
  .test-page {
    width: 100%;
    min-height: 100vh;
    background: #0b1444;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-bottom: 40px;
    position: relative;
  }
  
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
  
  .test-title-container {
    position: relative;
    margin-top: 130px;
    margin-bottom: 20px;
    text-align: center;
    width: 95%;
    max-width: 1100px;
  }
  
  .test-title {
    font-family: 'Arial', Georgia, serif;
    font-size: 28px;
    font-weight: bold;
    color: #fbb599;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    margin: 0 0 10px 0;
    padding: 0 20px;
    letter-spacing: 1px;
  }
  
  .test-title-divider {
    height: 3px;
    background: linear-gradient(to right, transparent, #fbb599, transparent);
    width: 100%;
    max-width: 500px;
    margin: 0 auto 10px auto;
    border-radius: 2px;
  }
  
  .lesson-info {
    color: #fbb599;
    font-family: 'Arial', Georgia, serif;
    font-size: 18px;
    margin-top: 10px;
  }
  
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
  
  .inner-container {
    background: #fbb599;
    border-radius: 20px;
    padding: 30px;
    display: flex;
    flex-direction: column;
    gap: 25px;
  }
  
  .test-info, .test-content {
    background: #fedac4;
    border-radius: 15px;
    padding: 25px;
    border: 2px solid #F4886D;
  }
  
  .test-info h2, .test-content h2 {
    font-family: 'Arial', Georgia, serif;
    font-size: 22px;
    font-weight: bold;
    color: #592012;
    margin-bottom: 15px;
    text-align: center;
  }
  
  .info-content {
    font-family: 'Arial', Georgia, serif;
    color: #592012;
  }
  
  .info-content p {
    margin: 10px 0;
  }
  
  .questions-placeholder {
    background: white;
    border-radius: 10px;
    padding: 30px;
    text-align: center;
    color: #592012;
    font-family: 'Arial', Georgia, serif;
    border: 2px solid #d67962;
  }
  
  .questions-placeholder ul {
    text-align: left;
    margin: 20px 0;
    padding-left: 20px;
  }
  
  .questions-placeholder li {
    margin: 10px 0;
  }
  
  .submit-btn {
    background: #F4886D;
    color: #592012;
    border: none;
    border-radius: 10px;
    padding: 15px 40px;
    font-family: 'Arial', Georgia, serif;
    font-weight: bold;
    font-size: 18px;
    cursor: pointer;
    transition: all 0.3s;
    align-self: center;
    margin-top: 20px;
  }
  
  .submit-btn:hover {
    background: #E0785D;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(244, 136, 109, 0.3);
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
    
    .test-title {
      font-size: 24px;
    }
  }
  </style>