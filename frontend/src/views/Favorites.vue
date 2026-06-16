<template>
  <div class="favorites">
    <el-page-header @back="$router.push('/')" title="返回首页">
      <template #content>
        <span class="page-title">收藏夹</span>
      </template>
    </el-page-header>

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

    <!-- 收藏列表 -->
    <div v-if="questions.length > 0" class="favorites-list">
      <div
        v-for="(q, index) in questions"
        :key="q.id"
        class="fav-item"
        :style="{ animationDelay: `${index * 0.05}s` }"
      >
        <div class="question-header">
          <span class="item-index">{{ index + 1 }}</span>
          <span class="type-tag" :class="q.type">{{ getTypeText(q.type) }}</span>
          <span v-if="q.status === 'correct'" class="status-tag correct">✅ 已答对</span>
          <span v-else-if="q.status === 'wrong'" class="status-tag wrong">❌ 答错</span>
          <button class="remove-btn" @click="removeFav(q)">
            <span class="star-icon">⭐</span>
            <span>取消收藏</span>
          </button>
        </div>
        <div class="question-content">{{ q.content }}</div>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">⭐</div>
      <div class="empty-text">暂无收藏</div>
      <div class="empty-desc">做题时点击收藏按钮，题目就会出现在这里</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSubjects, getFavorites, removeFavorite } from '../api'

const currentSubject = ref('习概')
const subjectId = ref(null)
const questions = ref([])

const subjects = [
  { name: '习概', icon: '🇨🇳' },
  { name: '马原', icon: '📕' }
]

const switchSubject = (name) => {
  currentSubject.value = name
  loadData()
}

const loadData = async () => {
  const { data: subjectsData } = await getSubjects()
  const subject = subjectsData.data.find(s => s.name === currentSubject.value)
  if (subject) {
    subjectId.value = subject.id
    const { data } = await getFavorites(subject.id)
    questions.value = data.data
  }
}

const getTypeText = (type) => {
  const map = { single: '单选', multiple: '多选', blank: '填空', judge: '判断' }
  return map[type] || ''
}

const removeFav = async (q) => {
  await removeFavorite(q.id)
  ElMessage.success('已取消收藏')
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.favorites {
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

.page-title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 科目切换 */
.subject-tabs {
  display: flex;
  gap: 12px;
  margin: 20px 0;
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

/* 收藏列表 */
.favorites-list {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(255, 255, 255, 0.6);
  overflow: hidden;
}

.fav-item {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
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

.fav-item:hover {
  background: rgba(255, 107, 157, 0.05);
}

.fav-item:last-child {
  border-bottom: none;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.item-index {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-light) 0%, var(--secondary-light) 100%);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.type-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.type-tag.single {
  background: rgba(255, 107, 157, 0.1);
  color: var(--primary);
}

.type-tag.multiple {
  background: rgba(32, 201, 151, 0.1);
  color: var(--accent);
}

.type-tag.blank {
  background: rgba(255, 192, 120, 0.1);
  color: #F57C00;
}

.type-tag.judge {
  background: rgba(132, 94, 247, 0.1);
  color: var(--secondary);
}

.status-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-tag.correct {
  background: rgba(32, 201, 151, 0.1);
  color: #388E3C;
}

.status-tag.wrong {
  background: rgba(255, 107, 107, 0.1);
  color: #D32F2F;
}

.remove-btn {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(255, 192, 120, 0.1);
  border: 1px solid rgba(255, 192, 120, 0.3);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  color: #F57C00;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background: rgba(255, 192, 120, 0.2);
  transform: translateY(-1px);
}

.star-icon {
  font-size: 14px;
}

.question-content {
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-primary);
  padding-left: 38px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 响应式 */
@media (max-width: 768px) {
  .subject-tabs {
    flex-direction: column;
  }

  .question-header {
    gap: 8px;
  }

  .remove-btn {
    margin-left: 0;
    width: 100%;
    justify-content: center;
  }

  .question-content {
    padding-left: 0;
  }
}
</style>
