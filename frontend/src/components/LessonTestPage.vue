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
        <h1 class="test-title">{{ pageTitle }}</h1>
        <div class="test-title-divider"></div>
        <p class="test-subtitle">{{ lessonTitle }}</p>
        <p v-if="testInfo" class="test-info">Вопросов: {{ testInfo.questions_count }} | Статус: {{ testInfo.is_finalized ? 'Опубликован' : 'Черновик' }}</p>
      </div>
  
      <!-- Основной контейнер -->
      <div class="main-container">
        <div class="inner-container">
          
          <!-- Формирование тестовой части (ТОЛЬКО для репетитора ДО сохранения) -->
          <div v-if="isTutorMode && !isSaved && !isReadonlyMode" class="section-box">
            <h2 class="section-header">Формирование тестовой части урока</h2>
            <div class="section-divider"></div>
            
            <div class="feedback-box">
              <textarea
                v-model="feedbackComment"
                class="feedback-textarea"
                :placeholder="feedbackPlaceholder"
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

          <!-- Статистика прохождения (для репетитора при просмотре) -->
          <div v-if="isTutorMode && isReadonlyMode && testStats" class="section-box">
            <h2 class="section-header">Статистика прохождения теста</h2>
            <div class="section-divider"></div>
            
            <div class="test-stats">
              <div class="stats-content">
                <div class="stat-item">
                  <span class="stat-label">Всего учеников:</span>
                  <span class="stat-value">{{ testStats.total_students }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Прошли тест:</span>
                  <span class="stat-value">{{ testStats.completed_tests }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Ожидают прохождения:</span>
                  <span class="stat-value">{{ testStats.pending_tests }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Средний балл:</span>
                  <span class="stat-value">{{ testStats.average_score }}%</span>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Задания теста (показываем только после генерации или если уже есть задачи) -->
          <template v-if="showTestQuestions">
            <div v-for="(task, index) in tasks" :key="task.question_id || index" class="task-box">
              <div class="task-header">
                <h3>Задание №{{ index + 1 }}</h3>
                <span v-if="isReadonlyMode && task.student_score !== undefined" class="task-score">
                  Балл: {{ task.student_score }}/{{ task.max_score || 1 }}
                </span>
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
                    :readonly="isTutorMode || isSaved || isReadonlyMode"
                    :maxlength="task.max_length"
                    :class="{ 'readonly-input': isTutorMode || isSaved || isReadonlyMode }"
                    @input="onAnswerInput"
                  ></textarea>
                  <div class="char-counter" v-if="task.max_length">
                    {{ task.userAnswer?.length || 0 }}/{{ task.max_length }} символов
                  </div>
                  <div v-if="!isTutorMode && !isTaskCompleted(task)" class="validation-error">
                    Это поле обязательно для заполнения
                  </div>
                  
                  <!-- Ответ ученика (только в режиме просмотра репетитора) -->
                  <div v-if="isReadonlyMode && task.userAnswer" class="student-answer-display" :class="{'answer-correct': task.student_correct, 'answer-incorrect': !task.student_correct}">
                    <div class="student-answer-label">
                      {{ task.student_correct ? '✓ Правильный ответ ученика' : '✗ Ответ ученика' }}
                    </div>
                    <div class="student-answer-text">
                      {{ task.userAnswer }}
                    </div>
                  </div>
                </div>
                
                <!-- Тип: Одиночный выбор (single_choice) -->
                <div v-else-if="task.type === 'single_choice'" class="task-type">
                  <p class="task-subtitle">Выберите один подходящий вариант ответа</p>
                  <div class="options">
                    <label 
                      v-for="(option, optIndex) in task.options" 
                      :key="optIndex"
                      :class="{'selected-option': isReadonlyMode && String(task.userAnswer) === String(optIndex)}"
                    >
                      <input 
                        type="radio" 
                        :name="'q' + index"
                        :value="optIndex"
                        v-model="task.userAnswer"
                        :disabled="isTutorMode || isSaved || isReadonlyMode"
                        @change="onAnswerInput"
                      />
                      {{ option }}
                    </label>
                  </div>
                  <div v-if="!isTutorMode && !isTaskCompleted(task)" class="validation-error">
                    Выберите один вариант ответа
                  </div>
                  
                  <!-- Ответ ученика (только в режиме просмотра репетитора) -->
                  <div v-if="isReadonlyMode && task.userAnswer !== ''" class="student-answer-display" :class="{'answer-correct': task.student_correct, 'answer-incorrect': !task.student_correct}">
                    <div class="student-answer-label">
                      {{ task.student_correct ? '✓ Правильный ответ ученика' : '✗ Ответ ученика' }}
                    </div>
                    <div class="student-answer-text">
                      <strong>Выбрано:</strong> 
                      <span v-if="task.userAnswer !== '' && task.options[task.userAnswer]">
                        {{ task.options[task.userAnswer] }}
                      </span>
                      <span v-else>
                        Не выбрано
                      </span>
                    </div>
                  </div>
                </div>
                
                <!-- Тип: Множественный выбор (multiple_choice) -->
                <div v-else-if="task.type === 'multiple_choice'" class="task-type">
                  <p class="task-subtitle">Выберите все подходящие варианты ответа</p>
                  <div class="options">
                    <label 
                      v-for="(option, optIndex) in task.options" 
                      :key="optIndex"
                      :class="{'selected-checkbox': isReadonlyMode && task.userAnswer && task.userAnswer.includes(String(optIndex))}"
                    >
                      <input 
                        type="checkbox" 
                        :checked="task.userAnswer?.includes(String(optIndex))"
                        @change="updateCheckbox(task, optIndex, $event.target.checked)"
                        :disabled="isTutorMode || isSaved || isReadonlyMode"
                      />
                      {{ option }}
                    </label>
                  </div>
                  <div v-if="!isTutorMode && !isTaskCompleted(task)" class="validation-error">
                    Выберите хотя бы один вариант ответа
                  </div>
                  
                  <!-- Ответ ученика (только в режиме просмотра репетитора) -->
                  <div v-if="isReadonlyMode && task.userAnswer" class="student-answer-display" :class="{'answer-correct': task.student_correct, 'answer-incorrect': !task.student_correct}">
                    <div class="student-answer-label">
                      {{ task.student_correct ? '✓ Правильный ответ ученика' : '✗ Ответ ученика' }}
                    </div>
                    <div class="student-answer-text">
                      <strong>Выбраны варианты:</strong>
                      <ul>
                        <li v-for="index in task.userAnswer" :key="index">
                          {{ task.options[index] }}
                        </li>
                        <li v-if="task.userAnswer.length === 0">Не выбрано ни одного варианта</li>
                      </ul>
                    </div>
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
                        :disabled="isTutorMode || isSaved || isReadonlyMode"
                        class="gap-select"
                        :class="{'selected-gap': isReadonlyMode && gap.userAnswer !== ''}"
                        @change="onAnswerInput"
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
                  <div v-if="!isTutorMode && !isTaskCompleted(task)" class="validation-error">
                    Заполните все пропуски
                  </div>
                  
                  <!-- Ответ ученика (только в режиме просмотра репетитора) -->
                  <div v-if="isReadonlyMode && task.gaps" class="student-answer-display" :class="{'answer-correct': task.student_correct, 'answer-incorrect': !task.student_correct}">
                    <div class="student-answer-label">
                      {{ task.student_correct ? '✓ Правильный ответ ученика' : '✗ Ответ ученика' }}
                    </div>
                    <div class="student-answer-text">
                      <strong>Ответы ученика:</strong>
                      <div v-for="gap in task.gaps" :key="gap.gap_id" class="gap-answer">
                        Пропуск [{{ gap.gap_id }}]: 
                        <span v-if="gap.userAnswer !== '' && gap.options[gap.userAnswer]">
                          {{ gap.options[gap.userAnswer] }}
                        </span>
                        <span v-else>
                          Не выбран
                        </span>
                      </div>
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

          <!-- Сообщение если нет вопросов -->
          <div v-if="!showTestQuestions && !isTutorMode" class="info-message">
            <h3>Тест урока еще не создан</h3>
            <p>Репетитор еще не создал тест для этого урока.</p>
          </div>

          <!-- Сообщение если урок недоступен -->
          <div v-if="!lessonAccess && !isTutorMode" class="info-message error">
            <h3>Урок недоступен</h3>
            <p>Этот урок еще не открыт репетитором.</p>
          </div>
  
          <!-- Сообщение если тест сгенерирован и сохранен -->
          <div v-if="isTutorMode && isSaved" class="info-message success">
            <h3>Тест успешно сохранен!</h3>
            <p>Тест урока сохранен и доступен ученикам.</p>
            <p>Всего вопросов: {{ tasks.length }}</p>
          </div>
  
            <!-- Кнопки действий -->
            <div class="action-buttons">
            <!-- Для ученика показываем кнопку "Завершить тест" -->
            <button 
                v-if="!isTutorMode && !isReadonlyMode && lessonAccess && tasks.length > 0" 
                @click="saveTest" 
                class="save-btn"
                :disabled="!isAllTasksCompleted || saving"
            >
                {{ saving ? 'Сохранение...' : 'Завершить тест' }}
            </button>
            
            <!-- Для репетитора показываем одну кнопку "Сохранить генерацию" -->
            <button 
                v-if="isTutorMode && !isSaved && tasks.length > 0 && !isReadonlyMode" 
                @click="saveTestGeneration" 
                class="save-generation-btn"
                :disabled="saving"
            >
                {{ saving ? 'Сохранение...' : 'Сохранить генерацию' }}
            </button>
            
            <!-- Кнопка оценки результатов (только для репетитора при просмотре ответов) -->
            <button 
                v-if="isTutorMode && isReadonlyMode && !studentResults && tasks.length > 0" 
                @click="evaluateResults"
                class="evaluate-btn"
                :disabled="evaluating"
            >
                {{ evaluating ? 'Оценка...' : 'Оценить результаты' }}
            </button>
            
            <button @click="goBack" class="exit-btn">
                {{ isTutorMode && isSaved ? 'Вернуться к уроку' : 'Выйти' }}
            </button>
            </div>
  
          <!-- Сообщение о незаполненных ответах -->
          <div v-if="showIncompleteMessage" class="incomplete-message">
            <p>Пожалуйста, заполните все ответы перед завершением теста.</p>
            <p>Незаполненных заданий: {{ incompleteTasksCount }}</p>
          </div>
  
          <!-- Результаты оценки (только для репетитора) -->
          <div v-if="studentResults" class="results-summary">
            <h3 class="results-title">Результаты оценки теста</h3>
            <div class="results-content">
              <div class="result-item">
                <span class="result-label">Общий балл:</span>
                <span class="result-value">{{ studentResults.score }}/{{ studentResults.max_score }}</span>
              </div>
              <div class="result-item">
                <span class="result-label">Процент выполнения:</span>
                <span class="result-value">{{ studentResults.percentage }}%</span>
              </div>
              <div class="result-item" v-if="studentResults.recommendations">
                <span class="result-label">Рекомендации:</span>
                <span class="result-value">{{ studentResults.recommendations.join(', ') }}</span>
              </div>
            </div>
          </div>
  
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, defineProps, defineEmits, watch } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useAuthStore } from "../stores/auth";
  import { config } from "../config.js";
  import AppHeader from "./Header.vue";
  
  const props = defineProps({
    lessonId: {
      type: Number,
      required: true
    },
    studentId: {
      type: Number,
      default: null
    }
  });
  
  const emit = defineEmits(['save', 'publish', 'generate', 'exit', 'evaluated']);
  
  const route = useRoute();
  const router = useRouter();
  const auth = useAuthStore();
  
  // Данные теста
  const feedbackComment = ref("");
  const generating = ref(false);
  const saving = ref(false);
  const evaluating = ref(false);
  const tasks = ref([]);
  const isSaved = ref(false);
  const hasGenerated = ref(false);
  const studentResults = ref(null);
  const testInfo = ref(null);
  const testStats = ref(null);
  const lessonAccess = ref(false);
  
  // Определяем режимы
  const isTutorMode = computed(() => {
    return auth.user?.role === "Репетитор" || route.query.isTutor === 'true';
  });
  
  const isReadonlyMode = computed(() => {
    return props.studentId && isTutorMode.value;
  });
  
  // Вычисляемое свойство для pageTitle
  const pageTitle = computed(() => {
    if (isTutorMode.value) {
      if (isReadonlyMode.value) {
        return 'Просмотр ответов ученика';
      }
      return route.query.editMode === 'true' ? 'Редактирование теста урока' : 'Тест урока';
    }
    return 'Тест урока';
  });
  
  const lessonTitle = computed(() => {
    return route.query.lessonTitle || `Урок ${props.lessonId}`;
  });
  
  // Вычисляемое свойство для placeholder
  const feedbackPlaceholder = computed(() => {
    return "Введите замечания по генерации теста урока (например: 'Сделать больше вопросов на Present Simple, добавить упражнения на лексику')";
  });
  
  // Вычисляемое свойство для отображения вопросов
  const showTestQuestions = computed(() => {
    return tasks.value.length > 0 && (!isTutorMode.value ? lessonAccess.value : true);
  });
  
  // Проверка заполнения всех задач
  const isAllTasksCompleted = computed(() => {
    if (props.isTutorMode || props.isReadonlyMode) return true;
    return tasks.value.every(task => isTaskCompleted(task));
  });
  
  // Количество незаполненных задач
  const incompleteTasksCount = computed(() => {
    return tasks.value.filter(task => !isTaskCompleted(task)).length;
  });
  
  // Показывать сообщение о незаполненных ответах
  const showIncompleteMessage = computed(() => {
    return !isTutorMode.value && !isReadonlyMode.value && incompleteTasksCount.value > 0;
  });
  
  // Показывать правильные ответы репетитору
  const showCorrectAnswers = computed(() => {
    return isTutorMode.value && !isSaved.value && !isReadonlyMode.value;
  });
  
  // Инициализация
  onMounted(async () => {
    await loadTestData();
    
    if (isTutorMode.value && isReadonlyMode.value) {
      await loadStudentAnswers();
      await loadTestStats();
    }
  });
  
  // Загрузка данных теста
  async function loadTestData() {
    try {
      const baseUrl = config.apiUrl;
      const token = localStorage.getItem('token');
      
      // Загружаем тест урока
      const response = await fetch(`${baseUrl}/lesson-tests/lessons/${props.lessonId}/test`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        testInfo.value = {
          questions_count: data.questions_count,
          is_finalized: data.is_finalized,
          generated_at: data.generated_at
        };
        lessonAccess.value = data.lesson_access || false;
        
        if (data.test_data && data.test_data.questions) {
          initializeTasks(data.test_data.questions);
        }
      } else if (response.status === 404) {
        // Тест еще не создан
        testInfo.value = {
          questions_count: 0,
          is_finalized: false
        };
        tasks.value = [];
      }
    } catch (error) {
      console.error("Ошибка загрузки теста:", error);
      testInfo.value = {
        questions_count: 0,
        is_finalized: false
      };
      tasks.value = [];
    }
  }
  
  // Загрузка статистики теста (для репетитора)
  async function loadTestStats() {
    try {
      const baseUrl = config.apiUrl;
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${baseUrl}/lesson-tests/lessons/${props.lessonId}/students/test-results`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        let totalScore = 0;
        let studentCount = 0;
        
        Object.values(data.students_results || {}).forEach(student => {
          const results = student.results;
          if (results && results.percentage !== undefined) {
            totalScore += results.percentage;
            studentCount++;
          }
        });
        
        const completedTests = Object.values(data.students_results || {}).filter(
          student => student.results && student.results.completed_at
        ).length;
        
        testStats.value = {
          total_students: data.students_count || 0,
          completed_tests: completedTests,
          pending_tests: (data.students_count || 0) - completedTests,
          average_score: studentCount > 0 ? Math.round(totalScore / studentCount) : 0
        };
      }
    } catch (error) {
      console.error("Ошибка загрузки статистики:", error);
    }
  }
  
  // Загрузка ответов ученика (для репетитора)
  async function loadStudentAnswers() {
    if (!props.studentId) return;
    
    try {
      const baseUrl = config.apiUrl;
      const token = localStorage.getItem('token');
      
      // Загружаем результаты ученика
      const response = await fetch(`${baseUrl}/lesson-tests/lessons/${props.lessonId}/students/${props.studentId}/test-results`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.results && data.results.detailed_results) {
          // Сопоставляем ответы ученика с вопросами
          tasks.value.forEach(task => {
            const studentResult = data.results.detailed_results.find(
              result => result.question_id === task.question_id
            );
            
            if (studentResult) {
              task.student_correct = studentResult.is_correct;
              task.student_score = studentResult.score;
              
              // Устанавливаем ответы ученика для отображения
              if (studentResult.user_answer !== undefined) {
                if (task.type === 'short_answer') {
                  task.userAnswer = studentResult.user_answer;
                } else if (task.type === 'single_choice') {
                  task.userAnswer = studentResult.user_answer;
                } else if (task.type === 'multiple_choice') {
                  task.userAnswer = studentResult.user_answer;
                } else if (task.type === 'gaps_choice') {
                  // Для gaps_choice нужно установить ответы для каждого пропуска
                  if (task.gaps && typeof studentResult.user_answer === 'object') {
                    task.gaps.forEach(gap => {
                      if (studentResult.user_answer[gap.gap_id] !== undefined) {
                        gap.userAnswer = studentResult.user_answer[gap.gap_id];
                      }
                    });
                  }
                }
              }
            }
          });
        }
      }
    } catch (error) {
      console.error("Ошибка загрузки ответов ученика:", error);
    }
  }
  
  // Инициализация задач
  function initializeTasks(newTasks) {
    tasks.value = JSON.parse(JSON.stringify(newTasks));
    
    // Инициализируем userAnswer для каждой задачи
    tasks.value.forEach(task => {
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
  
  // Проверка заполнения задачи
  function isTaskCompleted(task) {
    if (!task) return false;
    
    switch (task.type) {
      case 'short_answer':
        return task.userAnswer?.trim().length > 0;
        
      case 'single_choice':
        return task.userAnswer !== '' && task.userAnswer !== null && task.userAnswer !== undefined;
        
      case 'multiple_choice':
        return Array.isArray(task.userAnswer) && task.userAnswer.length > 0;
        
      case 'gaps_choice':
        if (!task.gaps) return false;
        return task.gaps.every(gap => gap.userAnswer !== '' && gap.userAnswer !== null && gap.userAnswer !== undefined);
        
      default:
        return false;
    }
  }
  
  // Обработчик ввода ответа
  function onAnswerInput() {
    // Триггерим пересчет вычисляемых свойств
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
    
    onAnswerInput();
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
    if (!isTutorMode.value) {
      alert("Только репетитор может генерировать тесты");
      return;
    }
    
    generating.value = true;
    
    try {
      const baseUrl = config.apiUrl;
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${baseUrl}/lesson-tests/lessons/${props.lessonId}/test/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          feedback: feedbackComment.value || ""
        })
      });
      
      if (!response.ok) {
        throw new Error(`Ошибка API: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.questions && Array.isArray(data.questions)) {
        initializeTasks(data.questions);
        
        if (feedbackComment.value) {
          alert(`Тест сгенерирован с учетом замечаний: "${feedbackComment.value}"`);
        } else {
          alert("Тест успешно сгенерирован!");
        }
      } else {
        alert("API вернул некорректный формат данных.");
        generateDemoTest();
      }
      
      feedbackComment.value = "";
      
      emit('generate', feedbackComment.value);
      
    } catch (error) {
      console.error("Ошибка генерации теста:", error);
      alert("Ошибка соединения с сервером. Используется демо-генерация.");
      generateDemoTest();
    } finally {
      generating.value = false;
    }
  }
  
  // Генерация демо-теста (резервный вариант)
  function generateDemoTest() {
    const feedback = feedbackComment.value.toLowerCase();
    
    let questions = [];
    
    if (feedback.includes('present simple') || feedback.includes('времена')) {
      questions = [
        {
          question_id: "1",
          type: "short_answer",
          question: "Explain when to use Present Simple tense.",
          max_length: 300,
          correct_answer: "Present Simple is used for regular actions, habits, and general truths."
        },
        {
          question_id: "2",
          type: "single_choice",
          question: "Which sentence is in Present Simple?",
          options: [
            "I am reading a book now",
            "I read books every day",
            "I was reading yesterday",
            "I have read this book"
          ],
          correct_answer: 1
        }
      ];
    } else if (feedback.includes('vocabulary') || feedback.includes('лексика')) {
      questions = [
        {
          question_id: "1",
          type: "multiple_choice",
          question: "Which words are related to daily routine?",
          options: ["wake up", "computer", "breakfast", "go to bed", "swim"],
          correct_answers: [0, 2, 3]
        }
      ];
    } else {
      // Стандартные демо-вопросы для урока
      questions = [
        {
          question_id: "1",
          type: "short_answer",
          question: "What did you learn in this lesson?",
          max_length: 200,
          correct_answer: "I learned about Present Simple tense and daily routines."
        },
        {
          question_id: "2",
          type: "single_choice",
          question: "What is the correct form for 'he' in Present Simple?",
          options: [
            "he go",
            "he goes",
            "he going",
            "he is go"
          ],
          correct_answer: 1
        },
        {
          question_id: "3",
          type: "gaps_choice",
          question: "I usually [1] up at 7 am. Then I [2] breakfast and [3] to work. In the evening, I [4] TV.",
          gaps: [
            {
              gap_id: 1,
              options: ["wake", "wakes", "waking", "woke"],
              correct_answer: 0
            },
            {
              gap_id: 2,
              options: ["have", "has", "having", "had"],
              correct_answer: 0
            },
            {
              gap_id: 3,
              options: ["go", "goes", "going", "went"],
              correct_answer: 0
            },
            {
              gap_id: 4,
              options: ["watch", "watches", "watching", "watched"],
              correct_answer: 0
            }
          ]
        }
      ];
    }
    
    initializeTasks(questions);
    
    alert(`Демо-тест урока сгенерирован! Вопросов: ${questions.length}`);
  }
  
  // Сохранение теста
  async function saveTest() {
  // Для ученика проверяем заполнение всех ответов
    if (!isTutorMode.value && !isAllTasksCompleted.value) {
        alert(`Пожалуйста, заполните все ответы перед завершением теста. Осталось заполнить: ${incompleteTasksCount.value} заданий.`);
        return;
    }
    
    if (isTutorMode.value) {
        // Для репетитора используем новую функцию
        await saveTestGeneration();
    } else {
        // Для ученика - завершение теста
        saving.value = true;
        
        try {
        const baseUrl = config.apiUrl;
        const token = localStorage.getItem('token');
        
        // Подготавливаем данные для отправки
        const testData = {
            tasks: tasks.value.map(task => {
            const cleanTask = {
                question_id: task.question_id,
                type: task.type,
                userAnswer: task.userAnswer
            };
            
            // Для gaps_choice нужно преобразовать структуру
            if (task.type === 'gaps_choice' && task.gaps) {
                cleanTask.gaps = task.gaps.map(gap => ({
                gap_id: gap.gap_id,
                userAnswer: gap.userAnswer
                }));
            }
            
            return cleanTask;
            }),
            metadata: {
            completedAt: new Date().toISOString(),
            lessonId: props.lessonId
            }
        };
        
        // Отправляем результаты на сервер
        const response = await fetch(`${baseUrl}/lesson-tests/lessons/${props.lessonId}/students/${auth.user.user_id}/submit-test`, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(testData)
        });
        
        if (!response.ok) {
            throw new Error(`Ошибка отправки: ${response.status}`);
        }
        
        const data = await response.json();
        
        alert(data.message || "Тест успешно завершен!");
        
        emit('save', testData);
        
        // Возвращаемся назад
        goBack();
        
        } catch (error) {
        console.error("Ошибка при отправке результатов:", error);
        alert(`Ошибка сохранения результатов: ${error.message}. Попробуйте снова.`);
        } finally {
        saving.value = false;
        }
    }
    }
  
    async function saveTestGeneration() {
        if (!isTutorMode.value) {
            return;
        }
        
        // Для репетитора - сохранение и публикация теста урока
        if (!confirm("Сохранить и опубликовать тест урока? После сохранения он будет доступен ученикам.")) {
            return;
        }
        
        try {
            saving.value = true;
            
            const baseUrl = config.apiUrl;
            const token = localStorage.getItem('token');
            
            // Подготавливаем данные теста (убираем лишние поля)
            const testData = {
            questions: tasks.value.map(task => {
                const cleanTask = { ...task };
                // Удаляем временные поля
                delete cleanTask.userAnswer;
                delete cleanTask.student_correct;
                delete cleanTask.student_score;
                
                // Для gaps_choice также чистим поля
                if (cleanTask.gaps) {
                cleanTask.gaps = cleanTask.gaps.map(gap => {
                    const cleanGap = { ...gap };
                    delete cleanGap.userAnswer;
                    return cleanGap;
                });
                }
                
                return cleanTask;
            }),
            generated_at: new Date().toISOString(),
            is_finalized: true
            };
            
            // Используем новый эндпоинт для сохранения и финализации
            const response = await fetch(`${baseUrl}/lesson-tests/lessons/${props.lessonId}/test/save-and-finalize`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                test_data: testData
            })
            });
            
            if (!response.ok) {
            // Если новый эндпоинт не работает, пробуем старый подход
            if (response.status === 404 || response.status === 405) {
                console.log("Новый эндпоинт не найден, используем старый подход");
                
                // Сначала сохраняем тест
                const saveResponse = await fetch(`${baseUrl}/lesson-tests/lessons/${props.lessonId}/test`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    test_data: testData
                })
                });
                
                if (!saveResponse.ok) {
                throw new Error(`Ошибка сохранения: ${saveResponse.status}`);
                }
                
                // Затем финализируем
                const finalizeResponse = await fetch(`${baseUrl}/lesson-tests/lessons/${props.lessonId}/test/finalize`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    finalize: true
                })
                });
                
                if (!finalizeResponse.ok) {
                throw new Error(`Ошибка публикации: ${finalizeResponse.status}`);
                }
                
                const data = await finalizeResponse.json();
                isSaved.value = true;
                alert(data.message || "Тест урока успешно сохранен и опубликован!");
            } else {
                throw new Error(`Ошибка сохранения: ${response.status}`);
            }
            } else {
            const data = await response.json();
            isSaved.value = true;
            alert(data.message || "Тест урока успешно сохранен и опубликован!");
            }
            
            emit('save', {
            tasks: tasks.value,
            isFinalized: true
            });
            
        } catch (error) {
            console.error("Ошибка сохранения теста:", error);
            alert(`Ошибка сохранения теста: ${error.message}. Проверьте, запущен ли бэкенд на порту 8000.`);
        } finally {
            saving.value = false;
        }
    }
  
  // Оценка результатов ученика (для репетитора)
  async function evaluateResults() {
    if (!isTutorMode.value || !isReadonlyMode.value || !props.studentId) {
      return;
    }
    
    evaluating.value = true;
    
    try {
      const baseUrl = config.apiUrl;
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${baseUrl}/lesson-tests/lessons/${props.lessonId}/students/${props.studentId}/evaluate-test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Ошибка оценки: ${response.status}`);
      }
      
      const data = await response.json();
      studentResults.value = data.results || data;
      
      alert("Результаты успешно оценены!");
      
      emit('evaluated', data);
      
    } catch (error) {
      console.error("Ошибка оценки результатов:", error);
      alert("Ошибка оценки результатов. Попробуйте снова.");
    } finally {
      evaluating.value = false;
    }
  }
  
  // Навигация назад
  function goBack() {
    if (route.query.courseId) {
      router.push({
        path: `/lesson/${props.lessonId}`,
        query: { courseId: route.query.courseId }
      });
    } else {
      router.back();
    }
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

    .test-info {
    color: #f4886d;
    font-family: 'Arial', Georgia, serif;
    font-size: 14px;
    margin-top: 5px;
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

    .test-stats {
    background: #FFFFFF;
    border: 2px solid #F4886D;
    border-radius: 15px;
    padding: 20px;
    margin-top: 15px;
    }

    .stats-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    }

    .stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border-bottom: 1px solid #eee;
    }

    .stat-label {
    font-size: 14px;
    color: #555;
    font-family: 'Arial', Georgia, serif;
    }

    .stat-value {
    font-size: 16px;
    font-weight: bold;
    color: #1976D2;
    font-family: 'Arial', Georgia, serif;
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

    .info-message.success {
    background: #e8f5e8;
    border-color: #4CAF50;
    }

    .info-message.error {
    background: #ffebee;
    border-color: #F44336;
    }

    .info-message h3 {
    margin-top: 0;
    color: #592012;
    }

    .info-message.success h3 {
    color: #2E7D32;
    }

    .info-message.error h3 {
    color: #C62828;
    }

    .info-message p {
    margin: 10px 0;
    font-size: 16px;
    }

    .action-buttons {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 15px;
    margin-top: 30px;
    }

    .save-btn, .exit-btn, .finalize-btn, .evaluate-btn {
    padding: 12px 24px;
    border: none;
    border-radius: 10px;
    font-family: 'Arial', Georgia, serif;
    font-weight: bold;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;
    min-width: 160px;
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

    .finalize-btn {
    background: #FF9800;
    color: white;
    }

    .finalize-btn:hover:not(:disabled) {
    background: #F57C00;
    transform: translateY(-2px);
    }

    .evaluate-btn {
    background: #2196F3;
    color: white;
    }

    .evaluate-btn:hover:not(:disabled) {
    background: #1976D2;
    transform: translateY(-2px);
    }

    .exit-btn {
    background: #592012;
    color: #f4886d;
    }

    .exit-btn:hover {
    background: #3d150c;
    transform: translateY(-2px);
    }

    @media (max-width: 768px) {
    .action-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .save-btn, .exit-btn, .finalize-btn, .evaluate-btn {
        width: 100%;
        max-width: 300px;
    }
    }

    .incomplete-message {
    background: #fff3e0;
    border: 1px solid #FF9800;
    border-radius: 8px;
    padding: 15px;
    margin-top: 20px;
    text-align: center;
    color: #E65100;
    }

    .incomplete-message p {
    margin: 5px 0;
    }

    .results-summary {
    background: #e8f5e8;
    border: 2px solid #4CAF50;
    border-radius: 15px;
    padding: 20px;
    margin-top: 20px;
    }

    .results-title {
    text-align: center;
    color: #2E7D32;
    margin-bottom: 15px;
    font-family: 'Arial', Georgia, serif;
    }

    .results-content {
    display: flex;
    flex-direction: column;
    gap: 10px;
    }

    .result-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #d4edda;
    }

    .result-label {
    font-weight: bold;
    color: #555;
    font-family: 'Arial', Georgia, serif;
    }

    .result-value {
    color: #2E7D32;
    font-family: 'Arial', Georgia, serif;
    text-align: right;
    }

    /* Дополнительные стили */
    .task-score {
    background: #4CAF50;
    color: white;
    padding: 4px 12px;
    border-radius: 15px;
    font-size: 14px;
    font-weight: bold;
    }

    .validation-error {
    color: #F44336;
    font-size: 14px;
    margin-top: 5px;
    padding: 5px 10px;
    background: #ffebee;
    border-radius: 4px;
    border-left: 3px solid #F44336;
    }

    .student-answer-display {
    margin-top: 10px;
    padding: 10px;
    border-radius: 5px;
    background-color: #f0f7ff;
    border-left: 3px solid #2196F3;
    }

    .student-answer-label {
    font-weight: bold;
    color: #1976D2;
    margin-bottom: 5px;
    }

    .student-answer-text {
    font-size: 14px;
    color: #333;
    padding: 5px;
    background: white;
    border-radius: 3px;
    border: 1px solid #ddd;
    }

    .answer-correct {
    background-color: #e8f5e8 !important;
    border-left-color: #4CAF50 !important;
    }

    .answer-correct .student-answer-label {
    color: #2E7D32 !important;
    }

    .answer-incorrect {
    background-color: #ffebee !important;
    border-left-color: #F44336 !important;
    }

    .answer-incorrect .student-answer-label {
    color: #C62828 !important;
    }
    
    .save-generation-btn {
    background: #4CAF50;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-family: 'Arial', Georgia, serif;
    font-weight: bold;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;
    min-width: 160px;
    text-align: center;
    }

    .save-generation-btn:hover:not(:disabled) {
    background: #3d8b40;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }

    .save-generation-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    }
  </style>