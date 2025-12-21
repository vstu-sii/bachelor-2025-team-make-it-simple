<template>
  <div>
    <!-- Входное тестирование -->
    <div class="section">
      <h1 class="title">Входное тестирование</h1>
      <div class="divider"></div>
      
      <div class="test-box">
        <!-- Отображаем правильное количество вопросов или информацию о том, что тест не сформирован -->
        <div v-if="testStatus.is_test_generated && testStatus.is_test_finalized" class="test-info">
          <p class="test-status">
            <strong>Статус:</strong> 
            <span class="status-finalized">Доступен для прохождения</span>
          </p>
          <p class="test-questions">
            <strong>Количество вопросов:</strong> {{ testStatus.questions_count || 0 }}
          </p>
          <p class="test-note">
            Ваш прогресс будет доступен после проверки репетитором
          </p>
        </div>
        <div v-else-if="testStatus.is_test_generated && !testStatus.is_test_finalized" class="test-info">
          <p class="test-status">
            <strong>Статус:</strong> 
            <span class="status-draft">Подготовка репетитором</span>
          </p>
          <p class="test-note">
            Репетитор готовит входное тестирование. Оно станет доступно после завершения подготовки.
          </p>
        </div>
        <div v-else class="test-info">
          <p class="test-status">
            <strong>Статус:</strong> 
            <span class="status-not-generated">Не сформирован</span>
          </p>
          <p class="test-note">
            Входное тестирование для этого курса еще не создано.
          </p>
        </div>
        
        <button 
          class="test-btn" 
          @click="startInputTest"
          :disabled="!testStatus.is_test_generated || !testStatus.is_test_finalized"
        >
          {{ testStatus.is_test_generated && testStatus.is_test_finalized ? 'Пройти тест' : 'Тест не доступен' }}
        </button>
      </div>
    </div>

    <!-- Мои пробелы в знаниях -->
    <div class="section">
      <h1 class="title">Мои пробелы в знаниях</h1>
      <div class="divider"></div>
      
      <textarea 
        v-model="knowledgeGaps" 
        placeholder="Ваши пробелы в знаниях..."
        :disabled="true"
      ></textarea>
    </div>

    <!-- Граф курса -->
    <div class="section graph-section">
      <h1 class="title">Граф курса</h1>
      <div class="divider"></div>
      
      <div class="form-group">
        <label>Ваша индивидуальная траектория обучения</label>
      </div>

      <div class="graph-box">
        <CourseGraph 
          v-if="graphData && graphData.nodes && graphData.nodes.length > 0 && testStatus.is_test_finalized"
          :graphData="graphData"
          :courseId="parseInt(courseId)"
          :studentId="auth.user.user_id"
          @node-click="onGraphNodeClick"
        />
        <div v-else-if="loadingGraph" class="loading-graph">
          <div class="spinner"></div>
          <p>Загрузка графа курса...</p>
        </div>
        <div v-else-if="graphError" class="no-graph">
          <p class="error-message">{{ graphError }}</p>
          <button @click="loadGraphData" class="retry-btn">Попробовать снова</button>
        </div>
        <div v-else-if="!testStatus.is_test_finalized" class="no-graph">
          <p>Граф курса будет доступен после того как репетитор опубликует входное тестирование</p>
        </div>
        <div v-else class="no-graph">
          <p>Граф курса еще не сгенерирован</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits, computed } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import api from "../api/axios";
import CourseGraph from './CourseGraph.vue'

const props = defineProps({
  courseId: {
    type: String,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  courseInfo: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['load-course-data']);
const auth = useAuthStore();
const router = useRouter();

// Состояния
const loading = ref(false);
const loadingGraph = ref(false);
const knowledgeGaps = ref("");
const graphData = ref(null);
const graphError = ref("");
const testStatus = ref({
  is_test_generated: false,
  is_test_finalized: false,
  questions_count: 0
});
const courseData = ref({});

// Вычисляемое свойство для получения courseId как числа
const courseId = computed(() => {
  const id = props.courseId;
  if (typeof id === 'string') {
    return parseInt(id) || null;
  }
  return id || null;
});

function onGraphNodeClick({ node, lessonId }) {
    console.log('Клик по узлу графа:', node.data.label, 'lessonId:', lessonId);
    
    if (lessonId) {          
        router.push({
            path: `/lesson/${lessonId}`,
            query: {
                courseId: courseId.value,
                studentId: auth.user.user_id,
                fromGraph: 'true'
            }
        });
    }
}

// Загрузка данных для ученика
async function loadStudentCourseData() {
  try {
    const studentId = auth.user.user_id;
    
    // Загружаем информацию о курсе
    const courseResponse = await api.get(`/courses/${courseId.value}`);
    courseData.value = courseResponse.data;
    
    // Загружаем данные ученика на курсе
    const studentResponse = await api.get(`/courses/students/${studentId}/course`);
    
    // Устанавливаем пробелы в знаниях для ученика
    knowledgeGaps.value = studentResponse.data.knowledge_gaps || "";
    
    // Загружаем статус входного теста КУРСА (теперь из курса, а не из user_course)
    await loadTestStatus();
    
    // Загружаем граф курса только если тест финализирован
    if (testStatus.value.is_test_finalized) {
      await loadGraphData();
    }
    
  } catch (error) {
    console.error("Ошибка загрузки данных ученика:", error);
  }
}

// Загрузка статуса входного теста КУРСА
async function loadTestStatus() {
  try {
    // Используем новый маршрут для получения статуса теста КУРСА
    const response = await api.get(`/tests/courses/${courseId.value}/entry-test/status`);
    
    if (response.data) {
      testStatus.value = {
        is_test_generated: response.data.is_test_generated || false,
        is_test_finalized: response.data.is_test_finalized || false,
        questions_count: response.data.questions_count || 0
      };
      console.log("Статус теста курса загружен:", testStatus.value);
    }
  } catch (error) {
    console.error("Ошибка загрузки статуса теста курса:", error);
    testStatus.value = {
      is_test_generated: false,
      is_test_finalized: false,
      questions_count: 0
    };
  }
}

// Загрузка графа курса
async function loadGraphData() {
  try {
    loadingGraph.value = true;
    graphError.value = "";
    
    // Используем тот же маршрут для графа, так как граф все еще индивидуален для ученика
    const response = await api.get(`/courses/${courseId.value}/student/${auth.user.user_id}/graph`);
    
    if (response.data && response.data.graph_data) {
      graphData.value = response.data.graph_data;
      console.log("Граф загружен:", graphData.value);
      
      if (graphData.value.nodes) {
        graphData.value.nodes.forEach(node => {
          if (node.group === undefined) {
            node.group = 2;
          }
        });
      }
    } else {
      graphError.value = "Граф не содержит данных";
    }
    
  } catch (error) {
    console.error("Ошибка загрузки графа:", error);
    
    if (error.response?.status === 404) {
      graphError.value = "Граф курса еще не сгенерирован для вас";
    } else if (error.response?.status === 403) {
      graphError.value = "Нет доступа к графу курса";
    } else {
      graphError.value = "Ошибка загрузки графа курса";
    }
  } finally {
    loadingGraph.value = false;
  }
}

function startInputTest() {
  if (!testStatus.value.is_test_generated || !testStatus.value.is_test_finalized) {
    alert("Входное тестирование пока недоступно. Репетитор еще не опубликовал тест.");
    return;
  }
  
  console.log("Переход к входному тесту курса");
  
  router.push({
    name: "input-test",
    params: { courseId: courseId.value },
    query: {
      courseTitle: courseData.value.title || props.courseInfo?.title || `Курс ${courseId.value}`,
      testData: JSON.stringify({
        test_type: "placement",
        questions: testStatus.value.questions_count,
        time_limit: 20
      })
    }
  });
}

// Инициализация
onMounted(() => {
  loadStudentCourseData();
});
</script>

<style scoped>
/* Стили остаются без изменений */
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
  height: 100px;
  resize: none;
  margin-top: 10px;
}

textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.7;
}

.test-box {
  background: #FFFFFF;
  border: 2px solid #F4886D;
  border-radius: 15px;
  padding: 20px;
  text-align: left;
  color: #592012;
  font-family: 'Arial', Georgia, serif;
}

.test-info {
  margin-bottom: 15px;
}

.test-status,
.test-questions,
.test-note {
  margin: 8px 0;
  font-size: 15px;
}

.status-not-generated {
  color: #F44336;
  font-weight: bold;
}

.status-draft {
  color: #FF9800;
  font-weight: bold;
}

.status-finalized {
  color: #4CAF50;
  font-weight: bold;
}

.test-btn {
  display: block;
  background: #F4886D;
  color: #592012;
  border: none;
  border-radius: 10px;
  padding: 15px 30px;
  cursor: pointer;
  white-space: nowrap;
  font-family: 'Arial', Georgia, serif;
  font-weight: bold;
  transition: all 0.3s;
  font-size: 16px;
  margin: 15px auto 0 auto;
  text-align: center;
  width: 100%;
  max-width: 250px;
}

.test-btn:hover:not(:disabled) {
  background: #E0785D;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(244, 136, 109, 0.3);
}

.test-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #cccccc;
  color: #666666;
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
  padding: 20px;
}

.error-message {
  color: #F44336;
  margin-bottom: 15px;
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

@media (max-width: 768px) {
  .title {
    font-size: 24px;
  }
  
  .test-btn {
    max-width: none;
  }
}

@media (max-width: 480px) {
  .section {
    padding: 15px;
  }
  
  .title {
    font-size: 20px;
  }
  
  textarea {
    padding: 10px 12px;
    font-size: 14px;
  }
  
  .graph-box {
    min-height: 250px;
  }
  
  .test-info p {
    font-size: 14px;
  }
}
</style>