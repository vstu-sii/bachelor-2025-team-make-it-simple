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
    :is-readonly-mode="isReadonlyMode"
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
import { config } from "../config.js"; // Импортируем конфиг
import TestPage from "../components/TestPage.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const courseId = ref(null);
const courseTitle = ref("");
const tasks = ref([]);
const isTutorMode = ref(false);
const isEditable = ref(true);
const isReadonlyMode = ref(false);
const courseData = ref({});
const selectedStudentId = ref(null);
const studentTestResults = ref(null);

// Конфигурация API - используем URL из конфига
const apiConfig = ref({
  baseUrl: config.apiUrl,
  courseData: {}
});

// Вычисляемые свойства
const pageTitle = computed(() => {
  if (isTutorMode.value && isReadonlyMode.value) {
    return `Просмотр теста ученика`;
  }
  if (isTutorMode.value) {
    return 'Входное тестирование курса';
  }
  return 'Входное тестирование';
});

onMounted(async () => {
  courseId.value = route.params.courseId;
  
  // Определяем режим
  isTutorMode.value = auth.user?.role === "Репетитор";
  isEditable.value = isTutorMode.value && !route.query.studentId;
  
  // Проверяем, смотрим ли мы ответы ученика
  if (route.query.studentId && isTutorMode.value) {
    selectedStudentId.value = route.query.studentId;
    isReadonlyMode.value = true;
    isEditable.value = false;
    
    // Загружаем результаты теста ученика
    await loadStudentTestResults();
  }
  
  // Загружаем данные курса
  await loadCourseData();
  
  // Загружаем тест КУРСА
  await loadTest();
  
  courseTitle.value = route.query.courseTitle || `Курс ${courseId.value}`;
  
  // Настраиваем API конфигурацию
  apiConfig.value = {
    baseUrl: config.apiUrl,
    courseData: courseData.value
  };
});

// Загрузка данных курса
async function loadCourseData() {
  try {
    const response = await fetch(`${config.apiUrl}/courses/${courseId.value}`, {
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
      isTutor: isTutorMode.value,
      isReadonlyMode: isReadonlyMode.value,
      studentId: selectedStudentId.value
    });
    
    // Используем новый маршрут для получения теста КУРСА
    const response = await fetch(`${config.apiUrl}/tests/courses/${courseId.value}/entry-test`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log("Получены данные теста курса:", data);
      
      if (data.test_data && data.test_data.questions) {
        // Если это режим просмотра ответов ученика, загружаем его ответы
        if (isReadonlyMode.value && studentTestResults.value) {
          tasks.value = mergeStudentAnswersWithTest(
            data.test_data.questions,
            studentTestResults.value
          );
        } else {
          // Иначе преобразуем вопросы из формата AI в формат для отображения
          tasks.value = convertAIQuestionsToTasks(data.test_data.questions);
        }
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

// Загрузка результатов теста ученика
async function loadStudentTestResults() {
  try {
    console.log(`Загрузка результатов теста для ученика ${selectedStudentId.value}`);
    
    const response = await fetch(`${config.apiUrl}/tests/courses/${courseId.value}/student/${selectedStudentId.value}/test-status`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.results) {
        studentTestResults.value = data.results;
        console.log("Результаты теста ученика загружены:", {
          score: data.results.score,
          percentage: data.results.percentage,
          detailed_results_count: data.results.detailed_results?.length
        });
        
        // Выводим отладочную информацию о типах ответов
        if (data.results.detailed_results) {
          data.results.detailed_results.forEach((result, index) => {
            console.log(`Вопрос ${index + 1}:`, {
              type: result.type,
              user_answer: result.user_answer,
              is_correct: result.is_correct
            });
          });
        }
      } else {
        console.log("Ученик еще не прошел тест");
        studentTestResults.value = null;
      }
    } else {
      console.log("Ошибка загрузки результатов теста:", response.status);
      studentTestResults.value = null;
    }
  } catch (error) {
    console.error("Ошибка загрузки результатов теста ученика:", error);
    studentTestResults.value = null;
  }
}

// Объединение ответов ученика с вопросами теста
function mergeStudentAnswersWithTest(testQuestions, studentResults) {
  const studentAnswers = studentResults.detailed_results || [];
  const answersMap = {};
  
  // Создаем карту ответов ученика для быстрого доступа
  studentAnswers.forEach(answer => {
    answersMap[answer.question_id] = {
      user_answer: answer.user_answer,
      is_correct: answer.is_correct,
      correct_answer: answer.correct_answer
    };
  });
  
  return testQuestions.map((question, index) => {
    const questionId = question.question_id || `q${index + 1}`;
    const studentAnswer = answersMap[questionId];
    
    // Базовая структура задачи
    const baseTask = {
      question_id: questionId,
      type: question.type,
      question: question.question,
      correct_answer: question.correct_answer,
      max_length: question.max_length,
      student_correct: studentAnswer ? studentAnswer.is_correct : false,
      // Для правильного отображения ответов ученика в readonly режиме
      userAnswer: studentAnswer ? studentAnswer.user_answer : ''
    };
    
    switch (question.type) {
      case 'short_answer':
        return {
          ...baseTask,
          options: question.options || [],
          // Для short_answer userAnswer должен быть строкой
          userAnswer: studentAnswer ? String(studentAnswer.user_answer || '') : ''
        };
        
      case 'single_choice':
        return {
          ...baseTask,
          options: question.options || [],
          // Для single_choice userAnswer должен быть строкой (индекс)
          userAnswer: studentAnswer ? String(studentAnswer.user_answer || '') : '',
          // Добавляем правильный ответ для отображения репетитору
          correct_answer_index: question.correct_answer,
          correct_answer_text: question.options ? question.options[question.correct_answer] : ''
        };
        
      case 'multiple_choice':
        // Для multiple_choice userAnswer должен быть массивом индексов
        let userAnswerArray = [];
        if (studentAnswer && studentAnswer.user_answer) {
          if (Array.isArray(studentAnswer.user_answer)) {
            userAnswerArray = studentAnswer.user_answer.map(item => String(item));
          } else if (typeof studentAnswer.user_answer === 'string') {
            try {
              // Пытаемся распарсить строку как JSON массив
              const parsed = JSON.parse(studentAnswer.user_answer);
              if (Array.isArray(parsed)) {
                userAnswerArray = parsed.map(item => String(item));
              }
            } catch {
              // Если не JSON, пробуем как разделенную запятыми строку
              userAnswerArray = studentAnswer.user_answer
                .split(',')
                .map(item => item.trim())
                .filter(item => item);
            }
          }
        }
        
        return {
          ...baseTask,
          options: question.options || [],
          correct_answers: question.correct_answers || [],
          userAnswer: userAnswerArray
        };
        
      case 'gaps_choice':
        // Для gaps_choice обрабатываем каждый пропуск отдельно
        const gaps = (question.gaps || []).map(gap => {
          // Получаем ответ ученика для этого пропуска
          let gapUserAnswer = '';
          
          if (studentAnswer && studentAnswer.user_answer) {
            // Ответы для gaps_choice могут храниться как объект
            if (typeof studentAnswer.user_answer === 'object') {
              gapUserAnswer = String(studentAnswer.user_answer[gap.gap_id] || '');
            } else if (typeof studentAnswer.user_answer === 'string') {
              try {
                // Пытаемся распарсить JSON
                const parsed = JSON.parse(studentAnswer.user_answer);
                if (parsed && typeof parsed === 'object') {
                  gapUserAnswer = String(parsed[gap.gap_id] || '');
                }
              } catch {
                // Если не JSON, оставляем пустым
                gapUserAnswer = '';
              }
            }
          }
          
          return {
            ...gap,
            userAnswer: gapUserAnswer
          };
        });
        
        return {
          ...baseTask,
          gaps: gaps,
          // Для gaps_choice храним ответы как объект
          userAnswer: gaps.reduce((acc, gap) => {
            acc[gap.gap_id] = gap.userAnswer;
            return acc;
          }, {})
        };
        
      default:
        return baseTask;
    }
  });
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
  
  if (isTutorMode.value && !isReadonlyMode.value) {
    alert("Тест курса успешно сохранен и доступен всем ученикам!");
    goBack();
  } else if (!isTutorMode.value) {
    // Для ученика - сохраняем результаты теста
    saveStudentTestResults(testData);
  }
}

async function saveStudentTestResults(testData) {
  try {
    const response = await fetch(`${config.apiUrl}/tests/courses/${courseId.value}/student/${auth.user.user_id}/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(testData)
    });
    
    if (response.ok) {
      alert("Тестирование завершено! Результаты сохранены.");
      goBack();
    } else {
      alert("Ошибка при сохранении результатов теста.");
    }
  } catch (error) {
    console.error("Ошибка сохранения результатов теста:", error);
    alert("Ошибка соединения с сервером.");
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