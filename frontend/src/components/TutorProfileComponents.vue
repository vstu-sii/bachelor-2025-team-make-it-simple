<template>
  <!-- Внешний контейнер для информации о курсах -->
  <div class="course-outer-container">
    <div class="tutor-courses-content">
      
      <!-- Контейнер 1: Поиск и добавление курса -->
      <div class="tutor-courses-header inner-box">
        <h2>Информация о курсах</h2>
        
        <!-- Статистика курсов -->
        <div class="courses-stats">
          <div class="stat-item">
            <span class="stat-value">{{ totalCourses }}</span>
            <span class="stat-label">активных курсов</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ totalStudents }}</span>
            <span class="stat-label">учеников</span>
          </div>
        </div>
        
        <div class="courses-header-content">
          
          <!-- Строка поиска и кнопка "Найти" -->
          <div class="search-section">
            <div class="search-input-wrapper">
              <input 
                v-model="searchQuery" 
                @keyup.enter="searchStudent"
                placeholder="Введите ФИО ученика или название курса" 
                class="search-input"
                :disabled="loading"
              />
              <div class="search-actions">
                <button @click="searchStudent" class="search-btn" :disabled="loading">
                  <span v-if="loading">Поиск...</span>
                  <span v-else>Найти</span>
                </button>
                <button @click="clearSearch" class="clear-search-btn" v-if="searchQuery">
                  Сброс
                </button>
              </div>
            </div>
            <div v-if="searchQuery && filteredCourses.length !== courses.length" class="search-results-info">
              Найдено: {{ filteredCourses.length }} из {{ courses.length }}
            </div>
          </div>
          
          <!-- Кнопка "Добавить новый курс" с иконкой -->
          <button 
            @click="toggleAddForm" 
            class="add-course-btn"
            :class="{ 'active': showAddForm }"
          >
            {{ showAddForm ? 'Отмена' : 'Добавить курс' }}
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
          <h4>Создание нового курса</h4>
          <div class="form-group">
            <label for="courseTitle">Название курса *</label>
            <input 
              id="courseTitle"
              v-model="newCourse.title" 
              class="form-input" 
              placeholder="Например: Математика для начинающих"
              @keyup.enter="addNewCourse"
            />
            <div class="form-hint">Обязательное поле</div>
          </div>
          
          <div class="form-group">
            <label for="courseDescription">Описание курса</label>
            <textarea 
              id="courseDescription"
              v-model="newCourse.description" 
              class="form-textarea" 
              placeholder="Краткое описание целей и содержания курса..."
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-note">
            <p><strong>Примечание:</strong> После создания курса вы сможете добавить учеников через поиск.</p>
          </div>
          
          <div class="form-actions">
            <button @click="addNewCourse" class="submit-course-btn" :disabled="!newCourse.title.trim()">
              <span v-if="creatingCourse">Создание...</span>
              <span v-else>Создать курс</span>
            </button>
            <button @click="resetForm" class="cancel-form-btn">
              Очистить форму
            </button>
          </div>
        </div>
      </div>
      
      <!-- Контейнер 2: Таблица курсов -->
      <div class="tutor-courses-table-container inner-box">
        <div class="table-header-section">
          <h3>Список курсов</h3>
          <div class="table-actions">
            <button @click="refreshCourses" class="refresh-btn" :disabled="loading">
              <span class="refresh-icon">↻</span>
              Обновить
            </button>
          </div>
        </div>
        
        <div v-if="loading && courses.length === 0" class="loading-courses">
          <div class="loading-spinner"></div>
          <p>Загрузка курсов...</p>
        </div>
        
        <div v-else-if="courses.length === 0" class="no-courses">
          <div class="no-courses-icon">📚</div>
          <p class="no-courses-title">У вас пока нет курсов</p>
          <p class="no-courses-subtitle">Создайте первый курс, чтобы начать работу с учениками</p>
          <button @click="toggleAddForm" class="create-first-course-btn">
            Создать первый курс
          </button>
        </div>
        
        <div v-else-if="filteredCourses.length === 0" class="no-search-results">
          <p>По запросу "{{ searchQuery }}" ничего не найдено</p>
          <button @click="clearSearch" class="show-all-btn">
            Показать все курсы
          </button>
        </div>
        
        <div v-else class="courses-table-wrapper">
          <div class="courses-table">
            <!-- Заголовки таблицы -->
            <div class="table-header">
              <div class="table-cell student-col">Ученик</div>
              <div class="table-cell course-col">Курс</div>
              <div class="table-cell date-col">Дата создания</div>
              <div class="table-cell actions-col">Действия</div>
            </div>
            
            <!-- Строки таблицы -->
            <div 
              v-for="course in filteredCourses" 
              :key="course.has_student ? `${course.course_id}-${course.student_id}` : `empty-${course.course_id}`" 
              class="table-row"
            >
              <div class="table-cell student-col">
                <div class="student-info">
                  <!-- Для курсов без учеников показываем прочерк -->
                  <span 
                    v-if="!course.has_student" 
                    class="no-student"
                  >
                    -
                  </span>
                  
                  <!-- Для курсов с учениками - кликабельная ссылка -->
                  <a 
                    v-else
                    @click="viewStudentProfile(course.student_id)" 
                    class="student-name-link"
                    :title="`Перейти к профилю ${course.student_name}`"
                  >
                    {{ course.student_name }}
                  </a>
                </div>
              </div>
              <div class="table-cell course-col">
                <div class="course-info">
                  <div class="course-title">{{ course.course_name }}</div>
                </div>
              </div>
              <div class="table-cell date-col">
                <div class="date-info">
                  <div class="course-date">{{ formatDate(course.created_at) }}</div>
                </div>
              </div>
              <div class="table-cell actions-col">
                <div class="action-buttons">
                  <button 
                    @click="goToCourse(course.course_id)" 
                    class="course-details-btn"
                    :title="course.has_student ? 'Перейти к курсу' : 'Перейти к пустому курсу'"
                  >
                    К курсу
                  </button>
                </div>
              </div>
            </div>
          </div> <!-- Закрывающий тег для .courses-table -->
          
          <div class="table-footer">
            <div class="pagination-info">
              Показано: {{ filteredCourses.length }} записей
            </div>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import api from "../api/axios";

const auth = useAuthStore();
const router = useRouter();

// Данные для поиска
const searchQuery = ref("");
const courses = ref([]);
const loading = ref(false);
const creatingCourse = ref(false);

// Состояние для нового курса
const newCourse = reactive({
  title: "",
  description: ""
});

// Флаг для показа формы добавления курса
const showAddForm = ref(false);

// Вычисляем отфильтрованные курсы
const filteredCourses = computed(() => {
  if (!searchQuery.value.trim()) {
    return courses.value;
  }
  
  const query = searchQuery.value.toLowerCase();
  return courses.value.filter(course => {
    // Проверяем название курса
    const courseMatches = course.course_name.toLowerCase().includes(query);
    
    // Проверяем имя ученика (только для курсов с учениками)
    const studentMatches = course.has_student && 
                          course.student_name.toLowerCase().includes(query);
    
    return courseMatches || studentMatches;
  });
});

// Загружаем курсы репетитора
onMounted(async () => {
  await loadCourses();
});

async function loadCourses() {
  try {
    loading.value = true;
    const response = await api.get(`/courses/tutors/${auth.user.user_id}/courses`);
    courses.value = response.data;
  } catch (error) {
    console.error("Ошибка загрузки курсов:", error);
    alert("Не удалось загрузить список курсов");
  } finally {
    loading.value = false;
  }
}

async function searchStudent() {
  if (!searchQuery.value.trim()) {
    return;
  }

  try {
    loading.value = true;
    const response = await api.get(`/courses/tutors/${auth.user.user_id}/courses/search`, {
      params: { query: searchQuery.value }
    });
    courses.value = response.data;
  } catch (error) {
    console.error("Ошибка поиска:", error);
    alert("Ошибка при поиске курсов");
  } finally {
    loading.value = false;
  }
}

function clearSearch() {
  searchQuery.value = "";
  loadCourses();
}

function toggleAddForm() {
  showAddForm.value = !showAddForm.value;
  if (!showAddForm.value) {
    resetForm();
  }
}

async function addNewCourse() {
  if (!newCourse.title.trim()) {
    alert("Пожалуйста, введите название курса");
    return;
  }

  try {
    creatingCourse.value = true;
    const response = await api.post(`/courses/tutors/${auth.user.user_id}/courses`, {
      title: newCourse.title,
      ...(newCourse.description && { description: newCourse.description })
    });
    
    resetForm();
    showAddForm.value = false;
    
    await loadCourses();
    alert(`Курс "${response.data.title}" успешно создан!`);
  } catch (error) {
    console.error("Ошибка создания курса:", error);
    alert("Ошибка при создании курса: " + (error.response?.data?.detail || error.message));
  } finally {
    creatingCourse.value = false;
  }
}

function resetForm() {
  newCourse.title = "";
  newCourse.description = "";
}

function goToCourse(courseId) {
  router.push(`/course/${courseId}`);
}

function viewStudentProfile(studentId) {
  router.push(`/profile/${studentId}`);
}

async function refreshCourses() {
  await loadCourses();
}

function formatDate(dateString) {
  if (!dateString) return 'Не указана';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  } catch {
    return dateString;
  }
}

// Вычисляем общее количество курсов и учеников
const totalCourses = computed(() => {
  const uniqueCourses = new Set(courses.value.map(c => c.course_id));
  return uniqueCourses.size;
});

const totalStudents = computed(() => {
  const uniqueStudents = new Set(courses.value
    .filter(c => c.has_student && c.student_id)
    .map(c => c.student_id)
  );
  return uniqueStudents.size;
});
</script>

<style scoped>
/* Внешний контейнер для информации о курсах */
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

/* Статистика курсов */
.courses-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 25px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 12px;
}

.courses-stats .stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100px;
}

.courses-stats .stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #592012;
  line-height: 1;
}

.courses-stats .stat-label {
  font-size: 14px;
  color: #592012;
  opacity: 0.8;
  text-align: center;
  margin-top: 5px;
}

.courses-header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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
  margin-bottom: 8px;
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
  transition: all 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #f4886d;
  box-shadow: 0 0 0 3px rgba(244, 136, 109, 0.1);
}

.search-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.search-actions {
  display: flex;
  gap: 8px;
}

.search-btn {
  padding: 12px 20px;
  background: #f4886d;
  color: #592012;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  font-family: 'KyivType Titling', serif;
  white-space: nowrap;
  font-size: 14px;
  min-width: 80px;
}

.search-btn:hover:not(:disabled) {
  background: #cf7058;
  transform: translateY(-2px);
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.clear-search-btn {
  padding: 12px 15px;
  background: #6d718b;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  font-family: 'KyivType Titling', serif;
  white-space: nowrap;
  font-size: 14px;
}

.clear-search-btn:hover {
  background: #585c74;
}

.search-results-info {
  font-size: 13px;
  color: #666;
  margin-top: 5px;
  padding-left: 5px;
}

/* Кнопка добавления курса */
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
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 160px;
  justify-content: center;
}

.add-course-btn:hover {
  background: #cf7058;
  transform: translateY(-2px);
}

.add-course-btn.active {
  background: #6d718b;
  color: white;
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
  border: 2px solid #f4886d;
}

.add-course-form h4 {
  margin: 0 0 20px 0;
  color: #592012;
  font-size: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.form-group label {
  font-weight: bold;
  color: #592012;
  font-size: 15px;
}

.form-input, .form-textarea {
  padding: 12px 15px;
  border: 2px solid #d8b9a7;
  border-radius: 8px;
  background: #fff;
  font-family: 'KyivType Titling', serif;
  color: #592012;
  font-size: 15px;
  transition: all 0.3s;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #f4886d;
  box-shadow: 0 0 0 3px rgba(244, 136, 109, 0.1);
}

.form-textarea {
  min-height: 80px;
  resize: vertical;
}

.form-hint {
  font-size: 12px;
  color: #888;
  margin-top: 2px;
}

.form-note {
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  border-left: 4px solid #f4886d;
  margin-bottom: 20px;
}

.form-note p {
  margin: 0;
  font-size: 14px;
  color: #592012;
  line-height: 1.5;
}

.form-actions {
  display: flex;
  gap: 15px;
  align-items: center;
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
  font-size: 15px;
  min-width: 140px;
}

.submit-course-btn:hover:not(:disabled) {
  background: #45a049;
  transform: translateY(-2px);
}

.submit-course-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-form-btn {
  padding: 12px 20px;
  background: #6d718b;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  font-family: 'KyivType Titling', serif;
  font-size: 14px;
}

.cancel-form-btn:hover {
  background: #585c74;
}

/* Контейнер 2: Таблица курсов */
.tutor-courses-table-container {
  background: #fedac4;
  border-radius: 20px;
  padding: 25px 30px;
  box-shadow: 0 0 10px rgba(0,0,0,0.15);
  width: 100%;
}

.table-header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.tutor-courses-table-container h3 {
  font-size: 24px;
  color: #592012;
  margin: 0;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.refresh-btn {
  padding: 8px 15px;
  background: #6d718b;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  font-family: 'KyivType Titling', serif;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.refresh-btn:hover:not(:disabled) {
  background: #585c74;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  font-size: 16px;
}

/* Индикатор загрузки */
.loading-courses {
  text-align: center;
  padding: 60px 20px;
  color: #592012;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #f4886d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Нет курсов */
.no-courses {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.no-courses-icon {
  font-size: 48px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.no-courses-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #592012;
}

.no-courses-subtitle {
  font-size: 16px;
  margin-bottom: 30px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.create-first-course-btn {
  padding: 12px 30px;
  background: #f4886d;
  color: #592012;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  font-family: 'KyivType Titling', serif;
  font-size: 16px;
  transition: all 0.3s;
}

.create-first-course-btn:hover {
  background: #cf7058;
  transform: translateY(-2px);
}

/* Нет результатов поиска */
.no-search-results {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.no-search-results p {
  margin-bottom: 20px;
  font-size: 16px;
}

.show-all-btn {
  padding: 10px 20px;
  background: #6d718b;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  font-family: 'KyivType Titling', serif;
  font-size: 14px;
}

.show-all-btn:hover {
  background: #585c74;
}

/* Таблица курсов */
.courses-table-wrapper {
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid #d8b9a7;
}

.courses-table {
  display: flex;
  flex-direction: column;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 2fr 1fr 1fr;
  background: #d8b9a7;
  padding: 15px;
  font-weight: bold;
  color: #592012;
  font-size: 15px;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 2fr 1fr 1fr;
  background: #fff;
  padding: 15px;
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

/* Стиль для курсов без учеников */
.no-student {
  color: #888;
  font-style: italic;
  font-size: 15px;
}

/* Подсветка строк с курсами без учеников */
.table-row:has(.no-student) {
  background-color: #f9f9f9;
  opacity: 0.9;
}

.table-row:has(.no-student):hover {
  background-color: #f0f0f0;
}

/* Заголовок курса без учеников */
.table-row:has(.no-student) .course-title {
  color: #666;
}

/* Колонки таблицы */
.student-col {
  justify-content: flex-start;
}

.course-col {
  justify-content: flex-start;
}

.date-col {
  justify-content: center;
}

.actions-col {
  justify-content: center;
}

/* Информация об ученике */
.student-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

/* Стиль для кликабельного ФИО ученика */
.student-name-link {
  font-weight: bold;
  font-size: 15px;
  color: #592012;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-block;
  padding: 2px 4px;
  border-radius: 4px;
}

.student-name-link:hover {
  color: #f4886d;
  text-decoration: underline;
  background-color: rgba(244, 136, 109, 0.1);
  transform: translateY(-1px);
}

.student-name-link:active {
  transform: translateY(0);
}

/* Удалены стили для knowledge-gaps-badge */

/* Информация о курсе */
.course-info {
  display: flex;
  flex-direction: column;
}

.course-title {
  font-weight: bold;
  font-size: 15px;
}

.course-id {
  font-size: 12px;
  color: #888;
}

/* Информация о дате */
.date-info {
  text-align: center;
}

.course-date {
  font-size: 14px;
  color: #666;
}

/* Кнопки действий */
.action-buttons {
  display: flex;
  gap: 8px;
}

.course-details-btn {
  padding: 8px 15px;
  background: #f4886d;
  color: #592012;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  font-family: 'KyivType Titling', serif;
  font-size: 13px;
  white-space: nowrap;
}

.course-details-btn:hover {
  background: #cf7058;
  transform: translateY(-2px);
}

/* Футер таблицы */
.table-footer {
  background: #f5f5f5;
  padding: 12px 15px;
  border-top: 1px solid #e0d1c7;
}

.pagination-info {
  font-size: 13px;
  color: #666;
  text-align: right;
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
  }
  
  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 15px;
    padding: 15px;
  }
  
  .table-cell {
    justify-content: flex-start;
    text-align: left;
    padding: 5px 0;
  }
  
  .actions-col {
    justify-content: flex-start;
  }
  
  .action-buttons {
    justify-content: flex-start;
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
  
  .courses-stats {
    gap: 20px;
  }
  
  .courses-stats .stat-item {
    min-width: 80px;
  }
  
  .courses-stats .stat-value {
    font-size: 24px;
  }
  
  .table-header-section {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .table-actions {
    justify-content: center;
  }
}
</style>