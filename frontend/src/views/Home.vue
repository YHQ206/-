<template>
  <div class="home">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <h2>🌸 今天也要加油鸭！</h2>
        <p>坚持刷题，考试轻松过～</p>
      </div>
      <div class="banner-decoration">
        <span class="deco-emoji">📖</span>
        <span class="deco-emoji">✨</span>
        <span class="deco-emoji">🎯</span>
      </div>
    </div>

    <!-- 科目切换 -->
    <div class="subject-tabs">
      <div
        v-for="subject in subjects"
        :key="subject.name"
        class="subject-tab"
        :class="{ active: currentSubject === subject.name }"
        @click="switchSubject(subject.name)"
      >
        <span class="subject-icon">{{ subject.icon }}</span>
        <span class="subject-name">{{ subject.name }}</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">📚</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总题数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon done">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.done }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon accuracy">🎯</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.accuracy }}%</div>
          <div class="stat-label">正确率</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon today">🔥</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.today_count }}</div>
          <div class="stat-label">今日做题</div>
        </div>
      </div>
    </div>

    <!-- 功能卡片 -->
    <div class="feature-grid">
      <div class="feature-card continue" @click="continueLast">
        <div class="feature-icon">▶️</div>
        <div class="feature-info">
          <div class="feature-title">继续上次刷题</div>
          <div class="feature-desc">从上次离开的地方继续</div>
        </div>
        <div class="feature-arrow">→</div>
      </div>
      <div class="feature-card wrong-book" @click="$router.push('/wrong')">
        <div class="feature-icon">📝</div>
        <div class="feature-info">
          <div class="feature-title">错题本</div>
          <div class="feature-desc">复习做错的题目</div>
        </div>
        <div class="feature-arrow">→</div>
      </div>
      <div class="feature-card favorites" @click="$router.push('/favorites')">
        <div class="feature-icon">⭐</div>
        <div class="feature-info">
          <div class="feature-title">收藏夹</div>
          <div class="feature-desc">{{ stats.favorites }} 道题目</div>
        </div>
        <div class="feature-arrow">→</div>
      </div>
      <div class="feature-card random" @click="$router.push('/random')">
        <div class="feature-icon">🎲</div>
        <div class="feature-info">
          <div class="feature-title">随机刷题</div>
          <div class="feature-desc">随机抽取题目练习</div>
        </div>
        <div class="feature-arrow">→</div>
      </div>
    </div>

    <!-- 工具按钮 -->
    <div class="tool-actions">
      <button class="tool-btn import" @click="handleImport" :disabled="importing">
        <span class="btn-icon">📥</span>
        <span class="btn-text">{{ importing ? '导入中...' : '导入题库' }}</span>
      </button>
      <button class="tool-btn clear" @click="confirmClear">
        <span class="btn-icon">🗑️</span>
        <span class="btn-text">清空记录</span>
      </button>
    </div>

    <!-- 章节列表 -->
    <div class="chapter-section">
      <div class="section-header">
        <h3>📖 章节列表</h3>
        <span class="chapter-count">共 {{ chapters.length }} 章</span>
      </div>
      <div class="chapter-list">
        <div
          v-for="(chapter, index) in chapters"
          :key="chapter.id"
          class="chapter-item"
          @click="goChapter(chapter)"
          :style="{ animationDelay: `${index * 0.05}s` }"
        >
          <div class="chapter-left">
            <div class="chapter-number">{{ index + 1 }}</div>
            <div class="chapter-info">
              <div class="chapter-name">{{ chapter.name }}</div>
              <div class="chapter-progress-text">
                {{ chapter.done }}/{{ chapter.total }} 题
                <span v-if="chapter.done === chapter.total && chapter.total > 0" class="complete-badge">✨ 已完成</span>
              </div>
            </div>
          </div>
          <div class="chapter-right">
            <div class="mini-progress">
              <div
                class="mini-progress-bar"
                :style="{
                  width: chapter.total > 0 ? Math.round(chapter.done / chapter.total * 100) + '%' : '0%',
                  background: chapter.done === chapter.total && chapter.total > 0
                    ? 'linear-gradient(90deg, #20C997 0%, #38D9A9 100%)'
                    : 'linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%)'
                }"
              ></div>
            </div>
            <div class="chapter-percent">
              {{ chapter.total > 0 ? Math.round(chapter.done / chapter.total * 100) : 0 }}%
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSubjects, getChapters, getStatsOverview, getLastPosition, clearAllProgress, importQuestions } from '../api'

const router = useRouter()
const currentSubject = ref('习概')
const importing = ref(false)
const subjectId = ref(null)
const chapters = ref([])

const subjects = [
  { name: '习概', icon: '🇨🇳' },
  { name: '马原', icon: '📕' }
]

const stats = ref({
  total: 0,
  done: 0,
  correct: 0,
  wrong: 0,
  favorites: 0,
  accuracy: 0,
  today_count: 0
})

const switchSubject = (name) => {
  currentSubject.value = name
  loadData()
}

const loadData = async () => {
  const { data: subjectsData } = await getSubjects()
  const subject = subjectsData.data.find(s => s.name === currentSubject.value)
  if (subject) {
    subjectId.value = subject.id
    const [chaptersRes, statsRes] = await Promise.all([
      getChapters(subject.id),
      getStatsOverview(subject.id)
    ])
    chapters.value = chaptersRes.data.data
    stats.value = statsRes.data.data
  }
}

const goChapter = (chapter) => {
  router.push(`/chapter/${chapter.id}`)
}

const continueLast = async () => {
  const { data } = await getLastPosition(subjectId.value)
  if (data.data) {
    router.push(`/quiz/${data.data.chapter_id}/${data.data.question_index}`)
  } else {
    ElMessage.info('暂无刷题记录')
  }
}

const handleImport = () => {
  ElMessageBox.confirm(
    '增量更新：只更新变化的题目，保留做题记录\n全部重导：清空所有数据后重新导入',
    '导入题库',
    {
      type: 'info',
      confirmButtonText: '增量更新',
      cancelButtonText: '全部重导',
      distinguishCancelAndClose: true
    }
  ).then(() => {
    doImport('incremental')
  }).catch((action) => {
    if (action === 'cancel') {
      ElMessageBox.confirm(
        '全部重导会清空所有题目和做题记录，确定继续？',
        '确认全部重导',
        { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }
      ).then(() => doImport('full')).catch(() => {})
    }
  })
}

const doImport = async (mode) => {
  importing.value = true
  try {
    const { data } = await importQuestions(mode)
    if (data.code === 0) {
      if (mode === 'incremental') {
        const summary = data.data.map(r => {
          const q = r.questions
          return `${r.subject}：新增 ${q.added}，更新 ${q.updated}，删除 ${q.deleted}，不变 ${q.unchanged}`
        }).join('；')
        ElMessage.success(`增量更新完成！${summary}`)
      } else {
        const summary = data.data.map(r => `${r.subject}：导入 ${r.imported} 题`).join('，')
        ElMessage.success(`全部重导完成！${summary}`)
      }
      loadData()
    } else {
      ElMessage.error(data.message || '导入失败')
    }
  } catch (e) {
    ElMessage.error('导入失败：' + (e.response?.data?.message || e.message))
  } finally {
    importing.value = false
  }
}

const confirmClear = () => {
  ElMessageBox.confirm(
    '确定要清空所有做题记录吗？此操作不可恢复！',
    '警告',
    { type: 'warning' }
  ).then(async () => {
    await clearAllProgress()
    ElMessage.success('已清空所有记录')
    loadData()
  }).catch(() => {})
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.home {
  padding-bottom: 20px;
  animation: fadeInUp 0.6s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #FFB3D0 0%, #B197FC 50%, #96F2D7 100%);
  border-radius: var(--radius-lg);
  padding: 24px 32px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 8px 32px rgba(255, 107, 157, 0.2);
  position: relative;
  overflow: hidden;
}

.welcome-banner::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.banner-content h2 {
  font-size: 24px;
  color: #fff;
  margin-bottom: 8px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.banner-content p {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
}

.banner-decoration {
  display: flex;
  gap: 12px;
}

.deco-emoji {
  font-size: 36px;
  animation: float 3s ease-in-out infinite;
}

.deco-emoji:nth-child(2) {
  animation-delay: 0.5s;
}

.deco-emoji:nth-child(3) {
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* 科目切换 */
.subject-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.subject-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px 24px;
  background: var(--card-bg);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: var(--card-shadow);
}

.subject-tab:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-hover-shadow);
}

.subject-tab.active {
  border-color: var(--primary);
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.1) 0%, rgba(132, 94, 247, 0.1) 100%);
}

.subject-icon {
  font-size: 28px;
}

.subject-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--card-bg);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--card-shadow);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-hover-shadow);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #FFD8B1 0%, #FFC078 100%);
}

.stat-icon.done {
  background: linear-gradient(135deg, #B2F2BB 0%, #69DB7C 100%);
}

.stat-icon.accuracy {
  background: linear-gradient(135deg, #B197FC 0%, #845EF7 100%);
}

.stat-icon.today {
  background: linear-gradient(135deg, #FFB3BA 0%, #FF6B6B 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 功能卡片 */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.feature-card {
  background: var(--card-bg);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--card-shadow);
  border: 2px solid transparent;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-hover-shadow);
  border-color: var(--primary-light);
}

.feature-card:hover .feature-arrow {
  transform: translateX(4px);
  opacity: 1;
}

.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  background: linear-gradient(135deg, #FFF5F7 0%, #FFE6EC 100%);
}

.feature-card.wrong-book .feature-icon {
  background: linear-gradient(135deg, #FFF0F0 0%, #FFD6D6 100%);
}

.feature-card.favorites .feature-icon {
  background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
}

.feature-card.random .feature-icon {
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
}

.feature-info {
  flex: 1;
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.feature-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.feature-arrow {
  font-size: 20px;
  color: var(--primary);
  opacity: 0.5;
  transition: all 0.3s ease;
}

/* 工具按钮 */
.tool-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.tool-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 20px;
  border-radius: var(--radius-md);
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 15px;
  font-weight: 500;
  background: var(--card-bg);
  box-shadow: var(--card-shadow);
}

.tool-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-hover-shadow);
}

.tool-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.tool-btn.import {
  color: var(--warning);
  border-color: var(--warning);
}

.tool-btn.import:hover {
  background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
}

.tool-btn.clear {
  color: var(--danger);
  border-color: var(--danger);
}

.tool-btn.clear:hover {
  background: linear-gradient(135deg, #FFF0F0 0%, #FFD6D6 100%);
}

.btn-icon {
  font-size: 20px;
}

/* 章节列表 */
.chapter-section {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--card-shadow);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 107, 157, 0.1);
}

.section-header h3 {
  font-size: 18px;
  color: var(--text-primary);
  font-weight: 600;
}

.chapter-count {
  font-size: 14px;
  color: var(--text-secondary);
  background: rgba(255, 107, 157, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chapter-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 245, 247, 0.8) 100%);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 107, 157, 0.1);
  animation: slideIn 0.5s ease backwards;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.chapter-item:hover {
  transform: translateX(8px);
  box-shadow: 0 4px 20px rgba(255, 107, 157, 0.15);
  border-color: var(--primary-light);
}

.chapter-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.chapter-number {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}

.chapter-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.chapter-progress-text {
  font-size: 13px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.complete-badge {
  color: var(--accent);
  font-weight: 500;
}

.chapter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mini-progress {
  width: 100px;
  height: 8px;
  background: rgba(255, 107, 157, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.mini-progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
}

.chapter-percent {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
  min-width: 40px;
  text-align: right;
}

/* 暗黑主题特殊样式 */
.theme-dark .welcome-banner {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.3) 0%, rgba(255, 0, 255, 0.3) 100%);
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.theme-dark .banner-content h2 {
  color: #fff;
  text-shadow: 0 2px 10px rgba(0, 212, 255, 0.5);
}

.theme-dark .stat-icon.total {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.3) 0%, rgba(0, 212, 255, 0.1) 100%);
}

.theme-dark .stat-icon.done {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.3) 0%, rgba(0, 255, 136, 0.1) 100%);
}

.theme-dark .stat-icon.accuracy {
  background: linear-gradient(135deg, rgba(255, 0, 255, 0.3) 0%, rgba(255, 0, 255, 0.1) 100%);
}

.theme-dark .stat-icon.today {
  background: linear-gradient(135deg, rgba(255, 68, 68, 0.3) 0%, rgba(255, 68, 68, 0.1) 100%);
}

.theme-dark .feature-card:hover {
  border-color: var(--primary);
  box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
}

.theme-dark .chapter-item:hover {
  background: rgba(0, 212, 255, 0.05);
}

/* 玻璃主题特殊样式 */
.theme-glass .welcome-banner {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.4) 0%, rgba(236, 72, 153, 0.4) 100%);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.theme-glass .feature-card {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.theme-glass .stat-card {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.theme-glass .chapter-section {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.theme-glass .chapter-item {
  background: rgba(255, 255, 255, 0.1);
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }

  .welcome-banner {
    padding: 20px;
  }

  .banner-content h2 {
    font-size: 20px;
  }

  .deco-emoji {
    font-size: 28px;
  }
}
</style>
