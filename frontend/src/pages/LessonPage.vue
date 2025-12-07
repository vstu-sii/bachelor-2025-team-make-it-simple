<template>
  <div v-if="loading" class="loading-container">
    <div class="loader"></div>
  </div>
  <StudentLessonPageComponent 
    v-else-if="isStudent" 
    :lesson-id="lessonId" 
    :course-id="courseId"
  />
  <TutorLessonPageComponent 
    v-else-if="isTutor" 
    :lesson-id="lessonId" 
    :course-id="courseId"
  />
  <div v-else class="unauthorized">
    <h2>Доступ запрещен</h2>
    <p>У вас нет прав для просмотра этой страницы</p>
    <button @click="goBack">Вернуться назад</button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import StudentLessonPageComponent from "../components/StudentLessonPageComponent.vue";
import TutorLessonPageComponent from "../components/TutorLessonPageComponent.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const loading = ref(true);

// Получаем параметры из URL
const lessonId = computed(() => {
  const id = route.params.id;
  return id ? parseInt(id) : null;
});

const courseId = computed(() => {
  const id = route.query.courseId;
  return id ? parseInt(id) : null;
});

const isStudent = computed(() => auth.user?.role === "Ученик");
const isTutor = computed(() => auth.user?.role === "Репетитор");

function goBack() {
  if (courseId.value) {
    router.push(`/course/${courseId.value}`);
  } else {
    router.back();
  }
}

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
  
  // Проверяем наличие lessonId
  if (!lessonId.value) {
    router.push("/");
    return;
  }
  
  loading.value = false;
});
</script>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #0b1444;
}

.loader {
  border: 5px solid #f3f3f3;
  border-top: 5px solid #F4886D;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.unauthorized {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #0b1444;
  color: white;
  text-align: center;
  padding: 20px;
}

.unauthorized h2 {
  color: #fbb599;
  margin-bottom: 20px;
}

.unauthorized button {
  background: #F4886D;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 20px;
}

.unauthorized button:hover {
  background: #E0785D;
}
</style>