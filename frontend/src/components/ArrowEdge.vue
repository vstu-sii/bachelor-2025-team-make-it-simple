<template>
  <g class="arrow-edge">
    <!-- Основная линия -->
    <path
      :d="edgePath"
      class="vue-flow__edge-path"
      :style="edgeStyle"
    />
    
    <!-- Стрелка на конце -->
    <polygon
      :points="arrowPoints"
      class="arrow-head"
      :style="arrowStyle"
    />
  </g>
</template>

<script setup>
import { computed } from 'vue'

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

// Рассчитываем путь для линии с плавными кривыми
const edgePath = computed(() => {
  const { sourceX, sourceY, targetX, targetY, data } = props
  
  // Проверяем валидность координат
  if (isNaN(sourceX) || isNaN(sourceY) || isNaN(targetX) || isNaN(targetY)) {
    console.error('Invalid coordinates for edge:', { sourceX, sourceY, targetX, targetY })
    return 'M0,0 L0,0'
  }
  
  // Учитываем смещение для параллельных связей
  const offset = data?.offset || 0
  
  // Для обратных связей создаем красивую изогнутую линию
  if (data?.edgeType === 'curved') {
    const midX = (sourceX + targetX) / 2
    const midY = (sourceY + targetY) / 2
    
    // Рассчитываем вектор направления
    const dx = targetX - sourceX
    const dy = targetY - sourceY
    
    // Длина линии
    const length = Math.sqrt(dx * dx + dy * dy)
    
    // Нормаль к вектору (перпендикуляр)
    const nx = -dy / length
    const ny = dx / length
    
    // Смещение для красивой кривой
    const curveOffset = Math.min(length * 0.3, 100) + offset * 2
    
    const controlX1 = sourceX + dx * 0.5 + nx * curveOffset
    const controlY1 = sourceY + dy * 0.5 + ny * curveOffset
    
    const controlX2 = targetX - dx * 0.5 + nx * curveOffset
    const controlY2 = targetY - dy * 0.5 + ny * curveOffset
    
    // Плавная кубическая кривая Безье
    return `M${sourceX},${sourceY} C${controlX1},${controlY1} ${controlX2},${controlY2} ${targetX},${targetY}`
  } 
  // Для параллельных связей со смещением
  else if (offset !== 0) {
    const dx = targetX - sourceX
    const dy = targetY - sourceY
    const length = Math.sqrt(dx * dx + dy * dy)
    
    // Нормаль к вектору
    const nx = -dy / length
    const ny = dx / length
    
    const offsetX = offset * nx
    const offsetY = offset * ny
    
    // Небольшая кривизна для смещенных линий
    const curveFactor = Math.min(Math.abs(offset) * 0.01, 0.2)
    
    const controlX1 = sourceX + dx * 0.3 + offsetX * curveFactor
    const controlY1 = sourceY + dy * 0.3 + offsetY * curveFactor
    
    const controlX2 = targetX - dx * 0.3 + offsetX * curveFactor
    const controlY2 = targetY - dy * 0.3 + offsetY * curveFactor
    
    return `M${sourceX},${sourceY} C${controlX1},${controlY1} ${controlX2},${controlY2} ${targetX + offsetX},${targetY + offsetY}`
  } 
  // Прямая линия с небольшим изгибом для красоты
  else {
    const dx = targetX - sourceX
    const dy = targetY - sourceY
    
    // Минимальный изгиб для визуальной привлекательности
    const curveFactor = 0.1
    
    const controlX1 = sourceX + dx * 0.3
    const controlY1 = sourceY + dy * 0.3
    
    const controlX2 = targetX - dx * 0.3
    const controlY2 = targetY - dy * 0.3
    
    return `M${sourceX},${sourceY} C${controlX1},${controlY1} ${controlX2},${controlY2} ${targetX},${targetY}`
  }
})

// Рассчитываем плавную стрелку
const arrowPoints = computed(() => {
  const { sourceX, sourceY, targetX, targetY, data } = props
  
  // Проверяем валидность координат
  if (isNaN(sourceX) || isNaN(sourceY) || isNaN(targetX) || isNaN(targetY)) {
    return '0,0 0,0 0,0'
  }
  
  // Учитываем смещение для позиции стрелки
  const offset = data?.offset || 0
  let endX = targetX
  let endY = targetY
  
  if (offset !== 0) {
    const dx = targetX - sourceX
    const dy = targetY - sourceY
    const length = Math.sqrt(dx * dx + dy * dy)
    
    if (length > 0) {
      const nx = -dy / length
      const ny = dx / length
      
      endX = targetX + offset * nx
      endY = targetY + offset * ny
    }
  }
  
  // Рассчитываем направление для стрелки на конце кривой
  let angle
  
  if (data?.edgeType === 'curved') {
    // Для кривых вычисляем угол касательной в конечной точке
    const dx = targetX - sourceX
    const dy = targetY - sourceY
    const length = Math.sqrt(dx * dx + dy * dy)
    
    if (length > 0) {
      const nx = -dy / length
      const ny = dx / length
      const curveOffset = Math.min(length * 0.3, 100) + offset * 2
      
      // Угол касательной к кривой в конечной точке
      const tangentX = dx * 0.5 - nx * curveOffset * 2
      const tangentY = dy * 0.5 - ny * curveOffset * 2
      angle = Math.atan2(tangentY, tangentX)
    } else {
      angle = Math.atan2(endY - sourceY, endX - sourceX)
    }
  } else {
    // Для прямых линий используем прямой угол
    angle = Math.atan2(endY - sourceY, endX - sourceX)
  }
  
  // Размеры стрелки (пропорциональные толщине линии)
  const arrowLength = 14
  const arrowWidth = 7
  
  // Точка кончика стрелки (отодвинута от конца)
  const tipDistance = arrowLength * 1.2
  const tipX = endX - tipDistance * Math.cos(angle)
  const tipY = endY - tipDistance * Math.sin(angle)
  
  // Базовые точки стрелки с плавным изгибом
  const leftX = tipX + arrowWidth * Math.cos(angle + Math.PI / 2)
  const leftY = tipY + arrowWidth * Math.sin(angle + Math.PI / 2)
  
  const rightX = tipX + arrowWidth * Math.cos(angle - Math.PI / 2)
  const rightY = tipY + arrowWidth * Math.sin(angle - Math.PI / 2)
  
  // Возвращаем точки для полигона (стрелка с закругленными краями)
  return `${endX},${endY} ${leftX},${leftY} ${rightX},${rightY}`
})

const edgeStyle = computed(() => ({
  fill: 'none',
  stroke: '#666',
  strokeWidth: 2,
  ...props.style,
  transition: 'stroke-width 0.3s ease, stroke 0.3s ease, d 0.5s cubic-bezier(0.4, 0, 0.2, 1)'
}))

const arrowStyle = computed(() => ({
  fill: '#666',
  stroke: '#666',
  strokeWidth: 1,
  transition: 'fill 0.3s ease, stroke 0.3s ease, transform 0.3s ease'
}))
</script>

<style scoped>
.arrow-edge {
  transition: all 0.3s ease;
  pointer-events: all;
}

.vue-flow__edge-path {
  transition: stroke 0.3s ease, stroke-width 0.3s ease, d 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.vue-flow__edge-path:hover {
  stroke-width: 3 !important;
  stroke: #F4886D !important;
}

.arrow-head {
  transition: fill 0.3s ease, stroke 0.3s ease, transform 0.3s ease;
}

.arrow-edge:hover .arrow-head {
  fill: #F4886D !important;
  stroke: #F4886D !important;
  transform: scale(1.1);
}
</style>