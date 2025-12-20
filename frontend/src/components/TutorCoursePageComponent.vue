<template>
  <div>
    <!-- Контейнер 1: Добавление ученика -->
    <div class="section">
      <h1 class="title">Добавление ученика</h1>
      <div class="divider"></div>

      <div class="form-group">
        <label class="centered-label">Добавить ученика в курс</label>
        <div class="row centered-row">
          <input 
            v-model="newStudentEmail" 
            type="email" 
            placeholder="Введите почту ученика" 
            :disabled="loading"
            class="centered-input"
            @keyup.enter="addStudent"
          />
          <button 
            class="send-btn" 
            @click="addStudent"
            :disabled="loading || !newStudentEmail"
          >
            {{ loading ? 'Добавление...' : 'Добавить' }}
          </button>
        </div>
        <p v-if="addSuccess" class="info success">
          Ученик успешно добавлен в курс!
        </p>
        <p v-if="addError" class="info error">
          {{ addError }}
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

    <!-- Сообщение, если учеников нет -->
    <div v-if="courseStudents.length === 0" class="section">
      <div class="no-students-message">
        <h3>На курсе пока нет учеников</h3>
        <p>Добавьте учеников, используя форму выше</p>
      </div>
    </div>

    <!-- Входное тестирование -->
    <div class="section">
      <h1 class="title">Входное тестирование</h1>
      <div class="divider"></div>
      
      <div class="test-box">
        <p>
          Количество вопросов: 20<br />
          Граф курса будет доступен после проверки репетитором<br />
          входного тестирования
        </p>
        <button class="test-btn" @click="startTest">
          {{ hasTakenTest ? 'Просмотреть результаты' : 'Перейти к тесту' }}
        </button>
      </div>
    </div>

    <!-- Текущие пробелы - ПОКАЗЫВАЕМ ТОЛЬКО ЕСЛИ ВЫБРАН УЧЕНИК -->
    <div v-if="selectedStudentId && currentStudent" class="section">
      <h1 class="title">
        Текущие пробелы
        <span class="student-short-name">{{ getStudentShortName(currentStudent.student_name) }}</span>
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

    <!-- Граф курса - ПОКАЗЫВАЕМ ТОЛЬКО ЕСЛИ ВЫБРАН УЧЕНИК -->
    <div v-if="selectedStudentId && currentStudent" class="section graph-section">
      <h1 class="title">
        Граф курса
        <span class="student-short-name">{{ getStudentShortName(currentStudent.student_name) }}</span>
      </h1>
      <div class="divider"></div>
      
      <div v-if="!isGraphFinalized" class="form-group">
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
        <div v-else class="no-graph">
          <p>Граф курса еще не сгенерирован для этого ученика</p>
        </div>
      </div>

      <button 
        v-if="!isGraphFinalized"
        class="save-btn graph-save-btn" 
        @click="saveGraph"
        :disabled="loading || !graphData || !selectedStudentId"
      >
        Сохранить граф курса
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import api from "../api/axios";
import CourseGraph from './CourseGraph.vue'

const props = defineProps({
  courseId: {
    type: [String, Number],
    required: true
  }
});

const emit = defineEmits(['load-course-data']);
const auth = useAuthStore();
const router = useRouter();

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
const addSuccess = ref(false);
const addError = ref("");
const hasTakenTest = ref(false);
const isGraphFinalized = ref(false);

// Вычисляемое свойство для получения courseId как числа
const courseId = computed(() => {
  const id = props.courseId;
  if (typeof id === 'string') {
    return parseInt(id) || null;
  }
  return id || null;
});

// Загрузка данных для репетитора
async function loadTutorCourseData() {
  try {
    console.log("Загрузка данных репетитора для курса:", courseId.value);
    
    // Загружаем список учеников на курсе
    const response = await api.get(`/courses/${courseId.value}/students`);
    
    if (response.data && response.data.students) {
      courseStudents.value = response.data.students;
      console.log("Загружены ученики:", courseStudents.value);
      
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

// Функция добавления ученика в курс
async function addStudent() {
  if (!newStudentEmail.value) {
    addError.value = "Введите email ученика";
    return;
  }
  
  try {
    loading.value = true;
    addError.value = "";
    addSuccess.value = false;
    
    // Проверяем валидность email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(newStudentEmail.value)) {
      addError.value = "Введите корректный email адрес";
      loading.value = false;
      return;
    }
    
    // Вызываем API для добавления ученика
    const response = await api.post(`/courses/${courseId.value}/add-student`, {
      email: newStudentEmail.value
    });
    
    addSuccess.value = true;
    newStudentEmail.value = "";
    
    // Обновляем список учеников
    await loadTutorCourseData();
    
    // Сбрасываем успешное сообщение через 3 секунды
    setTimeout(() => {
      addSuccess.value = false;
    }, 3000);
    
  } catch (error) {
    console.error("Ошибка добавления ученика:", error);
    
    // Обрабатываем различные ошибки
    if (error.response?.status === 404) {
      if (error.response?.data?.detail?.includes("не найден")) {
        addError.value = "Ученик с указанным email не найден в системе";
      } else {
        addError.value = "Курс не найден";
      }
    } else if (error.response?.status === 400) {
      if (error.response?.data?.detail?.includes("уже записан")) {
        addError.value = "Ученик уже записан на курс или на другой курс";
      } else {
        addError.value = error.response.data.detail || "Некорректные данные";
      }
    } else if (error.response?.status === 403) {
      addError.value = "У вас нет прав для добавления учеников";
    } else if (error.response?.status === 500) {
      addError.value = "Ошибка сервера. Попробуйте позже";
    } else {
      addError.value = "Ошибка добавления ученика. Проверьте email и попробуйте снова";
    }
  } finally {
    loading.value = false;
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
    await loadStudentGraph(studentId);
    
  } catch (error) {
    console.error("Ошибка загрузки данных ученика:", error);
  }
}

// Загрузка графа ученика
async function loadStudentGraph(studentId = null) {
  const targetStudentId = studentId || selectedStudentId.value;
  
  if (!targetStudentId || !courseId.value) {
    console.error("Нет studentId или courseId для загрузки графа");
    console.log("studentId:", targetStudentId);
    console.log("courseId:", courseId.value);
    return;
  }
  
  try {
    loadingGraph.value = true;
    console.log(`Загрузка графа для студента ${targetStudentId}, курс ${courseId.value}`);
    
    const response = await api.get(
      `/courses/${courseId.value}/student/${targetStudentId}/graph`
    );
    
    console.log("Ответ от сервера при загрузке графа:", response.data);
    
    if (response.data && response.data.graph_data) {
      graphData.value = response.data.graph_data;
      
      // Проверяем, финализирован ли граф
      isGraphFinalized.value = response.data.is_finalized || false;
      console.log("Граф финализирован:", isGraphFinalized.value);
    }
  } catch (error) {
    console.error("Ошибка загрузки графа:", error);
    graphData.value = null;
    isGraphFinalized.value = false;
    
    if (error.response) {
      console.error("Детали ошибки:", error.response.data);
    }
  } finally {
    loadingGraph.value = false;
  }
}

// Обработчик выбора ученика
function onStudentSelected() {
  if (selectedStudentId.value) {
    const student = courseStudents.value.find(s => s.student_id === selectedStudentId.value);
    if (student) {
      currentStudent.value = student;
      knowledgeGaps.value = student.knowledge_gaps || "";
      loadStudentGraph(selectedStudentId.value);
    }
  } else {
    currentStudent.value = null;
    knowledgeGaps.value = "";
    graphData.value = null;
  }
}

// Удаление выбранного ученика из курса
async function removeSelectedStudent() {
  if (!selectedStudentId.value) {
    alert("Сначала выберите ученика из списка");
    return;
  }
  
  // Подтверждение удаления
  const student = courseStudents.value.find(s => s.student_id === selectedStudentId.value);
  const studentName = student ? student.student_name : "выбранного ученика";
  
  if (!confirm(`Вы уверены, что хотите удалить ученика ${studentName} из курса?`)) {
    return;
  }
  
  try {
    loading.value = true;
    
    // Вызываем API для удаления ученика
    const response = await api.delete(`/courses/${courseId.value}/students/${selectedStudentId.value}`);
    
    console.log("Ответ сервера при удалении:", response.data);
    
    // Обновляем список учеников
    await loadTutorCourseData();
    
    // Сбрасываем выбранного ученика
    selectedStudentId.value = "";
    currentStudent.value = null;
    knowledgeGaps.value = "";
    graphData.value = null;
    
    // Показываем уведомление
    alert(`Ученик ${studentName} успешно удален из курса`);
    
  } catch (error) {
    console.error("Ошибка удаления ученика:", error);
    console.error("Детали ошибки:", error.response?.data);
    
    // Обрабатываем различные ошибки
    let errorMessage = "Не удалось удалить ученика из курса";
    
    if (error.response?.status === 404) {
      errorMessage = error.response.data.detail || "Ученик или курс не найден";
    } else if (error.response?.status === 403) {
      errorMessage = "У вас нет прав для удаления учеников из курса";
    } else if (error.response?.status === 500) {
      errorMessage = "Ошибка сервера. Попробуйте позже";
    } else if (error.code === 'ERR_NETWORK') {
      errorMessage = "Ошибка сети. Проверьте подключение к интернету";
    }
    
    alert(errorMessage);
  } finally {
    loading.value = false;
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
    
    await api.put(`/courses/${courseId.value}/student/${selectedStudentId.value}/knowledge-gaps`, {
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
  
  // Снимаем флаг финализации при создании нового графа
  isGraphFinalized.value = false;
}

// Сохранение графа
async function saveGraph() {
  console.log("Начинаем сохранение графа...");
  console.log("graphData:", graphData.value);
  console.log("selectedStudentId:", selectedStudentId.value);
  console.log("courseId:", courseId.value);

  if (!graphData.value || !graphData.value.nodes || graphData.value.nodes.length === 0) {
    alert("Граф не может быть пустым");
    return;
  }

  try {
    // Проверяем необходимые данные
    if (!selectedStudentId.value) {
      alert("Выберите ученика");
      return;
    }

    if (!courseId.value) {
      alert("ID курса не определен");
      return;
    }

    // Подготовка данных для отправки
    const saveData = {
      ...graphData.value,
      is_finalized: true, // Добавляем флаг финализации
      saved_at: new Date().toISOString(),
      saved_by: auth.user?.user_id // ID пользователя, который сохранил
    };

    console.log("Отправляемые данные:", saveData);

    // Отправляем на сервер
    const response = await api.put(
      `/courses/${courseId.value}/student/${selectedStudentId.value}/graph`,
      saveData
    );

    console.log("Ответ сервера:", response.data);

    if (response.data) {
      // Помечаем граф как финализированный
      isGraphFinalized.value = true;
      
      // Очищаем поле для редактирования
      graphChanges.value = "";
      
      alert("Граф курса успешно сохранен как окончательный!");
      
      // Перезагружаем граф, чтобы получить обновленные данные с сервера
      await loadStudentGraph(selectedStudentId.value);
    }
    
  } catch (error) {
    console.error("Ошибка сохранения графа:", error);
    
    // Более детальная информация об ошибке
    if (error.response) {
      console.error("Статус ошибки:", error.response.status);
      console.error("Данные ошибки:", error.response.data);
      alert(`Ошибка сервера: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
    } else if (error.request) {
      console.error("Нет ответа от сервера:", error.request);
      alert("Не удалось подключиться к серверу");
    } else {
      console.error("Ошибка настройки запроса:", error.message);
      alert(`Ошибка: ${error.message}`);
    }
  }
}

// Обработчик клика по узлу графа
function onGraphNodeClick({ node, lessonId }) {
    console.log('Клик по узлу графа:', node.data.label, 'lessonId:', lessonId);
    
    if (lessonId) {
        router.push({
            path: `/lesson/${lessonId}`,
            query: {
                courseId: courseId.value,
                studentId: selectedStudentId.value || auth.user.user_id,
                fromGraph: 'true'
            }
        });
    }
}

// Начало тестирования
function startTest() 
{
  // Репетитор может просматривать входные тесты
  console.log("Переход к входному тесту курса");
  
  router.push({
    name: "input-test",
    params: { courseId: courseId.value },
    query: {
      testData: JSON.stringify({
        test_type: "placement",
        questions: 20,
        time_limit: 20
      }),
      isTutor: true // Флаг для режима просмотра репетитором
    }
  });
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

// Демо-функции
function createDemoStudents() {
  // Для демонстрации, если API недоступен
  courseStudents.value = [
    { student_id: 1, student_name: "Matokhin Ilya", knowledge_gaps: "Need practice with Past Simple" },
    { student_id: 6, student_name: "Z Z", knowledge_gaps: "Difficulty with vocabulary" }
  ];
  
  if (courseStudents.value.length > 0) {
    selectedStudentId.value = courseStudents.value[0].student_id;
    currentStudent.value = courseStudents.value[0];
  }
}

// Инициализация
onMounted(() => {
  console.log("TutorCoursePageComponent mounted with courseId:", courseId.value);
  loadTutorCourseData();
});

// Отслеживание изменения выбранного ученика
watch(selectedStudentId, (newStudentId) => {
  console.log("Выбран новый ученик:", newStudentId);
  if (newStudentId) {
    const student = courseStudents.value.find(s => s.student_id === newStudentId);
    if (student) {
      currentStudent.value = student;
      knowledgeGaps.value = student.knowledge_gaps || "";
      loadStudentGraph(newStudentId);
    }
  } else {
    currentStudent.value = null;
    knowledgeGaps.value = "";
    graphData.value = null;
    isGraphFinalized.value = false;
  }
});
</script>

<style scoped>
.section {
  background: #fedac4;
  border-radius: 15px;
  padding: 25px;
  border: none;
  margin-bottom: 20px;
}

.title {
  text-align: center;
  margin-bottom: 15px;
  font-size: 28px;
  font-weight: bold;
  color: #592012;
  font-family: 'Arial', Georgia, serif;
}

.student-short-name {
  color: #4CAF50;
  font-weight: bold;
  margin-left: 10px;
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

.send-btn,
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
.test-btn:hover:not(:disabled),
.save-btn:hover:not(:disabled),
.generate-btn:hover:not(:disabled) {
  background: #E0785D;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(244, 136, 109, 0.3);
}

.send-btn:disabled,
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

.centered-save-btn {
  display: block;
  margin: 20px auto 0 auto;
  padding: 12px 40px;
}

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

/* Сообщения для пользователя */
.no-students-message {
  text-align: center;
  padding: 30px 20px;
}

.no-students-message h3 {
  color: #592012;
  margin-bottom: 10px;
  font-size: 20px;
}

.no-students-message p {
  color: #666;
  font-size: 16px;
  line-height: 1.5;
}

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
  .remove-btn {
    width: 100%;
  }
  
  .send-btn,
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
  
  .no-students-message {
    padding: 20px 15px;
  }
  
  .no-students-message h3 {
    font-size: 18px;
  }
}

.no-student {
  color: #F44336;
  font-style: italic;
}
</style>