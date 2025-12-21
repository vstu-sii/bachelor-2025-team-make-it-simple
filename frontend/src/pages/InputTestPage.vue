<template>
  <TestPage
    :test-type="'input'"
    :title="pageTitle"
    :subtitle="courseTitle"
    :initial-tasks="tasks"
    :time-limit="20"
    :is-tutor-mode="isTutorMode"
    :show-scores="false"
    :is-editable="isEditable"
    :api-config="apiConfig"
    @save="handleSave"
    @publish="handlePublish"
    @generate="handleGenerate"
    @exit="goBack"
  />
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import TestPage from "../components/TestPage.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const courseId = ref(null);
const courseTitle = ref("");
const tasks = ref([]);
const isTutorMode = ref(false);
const isEditable = ref(true);
const courseData = ref({});

// Конфигурация API
const apiConfig = ref({
  baseUrl: "http://localhost:8000",
  courseData: {}
});

// Вычисляемые свойства
const pageTitle = computed(() => {
  if (isTutorMode.value) {
    return 'Формирование входного теста курса';
  }
  return 'Входное тестирование';
});

onMounted(async () => {
  courseId.value = route.params.courseId;
  
  // Определяем режим
  isTutorMode.value = auth.user?.role === "Репетитор";
  isEditable.value = isTutorMode.value;
  
  // Загружаем данные курса
  await loadCourseData();
  
  // Загружаем тест КУРСА
  await loadTest();
  
  courseTitle.value = route.query.courseTitle || `Курс ${courseId.value}`;
  
  // Настраиваем API конфигурацию
  apiConfig.value = {
    baseUrl: "http://localhost:8000",
    courseData: courseData.value
  };
});

// Загрузка данных курса
async function loadCourseData() {
  try {
    const response = await fetch(`http://localhost:8000/courses/${courseId.value}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      courseData.value = {
        course_title: data.title || "Английский курс",
        topics: [] // Здесь можно загрузить темы курса
      };
    }
  } catch (error) {
    console.error("Ошибка загрузки данных курса:", error);
    courseData.value = {
      course_title: "Английский курс",
      topics: ["Present Simple", "Articles", "Vocabulary"]
    };
  }
}

// Загрузка теста КУРСА
async function loadTest() {
  try {
    console.log("Загрузка теста курса:", {
      courseId: courseId.value,
      isTutor: isTutorMode.value
    });
    
    // Используем новый маршрут для получения теста КУРСА
    const response = await fetch(`http://localhost:8000/tests/courses/${courseId.value}/entry-test`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log("Получены данные теста курса:", data);
      
      if (data.test_data && data.test_data.questions) {
        // Преобразуем вопросы из формата AI в формат для отображения
        tasks.value = convertAIQuestionsToTasks(data.test_data.questions);
        console.log("Задачи преобразованы, количество:", tasks.value.length);
      } else {
        // Если теста нет, создаем пустой массив
        tasks.value = [];
        console.log("Тест курса не содержит вопросов");
      }
    } else if (response.status === 403) {
      // Для ученика тест может быть не опубликован
      if (!isTutorMode.value) {
        console.log("Тест курса еще не опубликован репетитором");
        tasks.value = [];
      } else {
        // Для репетитора создаем пустой тест
        tasks.value = [];
      }
    } else {
      tasks.value = [];
      console.log("Ошибка загрузки теста курса, статус:", response.status);
    }
  } catch (error) {
    console.error("Ошибка загрузки теста курса:", error);
    tasks.value = [];
  }
}

// Конвертация вопросов AI в формат задач для TestPage
function convertAIQuestionsToTasks(aiQuestions) {
  return aiQuestions.map((question, index) => {
    const baseTask = {
      question_id: question.question_id || `q${index + 1}`,
      type: question.type,
      question: question.question,
      userAnswer: '',
      correct_answer: question.correct_answer,
      max_length: question.max_length
    };
    
    switch (question.type) {
      case 'short_answer':
        return {
          ...baseTask,
          userAnswer: ''
        };
        
      case 'single_choice':
        return {
          ...baseTask,
          options: question.options || [],
          userAnswer: ''
        };
        
      case 'multiple_choice':
        return {
          ...baseTask,
          options: question.options || [],
          correct_answers: question.correct_answers || [],
          userAnswer: []
        };
        
      case 'gaps_choice':
        return {
          ...baseTask,
          gaps: (question.gaps || []).map(gap => ({
            ...gap,
            userAnswer: ''
          })),
          userAnswer: ''
        };
        
      default:
        return baseTask;
    }
  });
}

function handleSave(testData) {
  console.log("Сохранение входного теста курса:", testData);
  
  if (isTutorMode.value) {
    alert("Тест курса успешно сохранен и доступен всем ученикам!");
    goBack();
  } else {
    alert("Тестирование завершено! Результаты отправлены на проверку.");
    goBack();
  }
}

function handlePublish() {
  console.log("Публикация входного теста курса");
  // Не используется для входного теста
}

function handleGenerate(comment) {
  console.log("Генерация теста курса по комментарию:", comment);
  // Генерация обрабатывается в TestPage через API
}

function goBack() {
  router.back();
}
</script>