<script setup>
import { computed } from "vue";

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
});

// Можно добавить логику для ученика при необходимости
</script>

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
          <div class="course-value">{{ user?.tutor_full_name || "Не назначен" }}</div>
        </div>
        
        <div class="course-info-item">
          <div class="course-label">Название курса</div>
          <div class="course-value">{{ user?.course_name || "—" }}</div>
        </div>
      </div>
      
      <button class="course-details-btn">Подробности курса</button>
    </div>
  </div>
</template>

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
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.course-info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
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
}

.course-details-btn:hover {
  background: #cf7058 !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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
}
</style>