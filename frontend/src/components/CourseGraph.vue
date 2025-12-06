<template>
    <div class="course-graph-container">
      <!-- Контейнер для графа -->
      <div class="vue-flow-container" ref="vueFlowContainer">
        <VueFlow
          v-model="elements"
          :nodes-draggable="true"
          :nodes-connectable="false"
          :zoom-on-scroll="true"
          :zoom-on-pinch="true"
          :pan-on-scroll="true"
          :pan-on-scroll-speed="1"
          :max-zoom="2"
          :min-zoom="0.2"
          :fit-view-on-init="true"
          :zoom-on-double-click="false"
          @node-click="onNodeClick"
          @nodes-initialized="onNodesInitialized"
          @pane-ready="onPaneReady"
        >
          <template #node-custom="props">
            <CustomNode :data="props.data" :selected="selectedNodeId === props.id" />
          </template>
          
          <template #edge-custom="edgeProps">
            <ArrowEdge 
              :id="edgeProps.id" 
              :source="edgeProps.source" 
              :target="edgeProps.target" 
              :sourceX="edgeProps.sourceX" 
              :sourceY="edgeProps.sourceY" 
              :targetX="edgeProps.targetX" 
              :targetY="edgeProps.targetY" 
              :sourcePosition="edgeProps.sourcePosition" 
              :targetPosition="edgeProps.targetPosition" 
              :data="edgeProps.data" 
              :style="edgeProps.style" 
              :marker-end="edgeProps.markerEnd" 
            />
          </template>
          
          <!-- Убираем Background и Controls из шаблона -->
        </VueFlow>
      </div>
  
      <!-- Легенда графа -->
      <div class="legend">
        <div class="legend-item">
          <div class="legend-color" style="background-color: #4CAF50;"></div>
          <span>Успешно пройден</span>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #F44336;"></div>
          <span>Неуспешно пройден</span>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #FFC107;"></div>
          <span>Доступен</span>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #9E9E9E;"></div>
          <span>Недоступен</span>
        </div>
      </div>
      
      <!-- Кнопка пересчета позиций -->
      <div class="controls">
        <button @click="recalculatePositions" class="recalculate-btn">
          <span class="icon">↻</span>
          Пересчитать позиции
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch, nextTick } from 'vue'
  import { useRouter } from 'vue-router'
  import { VueFlow, MarkerType } from '@vue-flow/core'
  import '@vue-flow/core/dist/style.css'
  import '@vue-flow/core/dist/theme-default.css'
  import CustomNode from './CustomNode.vue'
  import ArrowEdge from './ArrowEdge.vue'
  
  const props = defineProps({
    graphData: {
      type: Object,
      default: () => ({ nodes: [], edges: [] })
    },
    studentId: {
      type: Number,
      default: null
    },
    courseId: {
      type: Number,
      required: true
    }
  })
  
  const emit = defineEmits(['node-click'])
  const router = useRouter()
  const vueFlowContainer = ref(null)
  const elements = ref([])
  const selectedNodeId = ref(null)
  
  // Оптимизированный алгоритм размещения узлов
  function calculateOptimalPositions(nodes, edges) {
    const positionedNodes = JSON.parse(JSON.stringify(nodes))
    
    // Если позиции уже заданы, используем их, но проверяем на пересечения
    if (positionedNodes.every(node => node.position && node.position.x && node.position.y)) {
      return adjustPositionsForOverlap(positionedNodes)
    }
    
    // Создаем иерархическую структуру на основе графа
    const { levels, adjacencyMap } = analyzeGraphStructure(positionedNodes, edges)
    
    // Рассчитываем позиции для каждого уровня
    const levelPositions = {}
    const nodeSpacing = 180  // Увеличиваем расстояние между узлами
    const levelSpacing = 250 // Увеличиваем расстояние между уровнями
    const centerX = 400
    
    levels.forEach((levelNodes, levelIndex) => {
      const y = 100 + levelIndex * levelSpacing
      const totalNodes = levelNodes.length
      
      // Распределяем узлы равномерно по горизонтали
      levelNodes.forEach((nodeId, nodeIndex) => {
        let x
        if (totalNodes === 1) {
          x = centerX
        } else {
          const startX = centerX - ((totalNodes - 1) * nodeSpacing) / 2
          x = startX + nodeIndex * nodeSpacing
        }
        
        levelPositions[nodeId] = { x, y }
      })
    })
    
    // Настраиваем позиции для оставшихся узлов
    const allNodeIds = new Set(positionedNodes.map(n => n.id))
    const positionedNodeIds = new Set(Object.keys(levelPositions))
    const unpositionedNodeIds = [...allNodeIds].filter(id => !positionedNodeIds.has(id))
    
    // Размещаем оставшиеся узлы
    if (unpositionedNodeIds.length > 0) {
      const extraLevelIndex = levels.length
      const y = 100 + extraLevelIndex * levelSpacing
      
      unpositionedNodeIds.forEach((nodeId, index) => {
        const x = centerX - ((unpositionedNodeIds.length - 1) * nodeSpacing) / 2 + index * nodeSpacing
        levelPositions[nodeId] = { x, y }
      })
    }
    
    // Применяем позиции к узлам
    positionedNodes.forEach(node => {
      if (levelPositions[node.id]) {
        node.position = levelPositions[node.id]
      } else {
        // Запасной вариант с случайным размещением
        node.position = { 
          x: 100 + Math.random() * 600, 
          y: 100 + Math.random() * 400 
        }
      }
    })
    
    // Финальная проверка и корректировка пересечений
    return adjustPositionsForOverlap(positionedNodes)
  }
  
  // Анализ структуры графа для иерархического размещения
  function analyzeGraphStructure(nodes, edges) {
    const adjacencyMap = {}
    const incomingMap = {}
    const outgoingMap = {}
    
    // Инициализация
    nodes.forEach(node => {
      adjacencyMap[node.id] = { id: node.id, incoming: [], outgoing: [] }
      incomingMap[node.id] = 0
      outgoingMap[node.id] = 0
    })
    
    // Строим связи
    edges.forEach(edge => {
      const sourceId = edge.source || edge.from
      const targetId = edge.target || edge.to
      
      if (adjacencyMap[sourceId] && adjacencyMap[targetId]) {
        adjacencyMap[sourceId].outgoing.push(targetId)
        adjacencyMap[targetId].incoming.push(sourceId)
        incomingMap[targetId]++
        outgoingMap[sourceId]++
      }
    })
    
    // Определяем уровни с использованием алгоритма топологической сортировки
    const levels = []
    const visited = new Set()
    
    // Находим корневые узлы (без входящих связей)
    let currentLevel = Object.keys(adjacencyMap).filter(
      nodeId => incomingMap[nodeId] === 0
    )
    
    while (currentLevel.length > 0) {
      levels.push([...currentLevel])
      currentLevel.forEach(nodeId => visited.add(nodeId))
      
      // Следующий уровень - все узлы, все предки которых посещены
      const nextLevel = new Set()
      
      currentLevel.forEach(nodeId => {
        adjacencyMap[nodeId].outgoing.forEach(childId => {
          if (!visited.has(childId)) {
            const allParentsVisited = adjacencyMap[childId].incoming.every(
              parentId => visited.has(parentId)
            )
            if (allParentsVisited) {
              nextLevel.add(childId)
            }
          }
        })
      })
      
      currentLevel = Array.from(nextLevel)
    }
    
    // Добавляем оставшиеся узлы (например, в циклах)
    const remainingNodes = Object.keys(adjacencyMap).filter(nodeId => !visited.has(nodeId))
    if (remainingNodes.length > 0) {
      levels.push(remainingNodes)
    }
    
    return { levels, adjacencyMap }
  }
  
  // Корректировка позиций для избежания пересечений
  function adjustPositionsForOverlap(nodes) {
    const adjustedNodes = JSON.parse(JSON.stringify(nodes))
    const nodeRadius = 65  // Радиус узла (половина ширины)
    const minDistance = nodeRadius * 2.5  // Минимальное расстояние между центрами
    
    let hasOverlap = true
    let iterations = 0
    const maxIterations = 50
    
    while (hasOverlap && iterations < maxIterations) {
      hasOverlap = false
      iterations++
      
      for (let i = 0; i < adjustedNodes.length; i++) {
        for (let j = i + 1; j < adjustedNodes.length; j++) {
          const nodeA = adjustedNodes[i]
          const nodeB = adjustedNodes[j]
          
          const dx = nodeA.position.x - nodeB.position.x
          const dy = nodeA.position.y - nodeB.position.y
          const distance = Math.sqrt(dx * dx + dy * dy)
          
          if (distance < minDistance) {
            hasOverlap = true
            
            // Вычисляем вектор отталкивания
            const force = (minDistance - distance) / 2
            const angle = Math.atan2(dy, dx)
            
            // Нормализуем вектор
            const nx = dx / distance
            const ny = dy / distance
            
            // Раздвигаем узлы
            nodeA.position.x += nx * force
            nodeA.position.y += ny * force
            nodeB.position.x -= nx * force
            nodeB.position.y -= ny * force
          }
        }
      }
      
      // Ограничиваем позиции в пределах разумных границ
      adjustedNodes.forEach(node => {
        node.position.x = Math.max(50, Math.min(750, node.position.x))
        node.position.y = Math.max(50, Math.min(550, node.position.y))
      })
    }
    
    return adjustedNodes
  }
  
  // Создание оптимизированных ребер
  function createOptimizedEdges(edges, nodes) {
    const edgeElements = []
    
    // Группируем связи по источникам и целям
    const connectionsBySource = {}
    const connectionsByTarget = {}
    
    edges.forEach(edge => {
      const sourceId = edge.source || edge.from
      const targetId = edge.target || edge.to
      
      if (!connectionsBySource[sourceId]) connectionsBySource[sourceId] = []
      if (!connectionsByTarget[targetId]) connectionsByTarget[targetId] = []
      
      connectionsBySource[sourceId].push({ ...edge, targetId })
      connectionsByTarget[targetId].push({ ...edge, sourceId })
    })
    
    // Создаем ребра с учетом смещений для параллельных связей
    edges.forEach(edge => {
      const sourceId = edge.source || edge.from
      const targetId = edge.target || edge.to
      
      // Определяем тип связи для лучшего рендеринга
      let edgeType = 'normal'
      const sourceEdges = connectionsBySource[sourceId] || []
      const targetEdges = connectionsByTarget[targetId] || []
      
      // Если есть обратная связь, делаем её изогнутой
      const hasReverseEdge = edges.some(e => 
        (e.source === targetId && e.target === sourceId) ||
        (e.from === targetId && e.to === sourceId)
      )
      
      if (hasReverseEdge) {
        edgeType = 'curved'
      }
      
      // Рассчитываем смещение для параллельных связей
      let offset = 0
      if (sourceEdges.length > 1) {
        const index = sourceEdges.findIndex(e => 
          (e.source === sourceId && e.target === targetId) ||
          (e.from === sourceId && e.to === targetId)
        )
        offset = (index - (sourceEdges.length - 1) / 2) * 15
      }
      
      // Создаем элемент ребра
      edgeElements.push({
        id: edge.id || `e${sourceId}-${targetId}`,
        source: sourceId,
        target: targetId,
        type: 'custom',
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: '#666'
        },
        style: {
          stroke: '#666',
          strokeWidth: 2,
          strokeDasharray: null,
          transition: 'all 0.3s ease'
        },
        data: {
          label: edge.label || '',
          offset: offset,
          edgeType: edgeType,
          originalEdge: edge
        }
      })
    })
    
    return edgeElements
  }
  
  // Преобразование данных графа в формат Vue Flow
  function prepareGraphElements(graphData) {
    const elements = []
    
    if (!graphData || !graphData.nodes || !graphData.edges) {
      console.warn('Нет данных графа для отображения')
      return elements
    }
  
    // Улучшенное расположение узлов
    const positionedNodes = calculateOptimalPositions(graphData.nodes, graphData.edges)
  
    // Создаем узлы
    positionedNodes.forEach(node => {
      const group = node.group || 3
      
      elements.push({
        id: node.id,
        type: 'custom',
        position: node.position,
        data: {
          label: node.label || `Урок ${node.id}`,
          group: group,
          lessonId: node.data?.lesson_id,
          isClickable: group === 0 || group === 1 || group === 2
        }
      })
    })
  
    // Создаем связи
    const edgeElements = createOptimizedEdges(graphData.edges, positionedNodes)
    elements.push(...edgeElements)
  
    return elements
  }
  
  // Обработка клика на узел
  function onNodeClick(event, node) {
    if (!node.data.isClickable) {
      return
    }
  
    selectedNodeId.value = node.id
    
    const lessonId = node.data.lessonId
    
    if (lessonId) {
      router.push(`/lesson/${lessonId}?courseId=${props.courseId}&studentId=${props.studentId}`)
    } else {
      alert(`Узел: ${node.data.label}\nСтатус: ${getStatusLabel(node.data.group)}`)
    }
    
    emit('node-click', { node, lessonId })
    
    // Сбрасываем выделение через 2 секунды
    setTimeout(() => {
      selectedNodeId.value = null
    }, 2000)
  }
  
  function getStatusLabel(group) {
    switch(group) {
      case 0: return 'Успешно пройден'
      case 1: return 'Неуспешно пройден'
      case 2: return 'Доступен для изучения'
      case 3: return 'Недоступен'
      default: return 'Неизвестно'
    }
  }
  
  // Пересчет позиций
  function recalculatePositions() {
    if (props.graphData) {
      elements.value = prepareGraphElements(props.graphData)
    }
  }
  
  // Обработчики событий Vue Flow
  function onNodesInitialized() {
    console.log('Nodes initialized')
  }
  
  function onPaneReady() {
    console.log('Pane ready')
  }
  
  // Инициализация графа
  onMounted(() => {
    if (props.graphData) {
      elements.value = prepareGraphElements(props.graphData)
    }
  })
  
  // Реактивность при изменении данных графа
  watch(() => props.graphData, (newData) => {
    if (newData) {
      nextTick(() => {
        elements.value = prepareGraphElements(newData)
      })
    }
  }, { deep: true })
  </script>
  
  <style scoped>
  .course-graph-container {
    width: 100%;
    height: 700px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .vue-flow-container {
    width: 100%;
    height: 550px;
    border: 2px solid #F4886D;
    border-radius: 15px;
    background-color: white;
    overflow: hidden;
    position: relative;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }
  
  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
    padding: 15px;
    background-color: #fedac4;
    border-radius: 10px;
    border: 1px solid #F4886D;
  }
  
  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Arial', Georgia, serif;
    color: #592012;
    font-size: 14px;
    font-weight: 500;
  }
  
  .legend-color {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  
  .controls {
    display: flex;
    justify-content: center;
    margin-top: 10px;
  }
  
  .recalculate-btn {
    background: #F4886D;
    color: #592012;
    border: none;
    border-radius: 10px;
    padding: 12px 25px;
    cursor: pointer;
    font-family: 'Arial', Georgia, serif;
    font-weight: bold;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    box-shadow: 0 4px 10px rgba(244, 136, 109, 0.2);
  }
  
  .recalculate-btn:hover {
    background: #E0785D;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(244, 136, 109, 0.3);
  }
  
  .recalculate-btn .icon {
    font-size: 18px;
    font-weight: bold;
  }
  
  /* Стили для Vue Flow */
  :deep(.vue-flow__node) {
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  :deep(.vue-flow__node:hover) {
    z-index: 1000 !important;
  }
  
  :deep(.vue-flow__edge) {
    z-index: 1;
  }
  
  :deep(.vue-flow__controls) {
    background-color: white;
    border: 1px solid #F4886D;
    border-radius: 8px;
    padding: 5px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  :deep(.vue-flow__controls-button) {
    background-color: #fbb599;
    border: 1px solid #F4886D;
    transition: all 0.2s ease;
  }
  
  :deep(.vue-flow__controls-button:hover) {
    background-color: #F4886D;
    transform: scale(1.05);
  }
  
  :deep(.vue-flow__controls-button svg) {
    fill: #592012;
  }
  
  /* Адаптивность */
  @media (max-width: 768px) {
    .course-graph-container {
      height: 600px;
    }
    
    .vue-flow-container {
      height: 450px;
    }
    
    .legend {
      flex-direction: column;
      align-items: center;
      gap: 10px;
    }
    
    .recalculate-btn {
      padding: 10px 20px;
      font-size: 14px;
    }
  }
  
  @media (max-width: 480px) {
    .course-graph-container {
      height: 500px;
    }
    
    .vue-flow-container {
      height: 350px;
    }
  }
  </style>