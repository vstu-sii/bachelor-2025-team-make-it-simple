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
        <!-- SVG defs для стрелок -->
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
        
        <template #node-custom="props">
          <CustomNode :data="props.data" :selected="selectedNodeId === props.id" />
        </template>
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
  </div>
</template>

<script setup>
  import { ref, onMounted, watch, nextTick } from 'vue'
  import { useRouter } from 'vue-router'
  import { VueFlow } from '@vue-flow/core'
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
  
  // Улучшенный алгоритм размещения узлов
  function calculateOptimalPositions(nodes, edges) {
    const positionedNodes = JSON.parse(JSON.stringify(nodes))
    
    // Проверяем, есть ли уже позиции
    const hasPositions = positionedNodes.every(node => 
      node.position && 
      typeof node.position.x === 'number' && 
      !isNaN(node.position.x) &&
      typeof node.position.y === 'number' && 
      !isNaN(node.position.y)
    )
    
    if (hasPositions) {
      return positionedNodes
    }
    
    // Строим карту зависимостей
    const dependencies = {}
    const reverseDependencies = {}
    
    // Инициализация
    positionedNodes.forEach(node => {
      dependencies[node.id] = []
      reverseDependencies[node.id] = []
    })
    
    // Строим граф зависимостей
    edges.forEach(edge => {
      const sourceId = edge.source || edge.from
      const targetId = edge.target || edge.to
      
      if (dependencies[sourceId] && reverseDependencies[targetId]) {
        dependencies[sourceId].push(targetId)
        reverseDependencies[targetId].push(sourceId)
      }
    })
    
    // Находим корневые узлы (без зависимостей)
    const rootNodes = positionedNodes.filter(node => 
      dependencies[node.id] && 
      dependencies[node.id].length === 0
    )
    
    // Если есть корневые узлы, размещаем их сверху
    if (rootNodes.length > 0) {
      const levels = {}
      const visited = new Set()
      
      // Функция для определения уровня узла
      function getLevel(nodeId, depth = 0) {
        if (visited.has(nodeId)) return depth
        visited.add(nodeId)
        
        if (!reverseDependencies[nodeId] || reverseDependencies[nodeId].length === 0) {
          levels[nodeId] = depth
          return depth
        }
        
        const parentLevels = reverseDependencies[nodeId].map(parentId => 
          getLevel(parentId, depth + 1)
        )
        const maxParentLevel = Math.max(...parentLevels)
        levels[nodeId] = maxParentLevel
        return maxParentLevel
      }
      
      // Определяем уровни для всех узлов
      positionedNodes.forEach(node => getLevel(node.id))
      
      // Группируем узлы по уровням
      const nodesByLevel = {}
      positionedNodes.forEach(node => {
        const level = levels[node.id] || 0
        if (!nodesByLevel[level]) nodesByLevel[level] = []
        nodesByLevel[level].push(node)
      })
      
      // Размещаем узлы по уровням
      const levelSpacing = 180
      const nodeSpacing = 160
      const startX = 100
      const startY = 100
      
      Object.keys(nodesByLevel).sort((a, b) => a - b).forEach((level, levelIndex) => {
        const levelNodes = nodesByLevel[level]
        const y = startY + levelIndex * levelSpacing
        
        levelNodes.forEach((node, nodeIndex) => {
          const totalNodesInLevel = levelNodes.length
          const x = startX + nodeIndex * nodeSpacing
          
          // Центрируем узлы на уровне
          const totalWidth = (totalNodesInLevel - 1) * nodeSpacing
          const centeredX = x + (400 - startX - totalWidth / 2) - nodeSpacing / 2
          
          node.position = {
            x: Math.max(50, Math.min(750, centeredX)),
            y: Math.max(50, Math.min(550, y))
          }
        })
      })
    } else {
      // Простая сетка для узлов без четкой структуры
      const gridCols = 3
      const nodeSpacingX = 200
      const nodeSpacingY = 150
      const startX = 100
      const startY = 100
      
      positionedNodes.forEach((node, index) => {
        const row = Math.floor(index / gridCols)
        const col = index % gridCols
        
        node.position = {
          x: startX + col * nodeSpacingX,
          y: startY + row * nodeSpacingY
        }
      })
    }
    
    return positionedNodes
  }
  
  // Создание улучшенных ребер
  function createOptimizedEdges(edges, nodes) {
    const edgeElements = []
    
    // Группируем связи по источникам
    const connectionsBySource = {}
    
    edges.forEach(edge => {
      const sourceId = edge.source || edge.from
      const targetId = edge.target || edge.to
      
      if (!connectionsBySource[sourceId]) connectionsBySource[sourceId] = []
      connectionsBySource[sourceId].push({ ...edge, targetId })
    })
    
    edges.forEach(edge => {
      const sourceId = edge.source || edge.from
      const targetId = edge.target || edge.to
      
      // Проверяем, существуют ли узлы
      const sourceNode = nodes.find(n => n.id === sourceId)
      const targetNode = nodes.find(n => n.id === targetId)
      
      if (!sourceNode || !targetNode) {
        console.warn(`Edge references non-existent node: ${sourceId} -> ${targetId}`)
        return
      }
      
      // Проверяем, существует ли обратное ребро
      const hasReverseEdge = edges.some(e => 
        (e.source === targetId && e.target === sourceId) ||
        (e.from === targetId && e.to === sourceId)
      )
      
      // Рассчитываем смещение для параллельных связей
      let offset = 0
      const sourceEdges = connectionsBySource[sourceId] || []
      if (sourceEdges.length > 1) {
        const index = sourceEdges.findIndex(e => 
          (e.source === sourceId && e.target === targetId) ||
          (e.from === sourceId && e.to === targetId)
        )
        offset = (index - (sourceEdges.length - 1) / 2) * 12
      }
      
      edgeElements.push({
        id: edge.id || `e${sourceId}-${targetId}`,
        source: sourceId,
        target: targetId,
        type: 'custom',
        style: {
          stroke: '#666',
          strokeWidth: 2,
          transition: 'all 0.3s ease'
        },
        data: {
          label: edge.label || '',
          offset: offset,
          edgeType: hasReverseEdge ? 'curved' : 'normal',
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
      console.warn('Нет данных графа для отображения', graphData)
      return elements
    }
  
    console.log('Подготовка графа:', {
      nodesCount: graphData.nodes?.length,
      edgesCount: graphData.edges?.length
    })
  
    // Улучшенное расположение узлов
    const positionedNodes = calculateOptimalPositions(graphData.nodes, graphData.edges)
  
    // Создаем узлы
    positionedNodes.forEach(node => {
      const group = node.group || 3
      const label = node.label || node.data?.label || `Урок ${node.id}`
      
      elements.push({
        id: String(node.id),
        type: 'custom',
        position: {
          x: Math.max(50, Math.min(750, node.position?.x || 100)),
          y: Math.max(50, Math.min(550, node.position?.y || 100))
        },
        data: {
          label: label,
          group: group,
          lessonId: node.data?.lesson_id || node.lessonId,
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
  function onNodeClick(event) {
    console.log('Клик по узлу (event):', event);
    
    const node = event.node;
    
    if (!node || !node.data || !node.data.isClickable) {
        console.log('Узел не кликабельный или отсутствует');
        return;
    }
  
    selectedNodeId.value = node.id;
    
    const lessonId = node.data.lessonId;
    
    if (lessonId) {
        const queryParams = {
        courseId: props.courseId
        };
        
        if (props.studentId) {
        queryParams.studentId = props.studentId;
        }
        
        console.log('Переход к уроку:', { lessonId, queryParams });
        
        router.push({
        path: `/lesson/${lessonId}`,
        query: queryParams
        });
    }
    
    emit('node-click', { node, lessonId });
    
    setTimeout(() => {
        selectedNodeId.value = null;
    }, 2000);
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
      console.log('Данные графа обновлены')
      nextTick(() => {
        elements.value = prepareGraphElements(newData)
      })
    }
  }, { deep: true })
  </script>

<style scoped>
.course-graph-container {
  width: 100%;
  height: 600px;
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