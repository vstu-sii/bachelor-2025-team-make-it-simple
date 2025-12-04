<template>
    <div class="add-course-page">
      <button class="back-btn">
        <img src="/src/assets/arrow-back.svg" alt="back" />
      </button>
  
      <div class="container">
        <h1 class="title">Создание нового курса</h1>
  
        <div class="block">
          <label>Введите название курса</label>
          <input type="text" placeholder="Название курса" />
  
          <label>Введите тему урока</label>
          <input type="text" placeholder="Название темы" />
        </div>
  
        <div class="row">
          <div class="column">
            <label>Введите описание урока</label>
            <textarea placeholder="Описание урока"></textarea>
            <button class="add-btn">
              Добавить новый урок
              <img src="/src/assets/plus.svg" />
            </button>
          </div>
  
          <div class="column">
            <label>Добавить учебный материал</label>
            <div class="dropzone">
              <p>Перетащите в это окно все учебные материалы<br />или нажмите на кнопку ниже</p>
              <img class="arrow-drop" src="/src/assets/upload-arrow.svg" />
            </div>
            <button class="add-btn">
              Добавить новый материал
              <img src="/src/assets/plus.svg" />
            </button>
          </div>
        </div>
  
        <div class="row lists">
          <div class="column">
            <label>Список уроков</label>
            <ul>
              <li><span></span><img class="remove" src="/src/assets/close.svg" /></li>
              <li><span></span><img class="remove" src="/src/assets/close.svg" /></li>
              <li><span></span><img class="remove" src="/src/assets/close.svg" /></li>
              <li><span></span><img class="remove" src="/src/assets/close.svg" /></li>
            </ul>
          </div>
  
          <div class="column">
            <label>Список материалов</label>
            <ul>
              <li><span></span><img class="remove" src="/src/assets/close.svg" /></li>
              <li><span></span><img class="remove" src="/src/assets/close.svg" /></li>
              <li><span></span><img class="remove" src="/src/assets/close.svg" /></li>
              <li><span></span><img class="remove" src="/src/assets/close.svg" /></li>
            </ul>
          </div>
        </div>
  
        <button class="submit-btn">Создать курс</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "AddCoursePage",
  };
  </script>
  
  <style scoped>
  .add-course-page {
    width: 100%;
    min-height: 100vh;
    background: #0b1444;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 20px;
  }
  
  .back-btn {
    position: absolute;
    left: 20px;
    top: 20px;
    background: none;
    border: none;
    cursor: pointer;
  }
  
  .container {
    width: 90%;
    max-width: 900px;
    background: #ffc7a7;
    padding: 25px;
    border-radius: 20px;
    border: 5px solid #e38c6e;
  }
  
  .title {
    text-align: center;
    margin-bottom: 20px;
    font-size: 28px;
    font-weight: bold;
  }
  
  .block label,
  .column label {
    font-size: 16px;
    margin: 5px 0;
    display: block;
  }
  
  input,
  textarea {
    width: 100%;
    padding: 10px;
    border-radius: 10px;
    border: 2px solid #f1a98a;
    background: #ffe9dd;
    margin-bottom: 10px;
  }
  
  .row {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    margin-top: 20px;
  }
  
  .column {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .add-btn {
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 8px 12px;
    background: #e38c6e;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 14px;
  }
  
  .dropzone {
    background: #ffe9dd;
    border: 2px dashed #f1a98a;
    height: 140px;
    border-radius: 15px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 10px;
  }
  
  .arrow-drop {
    margin-top: 10px;
    width: 35px;
  }
  
  .lists ul {
    list-style: none;
    padding: 0;
  }
  
  .lists li {
    background: #ffe9dd;
    border: 2px solid #f1a98a;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .remove {
    width: 20px;
    cursor: pointer;
  }
  
  .submit-btn {
    width: 200px;
    margin: 20px auto 0;
    display: block;
    padding: 12px;
    font-size: 16px;
    border: none;
    background: #e38c6e;
    color: white;
    border-radius: 12px;
    cursor: pointer;
  }
  </style>
  