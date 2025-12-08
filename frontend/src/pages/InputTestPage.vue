<template>
    <TestPage
      :test-type="'input'"
      :title="pageTitle"
      :subtitle="courseTitle"
      :initial-tasks="tasks"
      :time-limit="20"
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
  
  const courseId = ref(null);
  const courseTitle = ref("");
  const testData = ref(null);
  const tasks = ref([]);
  const isTutorMode = ref(false);
  const showScores = ref(false);
  const isEditable = ref(true);
  
  // Вычисляемые свойства
  const pageTitle = computed(() => {
    return isTutorMode.value ? 'Редактирование входного теста' : 'Входное тестирование';
  });
  
  onMounted(() => {
    courseId.value = route.params.courseId;
    
    // Определяем режим (репетитор или ученик)
    isTutorMode.value = route.query.isTutor === 'true';
    showScores.value = isTutorMode.value || route.query.showScores === 'true';
    isEditable.value = isTutorMode.value || route.query.editMode === 'true';
    
    // Парсим данные теста
    if (route.query.testData) {
      try {
        testData.value = JSON.parse(route.query.testData);
        
        // Если в testData есть задачи, используем их
        if (testData.value.tasks && Array.isArray(testData.value.tasks)) {
          tasks.value = testData.value.tasks;
        } else {
          // Иначе создаем демо-задачи на основе типа теста
          loadDemoTasks();
        }
      } catch (e) {
        console.error("Ошибка парсинга testData:", e);
        loadDemoTasks();
      }
    } else {
      loadDemoTasks();
    }
    
    courseTitle.value = route.query.courseTitle || `Курс ${courseId.value}`;
  });
  
  function loadDemoTasks() {
    // Демо-задачи для входного теста
    tasks.value = [
      {
        id: 1,
        type: 'radio',
        text: 'Выберите правильный перевод: "Я учу английский каждый день."',
        maxScore: 2,
        score: null,
        userAnswer: '',
        options: [
          'I study English every day.',
          'I am studying English every day.',
          'I studied English every day.',
          'I have studied English every day.'
        ],
        correctAnswer: 0
      },
      {
        id: 2,
        type: 'checkbox',
        text: 'Какие времена используются для описания регулярных действий?',
        maxScore: 3,
        score: null,
        userAnswer: [],
        options: [
          'Present Simple',
          'Present Continuous',
          'Past Simple',
          'Future Simple',
          'Present Perfect'
        ],
        correctAnswers: [0, 3]
      },
      {
        id: 3,
        type: 'text',
        text: 'Опишите свой текущий уровень английского языка и цели обучения.',
        maxScore: 10,
        score: null,
        userAnswer: '',
        placeholder: 'Напишите о вашем опыте изучения английского...'
      },
      {
        id: 4,
        type: 'fill-blanks',
        text: 'Заполните пропуски в диалоге:',
        maxScore: 6,
        score: null,
        parts: [
          { type: 'text', content: 'A: Hello! How' },
          { type: 'input', placeholder: 'глагол' },
          { type: 'text', content: 'you?' },
          { type: 'text', content: 'B: I' },
          { type: 'input', placeholder: 'глагол' },
          { type: 'text', content: 'fine, thank you.' }
        ]
      }
    ];
  }
  
  function handleSave(testData) {
    console.log("Сохранение входного теста:", testData);
    
    if (isTutorMode.value) {
        alert("Генерация теории сохранена!");
    } else {
        alert("Тест завершен! Результаты отправлены на проверку.");
        goBack();
    }
  }
  
  function handlePublish(testTasks) {
    console.log("Публикация входного теста:", testTasks);
    alert("Входной тест опубликован для всех учеников!");
  }
  
  function handleGenerate(comment) {
    if (!isTutorMode.value) {
        alert("Только репетитор может вносить замечания по генерации");
        return;
    }
    
    console.log("Генерация теста по комментарию:", comment);
    alert(`Тест будет сгенерирован на основе: "${comment}"`);
    }
  
  function goBack() {
    router.back();
  }
  </script>