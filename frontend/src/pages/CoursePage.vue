<template>
  <div class="course-page">
    <!-- Добавляем хедер как на других страницах -->
    <AppHeader :show-back-button="false" />
    
    <!-- Кнопка "назад" поверх контейнера -->
    <button class="back-btn" @click="goBack">
      <img src="/src/assets/arrow-back.svg" alt="back" />
    </button>

    <!-- Название курса над основным контейнером -->
    <div v-if="courseInfo.title" class="course-title-container">
      <h1 class="course-title">{{ courseInfo.title }}</h1>
      <div class="course-title-divider"></div>
    </div>

    <!-- Основной контейнер цвета #F4886D -->
    <div class="main-container">
      <!-- Внутренний общий контейнер цвета #fbb599 -->
      <div class="inner-container">
        <!-- Отображение компонента в зависимости от роли -->
        <StudentCoursePageComponent
          v-if="isStudent"
          :courseId="courseId"
          :loading="loading"
          :courseInfo="courseInfo"
          @load-course-data="loadCourseData"
        />
        
        <TutorCoursePageComponent
          v-else-if="isTutor"
          :courseId="courseId"
          :loading="loading"
          :courseInfo="courseInfo"
          @load-course-data="loadCourseData"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import api from "../api/axios";
import AppHeader from "../components/Header.vue";
import StudentCoursePageComponent from "../components/StudentCoursePageComponent.vue";
import TutorCoursePageComponent from "../components/TutorCoursePageComponent.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const courseId = ref(route.params.id);
const courseInfo = ref({});
const loading = ref(false);

// Вычисляемые свойства
const isTutor = computed(() => auth.user?.role === "Репетитор");
const isStudent = computed(() => auth.user?.role === "Ученик");

// Загрузка данных курса
async function loadCourseData() {
  try {
    loading.value = true;
    
    // Загружаем основную информацию о курсе
    const response = await api.get(`/courses/${courseId.value}`);
    courseInfo.value = response.data;
    
  } catch (error) {
    console.error("Ошибка загрузки данных курса:", error);
    alert("Не удалось загрузить данные курса");
    // Возвращаем на предыдущую страницу при ошибке
    router.back();
  } finally {
    loading.value = false;
  }
}

// Навигация
function goBack() {
  router.back();
}

// Инициализация
onMounted(() => {
  loadCourseData();
});
</script>

<style scoped>
.course-page {
  width: 100%;
  min-height: 100vh;
  background: #0b1444;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 40px;
  position: relative;
}

/* Кнопка "назад" */
.back-btn {
  position: absolute;
  left: 50%;
  transform: translateX(calc(-50% - 535px));
  top: 190px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 10px;
  transition: transform 0.3s;
  z-index: 10;
}

.back-btn:hover {
  transform: translateX(calc(-50% - 535px - 5px));
}

.back-btn img {
  width: 80px;
  height: 80px;
}

/* Название курса */
.course-title-container {
  position: relative;
  margin-top: 130px;
  margin-bottom: 20px;
  text-align: center;
  width: 95%;
  max-width: 1100px;
}

.course-title {
  font-family: 'Arial', Georgia, serif;
  font-size: 36px;
  font-weight: bold;
  color: #fbb599;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  margin: 0;
  padding: 0 20px;
  letter-spacing: 1px;
}

.course-title-divider {
  height: 3px;
  background: linear-gradient(to right, transparent, #fbb599, transparent);
  width: 100%;
  max-width: 600px;
  margin: 10px auto 0 auto;
  border-radius: 2px;
}

/* Основной контейнер цвета #F4886D */
.main-container {
  width: 95%;
  max-width: 1100px;
  background: #F4886D;
  border-radius: 25px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  position: relative;
  margin-top: 10px;
}

/* Внутренний общий контейнер цвета #fbb599 */
.inner-container {
  background: #fbb599;
  border-radius: 20px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Адаптивность */
@media (max-width: 1200px) {
  .back-btn {
    left: 10px;
    transform: none;
  }
  
  .back-btn:hover {
    transform: translateX(-5px);
  }
  
  .course-title {
    font-size: 32px;
  }
}

@media (max-width: 1024px) {
  .main-container {
    width: 98%;
    padding: 25px;
  }
  
  .back-btn {
    left: 30px;
    top: 90px;
  }
  
  .inner-container {
    padding: 25px;
  }
  
  .course-title-container {
    margin-top: 120px;
    margin-bottom: 15px;
  }
  
  .course-title {
    font-size: 28px;
  }
}

@media (max-width: 768px) {
  .back-btn {
    left: 20px;
    top: 80px;
  }
  
  .back-btn img {
    width: 60px;
    height: 60px;
  }
  
  .main-container {
    margin-top: 5px;
    padding: 20px;
  }
  
  .inner-container {
    padding: 20px;
    gap: 20px;
  }
  
  .course-title-container {
    margin-top: 110px;
    margin-bottom: 10px;
  }
  
  .course-title {
    font-size: 24px;
    padding: 0 15px;
  }
}

@media (max-width: 480px) {
  .back-btn {
    left: 15px;
    top: 70px;
  }
  
  .back-btn img {
    width: 50px;
    height: 50px;
  }
  
  .main-container {
    padding: 15px;
  }
  
  .inner-container {
    padding: 15px;
  }
  
  .course-title-container {
    margin-top: 100px;
    margin-bottom: 10px;
  }
  
  .course-title {
    font-size: 20px;
    padding: 0 10px;
  }
  
  .course-title-divider {
    max-width: 300px;
  }
}
</style>