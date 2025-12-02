<template>
  <!-- Внешний контейнер для информации о курсе -->
  <div class="course-outer-container">
    <!-- Информация о курсе -->
    <div class="course-card">
      <h2>Информация о курсе</h2>
      <div class="course-divider"></div>
      
      <div class="course-info-grid">
        <div class="course-info-item">
          <div class="course-label">Твой репетитор</div>
          <div class="course-value">{{ tutorName }}</div>
        </div>
        
        <div v-if="courseInfo.course_name" class="course-info-item">
          <div class="course-label">Название курса</div>
          <div class="course-value">{{ courseInfo.course_name }}</div>
        </div>

        <div v-if="courseInfo.created_at" class="course-info-item">
          <div class="course-label">Дата начала</div>
          <div class="course-value">{{ formatDate(courseInfo.created_at) }}</div>
        </div>

        <div v-if="courseInfo.knowledge_gaps" class="course-info-item full-width">
          <div class="course-label">Пробелы в знаниях</div>
          <div class="course-value knowledge-gaps">{{ courseInfo.knowledge_gaps }}</div>
        </div>
      </div>
      
      <button 
        v-if="isOwnProfile && courseInfo.course_id" 
        @click="goToCourse" 
        class="course-details-btn"
      >
        Подробности курса
      </button>
      <button 
        v-else-if="isOwnProfile && !courseInfo.course_id" 
        class="course-details-btn disabled"
        disabled
      >
        Вы еще не записаны на курс
      </button>
      <div v-else class="not-owner-note">
        Подробности курса доступны только владельцу профиля
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  user: {
    type: Object,
    required: true
  },
  isOwnProfile: {
    type: Boolean,
    default: true
  }
});

const router = useRouter();

// Вычисляем данные курса
const courseInfo = computed(() => props.user.course_info || {});
const tutorName = computed(() => props.user.tutor_full_name || "Не назначен");

// Функция форматирования даты
function formatDate(dateString) {
  if (!dateString) return 'Не указана';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
}

// Функция перехода к курсу
function goToCourse() {
  if (courseInfo.value.course_id) {
    router.push(`/course/${courseInfo.value.course_id}`);
  }
}
</script>

<style scoped>
/* Стили для контейнера курса ученика */
.course-outer-container {
  background: #fbb599;
  border-radius: 25px;
  padding: 30px;
  width: 1000px;
  box-shadow: 0 0 20px rgba(0,0,0,0.25);
}

.course-card {
  background: #fedac4;
  border-radius: 20px;
  padding: 30px 40px;
  text-align: center;
  box-shadow: 0 0 15px rgba(0,0,0,0.2);
  width: 100%;
  margin: 0;
}

.course-card h2 {
  font-size: 26px;
  margin-bottom: 8px;
  color: #592012;
}

.course-divider {
  width: 100%;
  height: 2px;
  background: #000;
  opacity: 0.25;
  margin-bottom: 25px;
}

.course-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.course-info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.course-info-item.full-width {
  grid-column: 1 / -1;
}

.course-label {
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 0;
  color: #592012;
}

.course-value {
  background: white;
  padding: 8px 16px;
  border-radius: 10px;
  display: inline-block;
  font-weight: bold;
  min-width: 180px;
  text-align: center;
  color: #592012;
  width: 100%;
  box-sizing: border-box;
}

.knowledge-gaps {
  font-size: 14px;
  font-weight: normal;
  text-align: justify;
  line-height: 1.4;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: pre-wrap;
  word-break: break-word;
}

.course-details-btn {
  background: #f4886d !important;
  color: #592012 !important;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: bold;
  margin-top: 25px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
  font-family: 'KyivType Titling', serif;
  min-width: 200px;
}

.course-details-btn:hover:not(.disabled) {
  background: #cf7058 !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.course-details-btn.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #a0a0a0 !important;
  color: #666 !important;
}

.not-owner-note {
  margin-top: 25px;
  color: #777;
  font-style: italic;
  font-size: 14px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 8px;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .course-outer-container {
    width: 95%;
    padding: 20px;
  }

  .course-info-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .course-card {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .course-card h2 {
    font-size: 22px;
  }
  
  .course-label {
    font-size: 16px;
  }
  
  .course-value {
    min-width: 120px;
    font-size: 14px;
  }
  
  .course-details-btn {
    min-width: 160px;
    font-size: 14px;
    padding: 10px 20px;
  }
}
</style>