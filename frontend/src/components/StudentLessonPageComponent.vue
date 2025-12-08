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
        <h1 class="lesson-title">{{ lessonTitle }}</h1>
        <div class="lesson-title-divider"></div>
      </div>
  
      <!-- Основной контейнер -->
      <div class="main-container">
        <div class="inner-container">
          
          <!-- Теоретическая часть -->
          <div class="section-box">
            <h2 class="section-header">Теоретическая часть</h2>
            <div class="section-divider"></div>
            
            <textarea 
              v-model="theoryText" 
              class="textarea"
              readonly
              placeholder="Теория будет загружена..."
            ></textarea>
            
            <div class="actions">
              <span v-if="progress.theory_completed" class="completed-badge">
                ✓ Теория изучена
              </span>
            </div>
          </div>
  
          <!-- Задание на чтение -->
          <div class="section-box">
            <h2 class="section-header">Задание на чтение</h2>
            <div class="section-divider"></div>
            
            <textarea 
              v-model="readingText" 
              class="textarea"
              readonly
              placeholder="Задание будет загружено..."
            ></textarea>
            
            <div class="actions">
              <span v-if="progress.reading_completed" class="completed-badge">
                ✓ Чтение выполнено
              </span>
            </div>
          </div>
  
          <!-- Задание на говорение -->
          <div class="section-box">
            <h2 class="section-header">Задание на говорение</h2>
            <div class="section-divider"></div>
            
            <textarea 
              v-model="speakingText" 
              class="textarea"
              readonly
              placeholder="Задание будет загружено..."
            ></textarea>
            
            <div class="actions">
              <span v-if="progress.speaking_completed" class="completed-badge">
                ✓ Говорение выполнено
              </span>
            </div>
          </div>
  
          <!-- Тестовая часть -->
          <div class="section-box">
            <h2 class="section-header">Тестовая часть</h2>
            <div class="section-divider"></div>
            
            <div v-if="lessonTest" class="test-info">
              <p>Тест урока содержит вопросы по пройденному материалу</p>
              <div class="questions-preview">
                <p><strong>Количество вопросов:</strong> {{ lessonTest.questions?.length || 0 }}</p>
              </div>
              
              <div class="test-button-container">
                <button 
                  v-if="lessonData?.is_access && !progress.test_completed" 
                  @click="startTest" 
                  class="btn-test"
                >
                  Перейти к тесту
                </button>
                <button 
                  v-if="progress.test_completed" 
                  class="btn-test disabled"
                  disabled
                >
                  Тест пройден ({{ progress.test_score }} баллов)
                </button>
              </div>
            </div>
            
            <div v-if="progress.test_completed" class="test-results">
              <h3>Результаты урока:</h3>
              <p>Оценка: <strong>{{ progress.test_score }} баллов</strong></p>
              <p>Тест пройден: {{ progress.test_completed ? 'Да' : 'Нет' }}</p>
            </div>
          </div>
  
          <!-- Результаты урока -->
          <div class="section-box">
            <h2 class="section-header">Результаты урока</h2>
            <div class="section-divider"></div>
            
            <textarea 
              v-model="resultNotes" 
              class="textarea"
              readonly
              :placeholder="resultNotesPlaceholder"
            ></textarea>
          </div>
  
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, watch, defineProps } from "vue";
  import { useRouter } from "vue-router";
  import { useAuthStore } from "../stores/auth";
  import api from "../api/axios";
  import AppHeader from "../components/Header.vue";
  
  // Определяем props
  const props = defineProps({
    lessonId: {
      type: Number,
      required: true
    },
    courseId: {
      type: Number,
      default: null
    }
  });
  
  const router = useRouter();
  const auth = useAuthStore();
  
  // Используем props вместо получения из route
  const lessonIdRef = ref(props.lessonId);
  const courseIdRef = ref(props.courseId);
  const studentId = ref(auth.user?.user_id);
  
  // Данные урока
  const lessonData = ref(null);
  const loading = ref(false);
  
  // Прогресс ученика
  const progress = ref({
    theory_completed: false,
    reading_completed: false,
    speaking_completed: false,
    test_completed: false,
    test_score: 0
  });
  
  // Данные урока
  const theoryText = ref("");
  const readingText = ref("");
  const speakingText = ref("");
  const resultNotes = ref("");
  const lessonTest = ref(null);
  
  // Вычисляемые свойства
  const lessonTitle = computed(() => {
    if (lessonData.value) {
      const title = lessonData.value.theory_text?.length > 50 
        ? lessonData.value.theory_text.substring(0, 50) + "..." 
        : lessonData.value.theory_text || "";
      return `Урок ${lessonIdRef.value}: ${title}`;
    }
    return `Урок №${lessonIdRef.value}`;
  });
  
  const resultNotesPlaceholder = computed(() => {
    if (progress.value.test_completed) {
      return "Комментарии репетитора будут загружены...";
    }
    return "Результаты и комментарии появятся после прохождения теста";
  });
  
  async function loadLessonData() {
    if (!lessonIdRef.value) return;
    
    try {
      loading.value = true;
      
      // Загружаем информацию об уроке
      const response = await api.get(`/lessons/${lessonIdRef.value}`);
      lessonData.value = response.data;
      
      // Загружаем контент урока
      theoryText.value = lessonData.value.theory_text || "";
      readingText.value = lessonData.value.reading_text || "";
      speakingText.value = lessonData.value.speaking_text || "";
      resultNotes.value = lessonData.value.result_notes || "";
      
      // Загружаем тест урока
      if (lessonData.value.lesson_test_json) {
        try {
          lessonTest.value = typeof lessonData.value.lesson_test_json === 'string'
            ? JSON.parse(lessonData.value.lesson_test_json)
            : lessonData.value.lesson_test_json;
        } catch (e) {
          console.error("Error parsing lesson test:", e);
          lessonTest.value = null;
        }
      }
      
    } catch (error) {
      console.error("Ошибка загрузки данных урока:", error);
      alert("Не удалось загрузить данные урока");
      goBack();
    } finally {
      loading.value = false;
    }
  }
  
  // Тест
  function startTest() {
    if (lessonTest.value) {
      router.push(`/lesson/${lessonIdRef.value}/test?courseId=${courseIdRef.value}`);
    } else {
      alert("Тест для этого урока еще не создан");
    }
  }
  
  // Навигация
  function goBack() {
    if (courseIdRef.value) {
      router.push(`/course/${courseIdRef.value}`);
    } else {
      router.back();
    }
  }
  
  // Инициализация
  onMounted(async () => {
    // Проверяем аутентификацию
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    
    if (!auth.user) {
      await auth.fetchMe();
    }
    
    if (!auth.user) {
      router.push("/login");
      return;
    }
    
    studentId.value = auth.user.user_id;
    
    // Загружаем данные урока
    await loadLessonData();
  });
  
  // Следим за изменением props
  watch(
    () => props.lessonId,
    (newId) => {
      if (newId) {
        lessonIdRef.value = newId;
        loadLessonData();
      }
    }
  );
  
  watch(
    () => props.courseId,
    (newCourseId) => {
      courseIdRef.value = newCourseId;
    }
  );
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
    font-size: 28px;
    font-weight: bold;
    color: #fbb599;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    margin: 0 0 10px 0;
    padding: 0 20px;
    letter-spacing: 1px;
  }
  
  .lesson-title-divider {
    height: 3px;
    background: linear-gradient(to right, transparent, #fbb599, transparent);
    width: 100%;
    max-width: 500px;
    margin: 0 auto 10px auto;
    border-radius: 2px;
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
  
  .section-box {
    background: #fedac4;
    border-radius: 15px;
    padding: 25px;
    border: 2px solid #F4886D;
  }
  
  .section-header {
    font-family: 'Arial', Georgia, serif;
    font-size: 22px;
    font-weight: bold;
    color: #592012;
    margin-bottom: 10px;
    text-align: center;
  }
  
  .section-divider {
    height: 2px;
    background-color: #592012;
    width: 100%;
    margin-bottom: 20px;
    border-radius: 1px;
  }
  
  .textarea {
    width: 100%;
    height: 200px;
    padding: 15px;
    background: #ffffff;
    border: 2px solid #d67962;
    border-radius: 10px;
    font-family: 'Arial', Georgia, serif;
    font-size: 14px;
    color: #592012;
    resize: vertical;
    margin-bottom: 15px;
  }
  
  .textarea[readonly] {
    cursor: not-allowed;
  }
  
  .actions {
    display: flex;
    gap: 15px;
    align-items: center;
    margin-top: 10px;
  }
  
  .test-info {
    background: #ffffff;
    border-radius: 10px;
    padding: 15px;
    border: 2px solid #d67962;
    border-radius: 10px;
    margin-bottom: 20px;
    text-align: center;
    font-family: 'Arial', Georgia, serif;
    color: #592012;
  }
  
  .test-button-container {
    margin-top: 20px;
  }
  
  .btn-test {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-family: 'Arial', Georgia, serif;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s;
    background: #f4886d;
    color: #592012;
    font-size: 16px;
    width: auto;
    min-width: 180px;
  }
  
  .btn-test:hover:not(:disabled) {
    background: #e0785d;
    transform: translateY(-2px);
  }
  
  .btn-test.disabled {
    background: #6c757d;
    cursor: not-allowed;
  }
  
  .completed-badge {
    color: #28a745;
    font-weight: bold;
    font-family: 'Arial', Georgia, serif;
  }
  
  .test-results {
    background: rgba(255, 255, 255, 0.5);
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 20px;
    font-family: 'Arial', Georgia, serif;
    color: #592012;
  }
  
  .test-results h3 {
    margin-top: 0;
    margin-bottom: 10px;
  }
  
  /* Адаптивность (аналогично оригиналу) */
  @media (max-width: 1200px) {
    .back-btn {
      left: 10px;
      transform: none;
    }
    
    .back-btn:hover {
      transform: translateX(-5px);
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
      font-size: 18px;
      padding: 0 15px;
    }
    
    .section-box {
      padding: 20px;
    }
  }
  </style>