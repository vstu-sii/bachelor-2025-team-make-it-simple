<template>
  <div class="add-course-page">
    <!-- Добавляем хедер как на других страницах -->
    <AppHeader :show-back-button="false" />
    
    <!-- Кнопка "назад" поверх контейнера -->
    <button class="back-btn" @click="goBack">
      <img src="/src/assets/arrow-back.svg" alt="back" />
    </button>

    <!-- Основной контейнер цвета #F4886D -->
    <div class="main-container">
      <!-- Внутренний общий контейнер цвета #D9D9D9 -->
      <div class="inner-container">
        
        <!-- Контейнер для заголовка и основной информации -->
        <div class="section-container center-section">
          <h1 class="title">Создание нового курса</h1>
          <div class="divider"></div>
          
          <div class="form-group center-input">
            <label>Введите название курса</label>
            <div class="input-wrapper">
              <input type="text" placeholder="Название курса" />
            </div>
          </div>
          
          <div class="form-group center-input">
            <label>Введите тему урока</label>
            <div class="input-wrapper">
              <input type="text" placeholder="Название темы" />
            </div>
          </div>
        </div>

        <!-- Контейнер для описания урока и материалов -->
        <div class="section-container">
          <div class="row">
            <div class="column">
              <div class="form-group">
                <label>Введите описание урока</label>
                <div class="description-container">
                  <textarea 
                    placeholder="Введите подробное описание урока..."
                    class="description-textarea"
                  ></textarea>
                </div>
                <button class="add-btn lesson-btn">
                  Добавить новый урок
                  <img src="/src/assets/plus.svg" />
                </button>
              </div>
            </div>

            <div class="column">
              <div class="form-group">
                <label>Добавить учебный материал</label>
                <div class="dropzone">
                  <div class="dropzone-content">
                    <img class="upload-icon" src="/src/assets/upload-arrow.svg" />
                    <p class="dropzone-text">Перетащите сюда файлы<br />или нажмите для загрузки</p>
                    <p class="dropzone-hint">Поддерживаются: PDF, DOC, PPT, изображения, видео</p>
                  </div>
                </div>
                <button class="add-btn material-btn">
                  Добавить новый материал
                  <img src="/src/assets/plus.svg" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Контейнеры для списков -->
        <div class="row">
          <div class="column">
            <!-- Отдельный контейнер для списка уроков -->
            <div class="list-container">
              <div class="list-section">
                <label>Список уроков</label>
                <ul>
                  <li><span>Урок 1: Введение</span><img class="remove" src="/src/assets/close.svg" /></li>
                  <li><span>Урок 2: Основные понятия</span><img class="remove" src="/src/assets/close.svg" /></li>
                  <li><span>Урок 3: Практика</span><img class="remove" src="/src/assets/close.svg" /></li>
                  <li><span>Урок 4: Закрепление</span><img class="remove" src="/src/assets/close.svg" /></li>
                </ul>
              </div>
            </div>
          </div>

          <div class="column">
            <!-- Отдельный контейнер для списка материалов -->
            <div class="list-container">
              <div class="list-section">
                <label>Список материалов</label>
                <ul>
                  <li><span>Презентация.pdf</span><img class="remove" src="/src/assets/close.svg" /></li>
                  <li><span>Конспект.docx</span><img class="remove" src="/src/assets/close.svg" /></li>
                  <li><span>Тест.pdf</span><img class="remove" src="/src/assets/close.svg" /></li>
                  <li><span>Видео.mp4</span><img class="remove" src="/src/assets/close.svg" /></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <button class="submit-btn">Создать курс</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import AppHeader from "../components/Header.vue";

const router = useRouter();

function goBack() {
  router.push('/profile');
}
</script>

<style scoped>
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

/* Основной контейнер цвета #F4886D */
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

/* Внутренний общий контейнер цвета #D9D9D9 */
.inner-container {
  background: #fbb599;
  border-radius: 20px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Центрированная секция */
.center-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* Общие стили для всех контейнеров */
.section-container {
  background: #fedac4;
  border-radius: 15px;
  padding: 25px;
  border: none;
}

/* Контейнеры для списков */
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
  font-family: 'KyivType Titling', serif;
}

.divider {
  height: 3px;
  background: #592012;
  border-radius: 2px;
  margin: 20px 0 30px 0;
  width: 80%; /* Делаем разделитель короче */
  max-width: 600px; /* Ограничиваем максимальную ширину */
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
  font-family: 'KyivType Titling', serif;
}

/* Центрированные поля ввода */
.center-input {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.input-wrapper {
  width: 70%; /* Уменьшаем ширину полей */
  max-width: 500px; /* Ограничиваем максимальную ширину */
}

/* Текстовые поля с белым фоном и цветом текста #592012 */
input,
textarea {
  width: 100%;
  padding: 12px 15px;
  border-radius: 10px;
  border: none;
  background: #FFFFFF !important;
  color: #592012 !important;
  font-family: 'KyivType Titling', serif;
  font-size: 15px;
  box-sizing: border-box;
}

/* Уменьшаем размер шрифта в полях ввода для заголовков */
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

/* Контейнер для описания урока */
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
  font-family: 'KyivType Titling', serif;
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

/* Окно для перетаскивания файлов */
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
}

.dropzone:hover {
  border-color: #E0785D;
  background: #FFF5F2;
  transform: translateY(-2px);
}

.dropzone-content {
  text-align: center;
  padding: 20px;
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

/* Кнопки "Добавить новый урок" и "Добавить новый материал" */
.add-btn {
  margin-top: 15px;
  display: flex;
  align-items: center;
  justify-content: flex-start; /* Выравниваем по левому краю */
  gap: 8px;
  padding: 10px 15px; /* Уменьшаем padding для меньшего размера */
  background: #F4886D;
  color: #592012;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px; /* Уменьшаем размер шрифта */
  font-weight: bold;
  font-family: 'KyivType Titling', serif;
  transition: all 0.3s;
  width: auto; /* Убираем ширину 100% */
  max-width: 250px; /* Ограничиваем максимальную ширину */
}

.add-btn:hover {
  background: #E0785D;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(244, 136, 109, 0.3);
}

/* Списки */
.list-section {
  height: 100%;
}

.list-section label {
  font-size: 18px;
  margin-bottom: 15px;
  display: block;
  color: #592012;
  font-weight: bold;
  font-family: 'KyivType Titling', serif;
}

.list-container ul {
  list-style: none;
  padding: 0;
  margin: 0;
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
  font-family: 'KyivType Titling', serif;
}

.remove {
  width: 20px;
  height: 20px;
  cursor: pointer;
  transition: transform 0.2s;
  opacity: 0.7;
}

.remove:hover {
  transform: scale(1.1);
  opacity: 1;
}

/* Кнопка создания курса */
.submit-btn {
  width: 175px;
  margin: 10px auto 0;
  display: block;
  padding: 15px 30px;
  font-size: 18px;
  border: none;
  background: #F4886D;
  color: #592012;
  border-radius: 12px;
  cursor: pointer;
  font-family: 'KyivType Titling', serif;
  font-weight: bold;
  transition: all 0.3s;
}

.submit-btn:hover {
  background: #E0785D;
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(244, 136, 109, 0.4);
}

/* Адаптивность */
@media (max-width: 1200px) {
  .back-btn {
    left: 10px; /* Чуть левее на больших экранах */
  }
}

@media (max-width: 1024px) {
  .main-container {
    width: 98%;
    padding: 25px;
    margin-top: 110px;
  }
  
  .back-btn {
    left: 30px; /* Чуть левее на средних экранах */
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
    left: 20px; /* На мобилках оставляем как было */
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