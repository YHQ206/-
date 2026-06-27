<template>
  <div class="quiz-page">
    <!-- 连对特效 -->
    <CelebrationEffect :show="showCelebration" :streak="correctStreak" />

    <!-- 左侧题目区域 -->
    <div class="quiz-main">
      <el-page-header @back="goBack" :title="'返回章节'">
        <template #content>
          <span class="page-title">{{ chapterName }}</span>
        </template>
      </el-page-header>

      <div class="question-card" v-if="question">
        <!-- 题目头部 -->
        <div class="question-header">
          <div class="question-meta">
            <el-tag :type="typeTag" size="small">{{ typeText }}</el-tag>
            <span class="question-index">第 {{ currentIndex + 1 }} / {{ totalQuestions }} 题</span>
          </div>
          <el-button
            :type="question.is_favorite ? 'warning' : 'default'"
            link
            @click="toggleFavorite"
          >
            <el-icon><Star /></el-icon>
            {{ question.is_favorite ? '已收藏' : '收藏' }}
          </el-button>
        </div>

        <!-- 无答案提示 -->
        <el-alert
          v-if="!question.answer"
          title="该题暂无答案，可能是题目文本损坏"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        />

        <!-- 题目内容 -->
        <div class="question-content">{{ question.content }}</div>

        <!-- 选项（选择题） -->
        <div v-if="question.type === 'single' || question.type === 'multiple'" class="options">
          <div
            v-for="opt in question.options"
            :key="opt.key || opt.label"
            class="option-item"
            :class="{
              selected: isSelected(opt.key || opt.label),
              correct: showAnswer && isCorrectOption(opt.key || opt.label),
              wrong: showAnswer && isSelected(opt.key || opt.label) && !isCorrectOption(opt.key || opt.label)
            }"
            @click="selectOption(opt.key || opt.label)"
          >
            <span class="option-key">{{ opt.key || opt.label }}</span>
            <span class="option-text">{{ opt.text || opt.content }}</span>
            <el-icon v-if="showAnswer && isCorrectOption(opt.key || opt.label)" class="check-icon">
              <Check />
            </el-icon>
          </div>
        </div>

        <!-- 判断题 -->
        <div v-if="question.type === 'judge'" class="judge-options">
          <el-button
            :type="userAnswer === '√' ? 'success' : 'default'"
            :class="{
              'is-answer': showAnswer && question.answer === '√',
              'is-wrong': showAnswer && userAnswer === '√' && question.answer !== '√'
            }"
            @click="selectOption('√')"
            size="large"
          >
            <span class="judge-icon">√</span>
            <span>正确</span>
          </el-button>
          <el-button
            :type="userAnswer === '×' ? 'danger' : 'default'"
            :class="{
              'is-answer': showAnswer && question.answer === '×',
              'is-wrong': showAnswer && userAnswer === '×' && question.answer !== '×'
            }"
            @click="selectOption('×')"
            size="large"
          >
            <span class="judge-icon">×</span>
            <span>错误</span>
          </el-button>
        </div>

        <!-- 填空题 -->
        <div v-if="question.type === 'blank'" class="blank-input">
          <el-input
            v-model="userAnswer"
            placeholder="请输入答案，多个答案用顿号（、）分隔"
            :disabled="showAnswer"
            @keyup.enter="submit"
            size="large"
          />
        </div>

        <!-- 操作按钮 -->
        <div class="actions">
          <el-button v-if="!showAnswer" type="primary" @click="submit" :disabled="!userAnswer || !question.answer" size="large">
            提交答案
          </el-button>
          <el-button v-if="!showAnswer && !question.answer" @click="nextQuestion" size="large">
            跳过
          </el-button>
          <el-button v-else-if="showAnswer" type="primary" @click="nextQuestion" size="large">
            {{ currentIndex >= totalQuestions - 1 ? '完成本章' : '下一题' }}
          </el-button>
        </div>

        <!-- 答案解析 -->
        <div v-if="showAnswer" class="answer-section">
          <el-divider />
          <div class="result-box" :class="isCorrect ? 'correct' : 'wrong'">
            <div class="result-icon">
              <el-icon v-if="isCorrect"><CircleCheck /></el-icon>
              <el-icon v-else><CircleClose /></el-icon>
            </div>
            <div class="result-text">
              <div class="result-title">{{ isCorrect ? '回答正确！' : '回答错误' }}</div>
              <div class="result-answer">正确答案：{{ question.answer }}</div>
            </div>
          </div>
          <!-- 鼓励语 -->
          <EncourageMessage
            :show="showEncourage"
            :type="isCorrect ? 'correct' : 'wrong'"
            :streak="correctStreak"
          />
          <div v-if="question.explanation" class="explanation">
            <div class="explanation-title">📝 解析</div>
            <div class="explanation-content">{{ question.explanation }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧题号导航 -->
    <div class="quiz-sidebar">
      <div class="sidebar-header">题目导航</div>
      <div class="sidebar-stats">
        <div class="stat-item">
          <span class="stat-dot correct"></span>
          <span>正确 {{ correctCount }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-dot wrong"></span>
          <span>错误 {{ wrongCount }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-dot"></span>
          <span>未做 {{ unansweredCount }}</span>
        </div>
      </div>
      <div class="question-nav">
        <div
          v-for="(q, index) in questions"
          :key="q.id"
          class="nav-item"
          :class="{
            active: index === currentIndex,
            correct: q.status === 'correct',
            wrong: q.status === 'wrong',
            favorite: q.is_favorite
          }"
          @click="jumpTo(index)"
        >
          {{ index + 1 }}
          <el-icon v-if="q.is_favorite" class="fav-dot"><Star /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Star, Check, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import {
  getChapterQuestions,
  getQuestionDetail,
  submitAnswer,
  addFavorite,
  removeFavorite,
  savePosition,
  getLastPosition
} from '../api'
import CelebrationEffect from '../components/CelebrationEffect.vue'
import EncourageMessage from '../components/EncourageMessage.vue'

const route = useRoute()
const router = useRouter()

const chapterId = ref(parseInt(route.params.chapterId))
const hasExplicitIndex = route.params.index !== undefined
const currentIndex = ref(hasExplicitIndex ? parseInt(route.params.index) : 0)
const questions = ref([])
const question = ref(null)
const userAnswer = ref('')
const showAnswer = ref(false)
const isCorrect = ref(false)
const chapterName = ref('')

// 连胜相关
const correctStreak = ref(0)
const showCelebration = ref(false)
const showEncourage = ref(false)

const totalQuestions = computed(() => questions.value.length)

const correctCount = computed(() => questions.value.filter(q => q.status === 'correct').length)
const wrongCount = computed(() => questions.value.filter(q => q.status === 'wrong').length)
const unansweredCount = computed(() => questions.value.filter(q => q.status === 'unanswered').length)

const typeText = computed(() => {
  const map = { single: '单选题', multiple: '多选题', blank: '填空题', judge: '判断题' }
  return map[question.value?.type] || ''
})

const typeTag = computed(() => {
  const map = { single: '', multiple: 'success', blank: 'warning', judge: 'info' }
  return map[question.value?.type] || ''
})

const isSelected = (key) => {
  if (question.value?.type === 'multiple') {
    return userAnswer.value.toUpperCase().includes(key.toUpperCase())
  }
  return userAnswer.value.toUpperCase() === key.toUpperCase()
}

const isCorrectOption = (key) => {
  if (!question.value?.answer) return false
  if (question.value.type === 'multiple') {
    return question.value.answer.toUpperCase().includes(key.toUpperCase())
  }
  return question.value.answer.toUpperCase() === key.toUpperCase()
}

const selectOption = (key) => {
  if (showAnswer.value) return
  if (question.value.type === 'multiple') {
    const upper = userAnswer.value.toUpperCase()
    if (upper.includes(key)) {
      userAnswer.value = upper.replace(key, '').split('').sort().join('')
    } else {
      userAnswer.value = (upper + key).split('').sort().join('')
    }
  } else {
    userAnswer.value = key
  }
}

const loadQuestion = async () => {
  if (questions.value.length === 0) {
    const { data } = await getChapterQuestions(chapterId.value)
    questions.value = data.data.questions
    chapterName.value = data.data.chapter_name || `章节 ${chapterId.value}`

    // 恢复上次刷题位置（仅当没有指定题号时）
    if (!hasExplicitIndex) {
      try {
        const { data: posData } = await getLastPosition()
        const pos = posData.data
        if (pos && pos.chapter_id === chapterId.value && pos.question_index < questions.value.length) {
          currentIndex.value = pos.question_index
        }
      } catch (e) {
        // 无记录则忽略
      }
    }
  }

  if (currentIndex.value >= questions.value.length) {
    currentIndex.value = questions.value.length - 1
  }

  const qId = questions.value[currentIndex.value]?.id
  if (qId) {
    const { data } = await getQuestionDetail(qId)
    question.value = data.data
    userAnswer.value = ''
    showAnswer.value = false
    isCorrect.value = false

    // 如果已经做过，显示答案
    if (question.value.status !== 'unanswered') {
      showAnswer.value = true
      isCorrect.value = question.value.status === 'correct'
    }

    // 保存进度
    savePosition({
      chapter_id: chapterId.value,
      question_index: currentIndex.value
    })
  }
}

const submit = async () => {
  if (!userAnswer.value) {
    ElMessage.warning('请先选择答案')
    return
  }

  const { data } = await submitAnswer(question.value.id, userAnswer.value)
  isCorrect.value = data.data.is_correct
  showAnswer.value = true

  // 更新本地状态
  question.value.status = isCorrect.value ? 'correct' : 'wrong'
  questions.value[currentIndex.value].status = question.value.status

  // 更新连胜计数
  if (isCorrect.value) {
    correctStreak.value++
    // 连对3题以上触发庆祝特效
    if (correctStreak.value >= 3) {
      showCelebration.value = true
      setTimeout(() => {
        showCelebration.value = false
      }, 3000)
    }
  } else {
    correctStreak.value = 0
  }

  // 显示鼓励语
  showEncourage.value = true
}

const toggleFavorite = async () => {
  if (question.value.is_favorite) {
    await removeFavorite(question.value.id)
    question.value.is_favorite = false
    questions.value[currentIndex.value].is_favorite = false
    ElMessage.success('已取消收藏')
  } else {
    await addFavorite(question.value.id)
    question.value.is_favorite = true
    questions.value[currentIndex.value].is_favorite = true
    ElMessage.success('已收藏')
  }
}

const jumpTo = (index) => {
  currentIndex.value = index
  showEncourage.value = false
  loadQuestion()
}

const nextQuestion = () => {
  showEncourage.value = false
  if (currentIndex.value < totalQuestions.value - 1) {
    currentIndex.value++
    loadQuestion()
  } else {
    ElMessage.success('本章题目已完成！')
    router.push(`/chapter/${chapterId.value}`)
  }
}

const goBack = () => {
  router.push(`/chapter/${chapterId.value}`)
}

const onKeydown = (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
  if (e.key === 'ArrowLeft' && currentIndex.value > 0) {
    currentIndex.value--
    loadQuestion()
  } else if (e.key === 'ArrowRight') {
    if (showAnswer.value && currentIndex.value < totalQuestions.value - 1) {
      currentIndex.value++
      loadQuestion()
    }
  }
}

onMounted(() => {
  loadQuestion()
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.quiz-page {
  display: flex;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
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

/* 左侧题目区域 */
.quiz-main {
  flex: 1;
  min-width: 0;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.question-card {
  margin-top: 20px;
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow: var(--card-shadow);
  min-height: 500px;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
}

.question-card:hover {
  box-shadow: var(--card-hover-shadow);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 107, 157, 0.1);
}

.question-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.question-index {
  color: var(--text-secondary);
  font-size: 14px;
  background: rgba(255, 107, 157, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
}

.question-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-primary);
  margin-bottom: 24px;
  min-height: 80px;
  max-height: 200px;
  overflow-y: auto;
  padding: 16px;
  background: linear-gradient(135deg, rgba(255, 245, 247, 0.5) 0%, rgba(240, 230, 255, 0.5) 100%);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--primary);
}

/* 选项样式 */
.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 200px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.6);
}

.option-item:hover:not(.correct):not(.wrong) {
  border-color: var(--primary-light);
  background: rgba(255, 107, 157, 0.05);
  transform: translateX(8px);
}

.option-item.selected {
  border-color: var(--primary);
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.1) 0%, rgba(132, 94, 247, 0.1) 100%);
  box-shadow: 0 4px 15px rgba(255, 107, 157, 0.15);
}

.option-item.correct {
  border-color: var(--accent);
  background: linear-gradient(135deg, rgba(32, 201, 151, 0.1) 0%, rgba(150, 242, 215, 0.1) 100%);
  box-shadow: 0 4px 15px rgba(32, 201, 151, 0.15);
}

.option-item.wrong {
  border-color: var(--danger);
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 150, 150, 0.1) 100%);
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.15);
}

.option-key {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: rgba(255, 107, 157, 0.1);
  font-weight: 700;
  margin-right: 16px;
  flex-shrink: 0;
  font-size: 14px;
  color: var(--primary);
  transition: all 0.3s ease;
}

.option-item.selected .option-key {
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: #fff;
}

.option-item.correct .option-key {
  background: linear-gradient(135deg, var(--accent) 0%, #38D9A9 100%);
  color: #fff;
}

.option-item.wrong .option-key {
  background: linear-gradient(135deg, var(--danger) 0%, #FF9696 100%);
  color: #fff;
}

.option-text {
  flex: 1;
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-primary);
}

.check-icon {
  color: var(--accent);
  font-size: 22px;
  margin-left: 12px;
  animation: popIn 0.3s ease;
}

@keyframes popIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

/* 判断题 */
.judge-options {
  display: flex;
  gap: 24px;
  justify-content: center;
  min-height: 200px;
  align-items: center;
}

.judge-options .el-button {
  width: 160px;
  height: 80px;
  font-size: 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  border-radius: var(--radius-md) !important;
  transition: all 0.3s ease !important;
}

.judge-options .el-button:hover {
  transform: translateY(-4px);
}

.judge-icon {
  font-size: 28px;
  font-weight: bold;
}

.judge-options .is-answer {
  border-color: var(--accent) !important;
  background: linear-gradient(135deg, rgba(32, 201, 151, 0.1) 0%, rgba(150, 242, 215, 0.1) 100%) !important;
  box-shadow: 0 4px 15px rgba(32, 201, 151, 0.2);
}

.judge-options .is-wrong {
  border-color: var(--danger) !important;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 150, 150, 0.1) 100%) !important;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.2);
}

/* 填空题 */
.blank-input {
  max-width: 100%;
  min-height: 200px;
  display: flex;
  align-items: center;
}

.blank-input .el-input {
  font-size: 16px;
}

/* 操作按钮 */
.actions {
  margin-top: auto;
  padding-top: 24px;
  text-align: center;
}

.actions .el-button {
  min-width: 160px;
  border-radius: var(--radius-md) !important;
  font-weight: 600;
  padding: 12px 32px;
}

/* 答案解析 */
.answer-section {
  margin-top: auto;
  padding-top: 20px;
  animation: fadeInUp 0.4s ease;
}

.result-box {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: var(--radius-md);
  margin-bottom: 16px;
}

.result-box.correct {
  background: linear-gradient(135deg, rgba(32, 201, 151, 0.1) 0%, rgba(150, 242, 215, 0.1) 100%);
  border: 2px solid rgba(32, 201, 151, 0.2);
}

.result-box.wrong {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 150, 150, 0.1) 100%);
  border: 2px solid rgba(255, 107, 107, 0.2);
}

.result-icon {
  font-size: 40px;
  animation: popIn 0.4s ease;
}

.result-box.correct .result-icon {
  color: var(--accent);
}

.result-box.wrong .result-icon {
  color: var(--danger);
}

.result-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 6px;
}

.result-box.correct .result-title {
  color: var(--accent);
}

.result-box.wrong .result-title {
  color: var(--danger);
}

.result-answer {
  font-size: 14px;
  color: var(--text-secondary);
}

.explanation {
  padding: 20px;
  background: linear-gradient(135deg, rgba(255, 245, 247, 0.8) 0%, rgba(240, 230, 255, 0.8) 100%);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--secondary);
}

.explanation-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
  font-size: 15px;
}

.explanation-content {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);
}

/* 右侧题号导航 */
.quiz-sidebar {
  width: 260px;
  flex-shrink: 0;
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--card-shadow);
  position: sticky;
  top: 80px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.sidebar-header {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(255, 107, 157, 0.1);
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(255, 107, 157, 0.1);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-dot {
  width: 12px;
  height: 12px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.06);
}

.stat-dot.correct {
  background: linear-gradient(135deg, var(--accent) 0%, #38D9A9 100%);
}

.stat-dot.wrong {
  background: linear-gradient(135deg, var(--danger) 0%, #FF9696 100%);
}

.question-nav {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.nav-item {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  background: rgba(255, 255, 255, 0.6);
  color: var(--text-secondary);
}

.nav-item:hover {
  border-color: var(--primary-light);
  color: var(--primary);
  transform: scale(1.1);
}

.nav-item.active {
  border-color: transparent;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: #fff;
  box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
  transform: scale(1.1);
}

.nav-item.correct {
  border-color: var(--accent);
  background: rgba(32, 201, 151, 0.1);
  color: var(--accent);
}

.nav-item.correct.active {
  background: linear-gradient(135deg, var(--accent) 0%, #38D9A9 100%);
  color: #fff;
  box-shadow: 0 4px 15px rgba(32, 201, 151, 0.3);
}

.nav-item.wrong {
  border-color: var(--danger);
  background: rgba(255, 107, 107, 0.1);
  color: var(--danger);
}

.nav-item.wrong.active {
  background: linear-gradient(135deg, var(--danger) 0%, #FF9696 100%);
  color: #fff;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.fav-dot {
  position: absolute;
  top: -5px;
  right: -5px;
  color: var(--warning);
  font-size: 14px;
  filter: drop-shadow(0 2px 4px rgba(255, 192, 120, 0.4));
}

/* 暗黑主题特殊样式 */
.theme-dark .question-content {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(255, 0, 255, 0.05) 100%);
  border-left-color: var(--primary);
}

.theme-dark .option-item:hover:not(.correct):not(.wrong) {
  background: rgba(0, 212, 255, 0.08);
}

.theme-dark .explanation {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(255, 0, 255, 0.08) 100%);
  border-left-color: var(--secondary);
}

/* 玻璃主题特殊样式 */
.theme-glass .question-content {
  background: rgba(255, 255, 255, 0.1);
  border-left-color: rgba(255, 255, 255, 0.5);
}

.theme-glass .option-item {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.theme-glass .option-item:hover:not(.correct):not(.wrong) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.theme-glass .explanation {
  background: rgba(255, 255, 255, 0.1);
  border-left-color: rgba(255, 255, 255, 0.5);
}

.theme-glass .quiz-sidebar {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.2);
}

.theme-glass .nav-item {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 响应式 */
@media (max-width: 768px) {
  .quiz-page {
    flex-direction: column;
  }

  .quiz-sidebar {
    width: 100%;
    position: static;
    max-height: none;
  }

  .question-nav {
    grid-template-columns: repeat(8, 1fr);
  }
}
</style>
