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
        
        <!-- Формирование тестовой части (ТОЛЬКО для репетитора ДО сохранения) -->
        <div v-if="isTutorMode && !isSaved" class="section-box">
          <h2 class="section-header">Формирование тестовой части</h2>
          <div class="section-divider"></div>
          
          <div class="feedback-box">
            <textarea
              v-model="feedbackComment"
              class="feedback-textarea"
              placeholder="Введите замечания по генерации теста (например: 'Сделать больше вопросов на Present Simple, меньше на артикли')"
              rows="3"
              :disabled="generating"
            ></textarea>
            <button 
              class="send-btn" 
              @click="generateTest"
              :disabled="generating"
            >
              {{ generating ? 'Генерация...' : 'Сгенерировать тест' }}
            </button>
          </div>
        </div>

        <!-- Задания теста (показываем только после генерации или если уже есть задачи) -->
        <template v-if="showTestQuestions">
          <div v-for="(task, index) in tasks" :key="task.question_id || index" class="task-box">
            <div class="task-header">
              <h3>Задание №{{ index + 1 }}</h3>
            </div>
            
            <div class="task-content">
              <p class="task-text">{{ task.question }}</p>
              
              <!-- Тип: Краткий ответ (short_answer) -->
              <div v-if="task.type === 'short_answer'" class="task-type">
                <p class="task-subtitle">Введите ответ</p>
                <textarea 
                  v-model="task.userAnswer"
                  class="answer-input" 
                  :placeholder="`Введите ответ (максимум ${task.max_length} символов)`"
                  :readonly="isTutorMode || isSaved"
                  :maxlength="task.max_length"
                  :class="{ 'readonly-input': isTutorMode || isSaved }"
                ></textarea>
                <div class="char-counter" v-if="task.max_length">
                  {{ task.userAnswer?.length || 0 }}/{{ task.max_length }} символов
                </div>
              </div>
              
              <!-- Тип: Одиночный выбор (single_choice) -->
              <div v-else-if="task.type === 'single_choice'" class="task-type">
                <p class="task-subtitle">Выберите один подходящий вариант ответа</p>
                <div class="options">
                  <label v-for="(option, optIndex) in task.options" :key="optIndex">
                    <input 
                      type="radio" 
                      :name="'q' + index"
                      :value="optIndex"
                      v-model="task.userAnswer"
                      :disabled="isTutorMode || isSaved"
                    />
                    {{ option }}
                  </label>
                </div>
              </div>
              
              <!-- Тип: Множественный выбор (multiple_choice) -->
              <div v-else-if="task.type === 'multiple_choice'" class="task-type">
                <p class="task-subtitle">Выберите все подходящие варианты ответа</p>
                <div class="options">
                  <label v-for="(option, optIndex) in task.options" :key="optIndex">
                    <input 
                      type="checkbox" 
                      :checked="task.userAnswer?.includes(optIndex)"
                      @change="updateCheckbox(task, optIndex, $event.target.checked)"
                      :disabled="isTutorMode || isSaved"
                    />
                    {{ option }}
                  </label>
                </div>
              </div>
              
              <!-- Тип: Заполнение пропусков (gaps_choice) -->
              <div v-else-if="task.type === 'gaps_choice'" class="task-type">
                <p class="task-subtitle">Заполните пропуски</p>
                <div class="gaps-text">
                  <div class="gaps-content" v-html="formatGapsText(task)"></div>
                </div>
                <div class="gaps-selection">
                  <div v-for="gap in task.gaps" :key="gap.gap_id" class="gap-item">
                    <label class="gap-label">Пропуск [{{ gap.gap_id }}]:</label>
                    <select 
                      v-model="gap.userAnswer"
                      :disabled="isTutorMode || isSaved"
                      class="gap-select"
                    >
                      <option value="">Выберите вариант</option>
                      <option 
                        v-for="(option, optIndex) in gap.options" 
                        :key="optIndex"
                        :value="optIndex"
                      >
                        {{ option }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
              
              <!-- Правильный ответ (только для репетитора до сохранения) -->
              <div v-if="isTutorMode && !isSaved && showCorrectAnswers" class="correct-answer">
                <div class="feedback-divider"></div>
                <div class="feedback-content">
                  <strong>Правильный ответ:</strong>
                  <p>{{ getCorrectAnswerText(task) }}</p>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- Сообщение если тест сгенерирован и сохранен -->
        <div v-if="isTutorMode && isSaved" class="info-message">
          <h3>Тест успешно сохранен!</h3>
          <p>Входной тест сохранен и опубликован для учеников.</p>
          <p>Всего вопросов: {{ tasks.length }}</p>
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
          
          <!-- Для репетитора показываем кнопку "Сохранить генерацию" только если есть вопросы и не сохранено -->
          <button 
            v-if="isTutorMode && !isSaved && tasks.length > 0" 
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
  },
  // Конфигурация API
  apiConfig: {
    type: Object,
    default: () => ({
      baseUrl: "http://localhost:8000",
      courseData: {}
    })
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
const isSaved = ref(false);
const hasGenerated = ref(false);

// Вычисляемое свойство для отображения вопросов
const showTestQuestions = computed(() => {
  // Для ученика всегда показываем вопросы
  if (!props.isTutorMode) return true;
  
  // Для репетитора показываем вопросы только если они есть и тест еще не сохранен
  return tasks.value.length > 0 && !isSaved.value;
});

// Показывать правильные ответы репетитору
const showCorrectAnswers = computed(() => {
  return props.isTutorMode && !isSaved.value;
});

// Инициализация
onMounted(() => {
  // Загружаем задачи из props
  if (props.initialTasks && props.initialTasks.length > 0) {
    initializeTasks(props.initialTasks);
  } else {
    // Если нет задач, оставляем пустой массив
    tasks.value = [];
    hasGenerated.value = false;
  }
});

// Следим за изменением initialTasks
watch(() => props.initialTasks, (newTasks) => {
  if (newTasks && newTasks.length > 0) {
    initializeTasks(newTasks);
  } else {
    tasks.value = [];
    hasGenerated.value = false;
  }
}, { immediate: true });

// Инициализация задач
function initializeTasks(newTasks) {
  tasks.value = JSON.parse(JSON.stringify(newTasks));
  
  // Инициализируем userAnswer для каждой задачи
  tasks.value.forEach(task => {
    // Добавляем поле userAnswer если его нет
    if (!task.userAnswer) {
      if (task.type === 'multiple_choice') {
        task.userAnswer = [];
      } else if (task.type === 'gaps_choice' && task.gaps) {
        task.gaps.forEach(gap => {
          if (!gap.userAnswer) gap.userAnswer = '';
        });
      } else {
        task.userAnswer = '';
      }
    }
  });
  
  hasGenerated.value = true;
}

// Обновление checkbox ответов
function updateCheckbox(task, optionIndex, checked) {
  if (!task.userAnswer) task.userAnswer = [];
  
  if (checked && !task.userAnswer.includes(optionIndex)) {
    task.userAnswer.push(optionIndex);
  } else if (!checked) {
    const index = task.userAnswer.indexOf(optionIndex);
    if (index > -1) task.userAnswer.splice(index, 1);
  }
}

// Форматирование текста с пропусками
function formatGapsText(task) {
  if (!task.question || !task.gaps) return task.question;
  
  let text = task.question;
  task.gaps.forEach(gap => {
    const placeholder = `<span class="gap-placeholder">[${gap.gap_id}]</span>`;
    text = text.replace(`[${gap.gap_id}]`, placeholder);
  });
  
  return text;
}

// Получение текста правильного ответа
function getCorrectAnswerText(task) {
  switch (task.type) {
    case 'short_answer':
      return task.correct_answer;
      
    case 'single_choice':
      if (task.correct_answer !== undefined && task.options) {
        return task.options[task.correct_answer];
      }
      break;
      
    case 'multiple_choice':
      if (task.correct_answers && Array.isArray(task.correct_answers) && task.options) {
        const correctOptions = task.correct_answers
          .map(index => task.options[index])
          .filter(opt => opt !== undefined);
        return correctOptions.join(', ');
      }
      break;
      
    case 'gaps_choice':
      if (task.gaps) {
        return task.gaps.map(gap => {
          const correctOption = gap.options[gap.correct_answer];
          return `[${gap.gap_id}]: ${correctOption}`;
        }).join('; ');
      }
      break;
  }
  
  return 'Правильный ответ не указан';
}

// Генерация теста через API
async function generateTest() {
  if (!props.isTutorMode) {
    alert("Только репетитор может генерировать тесты");
    return;
  }
  
  generating.value = true;
  
  try {
    // Отправляем запрос на сервер для генерации теста
    const response = await fetch(`${props.apiConfig.baseUrl}/tests/courses/${route.params.courseId}/entry-test/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        feedback: feedbackComment.value || "Сгенерировать стандартный входной тест по указанным темам курса."
      })
    });
    
    if (!response.ok) {
      throw new Error(`Ошибка API: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Преобразуем вопросы из API в формат для отображения
    if (data.questions && Array.isArray(data.questions)) {
      tasks.value = data.questions.map(question => {
        const formattedQuestion = {
          ...question,
          userAnswer: question.type === 'multiple_choice' ? [] : ''
        };
        
        // Для gaps_choice инициализируем userAnswer для каждого пропуска
        if (question.type === 'gaps_choice' && question.gaps) {
          formattedQuestion.gaps = question.gaps.map(gap => ({
            ...gap,
            userAnswer: ''
          }));
        }
        
        return formattedQuestion;
      });
      
      hasGenerated.value = true;
      
      // Показываем сообщение об успехе
      if (feedbackComment.value) {
        alert(`Тест сгенерирован с учетом замечаний: "${feedbackComment.value}"`);
      } else {
        alert("Тест успешно сгенерирован!");
      }
    } else {
      // Если API не вернул вопросы, используем демо-данные
      alert("API вернул некорректный формат данных. Используются демо-вопросы.");
      generateDemoTest();
    }
    
    // Очищаем поле комментария
    feedbackComment.value = "";
    
    // Отправляем событие генерации
    emit('generate', feedbackComment.value);
    
  } catch (error) {
    console.error("Ошибка генерации теста:", error);
    
    // В случае ошибки API используем демо-генерацию
    alert("Ошибка соединения с сервером. Используется демо-генерация.");
    generateDemoTest();
  } finally {
    generating.value = false;
  }
}

// Генерация демо-теста (резервный вариант)
function generateDemoTest() {
  const courseTitle = props.subtitle || "Английский для начинающих";
  
  // Генерация вопросов на основе комментария
  let questions = [];
  
  if (feedbackComment.value.toLowerCase().includes('present simple') || 
      feedbackComment.value.toLowerCase().includes('времена')) {
    questions = [
      {
        question_id: "1",
        type: "short_answer",
        question: "Explain the difference between Present Simple and Present Continuous tenses.",
        max_length: 300,
        correct_answer: "Present Simple is used for regular actions and facts, while Present Continuous is used for actions happening now."
      },
      {
        question_id: "2",
        type: "single_choice",
        question: "Which sentence uses Present Simple correctly?",
        options: [
          "She is going to school every day",
          "She goes to school every day",
          "She go to school every day",
          "She going to school every day"
        ],
        correct_answer: 1
      }
    ];
  } else if (feedbackComment.value.toLowerCase().includes('articles') || 
             feedbackComment.value.toLowerCase().includes('артикли')) {
    questions = [
      {
        question_id: "1",
        type: "multiple_choice",
        question: "Which words are articles in English?",
        options: ["the", "a", "an", "is", "and"],
        correct_answers: [0, 1, 2]
      }
    ];
  } else {
    // Стандартные демо-вопросы
    questions = [
      {
        question_id: "1",
        type: "short_answer",
        question: "What is your name and how old are you?",
        max_length: 50,
        correct_answer: "My name is Alex, I am 25 years old"
      },
      {
        question_id: "2",
        type: "single_choice",
        question: "Choose the correct sentence in Present Simple:",
        options: [
          "I playing football every day",
          "I plays football every day",
          "I play football every day",
          "I am play football every day"
        ],
        correct_answer: 2
      },
      {
        question_id: "3",
        type: "multiple_choice",
        question: "Which words are articles in English?",
        options: ["the", "a", "an", "is", "and"],
        correct_answers: [0, 1, 2]
      },
      {
        question_id: "4",
        type: "gaps_choice",
        question: "If I [1] enough money, I [2] travel around the world. I [3] to visit Japan for a long time because I [4] fascinated by its culture. When I [5] there, I want to try traditional food and [6] historical temples.",
        gaps: [
          {
            gap_id: 1,
            options: ["have", "had", "will have", "would have"],
            correct_answer: 1
          },
          {
            gap_id: 2,
            options: ["would", "will", "can", "could"],
            correct_answer: 0
          },
          {
            gap_id: 3,
            options: ["have wanted", "want", "wanted", "wanting"],
            correct_answer: 0
          },
          {
            gap_id: 4,
            options: ["am", "was", "have been", "had been"],
            correct_answer: 0
          },
          {
            gap_id: 5,
            options: ["go", "will go", "went", "have gone"],
            correct_answer: 0
          },
          {
            gap_id: 6,
            options: ["visit", "visiting", "visited", "to visit"],
            correct_answer: 0
          }
        ]
      }
    ];
  }
  
  tasks.value = questions.map(q => ({
    ...q,
    userAnswer: q.type === 'multiple_choice' ? [] : ''
  }));
  
  hasGenerated.value = true;
  
  alert(`Демо-тест сгенерирован! Вопросов: ${questions.length}`);
}

// Регенерация теста
function regenerateTest() {
  if (confirm("Сгенерировать новый тест? Текущие изменения будут потеряны.")) {
    feedbackComment.value = "";
    tasks.value = [];
    hasGenerated.value = false;
  }
}

// Сохранение теста
async function saveTest() {
  if (props.isTutorMode) {
    // Для репетитора - финализация теста
    if (!confirm("Сохранить тест окончательно? После сохранения изменения будут недоступны.")) {
      return;
    }
    
    try {
      const response = await fetch(`${props.apiConfig.baseUrl}/tests/courses/${route.params.courseId}/entry-test/finalize`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          finalize: true
        })
      });
      
      if (!response.ok) {
        throw new Error(`Ошибка сохранения: ${response.status}`);
      }
      
      isSaved.value = true;
      alert("Тест успешно сохранен и опубликован для учеников!");
      
      // Отправляем событие сохранения
      emit('save', {
        tasks: tasks.value,
        isFinalized: true
      });
      
    } catch (error) {
      console.error("Ошибка сохранения теста:", error);
      alert("Ошибка сохранения теста. Попробуйте снова.");
    }
  } else {
    // Для ученика - завершение теста
    const testData = {
      tasks: tasks.value,
      metadata: {
        testType: props.testType,
        timeLimit: props.timeLimit,
        completedAt: new Date().toISOString()
      }
    };
    
    emit('save', testData);
    
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

.feedback-textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
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

.hint-box {
  margin-top: 15px;
  padding: 12px 15px;
  background: #fff9de;
  border: 1px solid #F4886D;
  border-radius: 8px;
  font-family: 'Arial', Georgia, serif;
  font-size: 14px;
  color: #592012;
}

.hint-box p {
  margin: 0;
}

.hint-box strong {
  color: #c85643;
}

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
  white-space: pre-line;
}

.task-subtitle {
  font-weight: bold;
  margin: 15px 0 10px 0;
  color: #592012;
}

.answer-input {
  width: 100%;
  height: 100px;
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

.char-counter {
  text-align: right;
  font-size: 12px;
  color: #666;
  margin-top: 5px;
  font-family: 'Arial', Georgia, serif;
}

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

.gaps-text {
  background: white;
  border: 2px solid #d67962;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 15px;
  line-height: 1.6;
  font-size: 16px;
}

.gaps-content {
  font-family: 'Arial', Georgia, serif;
  color: #592012;
}

.gap-placeholder {
  background: #fff9de;
  border: 1px dashed #c85643;
  border-radius: 4px;
  padding: 2px 6px;
  margin: 0 4px;
  color: #c85643;
  font-weight: bold;
}

.gaps-selection {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 10px;
  margin-top: 15px;
}

.gap-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.gap-label {
  font-weight: bold;
  font-size: 14px;
  color: #592012;
  font-family: 'Arial', Georgia, serif;
}

.gap-select {
  padding: 8px 12px;
  border: 2px solid #d67962;
  border-radius: 6px;
  background: white;
  font-family: 'Arial', Georgia, serif;
  font-size: 14px;
  color: #592012;
}

.gap-select:focus {
  outline: none;
  border-color: #c85643;
}

.gap-select:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.correct-answer {
  margin-top: 15px;
  padding: 15px;
  background-color: #e8f5e8;
  border-radius: 8px;
  border: 1px solid #4CAF50;
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
  color: #2E7D32;
}

.info-message {
  background: #fff9de;
  border: 2px solid #F4886D;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  color: #592012;
  font-family: 'Arial', Georgia, serif;
}

.info-message h3 {
  margin-top: 0;
  color: #2E7D32;
}

.info-message p {
  margin: 10px 0;
  font-size: 16px;
}

.generated-message {
  background: #e8f5e8;
  border-color: #4CAF50;
}

.generated-message h3 {
  color: #2E7D32;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
}

.save-btn, .exit-btn, .regenerate-btn {
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
  background: #4CAF50;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #3d8b40;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.regenerate-btn {
  background: #FF9800;
  color: white;
  order: 1;
}

.regenerate-btn:hover:not(:disabled) {
  background: #F57C00;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.exit-btn {
  background: #592012;
  color: #f4886d;
  order: 2;
}

.exit-btn:hover {
  background: #3d150c;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(89, 32, 18, 0.3);
}

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
  
  .gaps-selection {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .save-btn, .exit-btn, .regenerate-btn {
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
}
</style>