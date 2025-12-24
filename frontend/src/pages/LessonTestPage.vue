<template>
  <LessonTestPage
    :lesson-id="lessonId"
    :student-id="studentId"
    @save="handleSave"
    @publish="handlePublish"
    @generate="handleGenerate"
    @exit="goBack"
    @evaluated="handleEvaluated"
  />
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import LessonTestPage from "../components/LessonTestPage.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const lessonId = ref(null);
const studentId = ref(null);

onMounted(() => {
  lessonId.value = parseInt(route.params.lessonId);
  studentId.value = route.query.studentId ? parseInt(route.query.studentId) : null;
});

function handleSave(testData) {
  console.log("Сохранение теста урока:", testData);
  
  if (auth.user?.role === "Репетитор") {
    alert("Тест урока сохранен и опубликован!");
  } else {
    alert("Тест завершен! Результаты отправлены.");
  }
}

function handleGenerate(feedback) {
  console.log("Генерация теста с замечаниями:", feedback);
  alert(`Тест будет сгенерирован с учетом: "${feedback}"`);
}

function handleEvaluated(results) {
  console.log("Результаты оценки:", results);
  alert("Результаты ученика оценены!");
}

function goBack() {
  if (route.query.courseId) {
    router.push({
      path: `/lesson/${lessonId.value}`,
      query: { courseId: route.query.courseId }
    });
  } else {
    router.back();
  }
}
</script>