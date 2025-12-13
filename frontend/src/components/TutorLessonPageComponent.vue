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
      <h1 class="lesson-title">Тема урока: «{{ lessonTitle }}»</h1>
      <div class="lesson-title-divider"></div>
    </div>

    <!-- Контейнер доступа (справа сверху) -->
    <div class="access-control-container">
      <div class="access-control-inner">
        <div class="access-label-container">
          Доступ к уроку для ученика:
        </div>
        <button 
          :class="['access-toggle-btn', lessonData?.is_access ? 'access-open' : 'access-closed']"
          @click="toggleLessonAccess"
        >
          {{ lessonData?.is_access ? 'Открыт' : 'Закрыт' }}
        </button>
      </div>
    </div>

    <!-- Основной контейнер -->
    <div class="main-container">
      <div class="inner-container">

        <!-- Формирование теоретической части -->
        <div class="section-box">
          <h2 class="section-header">Формирование теоретической части урока</h2>
          <div class="section-divider"></div>
          
          <div class="generation-section">
            <div class="comment-input">
              <input 
                v-model="theoryComment" 
                placeholder="Внесите замечания по генерации теории"
                @keyup.enter="generateTheory"
              />
              <button @click="generateTheory" class="btn-generate">
                {{ theoryGenerating ? 'Генерация...' : 'Отправить' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Теоретическая часть -->
        <div class="section-box">
          <h2 class="section-header">Теоретическая часть</h2>
          <div class="section-divider"></div>
          
          <textarea 
            v-model="theoryText" 
            class="textarea"
            placeholder="Введите теоретическую часть урока"
          ></textarea>
          
          <div class="actions">
            <button 
              @click="saveTheory" 
              class="btn-save"
              :disabled="!theoryText"
            >
              Подтвердить генерацию теории
            </button>
          </div>
        </div>

        <!-- Формирование задания на чтение -->
        <div class="section-box">
          <h2 class="section-header">Формирование задания на чтение</h2>
          <div class="section-divider"></div>
          
          <div class="generation-section">
            <div class="comment-input">
              <input 
                v-model="readingComment" 
                placeholder="Внесите замечания по генерации задания на чтение"
                @keyup.enter="generateReading"
              />
              <button @click="generateReading" class="btn-generate">
                {{ readingGenerating ? 'Генерация...' : 'Отправить' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Задание на чтение -->
        <div class="section-box">
          <h2 class="section-header">Задание на чтение</h2>
          <div class="section-divider"></div>
          
          <textarea 
            v-model="readingText" 
            class="textarea"
            placeholder="Введите задание на чтение"
          ></textarea>
          
          <div class="actions">
            <button 
              @click="saveReading" 
              class="btn-save"
              :disabled="!readingText"
            >
              Подтвердить генерацию задания на чтение
            </button>
          </div>
        </div>

        <!-- Формирование задания на говорение -->
        <div class="section-box">
          <h2 class="section-header">Формирование задания на говорение</h2>
          <div class="section-divider"></div>
          
          <div class="generation-section">
            <div class="comment-input">
              <input 
                v-model="speakingComment" 
                placeholder="Внесите замечания по генерации задания на говорение"
                @keyup.enter="generateSpeaking"
              />
              <button @click="generateSpeaking" class="btn-generate">
                {{ speakingGenerating ? 'Генерация...' : 'Отправить' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Задание на говорение -->
        <div class="section-box">
          <h2 class="section-header">Задание на говорение</h2>
          <div class="section-divider"></div>
          
          <textarea 
            v-model="speakingText" 
            class="textarea"
            placeholder="Введите задание на говорение"
          ></textarea>
          
          <div class="actions">
            <button 
              @click="saveSpeaking" 
              class="btn-save"
              :disabled="!speakingText"
            >
              Подтвердить генерацию задания на говорение
            </button>
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
                @click="editTest" 
                class="btn-test"
              >
                Перейти к тесту
              </button>
            </div>
          </div>
        </div>

        <!-- Заметки по уроку -->
        <div class="section-box">
          <h2 class="section-header">Заметки по уроку</h2>
          <div class="section-divider"></div>
          
          <textarea 
            v-model="lessonNotes" 
            class="textarea"
            placeholder="Заметки репетитора по уроку..."
          ></textarea>
          
          <div class="actions">
            <button @click="saveNotes" class="btn-save">
              Сохранить заметки
            </button>
          </div>
        </div>

        <!-- Кнопка оценки результатов (ВНЕ контейнера результатов) -->
        <button @click="showResults" class="btn-results-section">
          {{ showResultsSection ? 'Скрыть результаты урока' : 'Оценить результаты урока' }}
        </button>

        <!-- Результаты урока (изначально скрыт) -->
        <div v-if="showResultsSection" class="section-box results-section">
          <h2 class="section-header">Результаты урока</h2>
          <div class="section-divider"></div>
          
          <div class="results-content">
            <!-- Белая область с информацией о результатах -->
            <div class="results-info">
              <!-- Шаблон-заглушка вместо данных о прогрессе -->
              <div class="template-info">
                <div class="template-header">
                  <h3>Анализ урока от ИИ</h3>
                </div>      
                <div class="template-sections">
                  <div class="template-section">
                    <h4>Анализ грамматики (на основе тестовой части):</h4>
                    <ul>
                      <li>...</li>
                      <li>...</li>
                      <li>...</li>
                    </ul>
                  </div>
                  
                  <div class="template-section">
                    <h4>Анализ заметок репетитора:</h4>
                    <ul>
                      <li>...</li>
                      <li>...</li>
                      <li>...</li>
                    </ul>
                  </div>
                  
                  <div class="template-section">
                    <h4>Итоговое заключение:</h4>
                    <ul>
                      <li>...</li>
                      <li>...</li>
                      <li>...</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="results-controls">
              <div class="controls-left">
                <label class="control-checkbox">
                  <input type="checkbox" v-model="requiresRetry"@change="updateAllStudentsRetry"/>Требуется повторное прохождение темы
                </label>
              </div>
              <div class="controls-right">
                <button @click="approveAllResults" class="btn-approve">
                  Утвердить результаты
                </button>
              </div>
            </div>
          </div>
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
  },
  lessonLabel: {
    type: String,
    default: ""
  }
});

const router = useRouter();
const auth = useAuthStore();

// Используем props вместо получения из route
const lessonIdRef = ref(props.lessonId);
const courseIdRef = ref(props.courseId);
const lessonLabelFromGraph = ref(props.lessonLabel); // Используем label из графа

// Данные урока
const lessonData = ref(null);
const loading = ref(false);

// Флаг отображения раздела результатов
const showResultsSection = ref(false);

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

// Прогресс учеников
const studentsProgress = ref([]);
const requiresRetry = ref(false);

// Вычисляемые свойства
const lessonTitle = computed(() => {
  // Используем label из графа, если он есть, иначе тему урока
  if (lessonLabelFromGraph.value) {
    return lessonLabelFromGraph.value;
  }
  
  if (lessonData.value?.topic?.title) {
    return lessonData.value.topic.title;
  }
  
  if (lessonData.value?.theory_text) {
    const title = lessonData.value.theory_text.length > 50 
      ? lessonData.value.theory_text.substring(0, 50) + "..." 
      : lessonData.value.theory_text;
    return title;
  }
  
  return "Урок";
});

// Методы
function calculateStudentProgress(student) {
  const total = 4;
  let completed = 0;
  
  if (student.theory_completed) completed++;
  if (student.reading_completed) completed++;
  if (student.speaking_completed) completed++;
  if (student.test_completed) completed++;
  
  return Math.round((completed / total) * 100);
}

async function toggleLessonAccess() {
  if (!lessonData.value) return;
  
  try {
      const newAccessState = !lessonData.value.is_access;
  
      await api.put(`/lessons/${lessonIdRef.value}/content`, {
      content_type: "access",
      is_access: newAccessState,
      content: ""
      });
      
      lessonData.value.is_access = newAccessState;
      
  } catch (error) {
      console.error("Ошибка изменения доступа к уроку:", error);
      
      if (error.response) {
      console.error("Детали ошибки:", error.response.data);
      } else {
      }
  }
  }

async function loadLessonData() {
  if (!lessonIdRef.value) return;
  
  try {
    loading.value = true;
    
    // Загружаем информацию об уроке с темой
    const response = await api.get(`/lessons/${lessonIdRef.value}?include_topic=true`);
    lessonData.value = response.data;
    
    // Загружаем контент урока
    theoryText.value = lessonData.value.theory_text || "";
    readingText.value = lessonData.value.reading_text || "";
    speakingText.value = lessonData.value.speaking_text || "";
    lessonNotes.value = lessonData.value.lesson_notes || "";
    
    // Загружаем тест урока
    if (lessonData.value.lesson_plan_json) {
      try {
        lessonTest.value = typeof lessonData.value.lesson_plan_json === 'string'
          ? JSON.parse(lessonData.value.lesson_plan_json)
          : lessonData.value.lesson_plan_json;
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

async function loadStudentsProgress() {
  if (!lessonIdRef.value || !courseIdRef.value) return;
  
  try {
    const response = await api.get(
      `/lessons/${lessonIdRef.value}/students-progress?course_id=${courseIdRef.value}`
    );
    
    studentsProgress.value = response.data.map(student => ({
      ...student,
      requires_retry: student.requires_retry || false
    }));
    
    // Устанавливаем общий флаг повторного прохождения
    if (studentsProgress.value.length > 0) {
      requiresRetry.value = studentsProgress.value.some(student => student.requires_retry);
    }
  } catch (error) {
    console.error("Ошибка загрузки прогресса учеников:", error);
    studentsProgress.value = [];
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
    const response = await api.post(`/lessons/${lessonIdRef.value}/generate/theory`, {
      comment: theoryComment.value
    });
    
    theoryText.value = response.data.generated_content;
    theoryComment.value = "";
    alert("Теория успешно сгенерирована");
    
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
    const response = await api.post(`/lessons/${lessonIdRef.value}/generate/reading`, {
      comment: readingComment.value
    });
    
    readingText.value = response.data.generated_content;
    readingComment.value = "";
    alert("Задание на чтение успешно сгенерировано");
    
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
    const response = await api.post(`/lessons/${lessonIdRef.value}/generate/speaking`, {
      comment: speakingComment.value
    });
    
    speakingText.value = response.data.generated_content;
    speakingComment.value = "";
    alert("Задание на говорение успешно сгенерировано");
    
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
    await api.put(`/lessons/${lessonIdRef.value}/content`, {
      content_type: "theory",
      content: theoryText.value
    });
    alert("Теоретическая часть подтверждена и сохранена");
  } catch (error) {
    console.error("Ошибка сохранения теории:", error);
    alert("Ошибка сохранения теории");
  }
}

async function saveReading() {
  try {
    await api.put(`/lessons/${lessonIdRef.value}/content`, {
      content_type: "reading",
      content: readingText.value
    });
    alert("Задание на чтение подтверждено и сохранено");
  } catch (error) {
    console.error("Ошибка сохранения задания:", error);
    alert("Ошибка сохранения задания");
  }
}

async function saveSpeaking() {
  try {
    await api.put(`/lessons/${lessonIdRef.value}/content`, {
      content_type: "speaking",
      content: speakingText.value
    });
    alert("Задание на говорение подтверждено и сохранено");
  } catch (error) {
    console.error("Ошибка сохранения задания:", error);
    alert("Ошибка сохранения задания");
  }
}

async function saveNotes() {
  try {
    await api.put(`/lessons/${lessonIdRef.value}/content`, {
      content_type: "notes",
      content: lessonNotes.value
    });
    alert("Заметки сохранены");
  } catch (error) {
    console.error("Ошибка сохранения заметок:", error);
    alert("Ошибка сохранения заметок");
  }
}

async function updateAllStudentsRetry() {
  try {
    // Обновляем все записи учеников (без уведомления)
    const promises = studentsProgress.value.map(student =>
      api.put(`/lessons/${lessonIdRef.value}/student/${student.student_id}/retry`, {
        requires_retry: requiresRetry.value
      })
    );
    
    await Promise.all(promises);
    // Уведомление удалено
  } catch (error) {
    console.error("Ошибка обновления настройки:", error);
  }
}

async function approveAllResults() {
  try {
    // Утверждаем результаты всех учеников
    const promises = studentsProgress.value.map(student =>
      api.post(`/lessons/${lessonIdRef.value}/student/${student.student_id}/approve`, {
        ...student
      })
    );
    
    await Promise.all(promises);
    alert("Результаты всех учеников утверждены");
  } catch (error) {
    console.error("Ошибка утверждения результатов:", error);
    alert("Ошибка утверждения результатов");
  }
}

function editTest() 
{
  // Редактирование теста урока
  router.push({
    name: "lesson-test",
    params: { lessonId: lessonIdRef.value },
    query: {
      courseId: courseIdRef.value,
      lessonTitle: lessonTitle.value,
      courseTitle: "Название курса",
      testData: JSON.stringify(lessonTest.value),
      editMode: true // Флаг режима редактирования для репетитора
    }
  });
}

function showResults() {
  // Переключаем видимость раздела результатов
  showResultsSection.value = !showResultsSection.value;
  
  // Если показываем раздел впервые, загружаем прогресс учеников
  if (showResultsSection.value && courseIdRef.value) {
    loadStudentsProgress();
  }
  
  console.log("Результаты урока:", showResultsSection.value ? "показаны" : "скрыты");
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
  
  // Загружаем данные урока
  await loadLessonData();
  
  // Раздел результатов изначально скрыт
  showResultsSection.value = false;
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

watch(
  () => props.lessonLabel,
  (newLabel) => {
    lessonLabelFromGraph.value = newLabel;
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

.access-control-container {
  position: absolute;
  right: 50%;
  transform: translateX(calc(50% + 535px));
  top: 190px;
  z-index: 10;
  background-color: #f4886d;
  border-radius: 10px;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  min-width: 180px;
}

.access-control-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.access-label-container {
  background-color: #b75a43;
  color: #592012;
  font-family: 'Arial', Georgia, serif;
  font-size: 14px;
  font-weight: bold;
  padding: 8px 12px;
  border-radius: 8px;
  white-space: nowrap;
  text-align: center;
  width: 100%;
  box-sizing: border-box;
}

.access-toggle-btn {
  background-color: #c94d50;
  color: #592012;
  font-family: 'Arial', Georgia, serif;
  font-size: 14px;
  font-weight: bold;
  border: none;
  padding: 8px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: 120px;
  width: 100%;
  box-sizing: border-box;
}

.access-toggle-btn.access-open {
  background-color: #ffffbe;
  color: #592012;
}

.access-toggle-btn.access-closed {
  background-color: #c94d50;
  color: #592012;
}

.access-toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.access-toggle-btn:active {
  transform: translateY(0);
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

.textarea:focus {
  outline: none;
  border-color: #c85643;
  background: #fff9de;
}

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
  background: #ffffff;
  font-family: 'Arial', Georgia, serif;
  color: #592012;
}

.comment-input input:focus {
  outline: none;
  border-color: #c85643;
  background: #fff9de;
}

.actions {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.btn-save, .btn-test, .btn-generate, .btn-approve {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-family: 'Arial', Georgia, serif;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-save {
  background: #f4886d;
  color: #592012;
}

.btn-save:hover:not(:disabled) {
  background: #e0785d;
  transform: translateY(-2px);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-generate {
  background: #f4886d;
  color: #592012;
  white-space: nowrap;
}

.btn-generate:hover {
  background: #e0785d;
  transform: translateY(-2px);
}

.btn-test {
  background: #f4886d;
  color: #592012;
  font-size: 16px;
  min-width: 180px;
  margin-top: 10px;
}

.btn-test:hover {
  background: #e0785d;
  transform: translateY(-2px);
}

.btn-results-section {
  background: #ffffff;
  color: #592012;
  border: 2px solid #592012;
  border-radius: 10px;
  padding: 12px 24px;
  font-family: 'Arial', Georgia, serif;
  font-weight: bold;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  display: block;
}

.btn-results-section:hover {
  background: #f5f5f5;
  transform: translateY(-2px);
}

.results-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  gap: 20px;
}

.controls-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.controls-right {
  display: flex;
  align-items: center;
}

.control-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Arial', Georgia, serif;
  color: #592012;
  font-size: 14px;
}

.control-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.btn-approve {
  background: #f4886d;
  color: #592012;
  padding: 10px 20px;
  font-size: 14px;
}

.btn-approve:hover {
  background: #e0785d;
  transform: translateY(-2px);
}

.test-info {
  background: #ffffff;
  border-radius: 10px;
  border: 2px solid #d67962;
  padding: 15px;
  margin-bottom: 20px;
  text-align: center;
  font-family: 'Arial', Georgia, serif;
  color: #592012;
}

.test-button-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.results-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.results-info {
  background: #ffffff;
  border-radius: 10px;
  border: 2px solid #d67962;
  padding: 20px;
}

/* Стили для шаблона-заглушки */
.template-info {
  font-family: 'Arial', Georgia, serif;
  color: #592012;
}

.template-header {
  text-align: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ddd;
}

.template-header h3 {
  font-size: 20px;
  color: #4a5568;
  margin-bottom: 8px;
}

.template-subtitle {
  font-size: 14px;
  color: #718096;
  font-style: italic;
}

.template-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 25px;
}

.template-section {
  background: #f7fafc;
  border-radius: 8px;
  padding: 15px;
  border-left: 4px solid #4299e1;
}

.template-section h4 {
  font-size: 16px;
  color: #2d3748;
  margin-top: 0;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.template-section ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.template-section li {
  margin-bottom: 6px;
  font-size: 14px;
  line-height: 1.4;
  color: #4a5568;
}

.template-note {
  background: #e6fffa;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #81e6d9;
  font-size: 13px;
  color: #234e52;
}

.template-note p {
  margin: 0;
  line-height: 1.5;
}

/* Анимация появления раздела результатов */
.results-section {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  
  .access-control-container {
    right: 10px;
    transform: none;
  }
  
  .lesson-title {
    font-size: 24px;
  }
  
  .btn-results-section {
    max-width: 350px;
  }
  
  .template-section {
    padding: 12px;
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
  
  .access-control-container {
    right: 30px;
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
  
  .access-label-container,
  .access-toggle-btn {
    font-size: 13px;
    padding: 6px 12px;
  }
  
  .section-header {
    font-size: 20px;
  }
  
  .btn-results-section {
    max-width: 300px;
    padding: 10px 20px;
    font-size: 15px;
  }
  
  .template-sections {
    gap: 15px;
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
  
  .access-control-container {
    right: 20px;
    top: 80px;
    padding: 6px 8px;
    min-width: 150px;
  }
  
  .access-label-container,
  .access-toggle-btn {
    font-size: 12px;
    padding: 5px 10px;
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
  
  .comment-input {
    flex-direction: column;
  }
  
  .comment-input input,
  .btn-generate {
    width: 100%;
  }
  
  .btn-results-section {
    max-width: 250px;
    font-size: 14px;
  }
  
  .template-header h3 {
    font-size: 18px;
  }
  
  .template-section h4 {
    font-size: 15px;
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
  
  .access-control-container {
    right: 15px;
    top: 70px;
    padding: 5px;
    min-width: 130px;
  }
  
  .access-label-container,
  .access-toggle-btn {
    font-size: 11px;
    padding: 4px 8px;
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
  
  .btn-results-section {
    max-width: 200px;
    padding: 8px 16px;
    font-size: 13px;
  }
  
  .template-section {
    padding: 10px;
  }
  
  .template-section h4 {
    font-size: 14px;
  }
}
</style>