<template>
  <div>
    <!-- Контейнер 1: Добавление ученика -->
    <div class="section">
      <h1 class="title">Добавление ученика</h1>
      <div class="divider"></div>

      <div class="form-group">
        <label class="centered-label">Добавить нового ученика</label>
        <div class="row centered-row">
          <input 
            v-model="newStudentEmail" 
            type="text" 
            placeholder="Введите почту ученика" 
            :disabled="loading"
            class="centered-input"
          />
          <button 
            class="send-btn" 
            @click="inviteStudent"
            :disabled="loading || !newStudentEmail"
          >
            {{ loading ? 'Отправка...' : 'Отправить' }}
          </button>
        </div>
        <p v-if="inviteSuccess" class="info success">
          Письмо успешно отправлено! Дождитесь подтверждения от ученика.
        </p>
        <p v-if="inviteError" class="info error">
          {{ inviteError }}
        </p>
      </div>
    </div>

    <!-- Контейнер 2: Список текущих учеников - ВЫПАДАЮЩИЙ СПИСОК -->
    <div v-if="courseStudents.length > 0" class="section">
      <h2 class="subtitle">Список текущих учеников</h2>
      <div class="divider"></div>

      <div class="form-group">
        <div class="student-selection-container">
          <div class="selection-row">
            <select 
              v-model="selectedStudentId" 
              :disabled="loading"
              class="student-select custom-select"
              @change="onStudentSelected"
            >
              <option value="">Выбрать ученика</option>
              <option 
                v-for="student in courseStudents" 
                :key="student.student_id" 
                :value="student.student_id"
              >
                {{ student.student_name }}
              </option>
            </select>
            
            <button 
              class="open-btn" 
              @click="openStudentCourse"
              :disabled="!selectedStudentId || loading"
            >
              Открыть курс
            </button>
            <button 
              class="remove-btn" 
              @click="removeSelectedStudent"
              :disabled="!selectedStudentId || loading"
            >
              Удалить из курса
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Входное тестирование -->
    <div class="section">
      <h1 class="title">Входное тестирование</h1>
      <div class="divider"></div>
      
      <div class="test-box">
        <p>
          Время прохождение тестирования ~20 мин<br />Количество вопросов: 20<br />
          Граф курса будет доступен после проверки репетитором<br />
          входного тестирования
        </p>
        <button class="test-btn" @click="startTest">
          {{ hasTakenTest ? 'Просмотреть результаты' : 'Перейти к тесту' }}
        </button>
      </div>
    </div>

    <!-- Текущие пробелы -->
    <div class="section">
      <h1 class="title">
        Текущие пробелы
        <span v-if="currentStudent"> {{ getStudentShortName(currentStudent.student_name) }}</span>
      </h1>
      <div class="divider"></div>
      
      <textarea 
        v-model="knowledgeGaps" 
        placeholder="Введите комментарии к результатам прохождения теста ученика"
      ></textarea>
      <button 
        class="save-btn centered-save-btn" 
        @click="saveKnowledgeGaps"
        :disabled="loading || !selectedStudentId"
      >
        {{ loading ? 'Сохранение...' : 'Сохранить' }}
      </button>
    </div>

    <!-- Граф курса -->
    <div class="section graph-section">
      <h1 class="title">Граф курса</h1>
      <div class="divider"></div>
      
      <div class="form-group">
        <label>
          Граф для ученика: 
          <span v-if="currentStudent" class="student-name">{{ getStudentShortName(currentStudent.student_name) }}</span>
          <span v-else class="no-student">(выберите ученика)</span>
        </label>
        <div class="row">
          <input 
            v-model="graphChanges" 
            type="text" 
            placeholder="Внесите изменения в граф (например: 'добавить узел Present Perfect')" 
            :disabled="loading || !selectedStudentId"
          />
          <button 
            class="generate-btn" 
            @click="generateGraph"
            :disabled="loading || !selectedStudentId"
          >
            {{ loading ? 'Обновление...' : 'Обновить граф' }}
          </button>
        </div>
      </div>

      <div class="graph-box">
        <CourseGraph 
          v-if="graphData && graphData.nodes && graphData.nodes.length > 0 && selectedStudentId"
          :graphData="graphData"
          :courseId="parseInt(courseId)"
          :studentId="selectedStudentId"
          @node-click="onGraphNodeClick"
        />
        <div v-else-if="loadingGraph" class="loading-graph">
          <div class="spinner"></div>
          <p>Загрузка графа курса...</p>
        </div>
        <div v-else-if="!selectedStudentId" class="no-graph">
          <p>Выберите ученика для просмотра его графа</p>
        </div>
        <div v-else class="no-graph">
          <p>Граф курса еще не сгенерирован для этого ученика</p>
          <button @click="loadStudentGraph" class="retry-btn">Загрузить граф</button>
        </div>
      </div>

      <button 
        class="save-btn graph-save-btn" 
        @click="saveGraph"
        :disabled="loading || !graphData || !selectedStudentId"
      >
        Сохранить изменения
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, defineProps, defineEmits } from "vue";
import { useAuthStore } from "../stores/auth";
import api from "../api/axios";
import CourseGraph from './CourseGraph.vue'

const props = defineProps({
  courseId: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['load-course-data']);

const auth = useAuthStore();

// Состояния
const loading = ref(false);
const loadingGraph = ref(false);
const courseStudents = ref([]);
const currentStudent = ref(null);
const newStudentEmail = ref("");
const selectedStudentId = ref("");
const knowledgeGaps = ref("");
const graphChanges = ref("");
const graphData = ref(null);
const inviteSuccess = ref(false);
const inviteError = ref("");
const hasTakenTest = ref(false);

// Загрузка данных для репетитора
async function loadTutorCourseData() {
  try {
    // Загружаем список учеников на курсе
    const tutorId = auth.user.user_id;
    const response = await api.get(`/courses/${props.courseId}/students`);
    
    if (response.data && response.data.students) {
      courseStudents.value = response.data.students;
      
      // Если есть ученики, выбираем первого
      if (courseStudents.value.length > 0) {
        selectedStudentId.value = courseStudents.value[0].student_id;
        currentStudent.value = courseStudents.value[0];
        await loadStudentData(selectedStudentId.value);
      }
    }
    
  } catch (error) {
    console.error("Ошибка загрузки данных репетитора:", error);
    // Для демонстрации создаем тестовых учеников
    createDemoStudents();
  }
}

// Загрузка данных ученика
async function loadStudentData(studentId) {
  try {
    // Загружаем пробелы в знаниях
    const student = courseStudents.value.find(s => s.student_id === studentId);
    if (student) {
      knowledgeGaps.value = student.knowledge_gaps || "";
    }
    
    // Загружаем граф ученика
    await loadStudentGraph();
    
  } catch (error) {
    console.error("Ошибка загрузки данных ученика:", error);
  }
}

// Загрузка графа ученика
async function loadStudentGraph() {
  if (!selectedStudentId.value) return;
  
  try {
    loadingGraph.value = true;
    
    const response = await api.get(`/courses/${props.courseId}/student/${selectedStudentId.value}/graph`);
    
    if (response.data && response.data.graph_data) {
      graphData.value = response.data.graph_data;
    } else {
      graphData.value = null;
    }
    
  } catch (error) {
    console.error("Ошибка загрузки графа ученика:", error);
    graphData.value = null;
  } finally {
    loadingGraph.value = false;
  }
}

// Создание демо-студентов для тестирования
function createDemoStudents() {
  courseStudents.value = [
    {
      student_id: 1,
      student_name: "Matokhin Ilya",
      email: "matokhin.ilya@yandex.ru",
      knowledge_gaps: "Gaps in Past Simple and articles"
    },
    {
      student_id: 6,
      student_name: "Ivanov Ivan",
      email: "ivanov@example.com",
      knowledge_gaps: "Difficulty with Present Continuous and vocabulary"
    },
    {
      student_id: 2,
      student_name: "Molchanova Liana",
      email: "liana@bk.ru",
      knowledge_gaps: "Need business communication practice"
    }
  ];
  
  if (courseStudents.value.length > 0) {
    selectedStudentId.value = courseStudents.value[0].student_id;
    currentStudent.value = courseStudents.value[0];
    knowledgeGaps.value = courseStudents.value[0].knowledge_gaps;
  }
}

// Обработчик выбора ученика
function onStudentSelected() {
  if (selectedStudentId.value) {
    const student = courseStudents.value.find(s => s.student_id === selectedStudentId.value);
    if (student) {
      currentStudent.value = student;
      knowledgeGaps.value = student.knowledge_gaps || "";
      loadStudentGraph();
    }
  } else {
    currentStudent.value = null;
    knowledgeGaps.value = "";
    graphData.value = null;
  }
}

// Приглашение ученика
async function inviteStudent() {
  if (!newStudentEmail.value) return;
  
  try {
    loading.value = true;
    inviteError.value = "";
    
    // Здесь должен быть API вызов для приглашения ученика
    await api.post(`/courses/${props.courseId}/invite`, {
      email: newStudentEmail.value
    });
    
    inviteSuccess.value = true;
    newStudentEmail.value = "";
    
    // Обновляем список учеников
    setTimeout(() => {
      inviteSuccess.value = false;
      loadTutorCourseData();
    }, 3000);
    
  } catch (error) {
    inviteError.value = error.response?.data?.detail || "Ошибка отправки приглашения";
    console.error("Ошибка приглашения ученика:", error);
  } finally {
    loading.value = false;
  }
}

// Удаление выбранного ученика из курса
async function removeSelectedStudent() {
  if (!selectedStudentId.value || !confirm("Вы уверены, что хотите удалить ученика из курса?")) {
    return;
  }
  
  try {
    loading.value = true;
    
    // Здесь должен быть API вызов для удаления ученика
    await api.delete(`/courses/${props.courseId}/students/${selectedStudentId.value}`);
    
    // Обновляем список учеников
    await loadTutorCourseData();
    
    // Сбрасываем выбранного ученика
    selectedStudentId.value = "";
    currentStudent.value = null;
    knowledgeGaps.value = "";
    graphData.value = null;
    
    alert("Ученик удален из курса");
    
  } catch (error) {
    console.error("Ошибка удаления ученика:", error);
    alert("Не удалось удалить ученика из курса");
  } finally {
    loading.value = false;
  }
}

// Открытие курса выбранного ученика
function openStudentCourse() {
  if (!selectedStudentId.value) {
    alert("Сначала выберите ученика из списка");
    return;
  }
  
  const selectedStudent = courseStudents.value.find(s => s.student_id === selectedStudentId.value);
  if (selectedStudent) {
    alert(`Открытие курса для ученика: ${selectedStudent.student_name}`);
    // Здесь можно добавить навигацию к подробному просмотру курса ученика
  }
}

// Сохранение пробелов в знаниях
async function saveKnowledgeGaps() {
  if (!selectedStudentId.value) {
    alert("Сначала выберите ученика из списка");
    return;
  }
  
  try {
    loading.value = true;
    
    await api.put(`/courses/${props.courseId}/student/${selectedStudentId.value}/knowledge-gaps`, {
      knowledge_gaps: knowledgeGaps.value
    });
    
    alert("Пробелы в знаниях сохранены");
    
  } catch (error) {
    console.error("Ошибка сохранения пробелов:", error);
    alert("Не удалось сохранить пробелы в знаниях");
  } finally {
    loading.value = false;
  }
}

// Генерация/обновление графа
async function generateGraph() {
  if (!selectedStudentId.value) {
    alert("Сначала выберите ученика из списка");
    return;
  }
  
  if (!graphChanges.value.trim()) {
    alert("Введите изменения для генерации графа");
    return;
  }
  
  try {
    loading.value = true;
    
    // Здесь должен быть API вызов для генерации графа
    // Пока используем демо-данные
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Создаем демо-граф на основе изменений
    createDemoGraph();
    
    graphChanges.value = "";
    alert("Граф успешно обновлен");
    
  } catch (error) {
    console.error("Ошибка генерации графа:", error);
    alert("Не удалось обновить граф");
  } finally {
    loading.value = false;
  }
}

// Создание демо-графа
function createDemoGraph() {
  if (!currentStudent.value) return;
  
  // Базовый граф курса
  const baseGraph = {
    "nodes": [
      {"id": "1", "label": "Present Simple", "data": {"lesson_id": 1}, "position": {"x": 200, "y": 150}, "group": 0},
      {"id": "2", "label": "Past Simple", "data": {"lesson_id": 2}, "position": {"x": 400, "y": 150}, "group": 1},
      {"id": "3", "label": "Future Tenses", "data": {"lesson_id": 3}, "position": {"x": 200, "y": 350}, "group": 2},
      {"id": "4", "label": "Articles", "data": {"lesson_id": 4}, "position": {"x": 400, "y": 350}, "group": 3},
      {"id": "5", "label": "Basic Vocabulary", "data": {"lesson_id": 5}, "position": {"x": 300, "y": 500}, "group": 2}
    ],
    "edges": [
      {"id": "e1-2", "source": "1", "target": "2", "label": "Next"},
      {"id": "e1-3", "source": "1", "target": "3", "label": "Alternative"},
      {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
      {"id": "e3-5", "source": "3", "target": "5", "label": "Next"},
      {"id": "e4-5", "source": "4", "target": "5", "label": "Next"}
    ]
  };
  
  // Клонируем граф
  graphData.value = JSON.parse(JSON.stringify(baseGraph));
}

// Сохранение графа
async function saveGraph() {
  if (!selectedStudentId.value || !graphData.value) {
    alert("Нет данных для сохранения");
    return;
  }
  
  try {
    loading.value = true;
    
    await api.put(`/courses/${props.courseId}/student/${selectedStudentId.value}/graph`, graphData.value);
    
    alert("Граф курса сохранен");
    
  } catch (error) {
    console.error("Ошибка сохранения графа:", error);
    alert("Не удалось сохранить граф");
  } finally {
    loading.value = false;
  }
}

// Обработчик клика по узлу графа
function onGraphNodeClick({ node, lessonId }) {
  console.log('Клик по узлу графа ученика:', node.data.label, 'lessonId:', lessonId);
}

// Начало тестирования
function startTest() {
  console.log("Начать тестирование");
}

// Функция для получения сокращенного имени ученика
function getStudentShortName(fullName) {
  if (!fullName) return '';
  const parts = fullName.split(' ');
  if (parts.length >= 2) {
    const lastName = parts[0];
    const firstNameInitial = parts[1].charAt(0) + '.';
    return `${lastName} ${firstNameInitial}`;
  }
  return fullName;
}

// Инициализация
onMounted(() => {
  loadTutorCourseData();
});

// Отслеживание изменения выбранного ученика
watch(selectedStudentId, (newStudentId) => {
  if (newStudentId) {
    const student = courseStudents.value.find(s => s.student_id === newStudentId);
    if (student) {
      currentStudent.value = student;
      knowledgeGaps.value = student.knowledge_gaps || "";
      loadStudentGraph();
    }
  } else {
    currentStudent.value = null;
    knowledgeGaps.value = "";
    graphData.value = null;
  }
});
</script>
  
  <style scoped>
  /* Общие стили для всех контейнеров */
  .section {
    background: #fedac4;
    border-radius: 15px;
    padding: 25px;
    border: none;
  }
  
  /* Заголовки и divider */
  .title {
    text-align: center;
    margin-bottom: 15px;
    font-size: 28px;
    font-weight: bold;
    color: #592012;
    font-family: 'Arial', Georgia, serif;
  }
  
  .subtitle {
    text-align: center;
    margin-bottom: 15px;
    font-size: 24px;
    font-weight: bold;
    color: #592012;
    font-family: 'Arial', Georgia, serif;
  }
  
  .divider {
    height: 3px;
    background: #592012;
    border-radius: 2px;
    margin: 0 auto 20px auto;
    width: 80%;
    max-width: 600px;
  }
  
  label {
    font-size: 16px;
    display: block;
    margin-bottom: 8px;
    color: #592012;
    font-weight: bold;
    font-family: 'Arial', Georgia, serif;
  }
  
  .centered-label {
    text-align: center;
    font-size: 14px;
    margin-bottom: 10px;
  }
  
  .row {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .centered-row {
    justify-content: center;
    align-items: center;
    max-width: 500px;
    margin: 0 auto;
  }
  
  .centered-input {
    width: 300px;
  }
  
  /* Выпадающий список для учеников */
  .student-selection-container {
    margin-top: 15px;
  }
  
  .selection-row {
    display: flex;
    gap: 10px;
    align-items: center;
  }
  
  .custom-select {
    width: 100%;
    padding: 12px 15px;
    padding-right: 40px;
    background: #FFFFFF url('/src/assets/arrow_list.svg') no-repeat right 15px center;
    background-size: 12px;
    border: 2px solid #F4886D;
    border-radius: 10px;
    font-family: 'Arial', Georgia, serif;
    font-size: 15px;
    color: #592012;
    box-sizing: border-box;
    cursor: pointer;
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
  }
  
  .custom-select::-ms-expand {
    display: none;
  }
  
  .custom-select:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(244, 136, 109, 0.3);
  }
  
  .custom-select:disabled {
    background: #f5f5f5 url('/src/assets/arrow_list.svg') no-repeat right 15px center;
    background-size: 12px;
    cursor: not-allowed;
    opacity: 0.7;
  }
  
  input,
  textarea {
    width: 100%;
    padding: 12px 15px;
    background: #FFFFFF;
    border: 2px solid #F4886D;
    border-radius: 10px;
    font-family: 'Arial', Georgia, serif;
    font-size: 15px;
    color: #592012;
    box-sizing: border-box;
  }
  
  input::placeholder,
  textarea::placeholder {
    color: #8A7D75;
    opacity: 0.7;
  }
  
  input:focus,
  textarea:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(244, 136, 109, 0.3);
  }
  
  input:disabled,
  textarea:disabled {
    background: #f5f5f5;
    cursor: not-allowed;
    opacity: 0.7;
  }
  
  textarea {
    height: 100px;
    resize: none;
    margin-top: 10px;
    font-family: 'Arial', Georgia, serif;
  }
  
  /* Кнопки */
  .send-btn,
  .open-btn,
  .remove-btn,
  .test-btn,
  .save-btn,
  .generate-btn {
    background: #F4886D;
    color: #592012;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    cursor: pointer;
    white-space: nowrap;
    font-family: 'Arial', Georgia, serif;
    font-weight: bold;
    transition: all 0.3s;
    font-size: 15px;
  }
  
  .send-btn:hover:not(:disabled),
  .open-btn:hover:not(:disabled),
  .test-btn:hover:not(:disabled),
  .save-btn:hover:not(:disabled),
  .generate-btn:hover:not(:disabled) {
    background: #E0785D;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(244, 136, 109, 0.3);
  }
  
  .send-btn:disabled,
  .open-btn:disabled,
  .remove-btn:disabled,
  .test-btn:disabled,
  .save-btn:disabled,
  .generate-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .remove-btn {
    background: #c46a57;
    color: white;
  }
  
  .remove-btn:hover:not(:disabled) {
    background: #b35a47;
  }
  
  /* Входное тестирование */
  .test-box {
    background: #FFFFFF;
    border: 2px solid #F4886D;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    color: #592012;
    font-family: 'Arial', Georgia, serif;
  }
  
  .test-btn {
    margin-top: 15px;
    padding: 15px 30px;
    font-size: 16px;
  }
  
  /* Кнопка Сохранить для пробелов */
  .centered-save-btn {
    display: block;
    margin: 20px auto 0 auto;
    padding: 12px 40px;
  }
  
  /* Граф курса */
  .graph-section .row {
    margin-bottom: 15px;
  }
  
  .graph-box {
    margin-top: 20px;
    min-height: 300px;
    background: #FFFFFF;
    border: 2px solid #F4886D;
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  
  .loading-graph,
  .graph-placeholder,
  .no-graph {
    text-align: center;
    color: #666;
    font-family: 'Arial', Georgia, serif;
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #F4886D;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .graph-save-btn {
    display: block;
    margin: 20px auto 0 auto;
    padding: 12px 40px;
  }
  
  .info {
    margin-top: 10px;
    padding: 10px;
    border-radius: 8px;
    font-size: 14px;
    font-family: 'Arial', Georgia, serif;
    text-align: center;
  }
  
  .info.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }
  
  .info.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
  
  /* Адаптивность */
  @media (max-width: 1024px) {
    .section {
      padding: 20px;
    }
    
    .selection-row {
      flex-wrap: wrap;
    }
    
    .custom-select {
      flex: 1;
      min-width: 200px;
    }
    
    .open-btn,
    .remove-btn {
      flex: 1;
    }
  }
  
  @media (max-width: 768px) {
    .title {
      font-size: 24px;
    }
    
    .subtitle {
      font-size: 20px;
    }
    
    .row {
      flex-direction: column;
      align-items: stretch;
    }
    
    .centered-row {
      flex-direction: row;
      justify-content: center;
    }
    
    .centered-input {
      width: 100%;
      max-width: 300px;
    }
    
    .selection-row {
      flex-direction: column;
    }
    
    .custom-select,
    .open-btn,
    .remove-btn {
      width: 100%;
    }
    
    .send-btn,
    .open-btn,
    .remove-btn,
    .test-btn,
    .save-btn,
    .generate-btn {
      width: 100%;
      margin-top: 5px;
    }
  }
  
  @media (max-width: 480px) {
    .section {
      padding: 15px;
    }
    
    .title {
      font-size: 20px;
    }
    
    .subtitle {
      font-size: 18px;
    }
    
    input,
    .custom-select,
    textarea {
      padding: 10px 12px;
      font-size: 14px;
    }
    
    .graph-box {
      min-height: 250px;
    }
  }

  .student-name {
    color: #4CAF50;
    font-weight: bold;
  }
  
  .no-student {
    color: #F44336;
    font-style: italic;
  }
  
  .retry-btn {
    background: #F4886D;
    color: #592012;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    cursor: pointer;
    margin-top: 15px;
    font-family: 'Arial', Georgia, serif;
    font-weight: bold;
    transition: all 0.3s;
  }
  
  .retry-btn:hover {
    background: #E0785D;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(244, 136, 109, 0.3);
  }
  </style>