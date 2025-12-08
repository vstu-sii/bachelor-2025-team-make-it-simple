<template>
    <div class="test-page">
      <!-- Хедер -->
      <AppHeader :show-back-button="true" />
      
      <!-- Кнопка "назад" -->
      <button class="back-btn" @click="goBack">
        <img src="/src/assets/arrow-back.svg" alt="back" />
      </button>
  
      <!-- Заголовок теста -->
      <div class="test-title-container">
        <h1 class="test-title">{{ title }}</h1>
        <div class="test-title-divider"></div>
        <p class="test-subtitle">{{ subtitle }}</p>
      </div>
  
      <!-- Основной контейнер -->
      <div class="main-container">
        <div class="inner-container">
          
          <!-- Формирование тестовой части (ТОЛЬКО для репетитора) -->
          <div v-if="isTutorMode" class="section-box">
            <h2 class="section-header">Формирование тестовой части</h2>
            <div class="section-divider"></div>
            
            <div class="feedback-box">
              <textarea
                v-model="feedbackComment"
                class="feedback-textarea"
                placeholder="Введите замечания по генерации теста"
                rows="3"
              ></textarea>
              <button 
                class="send-btn" 
                @click="generateTest"
                :disabled="generating || !feedbackComment.trim()"
              >
                {{ generating ? 'Генерация...' : 'Отправить' }}
              </button>
            </div>
          </div>
  
          <!-- Задания теста -->
          <div v-for="(task, index) in tasks" :key="index" class="task-box">
            <div class="task-header">
              <h3>Задание №{{ index + 1 }}</h3>
            </div>
            
            <div class="task-content">
              <p class="task-text">{{ task.text }}</p>
              
              <!-- Тип 1: Ввод ответа -->
              <div v-if="task.type === 'text'" class="task-type">
                <p class="task-subtitle">Введите ответ</p>
                <textarea 
                  v-model="task.userAnswer"
                  class="answer-input" 
                  :placeholder="task.placeholder || 'Напишите ответ на вопрос'"
                  :readonly="isTutorMode"
                  :class="{ 'readonly-input': isTutorMode }"
                ></textarea>
              </div>
              
              <!-- Тип 2: Множественный выбор (checkbox) -->
              <div v-else-if="task.type === 'checkbox'" class="task-type">
                <p class="task-subtitle">Выберите все подходящие варианты ответа</p>
                <div class="options">
                  <label v-for="(option, optIndex) in task.options" :key="optIndex">
                    <input 
                      type="checkbox" 
                      :checked="task.userAnswer?.includes(option)"
                      @change="updateCheckbox(task, option, $event.target.checked)"
                      :disabled="isTutorMode"
                    />
                    {{ option }}
                  </label>
                </div>
              </div>
              
              <!-- Тип 3: Одиночный выбор (radio) -->
              <div v-else-if="task.type === 'radio'" class="task-type">
                <p class="task-subtitle">Выберите один подходящий вариант ответа</p>
                <div class="options">
                  <label v-for="(option, optIndex) in task.options" :key="optIndex">
                    <input 
                      type="radio" 
                      :name="'q' + index"
                      :value="option"
                      v-model="task.userAnswer"
                      :disabled="isTutorMode"
                    />
                    {{ option }}
                  </label>
                </div>
              </div>
              
              <!-- Тип 4: Заполнение пропусков -->
              <div v-else-if="task.type === 'fill-blanks'" class="task-type">
                <p class="task-subtitle">Заполните пропуски</p>
                <div class="fill-blanks">
                  <span v-for="(part, partIndex) in task.parts" :key="partIndex">
                    <span v-if="part.type === 'text'">{{ part.content }} </span>
                    <input 
                      v-else-if="part.type === 'input'"
                      v-model="part.userAnswer"
                      :placeholder="part.placeholder || ''"
                      :readonly="isTutorMode"
                      class="blank-input"
                      :class="{ 'readonly-input': isTutorMode }"
                    />
                  </span>
                </div>
              </div>
              
              <!-- Оценка задания (только если showScores = true) -->
              <div v-if="showScores && isTutorMode" class="grade-section">
                <div class="grade">
                  Оценка ответа<br />
                  <span class="grade-value">
                    <span class="score-container">
                      {{ task.score || '0' }} / {{ task.maxScore || 5 }}
                    </span>
                  </span>
                </div>
              </div>
              
              <!-- Комментарий репетитора (только для репетитора) -->
              <div v-if="isTutorMode && task.feedback" class="tutor-feedback">
                <div class="feedback-divider"></div>
                <div class="feedback-content">
                  <strong>Замечания репетитора:</strong>
                  <p>{{ task.feedback }}</p>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Кнопки действий -->
          <div class="action-buttons">
            <!-- Для ученика ВСЕГДА показываем кнопку "Завершить тест" -->
            <button 
              v-if="!isTutorMode" 
              @click="saveTest" 
              class="save-btn"
            >
              Завершить тест
            </button>
            
            <!-- Для репетитора показываем кнопку "Сохранить генерацию" если он в режиме редактирования -->
            <button 
              v-if="isTutorMode && isEditable" 
              @click="saveTest" 
              class="save-btn"
            >
              Сохранить генерацию
            </button>
            
            <button @click="goBack" class="exit-btn">
              Выйти
            </button>
          </div>
  
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, defineProps, defineEmits, watch } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useAuthStore } from "../stores/auth";
  import AppHeader from "./Header.vue";
  
  const props = defineProps({
    // Основные параметры
    testType: {
      type: String,
      default: "lesson" // 'lesson', 'input'
    },
    title: {
      type: String,
      default: ""
    },
    subtitle: {
      type: String,
      default: ""
    },
    // Данные теста
    initialTasks: {
      type: Array,
      default: () => []
    },
    timeLimit: {
      type: Number,
      default: 20
    },
    // Режимы отображения
    isTutorMode: {
      type: Boolean,
      default: false
    },
    showScores: {
      type: Boolean,
      default: false
    },
    isEditable: {
      type: Boolean,
      default: true
    }
  });
  
  const emit = defineEmits(['save', 'publish', 'generate', 'exit']);
  
  const route = useRoute();
  const router = useRouter();
  const auth = useAuthStore();
  
  // Данные теста
  const feedbackComment = ref("");
  const generating = ref(false);
  const tasks = ref([]);
  
  // Инициализация
  onMounted(() => {
    // Загружаем задачи из props или создаем демо-задачи
    if (props.initialTasks && props.initialTasks.length > 0) {
      tasks.value = JSON.parse(JSON.stringify(props.initialTasks));
    } else {
      loadDemoTasks();
    }
  });
  
  // Следим за изменением initialTasks
  watch(() => props.initialTasks, (newTasks) => {
    if (newTasks && newTasks.length > 0) {
      tasks.value = JSON.parse(JSON.stringify(newTasks));
    }
  }, { immediate: true });
  
  // Демо-задачи для примера (используется только если нет initialTasks)
  function loadDemoTasks() {
    tasks.value = [
      {
        id: 1,
        type: 'text',
        text: 'Объясните, в чем разница между Present Simple и Present Continuous.',
        maxScore: 5,
        score: null,
        userAnswer: '',
        placeholder: 'Напишите развернутый ответ...',
        feedback: props.isTutorMode ? 'Уточните использование временных указателей' : null
      },
      {
        id: 2,
        type: 'checkbox',
        text: 'Какие из следующих предложений являются примерами Present Perfect?',
        maxScore: 3,
        score: null,
        userAnswer: [],
        options: [
          'I have never been to London.',
          'She is going to school.',
          'They have finished their homework.',
          'He works every day.',
          'We have seen that movie already.'
        ],
        correctAnswers: [0, 2, 4],
        feedback: props.isTutorMode ? 'Добавьте больше примеров с отрицательной формой' : null
      }
    ];
  }
  
  // Обновление checkbox ответов
  function updateCheckbox(task, option, checked) {
    if (!task.userAnswer) task.userAnswer = [];
    
    if (checked && !task.userAnswer.includes(option)) {
      task.userAnswer.push(option);
    } else if (!checked) {
      const index = task.userAnswer.indexOf(option);
      if (index > -1) task.userAnswer.splice(index, 1);
    }
  }
  
  // Генерация теста (для репетитора)
  function generateTest() {
    if (!feedbackComment.value.trim()) {
      alert("Введите комментарий для генерации");
      return;
    }
    
    if (!props.isTutorMode) {
      alert("Только репетитор может вносить замечания по генерации");
      return;
    }
    
    generating.value = true;
    emit('generate', feedbackComment.value);
    
    // Демо-генерация
    setTimeout(() => {
      alert("Тест успешно сгенерирован на основе ваших замечаний");
      feedbackComment.value = "";
      generating.value = false;
    }, 1500);
  }
  
  // Сохранение теста
  function saveTest() {
    const testData = {
      tasks: tasks.value,
      metadata: {
        testType: props.testType,
        timeLimit: props.timeLimit,
        savedAt: new Date().toISOString()
      }
    };
    
    emit('save', testData);
    
    if (props.isTutorMode) {
      alert("Замечания по генерации сохранены!");
    } else {
      alert("Тестирование завершено! Результаты отправлены на проверку.");
      goBack();
    }
  }
  
  // Навигация назад
  function goBack() {
    emit('exit');
    router.back();
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
  
  /* Заголовок теста */
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
    font-size: 32px;
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
  
  .test-subtitle {
    color: #fbb599;
    font-family: 'Arial', Georgia, serif;
    font-size: 18px;
    margin-top: 10px;
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
  
  /* Секции */
  .section-box, .task-box {
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
  
  /* Формирование теста (для репетитора) */
  .feedback-box {
    display: flex;
    gap: 15px;
    align-items: flex-start;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .feedback-textarea {
    flex: 1;
    min-width: 300px;
    padding: 12px 15px;
    background: #FFFFFF;
    border: 2px solid #d67962;
    border-radius: 10px;
    font-family: 'Arial', Georgia, serif;
    font-size: 15px;
    color: #592012;
    resize: vertical;
    min-height: 80px;
    max-width: 600px;
  }
  
  .feedback-textarea:focus {
    outline: none;
    border-color: #c85643;
    background: #fff9de;
  }
  
  .send-btn {
    background: #F4886D;
    color: #592012;
    border: none;
    border-radius: 10px;
    padding: 12px 25px;
    font-family: 'Arial', Georgia, serif;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s;
    white-space: nowrap;
    min-width: 120px;
    height: fit-content;
    align-self: flex-end;
    margin-top: 4px;
  }
  
  .send-btn:hover:not(:disabled) {
    background: #E0785D;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(244, 136, 109, 0.3);
  }
  
  .send-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  /* Задания */
  .task-box {
    margin-top: 15px;
  }
  
  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    border-bottom: 2px solid #d67962;
    padding-bottom: 10px;
  }
  
  .task-header h3 {
    font-family: 'Arial', Georgia, serif;
    font-size: 20px;
    font-weight: bold;
    color: #592012;
    margin: 0;
  }
  
  .task-content {
    font-family: 'Arial', Georgia, serif;
    color: #592012;
  }
  
  .task-text {
    background: white;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
    border: 2px solid #d67962;
    font-size: 16px;
    line-height: 1.5;
  }
  
  .task-subtitle {
    font-weight: bold;
    margin: 15px 0 10px 0;
    color: #592012;
  }
  
  /* Поля ввода */
  .answer-input {
    width: 100%;
    height: 120px;
    padding: 12px;
    background: white;
    border: 2px solid #d67962;
    border-radius: 10px;
    font-family: 'Arial', Georgia, serif;
    font-size: 15px;
    color: #592012;
    resize: vertical;
    box-sizing: border-box;
  }
  
  .answer-input:focus {
    outline: none;
    border-color: #c85643;
    background: #fff9de;
  }
  
  .readonly-input {
    background-color: #f5f5f5 !important;
    cursor: not-allowed !important;
  }
  
  /* Варианты ответов */
  .options {
    background: white;
    border: 2px solid #d67962;
    border-radius: 10px;
    padding: 15px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .options label {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    padding: 5px;
    border-radius: 5px;
    transition: background 0.2s;
  }
  
  .options label:hover {
    background: #fff9de;
  }
  
  .options input[type="checkbox"],
  .options input[type="radio"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
  
  .options input[disabled] {
    cursor: not-allowed;
  }
  
  /* Заполнение пропусков */
  .fill-blanks {
    background: white;
    border: 2px solid #d67962;
    border-radius: 10px;
    padding: 15px;
    line-height: 2;
    font-size: 16px;
  }
  
  .blank-input {
    padding: 5px 10px;
    border: 2px solid #d67962;
    border-radius: 5px;
    margin: 0 5px;
    font-family: 'Arial', Georgia, serif;
    font-size: 15px;
    color: #592012;
    min-width: 100px;
    text-align: center;
    background: white;
  }
  
  .blank-input:focus {
    outline: none;
    border-color: #c85643;
    background: white;
  }
  
  .blank-input[readonly] {
    background: #f5f5f5;
    cursor: not-allowed;
  }
  
  /* Оценка задания */
  .grade-section {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 2px dashed #d67962;
  }
  
  .grade {
    text-align: center;
    font-family: 'Arial', Georgia, serif;
    color: #592012;
    margin-bottom: 15px;
  }
  
  .score-container {
    display: inline-block;
    padding: 5px 15px;
    background-color: white;
    border-radius: 8px;
    font-size: 28px;
    font-weight: bold;
    color: #592012;
  }
  
  /* Комментарий репетитора */
  .tutor-feedback {
    margin-top: 15px;
    padding: 15px;
    background-color: #fff9de;
    border-radius: 8px;
    border: 1px solid #d67962;
  }
  
  .feedback-divider {
    height: 1px;
    background-color: #d67962;
    margin: 10px 0;
  }
  
  .feedback-content {
    font-family: 'Arial', Georgia, serif;
    color: #592012;
    font-size: 14px;
  }
  
  .feedback-content strong {
    display: block;
    margin-bottom: 5px;
  }
  
  /* Кнопки действий */
  .action-buttons {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
    margin-top: 30px;
  }
  
  .save-btn, .exit-btn {
    padding: 15px 30px;
    border: none;
    border-radius: 10px;
    font-family: 'Arial', Georgia, serif;
    font-weight: bold;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;
    min-width: 180px;
    width: 240px;
    text-align: center;
  }
  
  .save-btn {
    background: #f4886d;
    color: #592012;
  }
  
  .save-btn:hover {
    background: #E0785D;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(244, 136, 109, 0.3);
  }
  
  .exit-btn {
    background: #592012;
    color: #f4886d;
    order: 1;
  }
  
  .exit-btn:hover {
    background: #3d150c;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(89, 32, 18, 0.3);
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
    
    .test-title {
      font-size: 28px;
    }
    
    .main-container {
      width: 98%;
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
    
    .test-title-container {
      margin-top: 110px;
      margin-bottom: 15px;
    }
    
    .test-title {
      font-size: 24px;
    }
    
    .main-container {
      padding: 20px;
      margin-top: 5px;
    }
    
    .inner-container {
      padding: 20px;
    }
    
    .section-box, .task-box {
      padding: 20px;
    }
    
    .section-header {
      font-size: 20px;
    }
    
    .feedback-box {
      flex-direction: column;
      align-items: stretch;
    }
    
    .feedback-textarea {
      min-width: auto;
      max-width: none;
      width: 100%;
    }
    
    .send-btn {
      align-self: center;
      margin-top: 10px;
    }
    
    .action-buttons {
      flex-direction: column;
    }
    
    .save-btn, .exit-btn {
      width: 100%;
      min-width: auto;
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
    
    .test-title {
      font-size: 20px;
    }
    
    .test-subtitle {
      font-size: 16px;
    }
    
    .main-container {
      padding: 15px;
    }
    
    .inner-container {
      padding: 15px;
    }
    
    .task-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }
    
    .fill-blanks {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    
    .blank-input {
      width: 100%;
      margin: 5px 0;
    }
  }
  </style>