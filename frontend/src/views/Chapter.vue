<template>
  <div class="chapter">
    <el-page-header @back="$router.push('/')" :title="'返回首页'">
      <template #content>
        <span class="chapter-title">{{ chapterName }}</span>
      </template>
    </el-page-header>

    <!-- 题目列表 -->
    <div class="question-list-card">
      <div class="list-header">
        <div class="list-header-left">
          <span class="question-count">共 {{ questions.length }} 题</span>
          <button class="continue-btn" @click="continueLast" :disabled="lastPosition === null">
            <span class="btn-icon">▶️</span>
            <span>继续上次</span>
          </button>
        </div>
        <div class="filter-tabs">
          <button
            v-for="f in filters"
            :key="f.value"
            class="filter-tab"
            :class="{ active: filter === f.value }"
            @click="filter = f.value"
          >
            {{ f.label }}
            <span v-if="f.count !== undefined" class="filter-count">{{ f.count }}</span>
          </button>
        </div>
      </div>

      <div class="question-grid">
        <div
          v-for="(q, index) in filteredQuestions"
          :key="q.id"
          class="question-item"
          :class="q.status"
          @click="goQuiz(index)"
          :style="{ animationDelay: `${index * 0.02}s` }"
        >
          <span class="q-num">{{ getRealIndex(q) + 1 }}</span>
          <el-icon v-if="q.is_favorite" class="favorite-icon"><Star /></el-icon>
          <span class="q-status-icon">
            <span v-if="q.status === 'correct'" class="status-emoji">✅</span>
            <span v-else-if="q.status === 'wrong'" class="status-emoji">❌</span>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Star } from '@element-plus/icons-vue'
import { getChapterQuestions, getLastPosition } from '../api'

const route = useRoute()
const router = useRouter()
const chapterId = route.params.id
const chapterName = ref('')
const questions = ref([])
const filter = ref('all')
const lastPosition = ref(null)

const filters = computed(() => [
  { value: 'all', label: '全部', count: questions.value.length },
  { value: 'unanswered', label: '未做', count: questions.value.filter(q => q.status === 'unanswered').length },
  { value: 'wrong', label: '错题', count: questions.value.filter(q => q.status === 'wrong').length },
  { value: 'correct', label: '正确', count: questions.value.filter(q => q.status === 'correct').length }
])

const filteredQuestions = computed(() => {
  if (filter.value === 'all') return questions.value
  return questions.value.filter(q => q.status === filter.value)
})

const getRealIndex = (q) => {
  return questions.value.findIndex(item => item.id === q.id)
}

const goQuiz = (filteredIndex) => {
  const q = filteredQuestions.value[filteredIndex]
  const realIndex = questions.value.findIndex(item => item.id === q.id)
  router.push(`/quiz/${chapterId}/${realIndex}`)
}

const continueLast = () => {
  if (lastPosition.value !== null) {
    router.push(`/quiz/${chapterId}/${lastPosition.value}`)
  }
}

onMounted(async () => {
  const { data } = await getChapterQuestions(chapterId)
  questions.value = data.data.questions
  chapterName.value = data.data.chapter_name || `第 ${chapterId} 章`

  try {
    const { data: posData } = await getLastPosition()
    if (posData.data && posData.data.chapter_id == chapterId) {
      lastPosition.value = posData.data.question_index
    }
  } catch (e) {
    // 无记录则忽略
  }
})
</script>

<style scoped>
.chapter {
  padding-bottom: 20px;
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chapter-title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 题目列表卡片 */
.question-list-card {
  margin-top: 20px;
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 107, 157, 0.1);
  flex-wrap: wrap;
  gap: 12px;
}

.list-header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.question-count {
  font-size: 15px;
  color: var(--text-secondary);
  font-weight: 500;
}

.continue-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
}

.continue-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 157, 0.4);
}

.continue-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 12px;
}

/* 筛选标签 */
.filter-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.6);
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.filter-tab:hover {
  border-color: var(--primary-light);
  color: var(--primary);
}

.filter-tab.active {
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.1) 0%, rgba(132, 94, 247, 0.1) 100%);
  border-color: var(--primary);
  color: var(--primary);
}

.filter-count {
  background: rgba(255, 107, 157, 0.15);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

/* 题目网格 */
.question-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(64px, 1fr));
  gap: 12px;
}

.question-item {
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
  border: 2px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.6);
  animation: popIn 0.4s ease backwards;
}

@keyframes popIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.question-item:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-light);
}

.question-item.correct {
  border-color: var(--accent);
  background: linear-gradient(135deg, rgba(32, 201, 151, 0.1) 0%, rgba(150, 242, 215, 0.1) 100%);
}

.question-item.correct:hover {
  box-shadow: 0 8px 25px rgba(32, 201, 151, 0.2);
}

.question-item.wrong {
  border-color: var(--danger);
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 150, 150, 0.1) 100%);
}

.question-item.wrong:hover {
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.2);
}

.q-num {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.q-status-icon {
  position: absolute;
  bottom: 4px;
  right: 4px;
  font-size: 14px;
}

.status-emoji {
  display: block;
  transform: scale(0.9);
}

.favorite-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  color: var(--warning);
  font-size: 14px;
  filter: drop-shadow(0 2px 4px rgba(255, 192, 120, 0.4));
}

/* 响应式 */
@media (max-width: 768px) {
  .list-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-tabs {
    width: 100%;
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 4px;
  }

  .filter-tab {
    white-space: nowrap;
  }

  .question-grid {
    grid-template-columns: repeat(auto-fill, minmax(56px, 1fr));
    gap: 8px;
  }
}
</style>
