<template>
    <TestPage
      :test-type="'lesson'"
      :title="pageTitle"
      :subtitle="lessonTitle"
      :initial-tasks="tasks"
      :time-limit="15"
      :is-tutor-mode="isTutorMode"
      :show-scores="showScores"
      :is-editable="isEditable"
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
  
  const lessonId = ref(null);
  const courseId = ref(null);
  const lessonTitle = ref("");
  const courseTitle = ref("");
  const testData = ref(null);
  const tasks = ref([]);
  const isTutorMode = ref(false);
  const showScores = ref(false);
  const isEditable = ref(true);
  
  // Вычисляемые свойства
  const pageTitle = computed(() => {
    if (isTutorMode.value) {
      return route.query.editMode === 'true' ? 'Редактирование теста урока' : 'Просмотр теста урока';
    }
    return 'Тест урока';
  });
  
  onMounted(() => {
    lessonId.value = route.params.lessonId;
    courseId.value = route.query.courseId;
    
    // Определяем режим
    isTutorMode.value = auth.user?.role === "Репетитор" || route.query.editMode === 'true';
    showScores.value = isTutorMode.value || route.query.showResults === 'true';
    isEditable.value = isTutorMode.value && route.query.editMode !== 'false';
    
    // Загружаем данные
    lessonTitle.value = route.query.lessonTitle || `Урок ${lessonId.value}`;
    courseTitle.value = route.query.courseTitle || `Курс ${courseId.value}`;
    
    // Парсим данные теста
    if (route.query.testData) {
      try {
        testData.value = JSON.parse(route.query.testData);
        
        if (testData.value.tasks && Array.isArray(testData.value.tasks)) {
          tasks.value = testData.value.tasks;
        } else if (testData.value.questions) {
          // Конвертируем старый формат в новый
          tasks.value = testData.value.questions.map((q, index) => ({
            id: index + 1,
            type: 'text',
            text: typeof q === 'string' ? q : q.question || 'Вопрос',
            maxScore: 5,
            score: null,
            userAnswer: '',
            placeholder: 'Введите ответ...'
          }));
        } else {
          loadDemoTasks();
        }
      } catch (e) {
        console.error("Ошибка парсинга testData:", e);
        loadDemoTasks();
      }
    } else {
      loadDemoTasks();
    }
  });
  
  function loadDemoTasks() {
    // Демо-задачи для теста урока
    tasks.value = [
      {
        id: 1,
        type: 'radio',
        text: 'Выберите правильное предложение в Present Simple:',
        maxScore: 2,
        score: null,
        userAnswer: '',
        options: [
          'She is going to school now.',
          'She goes to school every day.',
          'She went to school yesterday.',
          'She has gone to school.'
        ],
        correctAnswer: 1
      },
      {
        id: 2,
        type: 'checkbox',
        text: 'Отметьте маркеры времени, которые используются с Present Simple:',
        maxScore: 4,
        score: null,
        userAnswer: [],
        options: [
          'every day',
          'now',
          'usually',
          'at the moment',
          'often',
          'yesterday'
        ],
        correctAnswers: [0, 2, 4]
      },
      {
        id: 3,
        type: 'text',
        text: 'Напишите три предложения о своих ежедневных привычках, используя Present Simple.',
        maxScore: 6,
        score: null,
        userAnswer: '',
        placeholder: 'Пример: I wake up at 7 am every day...'
      },
      {
        id: 4,
        type: 'fill-blanks',
        text: 'Заполните пропуски правильной формой глагола в Present Simple:',
        maxScore: 8,
        score: null,
        parts: [
          { type: 'text', content: 'My sister' },
          { type: 'input', placeholder: 'глагол (work)' },
          { type: 'text', content: 'in a hospital. She' },
          { type: 'input', placeholder: 'глагол (get up)' },
          { type: 'text', content: 'at 6 am' },
          { type: 'text', content: 'every morning.' }
        ]
      }
    ];
  }
  
  function handleSave(testData) {
    console.log("Сохранение теста урока:", testData);
    
    if (isTutorMode.value) {
        if (route.query.editMode === 'true') {
        alert("Генерация теории сохранена!");
        } else {
        alert("Замечания по генерации сохранены!");
        }
    } else {
        alert("Тестирование завершено! Результаты отправлены на проверку.");
        goBack();
    }
    }
  
  function handlePublish(testTasks) {
    console.log("Публикация теста урока:", testTasks);
    alert("Тест урока опубликован!");
  }
  
  function handleGenerate(comment) {
    if (!isTutorMode.value) {
        alert("Только репетитор может вносить замечания по генерации");
        return;
    }
    
    console.log("Генерация теста урока по комментарию:", comment);
    alert(`Тест урока будет сгенерирован на основе: "${comment}"`);
    }
  
  function goBack() {
    if (courseId.value && lessonId.value) {
      router.push({
        path: `/lesson/${lessonId.value}`,
        query: { courseId: courseId.value }
      });
    } else {
      router.back();
    }
  }
  </script>