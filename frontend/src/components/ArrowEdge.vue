<template>
    <g class="arrow-edge">
      <path
        :d="edgePath"
        class="vue-flow__edge-path"
        :style="edgeStyle"
        :marker-end="markerEnd"
      />
    </g>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  import { getBezierPath } from '@vue-flow/core'
  
  const props = defineProps({
    id: String,
    source: String,
    target: String,
    sourceX: Number,
    sourceY: Number,
    targetX: Number,
    targetY: Number,
    sourcePosition: String,
    targetPosition: String,
    data: Object,
    style: Object,
    markerEnd: String
  })
  
  // Рассчитываем оптимальный путь с минимальным пересечением
  const edgePath = computed(() => {
    const { sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition } = props;
    
    // Вычисляем расстояние между узлами
    const dx = targetX - sourceX;
    const dy = targetY - sourceY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    // Автоматически определяем лучшую кривизну на основе расстояния и угла
    let curvature = 0.25;
    
    // Увеличиваем кривизну для горизонтальных/вертикальных связей
    if (Math.abs(dx) < 100 && Math.abs(dy) > 150) {
      // Вертикальные связи
      curvature = 0.4;
    } else if (Math.abs(dx) > 150 && Math.abs(dy) < 100) {
      // Горизонтальные связи
      curvature = 0.4;
    }
    
    // Учитываем смещение из данных
    const offset = props.data?.offset || 0;
    const curvatureWithOffset = curvature + (offset * 0.02);
    
    // Используем вычисленный путь с адаптивной кривизной
    return getBezierPath({
      sourceX: sourceX,
      sourceY: sourceY,
      sourcePosition: sourcePosition,
      targetX: targetX,
      targetY: targetY,
      targetPosition: targetPosition,
      curvature: curvatureWithOffset
    })
  })
  
  const edgeStyle = computed(() => ({
    ...props.style,
    fill: 'none',
    strokeDasharray: null,
    // Добавляем плавную анимацию
    transition: 'stroke-width 0.2s ease, d 0.3s ease'
  }))
  </script>
  
  <style scoped>
  .arrow-edge {
    transition: all 0.3s ease;
    pointer-events: all;
  }
  
  .vue-flow__edge-path {
    transition: all 0.3s ease;
    stroke: #666;
    stroke-width: 2;
  }
  
  .arrow-edge:hover .vue-flow__edge-path {
    stroke-width: 3 !important;
    stroke: #F4886D !important;
    filter: drop-shadow(0 0 3px rgba(244, 136, 109, 0.3));
  }
  </style>