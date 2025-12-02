<template>
    <div class="course-page">
      <h1>Страница курса {{ courseId }}</h1>
      <!-- Здесь будет детальная информация о курсе -->
    </div>
  </template>
  
  <script setup>
  import { useRoute } from "vue-router";
  
  const route = useRoute();
  const courseId = route.params.id;
  </script>