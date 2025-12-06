<template>
    <div class="custom-node" :style="nodeStyle" @click="onClick" :title="tooltipText">
      <div class="node-content">
        <div class="node-label">{{ data.label }}</div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { defineProps, computed } from 'vue'
  
  const props = defineProps({
    data: {
      type: Object,
      required: true
    },
    selected: {
      type: Boolean,
      default: false
    }
  })
  
  const emit = defineEmits(['click'])
  
  const nodeStyle = computed(() => {
    const backgroundColor = getBackgroundColor(props.data.group)
    const borderColor = getBorderColor(props.data.group)
    
    // Увеличиваем размеры для большего пространства
    const nodeSize = props.selected ? 140 : 130;
    const borderWidth = props.selected ? 4 : 3;
    
    return {
      border: `${borderWidth}px solid ${borderColor}`,
      borderRadius: '50%',
      backgroundColor: backgroundColor,
      cursor: props.data.group === 3 ? 'not-allowed' : 'pointer',
      width: `${nodeSize}px`,
      height: `${nodeSize}px`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      textAlign: 'center',
      padding: '20px',
      fontSize: props.selected ? '15px' : '14px',
      fontWeight: 'bold',
      transition: 'all 0.3s ease',
      position: 'relative',
      overflow: 'hidden',
      boxShadow: props.selected ? '0 10px 30px rgba(0, 0, 0, 0.2)' : '0 5px 15px rgba(0, 0, 0, 0.1)',
      // Увеличиваем z-index для избежания перекрытия
      zIndex: props.selected ? 100 : 10
    }
  })
  
  const tooltipText = computed(() => {
    const status = getStatusLabel(props.data.group)
    return `${props.data.label}\nСтатус: ${status}${props.data.lessonId ? `\nID урока: ${props.data.lessonId}` : ''}`
  })
  
  function getBackgroundColor(group) {
    switch(group) {
      case 0: return '#E8F5E9' // светло-зеленый
      case 1: return '#FFEBEE' // светло-красный
      case 2: return '#FFF8E1' // светло-желтый
      case 3: return '#FAFAFA' // очень светло-серый
      default: return '#FAFAFA'
    }
  }
  
  function getBorderColor(group) {
    switch(group) {
      case 0: return '#4CAF50' // зеленый
      case 1: return '#F44336' // красный
      case 2: return '#FFC107' // желтый
      case 3: return '#BDBDBD' // серый
      default: return '#BDBDBD'
    }
  }
  
  function getStatusLabel(group) {
    switch(group) {
      case 0: return 'Успешно пройден'
      case 1: return 'Неуспешно пройден'
      case 2: return 'Доступен'
      case 3: return 'Недоступен'
      default: return 'Неизвестно'
    }
  }
  
  function onClick() {
    if (props.data.group !== 3) {
      emit('click')
    }
  }
  </script>
  
  <style scoped>
  .custom-node {
    font-family: 'Arial', Georgia, serif;
    position: relative;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  .custom-node:hover {
    transform: scale(1.12);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
    z-index: 1000;
  }
  
  .custom-node:active {
    transform: scale(1.05);
  }
  
  .node-content {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }
  
  .node-label {
    color: #333;
    font-weight: bold;
    word-wrap: break-word;
    overflow-wrap: break-word;
    line-height: 1.4;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 8px;
    max-width: 100%;
  }
  
  /* Индикатор статуса в углу */
  .custom-node::after {
    content: '';
    position: absolute;
    top: 10px;
    right: 10px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background-color: v-bind('props.data.group === 0 ? "#4CAF50" : props.data.group === 1 ? "#F44336" : props.data.group === 2 ? "#FFC107" : "#BDBDBD"');
    border: 2px solid white;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    z-index: 10;
  }
  
  /* Эффект свечения при наведении */
  .custom-node:hover::after {
    transform: scale(1.2);
    box-shadow: 0 0 10px rgba(0,0,0,0.4);
  }
  </style>