<template>
  <div class="random-quiz">
    <!-- 设置面板（未开始时显示） -->
    <div v-if="!started" class="settings-wrapper">
      <el-page-header @back="$router.push('/')" title="返回首页">
        <template #content>
          <span class="page-title">随机刷题</span>
        </template>
      </el-page-header>

      <div class="settings-card">
        <div class="settings-header">
          <span class="settings-icon">🎲</span>
          <span class="settings-title">随机抽题设置</span>
        </div>
        <div class="settings-form">
          <div class="form-item">
            <label class="form-label">科目</label>
            <div class="subject-select">
              <div
                v-for="subject in subjectOptions"
                :key="subject.value"
                class="subject-option"
                :class="{ active: settings.subject === subject.value }"
                @click="selectSubject(subject.value)"
              >
                <span class="subject-icon">{{ subject.icon }}</span>
                <span>{{ subject.label }}</span>
              </div>
            </div>
          </div>
          <div class="form-item">
            <label class="form-label">题数</label>
            <div class="count-input">
              <button class="count-btn" @click="settings.count = Math.max(1, settings.count - 1)">-</button>
              <span class="count-value">{{ settings.count }}</span>
              <button class="count-btn" @click="settings.count = Math.min(50, settings.count + 1)">+</button>
            </div>
          </div>
          <div class="form-item">
            <label class="form-label">范围</label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="settings.onlyUnanswered" />
              <span class="checkbox-text">只做未做过的题</span>
            </label>
          </div>
          <button class="start-btn" @click="startRandom">
            <span class="btn-icon">🚀</span>
            <span>开始刷题</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 做题区域（开始后显示） -->
    <div v-if="started && questions.length > 0" class="quiz-layout">
      <!-- 左侧题目区域 -->
      <div class="quiz-main">
        <el-page-header @back="goBack" title="返回设置">
          <template #content>
            <span class="page-title">随机刷题</span>
          </template>
        </el-page-header>

        <div class="question-card" v-if="currentQuestion">
          <!-- 题目头部 -->
          <div class="question-header">
            <div class="question-meta">
              <el-tag :type="typeTag" size="small">{{ typeText }}</el-tag>
              <span class="question-index">第 {{ currentIndex + 1 }} / {{ questions.length }} 题</span>
            </div>
          </div>

          <!-- 无答案提示 -->
          <el-alert
            v-if="!currentQuestion.answer"
            title="该题暂无答案，可能是题目文本损坏"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 16px"
          />

          <!-- 题目内容 -->
          <div class="question-content">{{ currentQuestion.content }}</div>

          <!-- 选项（选择题） -->
          <div v-if="currentQuestion.type === 'single' || currentQuestion.type === 'multiple'" class="options">
            <div
              v-for="opt in currentQuestion.options"
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
          <div v-if="currentQuestion.type === 'judge'" class="judge-options">
            <el-button
              :type="userAnswer === '√' ? 'success' : 'default'"
              :class="{
                'is-answer': showAnswer && currentQuestion.answer === '√',
                'is-wrong': showAnswer && userAnswer === '√' && currentQuestion.answer !== '√'
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
                'is-answer': showAnswer && currentQuestion.answer === '×',
                'is-wrong': showAnswer && userAnswer === '×' && currentQuestion.answer !== '×'
              }"
              @click="selectOption('×')"
              size="large"
            >
              <span class="judge-icon">×</span>
              <span>错误</span>
            </el-button>
          </div>

          <!-- 填空题 -->
          <div v-if="currentQuestion.type === 'blank'" class="blank-input">
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
            <el-button v-if="!showAnswer" type="primary" @click="submit" :disabled="!userAnswer || !currentQuestion.answer" size="large">
              提交答案
            </el-button>
            <el-button v-if="!showAnswer && !currentQuestion.answer" @click="nextQuestion" size="large">
              跳过
            </el-button>
            <el-button v-else-if="showAnswer" type="primary" @click="nextQuestion" size="large">
              {{ currentIndex >= questions.length - 1 ? '查看结果' : '下一题' }}
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
                <div class="result-answer">正确答案：{{ currentQuestion.answer }}</div>
              </div>
            </div>
            <div v-if="currentQuestion.explanation" class="explanation">
              <div class="explanation-title">📝 解析</div>
              <div class="explanation-content">{{ currentQuestion.explanation }}</div>
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
              wrong: q.status === 'wrong'
            }"
            @click="jumpTo(index)"
          >
            {{ index + 1 }}
          </div>
        </div>
      </div>
    </div>

    <!-- 结果页面 -->
    <div v-if="showResult" class="result-page">
      <div class="result-card">
        <div class="result-header">
          <span class="result-emoji">🎉</span>
          <h2>本轮刷题完成！</h2>
        </div>
        <div class="result-stats">
          <div class="result-stat-item">
            <div class="stat-num">{{ questions.length }}</div>
            <div class="stat-label">总题数</div>
          </div>
          <div class="result-stat-item">
            <div class="stat-num correct">{{ correctCount }}</div>
            <div class="stat-label">答对</div>
          </div>
          <div class="result-stat-item">
            <div class="stat-num wrong">{{ wrongCount }}</div>
            <div class="stat-label">答错</div>
          </div>
          <div class="result-stat-item">
            <div class="stat-num">{{ accuracy }}%</div>
            <div class="stat-label">正确率</div>
          </div>
        </div>
        <div class="result-actions">
          <button class="action-btn primary" @click="startRandom">
            <span>🔄</span> 再来一轮
          </button>
          <button class="action-btn" @click="goBack">
            <span>🏠</span> 返回首页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { getSubjects, getRandomQuestions, submitAnswer } from '../api'

const router = useRouter()

const subjectOptions = [
  { value: '习概', label: '习概', icon: '🇨🇳' },
  { value: '马原', label: '马原', icon: '📕' }
]

const settings = ref({
  subject: '习概',
  subjectId: null,
  count: 10,
  onlyUnanswered: false
})

const started = ref(false)
const showResult = ref(false)
const questions = ref([])
const currentIndex = ref(0)
const userAnswer = ref('')
const showAnswer = ref(false)
const isCorrect = ref(false)

const currentQuestion = computed(() => questions.value[currentIndex.value])

const correctCount = computed(() => questions.value.filter(q => q.status === 'correct').length)
const wrongCount = computed(() => questions.value.filter(q => q.status === 'wrong').length)
const unansweredCount = computed(() => questions.value.filter(q => q.status === 'unanswered').length)
const accuracy = computed(() => {
  const done = correctCount.value + wrongCount.value
  return done > 0 ? Math.round(correctCount.value / done * 100) : 0
})

const typeText = computed(() => {
  const map = { single: '单选题', multiple: '多选题', blank: '填空题', judge: '判断题' }
  return map[currentQuestion.value?.type] || ''
})

const typeTag = computed(() => {
  const map = { single: '', multiple: 'success', blank: 'warning', judge: 'info' }
  return map[currentQuestion.value?.type] || ''
})

const selectSubject = (name) => {
  settings.value.subject = name
  onSubjectChange()
}

const onSubjectChange = async () => {
  const { data } = await getSubjects()
  const subject = data.data.find(s => s.name === settings.value.subject)
  if (subject) {
    settings.value.subjectId = subject.id
  }
}

const startRandom = async () => {
  if (!settings.value.subjectId) {
    await onSubjectChange()
  }

  try {
    const { data } = await getRandomQuestions({
      subject_id: settings.value.subjectId,
      count: settings.value.count,
      only_unanswered: settings.value.onlyUnanswered
    })

    questions.value = data.data.map(q => ({ ...q, status: 'unanswered' }))
    currentIndex.value = 0
    userAnswer.value = ''
    showAnswer.value = false
    isCorrect.value = false
    started.value = true
    showResult.value = false
  } catch (e) {
    console.error('随机刷题失败:', e)
  }
}

const isSelected = (key) => {
  if (currentQuestion.value?.type === 'multiple') {
    return userAnswer.value.toUpperCase().includes(key.toUpperCase())
  }
  return userAnswer.value.toUpperCase() === key.toUpperCase()
}

const isCorrectOption = (key) => {
  if (!currentQuestion.value?.answer) return false
  if (currentQuestion.value.type === 'multiple') {
    return currentQuestion.value.answer.toUpperCase().includes(key.toUpperCase())
  }
  return currentQuestion.value.answer.toUpperCase() === key.toUpperCase()
}

const selectOption = (key) => {
  if (showAnswer.value) return
  if (currentQuestion.value.type === 'multiple') {
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

const submit = async () => {
  if (!userAnswer.value) {
    ElMessage.warning('请先选择答案')
    return
  }

  try {
    const { data } = await submitAnswer(currentQuestion.value.id, userAnswer.value)
    isCorrect.value = data.data.is_correct
    showAnswer.value = true

    // 更新题目状态
    currentQuestion.value.status = isCorrect.value ? 'correct' : 'wrong'
    currentQuestion.value.answer = data.data.correct_answer
    currentQuestion.value.explanation = data.data.explanation
  } catch (e) {
    console.error('提交失败:', e)
  }
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
    userAnswer.value = ''
    showAnswer.value = false
    isCorrect.value = false
  } else {
    showResult.value = true
  }
}

const jumpTo = (index) => {
  currentIndex.value = index
  userAnswer.value = ''
  showAnswer.value = false
  isCorrect.value = false
}

const goBack = () => {
  started.value = false
  showResult.value = false
  router.push('/')
}

onMounted(() => {
  onSubjectChange()
})
</script>

<style scoped>
.random-quiz {
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

/* 设置卡片 */
.settings-wrapper {
  max-width: 600px;
  margin: 0 auto;
}

.settings-card {
  margin-top: 20px;
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.settings-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 107, 157, 0.1);
}

.settings-icon {
  font-size: 32px;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.settings-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

/* 科目选择 */
.subject-select {
  display: flex;
  gap: 8px;
}

.subject-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.6);
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
}

.subject-option:hover {
  border-color: var(--primary-light);
  transform: translateY(-2px);
}

.subject-option.active {
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.1) 0%, rgba(132, 94, 247, 0.1) 100%);
  border-color: var(--primary);
}

.subject-icon {
  font-size: 24px;
}

/* 题数输入 */
.count-input {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.6);
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-md);
  padding: 6px;
}

.count-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 20px;
  font-weight: 700;
  transition: all 0.3s ease;
}

.count-btn:hover {
  transform: scale(1.1);
}

.count-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  min-width: 50px;
  text-align: center;
}

/* 复选框 */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 10px 0;
}

.checkbox-label input[type="checkbox"] {
  width: 20px;
  height: 20px;
  accent-color: var(--primary);
  cursor: pointer;
}

.checkbox-text {
  font-size: 15px;
  color: var(--text-primary);
}

/* 开始按钮 */
.start-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px 32px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 18px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 157, 0.4);
}

.btn-icon {
  font-size: 22px;
}

/* 做题布局 */
.quiz-layout {
  display: flex;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
}

.quiz-main {
  flex: 1;
  min-width: 0;
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
  from { transform: scale(0); }
  to { transform: scale(1); }
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
  margin-top: 20px;
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

/* 结果页面 */
.result-page {
  max-width: 500px;
  margin: 60px auto;
}

.result-card {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  padding: 40px;
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(255, 255, 255, 0.6);
  text-align: center;
}

.result-header {
  margin-bottom: 32px;
}

.result-emoji {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
}

.result-header h2 {
  font-size: 24px;
  color: var(--text-primary);
  font-weight: 700;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.result-stat-item {
  padding: 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: var(--radius-md);
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-num.correct {
  color: var(--accent);
}

.stat-num.wrong {
  color: var(--danger);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.result-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.action-btn.primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
}

.action-btn.primary:hover {
  box-shadow: 0 6px 20px rgba(255, 107, 157, 0.4);
}

/* 响应式 */
@media (max-width: 768px) {
  .quiz-layout {
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

  .result-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .result-actions {
    flex-direction: column;
  }
}
</style>
