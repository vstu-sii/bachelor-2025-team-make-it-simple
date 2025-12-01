<script setup>
import { ref, reactive, onMounted } from "vue";
import { useAuthStore } from "../stores/auth";
import api from "../api/axios";

const auth = useAuthStore();

// Данные для поиска
const searchQuery = ref("");
const courses = ref([]);

// Состояние для нового курса
const newCourse = reactive({
  student_name: "",
  course_name: "",
  description: ""
});

// Флаг для показа формы добавления курса
const showAddForm = ref(false);

// Загружаем курсы репетитора
onMounted(async () => {
  await loadCourses();
});

async function loadCourses() {
  try {
    const response = await api.get(`/tutors/${auth.user.user_id}/courses`);
    courses.value = response.data;
  } catch (error) {
    console.error("Ошибка загрузки курсов:", error);
  }
}

async function searchStudent() {
  if (!searchQuery.value.trim()) {
    await loadCourses();
    return;
  }

  try {
    const response = await api.get(`/tutors/${auth.user.user_id}/courses/search`, {
      params: { query: searchQuery.value }
    });
    courses.value = response.data;
  } catch (error) {
    console.error("Ошибка поиска:", error);
  }
}

async function addNewCourse() {
  try {
    await api.post(`/tutors/${auth.user.user_id}/courses`, newCourse);
    
    // Сбрасываем форму
    Object.keys(newCourse).forEach(key => newCourse[key] = "");
    showAddForm.value = false;
    
    // Обновляем список курсов
    await loadCourses();
    alert("Курс успешно добавлен!");
  } catch (error) {
    console.error("Ошибка добавления курса:", error);
    alert("Ошибка при добавлении курса");
  }
}

function goToCourse(courseId) {
  // Здесь можно реализовать переход к деталям курса
  console.log("Переход к курсу:", courseId);
  // Например: router.push(`/courses/${courseId}`);
}
</script>

<template>
  <!-- Внешний контейнер для информации о курсах (такой же как у ученика) -->
  <div class="course-outer-container">
    <div class="tutor-courses-content">
      
      <!-- Контейнер 1: Поиск и добавление курса -->
      <div class="tutor-courses-header inner-box">
        <h2>Информация о курсах</h2>
        <div class="courses-header-content">
          
          <!-- Строка поиска и кнопка "Найти" -->
          <div class="search-section">
            <div class="search-input-wrapper">
              <input 
                v-model="searchQuery" 
                @keyup.enter="searchStudent"
                placeholder="Введите ФИО ученика" 
                class="search-input"
              />
              <button @click="searchStudent" class="search-btn">
                Найти
              </button>
            </div>
          </div>
          
          <!-- Кнопка "Добавить новый курс" с иконкой -->
          <button 
            @click="showAddForm = !showAddForm" 
            class="add-course-btn"
          >
            {{ showAddForm ? 'Отмена' : 'Добавить новый курс' }}
            <img 
              src="/src/assets/vector.svg" 
              alt="добавить" 
              class="add-course-icon"
              v-if="!showAddForm"
            />
          </button>
          
        </div>
        
        <!-- Форма добавления нового курса -->
        <div v-if="showAddForm" class="add-course-form">
          <div class="form-group">
            <label>ФИО ученика:</label>
            <input v-model="newCourse.student_name" class="form-input" />
          </div>
          <div class="form-group">
            <label>Название курса:</label>
            <input v-model="newCourse.course_name" class="form-input" />
          </div>
          <div class="form-group">
            <label>Описание:</label>
            <textarea v-model="newCourse.description" class="form-textarea"></textarea>
          </div>
          <button @click="addNewCourse" class="submit-course-btn">
            Добавить курс
          </button>
        </div>
      </div>
      
      <!-- Контейнер 2: Таблица курсов -->
      <div class="tutor-courses-table-container inner-box">
        <h3>Мои курсы</h3>
        
        <div v-if="courses.length === 0" class="no-courses">
          Нет активных курсов
        </div>
        
        <div v-else class="courses-table">
          <!-- Заголовки таблицы -->
          <div class="table-header">
            <div class="table-cell">ФИО ученика</div>
            <div class="table-cell">Название курса</div>
            <div class="table-cell">Подробности</div>
          </div>
          
          <!-- Строки таблицы -->
          <div 
            v-for="course in courses" 
            :key="course.id" 
            class="table-row"
          >
            <div class="table-cell">
              <div class="student-name">{{ course.student_name }}</div>
            </div>
            <div class="table-cell">
              <div class="course-title">{{ course.course_name }}</div>
            </div>
            <div class="table-cell">
              <button 
                @click="goToCourse(course.id)" 
                class="course-details-btn"
              >
                Перейти к курсу
              </button>
            </div>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
/* Внешний контейнер для информации о курсах (такой же как у ученика) */
.course-outer-container {
  background: #fbb599;
  border-radius: 25px;
  padding: 30px;
  width: 1000px;
  box-shadow: 0 0 20px rgba(0,0,0,0.25);
  margin: 0 auto;
}

.tutor-courses-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Контейнер 1: Заголовок с поиском */
.tutor-courses-header {
  background: #fedac4;
  border-radius: 20px;
  padding: 25px 30px;
  box-shadow: 0 0 10px rgba(0,0,0,0.15);
  width: 100%;
}

.tutor-courses-header h2 {
  font-size: 26px;
  margin-bottom: 20px;
  color: #592012;
  text-align: center;
}

.courses-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

/* Секция поиска */
.search-section {
  flex: 1;
}

.search-input-wrapper {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 12px 15px;
  border: 2px solid #d8b9a7;
  border-radius: 10px;
  background: #fff;
  font-family: 'KyivType Titling', serif;
  font-size: 14px;
  color: #592012;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #f4886d;
}

.search-btn {
  padding: 12px 24px;
  background: #f4886d;
  color: #592012;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  font-family: 'KyivType Titling', serif;
  white-space: nowrap;
  font-size: 16px;
}

.search-btn:hover {
  background: #cf7058;
  transform: translateY(-2px);
}

/* Кнопка добавления курса с иконкой */
.add-course-btn {
  padding: 12px 20px 12px 24px;
  background: #f4886d;
  color: #592012;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  font-family: 'KyivType Titling', serif;
  white-space: nowrap;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-course-btn:hover {
  background: #cf7058;
  transform: translateY(-2px);
}

.add-course-icon {
  width: 16px;
  height: 16px;
  filter: brightness(0) saturate(100%) invert(14%) sepia(43%) saturate(1000%) hue-rotate(340deg) brightness(90%) contrast(90%);
}

/* Форма добавления курса */
.add-course-form {
  background: #ffe8d5;
  border-radius: 15px;
  padding: 25px;
  margin-top: 25px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-group label {
  font-weight: bold;
  color: #592012;
  font-size: 16px;
}

.form-input {
  padding: 12px 15px;
  border: 2px solid #d8b9a7;
  border-radius: 8px;
  background: #fff;
  font-family: 'KyivType Titling', serif;
  color: #592012;
  font-size: 15px;
}

.form-input:focus {
  outline: none;
  border-color: #f4886d;
  box-shadow: 0 0 0 2px rgba(244, 136, 109, 0.2);
}

.form-textarea {
  padding: 12px 15px;
  border: 2px solid #d8b9a7;
  border-radius: 8px;
  background: #fff;
  font-family: 'KyivType Titling', serif;
  color: #592012;
  min-height: 100px;
  resize: vertical;
  font-size: 15px;
}

.form-textarea:focus {
  outline: none;
  border-color: #f4886d;
  box-shadow: 0 0 0 2px rgba(244, 136, 109, 0.2);
}

.submit-course-btn {
  padding: 12px 24px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  font-family: 'KyivType Titling', serif;
  align-self: flex-start;
  font-size: 16px;
}

.submit-course-btn:hover {
  background: #45a049;
  transform: translateY(-2px);
}

/* Контейнер 2: Таблица курсов */
.tutor-courses-table-container {
  background: #fedac4;
  border-radius: 20px;
  padding: 25px 30px;
  box-shadow: 0 0 10px rgba(0,0,0,0.15);
  width: 100%;
}

.tutor-courses-table-container h3 {
  font-size: 24px;
  margin-bottom: 25px;
  color: #592012;
  text-align: center;
}

/* Таблица */
.courses-table {
  display: flex;
  flex-direction: column;
  gap: 0;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid #d8b9a7;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 2fr 1fr;
  background: #d8b9a7;
  padding: 18px 15px;
  font-weight: bold;
  color: #592012;
  font-size: 16px;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 2fr 1fr;
  background: #fff;
  padding: 18px 15px;
  border-bottom: 1px solid #e0d1c7;
  transition: background 0.3s;
}

.table-row:hover {
  background: #f9f0e9;
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  display: flex;
  align-items: center;
  padding: 0 10px;
  color: #592012;
}

.student-name, .course-title {
  font-weight: bold;
  font-size: 15px;
}

/* Кнопка в таблице */
.course-details-btn {
  padding: 10px 20px;
  background: #f4886d;
  color: #592012;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  font-family: 'KyivType Titling', serif;
  font-size: 14px;
  white-space: nowrap;
}

.course-details-btn:hover {
  background: #cf7058;
  transform: translateY(-2px);
}

.no-courses {
  text-align: center;
  padding: 40px;
  color: #777;
  font-style: italic;
  font-size: 18px;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .course-outer-container {
    width: 95%;
    padding: 20px;
  }
  
  .courses-header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .search-input-wrapper {
    flex-direction: column;
  }
  
  .add-course-btn {
    width: 100%;
    justify-content: center;
    padding: 12px;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 10px;
    padding: 15px;
  }
  
  .table-cell {
    justify-content: center;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .course-outer-container {
    padding: 15px;
  }
  
  .tutor-courses-header,
  .tutor-courses-table-container {
    padding: 20px;
  }
  
  .search-btn,
  .add-course-btn,
  .submit-course-btn {
    width: 100%;
    justify-content: center;
  }
  
  .form-group {
    width: 100%;
  }
}
</style>