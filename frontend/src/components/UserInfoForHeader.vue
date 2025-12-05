<!-- UserInfo.vue -->
<template>
    <div class="user-info-section">
      <div class="user-avatar-container">
        <img :src="user.avatar_path || defaultAvatar" alt="avatar" class="user-info-avatar" />
      </div>
      <div class="user-details">
        <div class="user-last-name">{{ user.last_name }}</div>
        <div class="user-full-name">{{ user.first_name }} {{ user.middle_name }}</div>
        <div class="user-role">{{ user.role }}</div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { defineProps } from "vue";
  
  const props = defineProps({
    user: {
      type: Object,
      required: true
    }
  });
  
  const defaultAvatar = "/src/assets/avatars/default_avatar.svg";
  </script>
  
  <style scoped>
  .user-info-section {
    display: flex;
    align-items: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 0, 68, 0.3);
  }
  
  .user-avatar-container {
    margin-right: 15px;
  }
  
  .user-info-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    border: 2px solid #ff0044;
    object-fit: cover;
  }
  
  .user-details {
    display: flex;
    flex-direction: column;
    color: white;
    font-family: 'Arial', serif;
  }
  
  .user-last-name {
    font-size: 16px;
    font-weight: bold;
    color: #ff0044;
    margin-bottom: 4px;
  }
  
  .user-full-name {
    font-size: 14px;
    margin-bottom: 4px;
    opacity: 0.9;
  }
  
  .user-role {
    font-size: 12px;
    color: #ff6b6b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  </style>