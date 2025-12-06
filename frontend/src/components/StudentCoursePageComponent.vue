<template>
    <div>
      <!-- Входное тестирование -->
      <div class="section">
        <h1 class="title">Входное тестирование</h1>
        <div class="divider"></div>
        
        <div class="test-box">
          <p>
            Время прохождение тестирования ~20 мин<br />Количество вопросов: 20<br />
            Ваш прогресс будет доступен после проверки репетитором<br />
            входного тестирования
          </p>
          <button class="test-btn" @click="startTest">
            {{ hasTakenTest ? 'Просмотреть результаты' : 'Перейти к тесту' }}
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
            v-if="graphData && graphData.nodes && graphData.nodes.length > 0"
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
          <div v-else class="no-graph">
            <p>Граф курса еще не сгенерирован</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, defineProps, defineEmits } from "vue";
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
  const knowledgeGaps = ref("");
  const graphData = ref(null);
  const graphError = ref("");
  const hasTakenTest = ref(false);
  
  function onGraphNodeClick({ node, lessonId }) {
    console.log('Клик по узлу графа:', node.data.label, 'lessonId:', lessonId);
    
    if (lessonId) {
      router.push({
        path: `/lesson/${lessonId}`,
        query: {
          courseId: props.courseId,
          studentId: auth.user.user_id
        }
      });
    }
  }

  // Загрузка данных для ученика
  async function loadStudentCourseData() {
    try {
      const studentId = auth.user.user_id;
      const response = await api.get(`/courses/students/${studentId}/course`);
      
      // Устанавливаем пробелы в знаниях для ученика
      knowledgeGaps.value = response.data.knowledge_gaps || "";
      
      // Загружаем граф курса
      await loadGraphData();
      
    } catch (error) {
      console.error("Ошибка загрузки данных ученика:", error);
    }
  }
  
  // Загрузка графа курса - ИСПРАВЛЕННЫЙ ENDPOINT
  async function loadGraphData() {
    try {
      loadingGraph.value = true;
      graphError.value = "";
      
      // Используем правильный endpoint из course_routes.py
      const response = await api.get(`/courses/${props.courseId}/student/${auth.user.user_id}/graph`);
      
      if (response.data && response.data.graph_data) {
        // Граф возвращается в поле graph_data
        graphData.value = response.data.graph_data;
        console.log("Граф загружен:", graphData.value);
        
        // Убедимся, что у узлов есть group (статус)
        if (graphData.value.nodes) {
          graphData.value.nodes.forEach(node => {
            // Если в данных графа нет group, устанавливаем по умолчанию 2 (Доступен)
            if (node.group === undefined) {
              node.group = 2; // Статус "Доступен" по умолчанию
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
        // НЕ создаем демо-граф, оставляем null
        // createDemoGraph(); // УБЕРИТЕ ЭТУ СТРОКУ!
      }
    } finally {
      loadingGraph.value = false;
    }
  }
  
  // Начало тестирования
  function startTest() {
    // Логика перехода к тесту
    console.log("Начать тестирование");
  }
  
  // Инициализация
  onMounted(() => {
    loadStudentCourseData();
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
  
  /* Кнопки */
  .test-btn {
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
    margin-top: 15px;
  }
  
  .test-btn:hover:not(:disabled) {
    background: #E0785D;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(244, 136, 109, 0.3);
  }
  
  .test-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  /* Кнопка повторной попытки */
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
  
  /* Граф курса */
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
  
  /* Адаптивность */
  @media (max-width: 768px) {
    .title {
      font-size: 24px;
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
  }
  </style>