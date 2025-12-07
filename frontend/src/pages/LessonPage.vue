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
      <div v-if="lessonData" class="lesson-status">
        <span :class="['status-badge', lessonData.is_access ? 'access-enabled' : 'access-disabled']">
          {{ lessonData.is_access ? 'Доступен' : 'Недоступен' }}
        </span>
        <span :class="['status-badge', lessonData.is_ended ? 'ended-true' : 'ended-false']">
          {{ lessonData.is_ended ? 'Завершен' : 'В процессе' }}
        </span>
      </div>
    </div>

    <!-- Основной контейнер -->
    <div class="main-container">
      <div class="inner-container">
        
        <!-- Информация о прогрессе (для ученика) -->
        <div v-if="isStudent" class="lesson-progress">
          <h2>Ваш прогресс по уроку</h2>
          <div class="progress-items">
            <div class="progress-item" :class="{ completed: progress.theory_completed }">
              <span>Теория</span>
              <span>{{ progress.theory_completed ? '✓' : '○' }}</span>
            </div>
            <div class="progress-item" :class="{ completed: progress.reading_completed }">
              <span>Чтение</span>
              <span>{{ progress.reading_completed ? '✓' : '○' }}</span>
            </div>
            <div class="progress-item" :class="{ completed: progress.speaking_completed }">
              <span>Говорение</span>
              <span>{{ progress.speaking_completed ? '✓' : '○' }}</span>
            </div>
            <div class="progress-item" :class="{ completed: progress.test_completed }">
              <span>Тест</span>
              <span>{{ progress.test_completed ? '✓' : '○' }}</span>
              <span v-if="progress.test_score" class="score">({{ progress.test_score }} баллов)</span>
            </div>
          </div>
        </div>

        <!-- Теоретическая часть -->
        <div class="section-box">
          <h2 class="section-header">Теоретическая часть</h2>
          
          <!-- Формирование теории (для репетитора) -->
          <div v-if="isTutor" class="generation-section">
            <h3 class="subtitle">Формирование теоретической части</h3>
            <div class="comment-input">
              <input 
                v-model="theoryComment" 
                placeholder="Внесите замечания по генерации теории"
                @keyup.enter="generateTheory"
              />
              <button @click="generateTheory" class="btn-generate">
                {{ theoryGenerating ? 'Генерация...' : 'Сгенерировать' }}
              </button>
            </div>
          </div>

          <textarea 
            v-model="theoryText" 
            class="textarea"
            :readonly="isStudent"
            :placeholder="isStudent ? 'Теория будет загружена...' : 'Введите теоретическую часть урока'"
          ></textarea>
          
          <div class="actions">
            <button 
              v-if="isTutor" 
              @click="saveTheory" 
              class="btn-save"
              :disabled="!theoryText"
            >
              Сохранить теорию
            </button>
            <button 
              v-if="isStudent && !progress.theory_completed && lessonData?.is_access" 
              @click="completeTheory" 
              class="btn-complete"
            >
              Отметить как изученное
            </button>
            <span v-if="isStudent && progress.theory_completed" class="completed-badge">
              ✓ Теория изучена
            </span>
          </div>
        </div>

        <!-- Задание на чтение -->
        <div class="section-box">
          <h2 class="section-header">Задание на чтение</h2>
          
          <!-- Формирование чтения (для репетитора) -->
          <div v-if="isTutor" class="generation-section">
            <h3 class="subtitle">Формирование задания на чтение</h3>
            <div class="comment-input">
              <input 
                v-model="readingComment" 
                placeholder="Внесите замечания по генерации задания"
                @keyup.enter="generateReading"
              />
              <button @click="generateReading" class="btn-generate">
                {{ readingGenerating ? 'Генерация...' : 'Сгенерировать' }}
              </button>
            </div>
          </div>

          <textarea 
            v-model="readingText" 
            class="textarea"
            :readonly="isStudent"
            :placeholder="isStudent ? 'Задание будет загружено...' : 'Введите задание на чтение'"
          ></textarea>
          
          <div class="actions">
            <button 
              v-if="isTutor" 
              @click="saveReading" 
              class="btn-save"
              :disabled="!readingText"
            >
              Сохранить задание
            </button>
            <button 
              v-if="isStudent && !progress.reading_completed && lessonData?.is_access" 
              @click="completeReading" 
              class="btn-complete"
            >
              Отметить как выполненное
            </button>
            <span v-if="isStudent && progress.reading_completed" class="completed-badge">
              ✓ Чтение выполнено
            </span>
          </div>
        </div>

        <!-- Задание на говорение -->
        <div class="section-box">
          <h2 class="section-header">Задание на говорение</h2>
          
          <!-- Формирование говорения (для репетитора) -->
          <div v-if="isTutor" class="generation-section">
            <h3 class="subtitle">Формирование задания на говорение</h3>
            <div class="comment-input">
              <input 
                v-model="speakingComment" 
                placeholder="Внесите замечания по генерации задания"
                @keyup.enter="generateSpeaking"
              />
              <button @click="generateSpeaking" class="btn-generate">
                {{ speakingGenerating ? 'Генерация...' : 'Сгенерировать' }}
              </button>
            </div>
          </div>

          <textarea 
            v-model="speakingText" 
            class="textarea"
            :readonly="isStudent"
            :placeholder="isStudent ? 'Задание будет загружено...' : 'Введите задание на говорение'"
          ></textarea>
          
          <div class="actions">
            <button 
              v-if="isTutor" 
              @click="saveSpeaking" 
              class="btn-save"
              :disabled="!speakingText"
            >
              Сохранить задание
            </button>
            <button 
              v-if="isStudent && !progress.speaking_completed && lessonData?.is_access" 
              @click="completeSpeaking" 
              class="btn-complete"
            >
              Отметить как выполненное
            </button>
            <span v-if="isStudent && progress.speaking_completed" class="completed-badge">
              ✓ Говорение выполнено
            </span>
          </div>
        </div>

        <!-- Тестовая часть -->
        <div class="section-box">
          <h2 class="section-header">Тестовая часть</h2>
          
          <!-- Информация о тесте -->
          <div v-if="lessonTest" class="test-info">
            <p>Тест урока содержит вопросы по пройденному материалу</p>
            <div v-if="lessonTest.questions" class="questions-preview">
              <p><strong>Количество вопросов:</strong> {{ lessonTest.questions.length }}</p>
            </div>
          </div>
          
          <!-- Результаты теста -->
          <div v-if="progress.test_completed" class="test-results">
            <h3>Ваши результаты:</h3>
            <p>Оценка: <strong>{{ progress.test_score }} баллов</strong></p>
            <p>Тест пройден: {{ progress.test_completed ? 'Да' : 'Нет' }}</p>
          </div>
          
          <div class="actions">
            <button 
              v-if="isStudent && lessonData?.is_access && !progress.test_completed" 
              @click="startTest" 
              class="btn-test"
            >
              Начать тест
            </button>
            <button 
              v-if="isStudent && progress.test_completed" 
              class="btn-test disabled"
              disabled
            >
              Тест пройден ({{ progress.test_score }} баллов)
            </button>
            <button 
              v-if="isTutor" 
              @click="editTest" 
              class="btn-save"
            >
              Редактировать тест
            </button>
          </div>
        </div>

        <!-- Для репетитора: заметки и управление доступом -->
        <div v-if="isTutor" class="tutor-sections">
          <!-- Заметки по уроку -->
          <div class="section-box">
            <h2 class="section-header">Заметки по уроку</h2>
            <textarea 
              v-model="lessonNotes" 
              class="textarea"
              placeholder="Заметки репетитора по уроку..."
            ></textarea>
            <button @click="saveNotes" class="btn-save">
              Сохранить заметки
            </button>
          </div>

          <!-- Управление доступом -->
          <div class="section-box">
            <h2 class="section-header">Управление уроком</h2>
            
            <div class="access-controls">
              <label class="control-checkbox">
                <input type="checkbox" v-model="isAccessEnabled" />
                Урок доступен для ученика
              </label>
              <label class="control-checkbox">
                <input type="checkbox" v-model="isEndedEnabled" />
                Урок завершен
              </label>
            </div>
            
            <div class="action-buttons">
              <button @click="saveAccessSettings" class="btn-save">
                Сохранить настройки
              </button>
            </div>
          </div>

          <!-- Результаты учеников -->
          <div v-if="studentsProgress.length > 0" class="section-box">
            <h2 class="section-header">Результаты учеников</h2>
            
            <div class="students-results">
              <div v-for="student in studentsProgress" :key="student.student_id" class="student-result">
                <h4>{{ student.student_name }}</h4>
                <div class="student-progress">
                  <span>Теория: {{ student.theory_completed ? '✓' : '○' }}</span>
                  <span>Чтение: {{ student.reading_completed ? '✓' : '○' }}</span>
                  <span>Говорение: {{ student.speaking_completed ? '✓' : '○' }}</span>
                  <span>Тест: {{ student.test_completed ? `✓ (${student.test_score})` : '○' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Кнопки навигации -->
        <div class="navigation-buttons">
          <button 
            class="nav-btn prev-btn" 
            @click="goToPrevLesson"
            :disabled="!hasPrevLesson"
          >
            ← Предыдущий урок
          </button>
          <button 
            class="nav-btn next-btn" 
            @click="goToNextLesson"
            :disabled="!hasNextLesson"
          >
            Следующий урок →
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import api from "../api/axios";
import AppHeader from "../components/Header.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

// Параметры из URL
const lessonId = ref(parseInt(route.params.id));
const courseId = ref(route.query.courseId ? parseInt(route.query.courseId) : null);
const studentId = ref(route.query.studentId ? parseInt(route.query.studentId) : auth.user?.user_id);

// Данные урока
const lessonData = ref(null);
const loading = ref(false);

// Роль пользователя
const isTutor = computed(() => auth.user?.role === "Репетитор");
const isStudent = computed(() => auth.user?.role === "Ученик");

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
const lessonNotes = ref("");
const lessonTest = ref(null);

// Комментарии для генерации
const theoryComment = ref("");
const readingComment = ref("");
const speakingComment = ref("");

// Флаги генерации
const theoryGenerating = ref(false);
const readingGenerating = ref(false);
const speakingGenerating = ref(false);

// Управление доступом
const isAccessEnabled = ref(false);
const isEndedEnabled = ref(false);

// Прогресс учеников (для репетитора)
const studentsProgress = ref([]);

// Навигация по урокам
const courseLessons = ref([]);
const currentLessonIndex = ref(0);

// Вычисляемые свойства
const lessonTitle = computed(() => {
  if (lessonData.value && lessonData.value.theory_text) {
    const title = lessonData.value.theory_text.length > 50 
      ? lessonData.value.theory_text.substring(0, 50) + "..." 
      : lessonData.value.theory_text;
    return `Урок ${lessonId.value}: ${title}`;
  }
  return `Урок №${lessonId.value}`;
});

const hasPrevLesson = computed(() => currentLessonIndex.value > 0);
const hasNextLesson = computed(() => currentLessonIndex.value < courseLessons.value.length - 1);

// Методы
async function loadLessonData() {
  if (!lessonId.value) return;
  
  try {
    loading.value = true;
    
    // Загружаем информацию об уроке
    const response = await api.get(`/lessons/${lessonId.value}`);
    lessonData.value = response.data;
    
    // Загружаем контент урока
    theoryText.value = lessonData.value.theory_text || "";
    readingText.value = lessonData.value.reading_text || "";
    speakingText.value = lessonData.value.speaking_text || "";
    lessonNotes.value = lessonData.value.lesson_notes || "";
    isAccessEnabled.value = lessonData.value.is_access || false;
    isEndedEnabled.value = lessonData.value.is_ended || false;
    
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
    
    // Загружаем уроки курса (если есть courseId)
    if (courseId.value) {
      await loadCourseLessons();
    }
    
    // Загружаем прогресс (для ученика)
    if (isStudent.value) {
      await loadLessonProgress();
    }
    
    // Загружаем прогресс учеников (для репетитора)
    if (isTutor.value && courseId.value) {
      await loadStudentsProgress();
    }
    
  } catch (error) {
    console.error("Ошибка загрузки данных урока:", error);
    alert("Не удалось загрузить данные урока");
    goBack();
  } finally {
    loading.value = false;
  }
}

async function loadCourseLessons() {
  if (!courseId.value) return;
  
  try {
    const response = await api.get(`/lessons/course/${courseId.value}/info`);
    courseLessons.value = response.data.lessons || [];
    
    // Находим текущий индекс урока
    currentLessonIndex.value = courseLessons.value.findIndex(
      lesson => lesson.lesson_id === lessonId.value
    );
    
  } catch (error) {
    console.error("Ошибка загрузки уроков курса:", error);
  }
}

async function loadLessonProgress() {
  if (!lessonId.value || !studentId.value) return;
  
  try {
    const response = await api.get(`/lessons/${lessonId.value}/progress/${studentId.value}`);
    progress.value = response.data;
  } catch (error) {
    console.error("Ошибка загрузки прогресса:", error);
  }
}

async function loadStudentsProgress() {
  if (!lessonId.value || !courseId.value) return;
  
  try {
    // Здесь должна быть логика получения прогресса всех учеников на курсе
    // Пока заглушка
    studentsProgress.value = [];
  } catch (error) {
    console.error("Ошибка загрузки прогресса учеников:", error);
  }
}

// Генерация контента
async function generateTheory() {
  if (!theoryComment.value.trim()) {
    alert("Введите комментарий для генерации");
    return;
  }
  
  try {
    theoryGenerating.value = true;
    const response = await api.post(`/lessons/${lessonId.value}/generate/theory`, {
      comment: theoryComment.value
    });
    
    theoryText.value = response.data.generated_content;
    theoryComment.value = "";
    
  } catch (error) {
    console.error("Ошибка генерации теории:", error);
    alert("Ошибка генерации теории");
  } finally {
    theoryGenerating.value = false;
  }
}

async function generateReading() {
  if (!readingComment.value.trim()) {
    alert("Введите комментарий для генерации");
    return;
  }
  
  try {
    readingGenerating.value = true;
    const response = await api.post(`/lessons/${lessonId.value}/generate/reading`, {
      comment: readingComment.value
    });
    
    readingText.value = response.data.generated_content;
    readingComment.value = "";
    
  } catch (error) {
    console.error("Ошибка генерации задания:", error);
    alert("Ошибка генерации задания");
  } finally {
    readingGenerating.value = false;
  }
}

async function generateSpeaking() {
  if (!speakingComment.value.trim()) {
    alert("Введите комментарий для генерации");
    return;
  }
  
  try {
    speakingGenerating.value = true;
    const response = await api.post(`/lessons/${lessonId.value}/generate/speaking`, {
      comment: speakingComment.value
    });
    
    speakingText.value = response.data.generated_content;
    speakingComment.value = "";
    
  } catch (error) {
    console.error("Ошибка генерации задания:", error);
    alert("Ошибка генерации задания");
  } finally {
    speakingGenerating.value = false;
  }
}

// Сохранение контента
async function saveTheory() {
  try {
    await api.put(`/lessons/${lessonId.value}/content`, {
      content_type: "theory",
      content: theoryText.value
    });
    alert("Теория сохранена");
  } catch (error) {
    console.error("Ошибка сохранения теории:", error);
    alert("Ошибка сохранения теории");
  }
}

async function saveReading() {
  try {
    await api.put(`/lessons/${lessonId.value}/content`, {
      content_type: "reading",
      content: readingText.value
    });
    alert("Задание на чтение сохранено");
  } catch (error) {
    console.error("Ошибка сохранения задания:", error);
    alert("Ошибка сохранения задания");
  }
}

async function saveSpeaking() {
  try {
    await api.put(`/lessons/${lessonId.value}/content`, {
      content_type: "speaking",
      content: speakingText.value
    });
    alert("Задание на говорение сохранено");
  } catch (error) {
    console.error("Ошибка сохранения задания:", error);
    alert("Ошибка сохранения задания");
  }
}

async function saveNotes() {
  try {
    await api.put(`/lessons/${lessonId.value}/content`, {
      content_type: "notes",
      content: lessonNotes.value
    });
    alert("Заметки сохранены");
  } catch (error) {
    console.error("Ошибка сохранения заметок:", error);
    alert("Ошибка сохранения заметок");
  }
}

async function saveAccessSettings() {
  try {
    await api.put(`/lessons/${lessonId.value}/content`, {
      content_type: "theory", // Можно использовать любое поле
      content: theoryText.value,
      is_access: isAccessEnabled.value,
      is_ended: isEndedEnabled.value
    });
    alert("Настройки сохранены");
  } catch (error) {
    console.error("Ошибка сохранения настроек:", error);
    alert("Ошибка сохранения настроек");
  }
}

// Отметка выполненных заданий (для ученика)
async function completeTheory() {
  try {
    await api.put(`/lessons/${lessonId.value}/progress/${studentId.value}`, {
      progress_type: "theory",
      data: { completed: true }
    });
    progress.value.theory_completed = true;
    alert("Теория отмечена как изученная");
  } catch (error) {
    console.error("Ошибка обновления прогресса:", error);
  }
}

async function completeReading() {
  try {
    await api.put(`/lessons/${lessonId.value}/progress/${studentId.value}`, {
      progress_type: "reading",
      data: { completed: true }
    });
    progress.value.reading_completed = true;
    alert("Задание на чтение отмечено как выполненное");
  } catch (error) {
    console.error("Ошибка обновления прогресса:", error);
  }
}

async function completeSpeaking() {
  try {
    await api.put(`/lessons/${lessonId.value}/progress/${studentId.value}`, {
      progress_type: "speaking",
      data: { completed: true }
    });
    progress.value.speaking_completed = true;
    alert("Задание на говорение отмечено как выполненное");
  } catch (error) {
    console.error("Ошибка обновления прогресса:", error);
  }
}

// Тест
function startTest() {
  if (lessonTest.value) {
    // Здесь должна быть логика начала теста
    alert("Начало теста (реализация теста)");
    // router.push(`/lesson/${lessonId.value}/test`);
  } else {
    alert("Тест для этого урока еще не создан");
  }
}

function editTest() {
  alert("Редактирование теста (реализация)");
}

// Навигация
function goBack() {
  if (courseId.value) {
    router.push(`/course/${courseId.value}`);
  } else {
    router.back();
  }
}

function goToPrevLesson() {
  if (hasPrevLesson.value) {
    const prevLesson = courseLessons.value[currentLessonIndex.value - 1];
    router.push(`/lesson/${prevLesson.lesson_id}?courseId=${courseId.value}&studentId=${studentId.value}`);
  }
}

function goToNextLesson() {
  if (hasNextLesson.value) {
    const nextLesson = courseLessons.value[currentLessonIndex.value + 1];
    router.push(`/lesson/${nextLesson.lesson_id}?courseId=${courseId.value}&studentId=${studentId.value}`);
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
  
  // Если ученик, используем его ID
  if (isStudent.value) {
    studentId.value = auth.user.user_id;
  }
  
  // Загружаем данные урока
  await loadLessonData();
});

// Следим за изменением ID урока
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      lessonId.value = parseInt(newId);
      loadLessonData();
    }
  }
);
</script>

<style scoped>
/* ===== ОСНОВНЫЕ СТИЛИ ===== */
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

.lesson-status {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 10px;
}

.status-badge {
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
  font-family: 'Arial', Georgia, serif;
}

.access-enabled {
  background: #4CAF50;
  color: white;
}

.access-disabled {
  background: #f44336;
  color: white;
}

.ended-true {
  background: #2196F3;
  color: white;
}

.ended-false {
  background: #FF9800;
  color: white;
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

/* ===== СТИЛИ ДЛЯ БЛОКОВ ===== */
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
  margin-bottom: 20px;
  text-align: center;
}

.subtitle {
  font-family: 'Arial', Georgia, serif;
  font-size: 16px;
  color: #592012;
  margin-bottom: 15px;
  text-align: center;
}

/* Прогресс урока */
.lesson-progress {
  background: #f8d0b8;
  border-radius: 12px;
  padding: 20px;
  border: 2px dashed #d8654f;
}

.lesson-progress h2 {
  font-family: 'Arial', Georgia, serif;
  font-size: 18px;
  color: #592012;
  margin-bottom: 15px;
  text-align: center;
}

.progress-items {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 15px;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: #ffe8d5;
  border-radius: 8px;
  font-family: 'Arial', Georgia, serif;
  color: #592012;
  min-width: 120px;
  justify-content: space-between;
}

.progress-item.completed {
  background: #d4edda;
  border: 1px solid #c3e6cb;
}

.progress-item.completed span:first-child {
  color: #155724;
}

.progress-item .score {
  font-size: 12px;
  color: #666;
}

/* Поля ввода */
.textarea {
  width: 100%;
  height: 200px;
  padding: 15px;
  background: #fff0e8;
  border: 2px solid #d67962;
  border-radius: 10px;
  font-family: 'Arial', Georgia, serif;
  font-size: 14px;
  color: #592012;
  resize: vertical;
  margin-bottom: 15px;
}

.textarea:focus {
  outline: none;
  border-color: #c85643;
  background: #fff9de;
}

.textarea[readonly] {
  background: #f5f5f5;
  cursor: not-allowed;
}

/* Секция генерации (для репетитора) */
.generation-section {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
}

.comment-input {
  display: flex;
  gap: 10px;
  align-items: center;
}

.comment-input input {
  flex: 1;
  padding: 10px;
  border: 2px solid #d67962;
  border-radius: 8px;
  background: #fff0e8;
  font-family: 'Arial', Georgia, serif;
  color: #592012;
}

.comment-input input:focus {
  outline: none;
  border-color: #c85643;
  background: #fff9de;
}

/* Кнопки */
.actions {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-top: 10px;
}

.btn-save, .btn-complete, .btn-test, .btn-generate {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-family: 'Arial', Georgia, serif;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-save {
  background: #d8654f;
  color: white;
}

.btn-save:hover:not(:disabled) {
  background: #c85643;
  transform: translateY(-2px);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-complete {
  background: #28a745;
  color: white;
}

.btn-complete:hover {
  background: #218838;
  transform: translateY(-2px);
}

.btn-test {
  background: #007bff;
  color: white;
  width: 100%;
  margin-top: 10px;
}

.btn-test:hover:not(:disabled) {
  background: #0069d9;
  transform: translateY(-2px);
}

.btn-test.disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.btn-generate {
  background: #6f42c1;
  color: white;
  white-space: nowrap;
}

.btn-generate:hover {
  background: #5a379c;
  transform: translateY(-2px);
}

.completed-badge {
  color: #28a745;
  font-weight: bold;
  font-family: 'Arial', Georgia, serif;
}

/* Информация о тесте */
.test-info {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
  text-align: center;
  font-family: 'Arial', Georgia, serif;
  color: #592012;
}

.test-info p {
  margin: 5px 0;
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

/* Контролы репетитора */
.access-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.control-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Arial', Georgia, serif;
  color: #592012;
  font-size: 14px;
}

.control-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}

/* Результаты учеников */
.students-results {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  padding: 15px;
}

.student-result {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
}

.student-result h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #592012;
  font-family: 'Arial', Georgia, serif;
}

.student-progress {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.student-progress span {
  font-family: 'Arial', Georgia, serif;
  color: #592012;
  font-size: 14px;
}

/* Кнопки навигации */
.navigation-buttons {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 20px;
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
    font-size: 24px;
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
    font-size: 20px;
  }
  
  .section-header {
    font-size: 20px;
  }
  
  .progress-items {
    flex-direction: column;
    align-items: center;
  }
  
  .progress-item {
    width: 100%;
    max-width: 300px;
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
  
  .navigation-buttons {
    flex-direction: column;
  }
  
  .nav-btn {
    width: 100%;
    text-align: center;
  }
  
  .comment-input {
    flex-direction: column;
  }
  
  .comment-input input,
  .btn-generate {
    width: 100%;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .student-progress {
    flex-direction: column;
    gap: 5px;
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
    font-size: 16px;
    padding: 0 10px;
  }
  
  .lesson-status {
    flex-direction: column;
    align-items: center;
    gap: 5px;
  }
  
  .status-badge {
    font-size: 12px;
    padding: 3px 10px;
  }
  
  .lesson-title-divider {
    max-width: 300px;
  }
  
  .section-box {
    padding: 15px;
  }
  
  .section-header {
    font-size: 18px;
  }
  
  .textarea {
    height: 150px;
    padding: 10px;
  }
  
  .nav-btn {
    padding: 12px 20px;
    font-size: 14px;
  }
}
</style>