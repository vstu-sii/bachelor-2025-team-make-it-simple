<template>
  <div class="add-course-page">
    <AppHeader :show-back-button="false" />
    
    <button class="back-btn" @click="goBack">
      <img src="/src/assets/arrow-back.svg" alt="back" />
    </button>

    <div class="main-container">
      <div class="inner-container">
        
        <div class="section-container center-section">
          <h1 class="title">Создание нового курса</h1>
          <div class="divider"></div>
          
          <div class="form-group center-input">
            <label>Введите название курса</label>
            <div class="input-wrapper">
              <input 
                type="text" 
                placeholder="Название курса" 
                v-model="courseTitle"
              />
            </div>
          </div>
          
          <div class="form-group center-input">
            <label>Введите название темы</label>
            <div class="input-wrapper">
              <input 
                type="text" 
                placeholder="Название темы" 
                v-model="newTopicTitle"
                @keyup.enter="addTopic"
                :disabled="isAddingTopic"
              />
            </div>
          </div>
        </div>

        <div class="section-container">
          <div class="row">
            <div class="column">
              <div class="form-group">
                <label>Введите описание темы</label>
                <div class="description-container">
                  <textarea 
                    placeholder="Введите подробное описание темы..."
                    class="description-textarea"
                    v-model="newTopicDescription"
                    :disabled="isAddingTopic"
                  ></textarea>
                </div>
                <button class="add-btn lesson-btn" @click="addTopic" :disabled="isAddingTopic">
                  <span v-if="isAddingTopic">Добавление...</span>
                  <span v-else>
                    Добавить новую тему
                    <img src="/src/assets/plus.svg" />
                  </span>
                </button>
                
                <div v-if="topicErrorMessage" class="error-message">
                  {{ topicErrorMessage }}
                </div>
                <div v-if="topicSuccessMessage" class="success-message">
                  {{ topicSuccessMessage }}
                </div>
              </div>
            </div>

            <div class="column">
              <div class="form-group">
                <label>Добавить учебный материал (PDF)</label>
                <div 
                  class="dropzone" 
                  @click="triggerFileInput"
                  @dragover.prevent="handleDragOver"
                  @drop.prevent="handleDrop"
                  :class="{ 'dropzone-dragover': isDragOver }"
                >
                  <div class="dropzone-content">
                    <img class="upload-icon" src="/src/assets/upload-arrow.svg" />
                    <p class="dropzone-text">Перетащите сюда PDF файлы<br />или нажмите для загрузки</p>
                    <p class="dropzone-hint">Поддерживается только PDF формат</p>
                  </div>
                </div>
                <input 
                  type="file" 
                  ref="fileInput" 
                  @change="handleFileSelect"
                  accept=".pdf"
                  style="display: none"
                />
                <button class="add-btn material-btn" @click="triggerFileInput" :disabled="isUploadingMaterial">
                  <span v-if="isUploadingMaterial">Загрузка...</span>
                  <span v-else>
                    Добавить новый материал
                    <img src="/src/assets/plus.svg" />
                  </span>
                </button>
                
                <div v-if="materialErrorMessage" class="error-message">
                  {{ materialErrorMessage }}
                </div>
                <div v-if="materialSuccessMessage" class="success-message">
                  {{ materialSuccessMessage }}
                </div>
                
                <div v-if="uploadProgress > 0" class="upload-progress">
                  <div class="progress-bar">
                    <div 
                      class="progress-fill" 
                      :style="{ width: uploadProgress + '%' }"
                    ></div>
                  </div>
                  <div class="progress-text">{{ uploadProgress }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="column">
            <div class="list-container">
              <div class="list-section">
                <label>Список тем ({{ topics.length }})</label>
                <ul>
                  <li v-for="(topic, index) in topics" :key="topic.topic_id">
                    <span>{{ index + 1 }}. {{ topic.title }}</span>
                    <img 
                      class="remove" 
                      src="/src/assets/close.svg"
                      @click="removeTopic(topic.topic_id)"
                      alt="Удалить"
                      :title="`Удалить тему: ${topic.title}`"
                      :disabled="isDeletingTopic === topic.topic_id"
                    />
                  </li>
                  <li v-if="topics.length === 0" class="empty-list">
                    <span>Список тем пуст. Добавьте первую тему.</span>
                  </li>
                </ul>
                <div v-if="isLoadingTopics" class="loading-message">
                  Загрузка тем...
                </div>
              </div>
            </div>
          </div>

          <div class="column">
            <div class="list-container">
              <div class="list-section">
                <label>Список материалов ({{ courseMaterials.length }})</label>
                <ul>
                  <li v-for="(material, index) in courseMaterials" :key="material.id || index">
                    <span>{{ index + 1 }}. {{ getFileName(material.file_path || material.name) }}</span>
                    <img 
                      class="remove" 
                      src="/src/assets/close.svg"
                      @click="removeCourseMaterial(material.material_id, index)"
                      alt="Удалить"
                      :title="`Удалить материал: ${getFileName(material.file_path || material.name)}`"
                      :disabled="isDeletingMaterial === material.material_id"
                    />
                  </li>
                  <li v-if="courseMaterials.length === 0" class="empty-list">
                    <span>Список материалов пуст. Добавьте первый материал.</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <button class="submit-btn" @click="createCourse" :disabled="isCreatingCourse">
          <span v-if="isCreatingCourse">Создание курса...</span>
          <span v-else>Создать курс</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import AppHeader from "../components/Header.vue";
import { config } from "../config";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const API_BASE_URL = config.apiUrl;
const fileInput = ref(null);

// Состояние для формы
const courseTitle = ref("");
const newTopicTitle = ref("");
const newTopicDescription = ref("");

// Динамические списки
const topics = ref([]);
const courseMaterials = ref([]); // Материалы, добавленные к этому курсу

// Состояния загрузки и ошибок для тем
const isLoadingTopics = ref(false);
const isAddingTopic = ref(false);
const isDeletingTopic = ref(null);
const topicErrorMessage = ref("");
const topicSuccessMessage = ref("");

// Состояния загрузки и ошибок для материалов
const isUploadingMaterial = ref(false);
const isCreatingCourse = ref(false);
const isDeletingMaterial = ref(null);
const materialErrorMessage = ref("");
const materialSuccessMessage = ref("");
const isDragOver = ref(false);
const uploadProgress = ref(0);

// Функция для выполнения авторизованных запросов
const makeAuthRequest = async (url, options = {}) => {
  const token = localStorage.getItem("token");
  
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  
  console.log(`API Request: ${options.method || 'GET'} ${url}`, {
    headers,
    body: options.body ? JSON.parse(options.body) : undefined
  });
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`API Error ${response.status}:`, errorData);
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`API Response ${response.status}:`, data);
    return data;
  } catch (error) {
    console.error("API Request error:", error);
    throw error;
  }
};

// Функция для загрузки файлов
const makeFileUploadRequest = async (url, formData) => {
  const token = localStorage.getItem("token");
  
  const headers = {};
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  
  console.log(`File Upload Request: POST ${url}`);
  
  try {
    const response = await fetch(url, {
      method: "POST",
      headers,
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`File Upload Error ${response.status}:`, errorData);
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`File Upload Response ${response.status}:`, data);
    return data;
  } catch (error) {
    console.error("File Upload error:", error);
    throw error;
  }
};

// Извлечение имени файла из пути
const getFileName = (filePath) => {
  const parts = filePath.split('/');
  return parts[parts.length - 1];
};

// Функция добавления темы в БД
const addTopic = async () => {
  if (!newTopicTitle.value.trim()) {
    topicErrorMessage.value = "Пожалуйста, введите название темы";
    setTimeout(() => topicErrorMessage.value = "", 3000);
    return;
  }

  isAddingTopic.value = true;
  topicErrorMessage.value = "";
  topicSuccessMessage.value = "";

  try {
    const topicData = {
      title: newTopicTitle.value.trim(),
      description_text: newTopicDescription.value.trim() || null
    };

    console.log("Создание новой темы:", topicData);
    
    const response = await makeAuthRequest(`${API_BASE_URL}/topics/`, {
      method: "POST",
      body: JSON.stringify(topicData)
    });

    console.log("Тема успешно создана в БД:", response);
    
    // Добавляем новую тему в список
    topics.value.unshift(response);
    
    // Показываем сообщение об успехе
    topicSuccessMessage.value = `Тема "${response.title}" успешно добавлена!`;
    
    // Очищаем поля ввода
    newTopicTitle.value = "";
    newTopicDescription.value = "";
    
    setTimeout(() => {
      topicSuccessMessage.value = "";
    }, 3000);
    
  } catch (error) {
    console.error("Ошибка при добавлении темы:", error);
    topicErrorMessage.value = error.message || "Не удалось добавить тему";
    setTimeout(() => topicErrorMessage.value = "", 5000);
  } finally {
    isAddingTopic.value = false;
  }
};

// Функция удаления темы из БД
const removeTopic = async (topicId) => {
  if (!topicId) {
    console.error("ID темы не указан");
    topicErrorMessage.value = "Ошибка: ID темы не указан";
    return;
  }

  const topicToDelete = topics.value.find(t => t.topic_id === topicId);
  if (!topicToDelete) {
    console.error("Тема не найдена в списке");
    topicErrorMessage.value = "Тема не найдена в списке";
    return;
  }

  if (!confirm(`Удалить тему "${topicToDelete.title}"?`)) {
    return;
  }

  isDeletingTopic.value = topicId;
  topicErrorMessage.value = "";
  topicSuccessMessage.value = "";

  try {
    console.log(`Удаление темы с ID: ${topicId} ("${topicToDelete.title}")`);
    
    await makeAuthRequest(`${API_BASE_URL}/topics/${topicId}`, {
      method: "DELETE"
    });

    console.log(`Тема с ID ${topicId} удалена из БД`);
    
    // Удаляем тему из списка
    const index = topics.value.findIndex(t => t.topic_id === topicId);
    if (index !== -1) {
      topics.value.splice(index, 1);
    }
    
    topicSuccessMessage.value = `Тема "${topicToDelete.title}" успешно удалена!`;
    setTimeout(() => {
      topicSuccessMessage.value = "";
    }, 3000);
    
  } catch (error) {
    console.error("Ошибка при удалении темы:", error);
    topicErrorMessage.value = error.message || "Не удалось удалить тему";
    setTimeout(() => topicErrorMessage.value = "", 5000);
  } finally {
    isDeletingTopic.value = null;
  }
};

// Drag & Drop обработчики
const handleDragOver = (event) => {
  event.preventDefault();
  isDragOver.value = true;
};

const handleDrop = (event) => {
  event.preventDefault();
  isDragOver.value = false;
  
  const files = event.dataTransfer.files;
  if (files.length > 0) {
    handleFiles(files[0]);
  }
};

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    handleFiles(file);
  }
  // Сброс input для возможности загрузки того же файла снова
  event.target.value = '';
};

// Обработка загрузки файла
const handleFiles = async (file) => {
  // Проверка типа файла
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    materialErrorMessage.value = "Поддерживается только PDF формат";
    setTimeout(() => materialErrorMessage.value = "", 5000);
    return;
  }

  // Проверка размера файла (макс 10MB)
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    materialErrorMessage.value = "Файл слишком большой (максимум 10MB)";
    setTimeout(() => materialErrorMessage.value = "", 5000);
    return;
  }

  isUploadingMaterial.value = true;
  uploadProgress.value = 0;
  materialErrorMessage.value = "";
  materialSuccessMessage.value = "";

  try {
    console.log(`Начало загрузки файла: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
    
    // Симуляция прогресса загрузки
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10;
      }
    }, 200);

    // Загружаем файл на сервер
    const formData = new FormData();
    formData.append("file", file);
    
    const response = await makeFileUploadRequest(`${API_BASE_URL}/materials/upload/`, formData);
    
    clearInterval(progressInterval);
    uploadProgress.value = 100;
    
    console.log("Файл успешно загружен в БД:", response);
    
    // Добавляем материал в список материалов курса
    courseMaterials.value.unshift(response);
    
    // Показываем сообщение об успехе
    materialSuccessMessage.value = `Файл "${file.name}" успешно загружен!`;
    
    setTimeout(() => {
      materialSuccessMessage.value = "";
      uploadProgress.value = 0;
    }, 3000);
    
  } catch (error) {
    console.error("Ошибка при загрузке файла:", error);
    materialErrorMessage.value = error.message || "Не удалось загрузить файл";
    setTimeout(() => materialErrorMessage.value = "", 5000);
    uploadProgress.value = 0;
  } finally {
    isUploadingMaterial.value = false;
  }
};

// Функция удаления материала из списка курса и из БД
const removeCourseMaterial = async (materialId, index) => {
  const materialToDelete = courseMaterials.value.find(m => m.material_id === materialId) || courseMaterials.value[index];
  if (!materialToDelete) {
    materialErrorMessage.value = "Материал не найден в списке";
    setTimeout(() => materialErrorMessage.value = "", 5000);
    return;
  }

  const fileName = getFileName(materialToDelete.file_path || materialToDelete.name);
  if (!confirm(`Удалить материал "${fileName}"?`)) {
    return;
  }

  isDeletingMaterial.value = materialId;
  materialErrorMessage.value = "";
  materialSuccessMessage.value = "";

  try {
    console.log(`Удаление материала с ID: ${materialId} ("${fileName}")`);
    
    await makeAuthRequest(`${API_BASE_URL}/materials/${materialId}`, {
      method: "DELETE"
    });

    console.log(`Материал с ID ${materialId} удален из БД`);
    
    // Удаляем материал из списка
    const listIndex = courseMaterials.value.findIndex(m => m.material_id === materialId);
    if (listIndex !== -1) {
      courseMaterials.value.splice(listIndex, 1);
    } else {
      // Если не нашли по ID, удаляем по индексу
      courseMaterials.value.splice(index, 1);
    }
    
    materialSuccessMessage.value = `Материал "${fileName}" успешно удален!`;
    setTimeout(() => {
      materialSuccessMessage.value = "";
    }, 3000);
    
  } catch (error) {
    console.error("Ошибка при удалении материала:", error);
    materialErrorMessage.value = error.message || "Не удалось удалить материал";
    setTimeout(() => materialErrorMessage.value = "", 5000);
  } finally {
    isDeletingMaterial.value = null;
  }
};

// Функция создания курса
const createCourse = async () => {
  if (!courseTitle.value.trim()) {
    topicErrorMessage.value = "Пожалуйста, введите название курса";
    setTimeout(() => topicErrorMessage.value = "", 3000);
    return;
  }
  
  if (topics.value.length === 0) {
    topicErrorMessage.value = "Добавьте хотя бы одну тему к курсу";
    setTimeout(() => topicErrorMessage.value = "", 3000);
    return;
  }

  isCreatingCourse.value = true;
  materialErrorMessage.value = "";
  topicErrorMessage.value = "";

  try {
    console.log("Начало создания курса...");
    
    // Подготавливаем данные для создания курса
    const courseData = {
      title: courseTitle.value.trim(),
      link_to_vector_db: `/static/vector_dbs/course_${Date.now()}`,
      input_test_json: {},
      topics_ids: topics.value.map(topic => topic.topic_id),
      materials_ids: courseMaterials.value.map(material => material.material_id)
    };
    
    console.log("Данные для создания курса:", courseData);
    
    // Создаем курс через API
    const response = await makeAuthRequest(`${API_BASE_URL}/courses/`, {
      method: "POST",
      body: JSON.stringify(courseData)
    });
    
    console.log("Курс успешно создан:", response);
    
    // Показываем сообщение об успехе
    alert(`Курс "${courseData.title}" успешно создан!\n\n` +
          `Тем: ${topics.value.length}\n` +
          `Материалов: ${courseMaterials.value.length}`);
    
    // Очищаем форму после успешного создания
    courseTitle.value = "";
    topics.value = [];
    courseMaterials.value = [];
    
    // Перенаправляем на страницу профиля
    router.push('/profile');
    
  } catch (error) {
    console.error("Ошибка при создании курса:", error);
    materialErrorMessage.value = error.message || "Не удалось создать курс";
    setTimeout(() => materialErrorMessage.value = "", 5000);
  } finally {
    isCreatingCourse.value = false;
  }
};

// Инициализация
onMounted(() => {
  console.log("Страница создания курса загружена");
  
  // Проверяем авторизацию
  const token = localStorage.getItem("token");
  if (!token) {
    const errorMsg = "Для создания курса необходимо авторизоваться";
    topicErrorMessage.value = errorMsg;
    materialErrorMessage.value = errorMsg;
    console.warn("Пользователь не авторизован");
    router.push('/login');
  } else {
    console.log("Пользователь авторизован, токен получен");
  }
});

function goBack() {
  router.push('/profile');
}
</script>

<style scoped>
/* Стили остаются без изменений */
.add-course-page {
  width: 100%;
  min-height: 100vh;
  background: #0b1444;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 40px;
  position: relative;
}

.back-btn {
  position: absolute;
  left: 50%;
  transform: translateX(calc(-50% - 535px));
  top: 100px;
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

.main-container {
  width: 95%;
  max-width: 1100px;
  background: #F4886D;
  border-radius: 25px;
  padding: 30px;
  margin-top: 120px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  position: relative;
}

.inner-container {
  background: #fbb599;
  border-radius: 20px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.center-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.section-container {
  background: #fedac4;
  border-radius: 15px;
  padding: 25px;
  border: none;
}

.list-container {
  background: #fedac4;
  border-radius: 15px;
  padding: 25px;
  border: none;
  height: 100%;
}

.title {
  text-align: center;
  margin-bottom: 15px;
  font-size: 32px;
  font-weight: bold;
  color: #592012;
  font-family: 'Arial', serif;
}

.divider {
  height: 3px;
  background: #592012;
  border-radius: 2px;
  margin: 20px 0 30px 0;
  width: 80%;
  max-width: 600px;
}

.form-group {
  margin-bottom: 20px;
  width: 100%;
}

.form-group label {
  font-size: 16px;
  margin-bottom: 8px;
  display: block;
  color: #592012;
  font-weight: bold;
  font-family: 'Arial', serif;
}

.center-input {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.input-wrapper {
  width: 70%;
  max-width: 500px;
}

input,
textarea {
  width: 100%;
  padding: 12px 15px;
  border-radius: 10px;
  border: none;
  background: #FFFFFF !important;
  color: #592012 !important;
  font-family: 'Arial', serif;
  font-size: 15px;
  box-sizing: border-box;
}

input:disabled,
textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.center-input input {
  font-size: 14px;
  padding: 10px 15px;
}

input::placeholder,
textarea::placeholder {
  color: #8A7D75;
  opacity: 0.7;
}

input:focus,
textarea:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(244, 136, 109, 0.3);
}

.row {
  display: flex;
  justify-content: space-between;
  gap: 25px;
}

.column {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.description-container {
  background: #FFFFFF;
  border: none;
  border-radius: 10px;
  overflow: hidden;
  height: 220px;
}

.description-textarea {
  width: 100%;
  height: 100%;
  padding: 15px;
  border: none;
  background: #FFFFFF !important;
  color: #592012 !important;
  font-family: 'Arial', serif;
  font-size: 15px;
  line-height: 1.5;
  resize: none;
  overflow-y: auto;
  outline: none;
  box-sizing: border-box;
}

.description-textarea::-webkit-scrollbar {
  width: 8px;
}

.description-textarea::-webkit-scrollbar-track {
  background: #E0E0E0;
  border-radius: 4px;
}

.description-textarea::-webkit-scrollbar-thumb {
  background: #B8B8B8;
  border-radius: 4px;
}

.description-textarea::-webkit-scrollbar-thumb:hover {
  background: #A0A0A0;
}

.dropzone {
  background: #FFFFFF;
  border: 2px solid #F4886D;
  border-radius: 10px;
  height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
}

.dropzone:hover {
  border-color: #E0785D;
  background: #FFF5F2;
  transform: translateY(-2px);
}

.dropzone-dragover {
  border-color: #4CAF50 !important;
  background-color: #E8F5E9 !important;
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
}

.dropzone-content {
  text-align: center;
  padding: 20px;
  position: relative;
  z-index: 1;
}

.upload-icon {
  width: 50px;
  height: 50px;
  margin-bottom: 15px;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.dropzone:hover .upload-icon {
  opacity: 1;
}

.dropzone-text {
  color: #592012;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
  line-height: 1.4;
}

.dropzone-hint {
  color: #8A7D75;
  font-size: 13px;
  margin-top: 5px;
}

.add-btn {
  margin-top: 15px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  padding: 10px 15px;
  background: #F4886D;
  color: #592012;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  font-family: 'Arial', serif;
  transition: all 0.3s;
  width: auto;
  max-width: 250px;
}

.add-btn:hover:not(:disabled) {
  background: #E0785D;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(244, 136, 109, 0.3);
}

.add-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.add-btn:disabled:hover {
  background: #F4886D;
  box-shadow: none;
}

.list-section {
  height: 100%;
}

.list-section label {
  font-size: 18px;
  margin-bottom: 15px;
  display: block;
  color: #592012;
  font-weight: bold;
  font-family: 'Arial', serif;
}

.list-container ul {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}

.list-container ul::-webkit-scrollbar {
  width: 8px;
}

.list-container ul::-webkit-scrollbar-track {
  background: #E0E0E0;
  border-radius: 4px;
}

.list-container ul::-webkit-scrollbar-thumb {
  background: #B8B8B8;
  border-radius: 4px;
}

.list-container li {
  background: #FFFFFF;
  border: 2px solid #F4886D;
  padding: 12px 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.list-container li.empty-list {
  background: #f8f8f8;
  border-style: dashed;
  border-color: #B8B8B8;
  color: #8A7D75;
  justify-content: center;
  animation: none;
}

.list-container li.empty-list span {
  text-align: center;
  font-style: italic;
}

.list-container li:not(.empty-list) {
  animation: slideIn 0.3s ease-out;
}

.list-container li:hover {
  background: #FFF5F2;
  transform: translateY(-2px);
  border-color: #E0785D;
}

.list-container li span {
  color: #592012;
  font-size: 15px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'Arial', serif;
}

.remove {
  width: 20px;
  height: 20px;
  cursor: pointer;
  transition: transform 0.2s;
  opacity: 0.7;
}

.remove:hover:not([disabled]) {
  transform: scale(1.1);
  opacity: 1;
}

.remove[disabled] {
  opacity: 0.3;
  cursor: not-allowed;
}

.remove[disabled]:hover {
  transform: none !important;
  opacity: 0.3;
}

.submit-btn {
  width: 200px;
  margin: 10px auto 0;
  display: block;
  padding: 15px 30px;
  font-size: 18px;
  border: none;
  background: #F4886D;
  color: #592012;
  border-radius: 12px;
  cursor: pointer;
  font-family: 'Arial', serif;
  font-weight: bold;
  transition: all 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background: #E0785D;
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(244, 136, 109, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  font-family: 'Arial', serif;
  animation: fadeIn 0.3s ease-in;
}

.success-message {
  color: #28a745;
  font-size: 14px;
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
  font-family: 'Arial', serif;
  animation: fadeIn 0.3s ease-in;
}

.loading-message {
  color: #592012;
  font-size: 14px;
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #e9ecef;
  border-radius: 4px;
  text-align: center;
  font-family: 'Arial', serif;
}

.upload-progress {
  margin-top: 15px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 5px;
}

.progress-fill {
  height: 100%;
  background-color: #4CAF50;
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  font-size: 12px;
  color: #592012;
  font-family: 'Arial', serif;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1200px) {
  .back-btn {
    left: 10px;
  }
}

@media (max-width: 1024px) {
  .main-container {
    width: 98%;
    padding: 25px;
    margin-top: 110px;
  }
  
  .back-btn {
    left: 30px;
    top: 90px;
  }
  
  .inner-container {
    padding: 25px;
  }
  
  .section-container,
  .list-container {
    padding: 20px;
  }
  
  .input-wrapper {
    width: 80%;
  }
  
  .add-btn {
    max-width: 220px;
  }
}

@media (max-width: 768px) {
  .back-btn {
    left: 20px;
    top: 80px;
  }
  
  .main-container {
    margin-top: 100px;
    padding: 20px;
  }
  
  .inner-container {
    padding: 20px;
    gap: 20px;
  }
  
  .row {
    flex-direction: column;
    gap: 20px;
  }
  
  .title {
    font-size: 28px;
  }
  
  .description-container,
  .dropzone {
    height: 200px;
  }
  
  .input-wrapper {
    width: 90%;
  }
  
  .add-btn {
    max-width: 100%;
    justify-content: center;
  }
  
  .submit-btn {
    width: 100%;
    max-width: 300px;
  }
}

@media (max-width: 480px) {
  .back-btn {
    left: 15px;
    top: 70px;
  }
  
  .main-container {
    padding: 15px;
    margin-top: 90px;
  }
  
  .inner-container {
    padding: 15px;
  }
  
  .section-container,
  .list-container {
    padding: 15px;
  }
  
  .title {
    font-size: 24px;
  }
  
  .description-container,
  .dropzone {
    height: 180px;
  }
  
  .dropzone-text {
    font-size: 14px;
  }
  
  .dropzone-hint {
    font-size: 12px;
  }
  
  .input-wrapper {
    width: 95%;
  }
  
  .center-input input {
    font-size: 13px;
    padding: 8px 12px;
  }
  
  .add-btn {
    font-size: 13px;
    padding: 8px 12px;
  }
}
</style>