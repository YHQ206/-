<template>
  <div class="wrong-book">
    <!-- 连对特效 -->
    <CelebrationEffect :show="showCelebration" :streak="correctStreak" />

    <el-page-header @back="$router.push('/')" title="返回首页">
      <template #content>
        <span class="page-title">错题本</span>
      </template>
    </el-page-header>

    <!-- 科目切换 -->
    <el-tabs v-model="currentSubject" @tab-change="loadData">
      <el-tab-pane label="习概" name="习概" />
      <el-tab-pane label="马原" name="马原" />
    </el-tabs>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card pending">
        <div class="stat-value">{{ pendingCount }}</div>
        <div class="stat-label">待复习</div>
      </div>
      <div class="stat-card mastered">
        <div class="stat-value">{{ masteredCount }}</div>
        <div class="stat-label">已掌握</div>
      </div>
      <div class="stat-card stubborn">
        <div class="stat-value">{{ stubbornCount }}</div>
        <div class="stat-label">顽固错题</div>
      </div>
    </div>

    <!-- 切换待复习/已掌握 -->
    <el-tabs v-model="activeTab" class="wrong-tabs">
      <el-tab-pane name="pending">
        <template #label>
          <span>待复习 ({{ pendingCount }})</span>
        </template>
      </el-tab-pane>
      <el-tab-pane name="mastered">
        <template #label>
          <span>已掌握 ({{ masteredCount }})</span>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- 导出和筛选栏 -->
    <div class="export-bar">
      <div class="export-left">
        <!-- 错误次数筛选 -->
        <el-select v-model="errorFilter" placeholder="错误次数筛选" style="width: 140px" @change="filterQuestions">
          <el-option label="全部错题" value="all" />
          <el-option label="错 ≥2 次" value="2" />
          <el-option label="错 ≥3 次" value="3" />
          <el-option label="错 ≥5 次" value="5" />
          <el-option label="错 ≥10 次" value="10" />
        </el-select>

        <!-- 导出按钮 -->
        <el-dropdown @command="handleExport" placement="bottom-start">
          <el-button type="primary" plain>
            <el-icon><Download /></el-icon>
            导出错题
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item :command="{ format: 'word', scope: 'selected' }" :disabled="selectedIds.length === 0">
                <el-icon><Document /></el-icon>
                导出勾选的题目 ({{ selectedIds.length }} 道)
              </el-dropdown-item>
              <el-dropdown-item :command="{ format: 'excel', scope: 'selected' }" :disabled="selectedIds.length === 0">
                <el-icon><Grid /></el-icon>
                导出勾选的题目 ({{ selectedIds.length }} 道)
              </el-dropdown-item>
              <el-dropdown-item divided :command="{ format: 'word', scope: 'filtered' }">
                <el-icon><Document /></el-icon>
                导出筛选结果 ({{ displayQuestions.length }} 道)
              </el-dropdown-item>
              <el-dropdown-item :command="{ format: 'excel', scope: 'filtered' }">
                <el-icon><Grid /></el-icon>
                导出筛选结果 ({{ displayQuestions.length }} 道)
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <div class="export-right">
        <el-button v-if="selectedIds.length > 0" text type="primary" @click="selectedIds = []">
          取消全选
        </el-button>
        <el-button text type="primary" @click="selectAll">
          {{ selectedIds.length === displayQuestions.length ? '取消全选' : '全选' }}
        </el-button>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar" v-if="activeTab === 'pending'">
      <div class="filter-tabs">
        <el-radio-group v-model="filter" @change="filterQuestions">
          <el-radio-button label="all">全部待复习</el-radio-button>
          <el-radio-button label="stubborn">顽固错题</el-radio-button>
        </el-radio-group>
      </div>
      <div class="actions">
        <el-button
          type="danger"
          @click="startWrongQuiz('stubborn')"
          :disabled="stubbornCount === 0"
        >
          <el-icon><Warning /></el-icon>
          刷顽固错题
        </el-button>
        <el-button
          type="primary"
          @click="startWrongQuiz('all')"
          :disabled="pendingCount === 0"
        >
          <el-icon><VideoPlay /></el-icon>
          刷待复习错题
        </el-button>
      </div>
    </div>

    <div class="action-bar" v-else>
      <div class="mastered-tip">
        <el-icon><CircleCheck /></el-icon>
        <span>这些题目你已经掌握了，可以随时回顾复习</span>
      </div>
      <el-button @click="startWrongQuiz('mastered')" :disabled="masteredCount === 0">
        <el-icon><RefreshRight /></el-icon>
        重新测试已掌握
      </el-button>
    </div>

    <!-- 错题列表 -->
    <el-card v-if="displayQuestions.length > 0" class="wrong-list">
      <div
        v-for="(q, index) in displayQuestions"
        :key="q.id"
        class="wrong-item"
        :class="{ stubborn: q.is_stubborn, mastered: q.mastered, selected: selectedIds.includes(q.id) }"
        @click="toggleSelect(q.id)"
      >
        <div class="item-header">
          <el-checkbox
            :model-value="selectedIds.includes(q.id)"
            @click.stop
            @change="toggleSelect(q.id)"
            class="item-checkbox"
          />
          <span class="item-index">{{ index + 1 }}</span>
          <el-tag :type="getTypeTag(q.type)" size="small">{{ getTypeText(q.type) }}</el-tag>
          <el-tag v-if="q.is_stubborn" type="danger" size="small" effect="dark">
            顽固错题
          </el-tag>
          <el-tag v-if="q.mastered" type="success" size="small" effect="plain">
            已掌握
          </el-tag>
          <div class="error-info">
            <span class="error-count" :class="{ 'high': q.attempt_count >= 3 }">
              错误 <strong>{{ q.attempt_count }}</strong> 次
            </span>
            <span class="error-time">{{ q.last_attempt_at }}</span>
          </div>
        </div>
        <div class="question-content">{{ q.content }}</div>
      </div>
    </el-card>

    <el-empty v-else :description="emptyText" />

    <!-- 错题刷题弹窗 -->
    <el-dialog
      v-model="showQuiz"
      :title="quizDialogTitle"
      width="800px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="true"
      @close="closeQuiz"
    >
      <div class="wrong-quiz" v-if="currentQuestion">
        <div class="quiz-header">
          <div class="quiz-progress">
            第 <strong>{{ quizIndex + 1 }}</strong> / {{ quizQuestions.length }} 题
          </div>
          <div class="quiz-tags">
            <el-tag :type="getTypeTag(currentQuestion.type)" size="small">
              {{ getTypeText(currentQuestion.type) }}
            </el-tag>
            <el-tag v-if="currentQuestion.is_stubborn" type="danger" size="small" effect="dark">
              顽固错题
            </el-tag>
            <span class="quiz-error-count">已错 {{ currentQuestion.attempt_count }} 次</span>
          </div>
        </div>

        <div class="quiz-content">{{ currentQuestion.content }}</div>

        <!-- 选项（选择题） -->
        <div v-if="currentQuestion.type === 'single' || currentQuestion.type === 'multiple'" class="quiz-options">
          <div
            v-for="opt in currentQuestion.options"
            :key="opt.label"
            class="quiz-option"
            :class="{
              selected: isSelected(opt.label),
              correct: showAnswer && isCorrectOption(opt.label),
              wrong: showAnswer && isSelected(opt.label) && !isCorrectOption(opt.label)
            }"
            @click="selectOption(opt.label)"
          >
            <span class="option-key">{{ opt.label }}</span>
            <span class="option-text">{{ opt.content }}</span>
          </div>
        </div>

        <!-- 判断题 -->
        <div v-if="currentQuestion.type === 'judge'" class="quiz-judge">
          <el-button
            :type="userAnswer === '√' ? 'success' : 'default'"
            @click="selectOption('√')"
            :disabled="showAnswer"
            size="large"
          >√ 正确</el-button>
          <el-button
            :type="userAnswer === '×' ? 'danger' : 'default'"
            @click="selectOption('×')"
            :disabled="showAnswer"
            size="large"
          >× 错误</el-button>
        </div>

        <!-- 填空题 -->
        <div v-if="currentQuestion.type === 'blank'" class="quiz-blank">
          <el-input
            v-model="userAnswer"
            placeholder="请输入答案，多个答案用顿号分隔"
            :disabled="showAnswer"
            @keyup.enter="submitAnswer"
            size="large"
          />
        </div>

        <!-- 答案结果 -->
        <div v-if="showAnswer" class="quiz-result" :class="isCorrect ? 'correct' : 'wrong'">
          <div class="result-icon">
            <el-icon v-if="isCorrect"><CircleCheck /></el-icon>
            <el-icon v-else><CircleClose /></el-icon>
          </div>
          <div class="result-info">
            <div class="result-text">{{ isCorrect ? '回答正确！' : '回答错误' }}</div>
            <div class="result-answer">正确答案：{{ currentQuestion.answer }}</div>
          </div>
        </div>

        <!-- 查看解析按钮 -->
        <div v-if="showAnswer && currentQuestion.explanation" class="explanation-toggle">
          <el-button
            type="primary"
            plain
            @click="showExplanation = !showExplanation"
            :icon="showExplanation ? 'ArrowUp' : 'ArrowDown'"
          >
            {{ showExplanation ? '收起解析' : '查看解析' }}
          </el-button>
        </div>

        <!-- 解析内容 -->
        <transition name="fade">
          <div v-if="showExplanation && currentQuestion.explanation" class="explanation">
            <div class="explanation-title">📝 解析</div>
            <div class="explanation-content">{{ currentQuestion.explanation }}</div>
          </div>
        </transition>
        <!-- 鼓励语 -->
        <EncourageMessage
          :show="showEncourage"
          :type="isCorrect ? 'correct' : 'wrong'"
          :streak="correctStreak"
        />
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeQuiz">退出刷题</el-button>
          <el-button v-if="!showAnswer" type="primary" @click="submitAnswer" :disabled="!userAnswer">
            提交答案
          </el-button>
          <el-button v-else type="primary" @click="nextQuestion">
            {{ quizIndex >= quizQuestions.length - 1 ? '完成' : '下一题' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VideoPlay, Warning, CircleCheck, CircleClose, RefreshRight, Download, Document, Grid, ArrowDown, ArrowUp } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getSubjects, getWrongQuestions, getQuestionDetail, submitAnswer as submitAnswerApi } from '../api'
import CelebrationEffect from '../components/CelebrationEffect.vue'
import EncourageMessage from '../components/EncourageMessage.vue'

const router = useRouter()
const currentSubject = ref('习概')
const subjectId = ref(null)
const questions = ref([])
const activeTab = ref('pending')
const filter = ref('all')
const errorFilter = ref('all')  // 错误次数筛选
const selectedIds = ref([])  // 勾选的题目 ID

// 顽固错题阈值（错误次数 >= 3 次）
const STUBBORN_THRESHOLD = 3

// 刷题相关
const showQuiz = ref(false)
const quizType = ref('pending')
const quizQuestions = ref([]) // 快照，与源数据完全独立，不受 pendingQuestions 变化影响
const quizIndex = ref(0)
const currentQuestion = ref(null)
const userAnswer = ref('')
const showAnswer = ref(false)
const isCorrect = ref(false)
const showExplanation = ref(false)

// 连胜相关
const correctStreak = ref(0)
const showCelebration = ref(false)
const showEncourage = ref(false)

// 计算各类题目数量
const pendingQuestions = computed(() => questions.value.filter(q => !q.mastered))
const masteredQuestions = computed(() => questions.value.filter(q => q.mastered))
const pendingCount = computed(() => pendingQuestions.value.length)
const masteredCount = computed(() => masteredQuestions.value.length)
const stubbornCount = computed(() => pendingQuestions.value.filter(q => q.attempt_count >= STUBBORN_THRESHOLD).length)

// 当前显示的题目列表
const displayQuestions = computed(() => {
  let list = activeTab.value === 'pending' ? pendingQuestions.value : masteredQuestions.value
  if (activeTab.value === 'pending' && filter.value === 'stubborn') {
    list = list.filter(q => q.attempt_count >= STUBBORN_THRESHOLD)
  }
  // 错误次数筛选
  if (errorFilter.value !== 'all') {
    const minCount = parseInt(errorFilter.value)
    list = list.filter(q => q.attempt_count >= minCount)
  }
  return list
})

// 全选/取消全选
const selectAll = () => {
  if (selectedIds.value.length === displayQuestions.value.length) {
    selectedIds.value = []
  } else {
    selectedIds.value = displayQuestions.value.map(q => q.id)
  }
}

// 切换选中状态
const toggleSelect = (id) => {
  const index = selectedIds.value.indexOf(id)
  if (index === -1) {
    selectedIds.value.push(id)
  } else {
    selectedIds.value.splice(index, 1)
  }
}

// 空状态文字
const emptyText = computed(() => {
  if (activeTab.value === 'pending') {
    return filter.value === 'stubborn' ? '暂无顽固错题' : '暂无待复习的错题，继续努力！'
  }
  return '暂无已掌握的错题'
})

// 弹窗标题
const quizDialogTitle = computed(() => {
  const map = {
    all: '待复习错题刷题',
    stubborn: '顽固错题刷题',
    mastered: '已掌握错题测试'
  }
  return map[quizType.value] || '错题刷题'
})

const loadData = async () => {
  const { data: subjects } = await getSubjects()
  const subject = subjects.data.find(s => s.name === currentSubject.value)
  if (subject) {
    subjectId.value = subject.id
    const { data } = await getWrongQuestions(subject.id)
    questions.value = data.data.map(q => ({
      ...q,
      is_stubborn: q.attempt_count >= STUBBORN_THRESHOLD
    }))
  }
}

const filterQuestions = () => {
  // 由 computed 自动处理
}

const getTypeText = (type) => {
  const map = { single: '单选', multiple: '多选', blank: '填空', judge: '判断' }
  return map[type] || ''
}

const getTypeTag = (type) => {
  const map = { single: '', multiple: 'success', blank: 'warning', judge: 'info' }
  return map[type] || ''
}

// 开始刷错题
const startWrongQuiz = (type) => {
  quizType.value = type
  // 深拷贝每道题，避免与源数据共享引用导致 reactvity 穿透
  const cloneQuestions = (list) => list.map(q => ({ ...q }))
  if (type === 'stubborn') {
    quizQuestions.value = cloneQuestions(pendingQuestions.value.filter(q => q.attempt_count >= STUBBORN_THRESHOLD))
  } else if (type === 'mastered') {
    quizQuestions.value = cloneQuestions(masteredQuestions.value)
  } else {
    quizQuestions.value = cloneQuestions(pendingQuestions.value)
  }

  if (quizQuestions.value.length === 0) {
    ElMessage.warning('暂无题目')
    return
  }

  quizIndex.value = 0
  showQuiz.value = true
  loadQuizQuestion()
}

// 加载当前题目
const loadQuizQuestion = async () => {
  const q = quizQuestions.value[quizIndex.value]
  if (q) {
    const { data } = await getQuestionDetail(q.id)
    currentQuestion.value = {
      ...data.data,
      attempt_count: q.attempt_count,
      is_stubborn: q.is_stubborn
    }
    userAnswer.value = ''
    showAnswer.value = false
    isCorrect.value = false
    showExplanation.value = false
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

const submitAnswer = async () => {
  if (!userAnswer.value) {
    ElMessage.warning('请先选择答案')
    return
  }

  const { data } = await submitAnswerApi(currentQuestion.value.id, userAnswer.value)
  isCorrect.value = data.data.is_correct
  showAnswer.value = true
  // 答错自动显示解析，答对隐藏解析
  showExplanation.value = !isCorrect.value

  // 更新本地数据
  const qIndex = questions.value.findIndex(q => q.id === currentQuestion.value.id)
  if (qIndex !== -1) {
    if (!isCorrect.value) {
      // 答错了，增加错误次数
      questions.value[qIndex].attempt_count++
      questions.value[qIndex].is_stubborn = questions.value[qIndex].attempt_count >= STUBBORN_THRESHOLD
    }
    questions.value[qIndex].status = isCorrect.value ? 'correct' : 'wrong'
    questions.value[qIndex].mastered = isCorrect.value
  }

  // 更新当前题目显示
  currentQuestion.value.attempt_count = questions.value[qIndex]?.attempt_count || currentQuestion.value.attempt_count
  currentQuestion.value.is_stubborn = questions.value[qIndex]?.is_stubborn || false

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

const nextQuestion = () => {
  showEncourage.value = false
  if (quizIndex.value < quizQuestions.value.length - 1) {
    quizIndex.value++
    loadQuizQuestion()
  } else {
    const correctCount = quizQuestions.value.filter(q => {
      const original = questions.value.find(o => o.id === q.id)
      return original?.status === 'correct'
    }).length
    ElMessage.success(`刷题完成！答对 ${correctCount}/${quizQuestions.value.length} 题`)
    closeQuiz()
  }
}

const closeQuiz = () => {
  showQuiz.value = false
  currentQuestion.value = null
  loadData() // 重新从后端获取数据
}

onMounted(() => {
  loadData()
})

// 导出错题
const handleExport = async ({ format, scope }) => {
  let exportIds = []

  if (scope === 'selected') {
    // 导出勾选的题目
    if (selectedIds.value.length === 0) {
      ElMessage.warning('请先勾选要导出的题目')
      return
    }
    exportIds = selectedIds.value
  } else {
    // 导出筛选结果
    if (displayQuestions.value.length === 0) {
      ElMessage.warning('暂无错题可导出')
      return
    }
    exportIds = displayQuestions.value.map(q => q.id)
  }

  try {
    const baseUrl = import.meta.env.DEV ? 'http://localhost:5000' : ''
    const idsParam = exportIds.join(',')
    const url = `${baseUrl}/api/export/wrong/${format}?subject_id=${subjectId.value}&tab=${activeTab.value}&ids=${idsParam}`

    // 创建隐藏的 a 标签来下载
    const link = document.createElement('a')
    link.href = url
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success(`正在导出 ${exportIds.length} 道错题...`)
  } catch (error) {
    ElMessage.error('导出失败，请稍后重试')
    console.error('Export error:', error)
  }
}
</script>

<style scoped>
.wrong-book {
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

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 20px 0;
}

.stat-card {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
  padding: 24px;
  text-align: center;
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-hover-shadow);
}

.stat-card.pending {
  background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
  border-color: #FFD54F;
}

.stat-card.mastered {
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
  border-color: #81C784;
}

.stat-card.stubborn {
  background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
  border-color: #EF9A9A;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-card.pending .stat-value {
  color: #F57C00;
}

.stat-card.mastered .stat-value {
  color: #388E3C;
}

.stat-card.stubborn .stat-value {
  color: #D32F2F;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 8px;
  font-weight: 500;
}

/* 切换标签 */
.wrong-tabs {
  margin-bottom: 0;
}

/* 导出栏 */
.export-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0;
  padding: 12px 20px;
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.export-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.export-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.export-tip {
  font-size: 13px;
  color: var(--text-secondary);
}

.item-checkbox {
  margin-right: 4px;
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0;
  padding: 16px 20px;
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.mastered-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #388E3C;
  font-size: 14px;
  font-weight: 500;
}

.mastered-tip .el-icon {
  font-size: 20px;
}

.actions {
  display: flex;
  gap: 12px;
}

/* 错题列表 */
.wrong-list {
  margin-top: 0;
}

.wrong-item {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.wrong-item:hover {
  background: rgba(255, 107, 157, 0.05);
  transform: translateX(4px);
}

.wrong-item.stubborn {
  border-left-color: var(--danger);
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.05) 0%, rgba(255, 150, 150, 0.05) 100%);
}

.wrong-item.stubborn:hover {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 150, 150, 0.1) 100%);
}

.wrong-item.mastered {
  border-left-color: var(--accent);
  background: linear-gradient(135deg, rgba(32, 201, 151, 0.05) 0%, rgba(150, 242, 215, 0.05) 100%);
}

.wrong-item.mastered:hover {
  background: linear-gradient(135deg, rgba(32, 201, 151, 0.1) 0%, rgba(150, 242, 215, 0.1) 100%);
}

.wrong-item.selected {
  background: linear-gradient(135deg, rgba(102, 177, 255, 0.08) 0%, rgba(132, 94, 247, 0.08) 100%);
  border-left-color: var(--primary);
}

.wrong-item.selected:hover {
  background: linear-gradient(135deg, rgba(102, 177, 255, 0.15) 0%, rgba(132, 94, 247, 0.15) 100%);
}

.wrong-item:last-child {
  border-bottom: none;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
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

.error-info {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 16px;
}

.error-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.error-count.high {
  color: var(--danger);
  font-weight: 600;
}

.error-count strong {
  font-size: 16px;
}

.error-time {
  font-size: 13px;
  color: var(--text-light);
}

.question-content {
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-primary);
}

/* 刷题弹窗样式 */
.wrong-quiz {
  min-height: 300px;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 107, 157, 0.1);
}

.quiz-progress {
  font-size: 14px;
  color: var(--text-secondary);
}

.quiz-progress strong {
  font-size: 18px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
}

.quiz-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quiz-error-count {
  font-size: 13px;
  color: var(--danger);
  font-weight: 500;
}

.quiz-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-primary);
  margin-bottom: 24px;
  min-height: 50px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(255, 245, 247, 0.5) 0%, rgba(240, 230, 255, 0.5) 100%);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--primary);
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quiz-option {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.6);
}

.quiz-option:hover:not(.correct):not(.wrong) {
  border-color: var(--primary-light);
  background: rgba(255, 107, 157, 0.05);
  transform: translateX(8px);
}

.quiz-option.selected {
  border-color: var(--primary);
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.1) 0%, rgba(132, 94, 247, 0.1) 100%);
  box-shadow: 0 4px 15px rgba(255, 107, 157, 0.15);
}

.quiz-option.correct {
  border-color: var(--accent);
  background: linear-gradient(135deg, rgba(32, 201, 151, 0.1) 0%, rgba(150, 242, 215, 0.1) 100%);
  box-shadow: 0 4px 15px rgba(32, 201, 151, 0.15);
}

.quiz-option.wrong {
  border-color: var(--danger);
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 150, 150, 0.1) 100%);
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.15);
}

.quiz-option .option-key {
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
  color: var(--primary);
  transition: all 0.3s ease;
}

.quiz-option.selected .option-key {
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: #fff;
}

.quiz-option.correct .option-key {
  background: linear-gradient(135deg, var(--accent) 0%, #38D9A9 100%);
  color: #fff;
}

.quiz-option.wrong .option-key {
  background: linear-gradient(135deg, var(--danger) 0%, #FF9696 100%);
  color: #fff;
}

.quiz-judge {
  display: flex;
  gap: 24px;
  justify-content: center;
}

.quiz-judge .el-button {
  width: 160px;
  height: 80px;
  font-size: 18px;
  border-radius: var(--radius-md) !important;
  transition: all 0.3s ease !important;
}

.quiz-judge .el-button:hover {
  transform: translateY(-4px);
}

.quiz-blank {
  max-width: 100%;
}

.quiz-result {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: var(--radius-md);
  margin-top: 24px;
  animation: popIn 0.4s ease;
}

@keyframes popIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.quiz-result.correct {
  background: linear-gradient(135deg, rgba(32, 201, 151, 0.1) 0%, rgba(150, 242, 215, 0.1) 100%);
  border: 2px solid rgba(32, 201, 151, 0.2);
}

.quiz-result.wrong {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 150, 150, 0.1) 100%);
  border: 2px solid rgba(255, 107, 107, 0.2);
}

.result-icon {
  font-size: 40px;
}

.quiz-result.correct .result-icon {
  color: var(--accent);
}

.quiz-result.wrong .result-icon {
  color: var(--danger);
}

.result-text {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 6px;
}

.quiz-result.correct .result-text {
  color: var(--accent);
}

.quiz-result.wrong .result-text {
  color: var(--danger);
}

.result-answer {
  font-size: 14px;
  color: var(--text-secondary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 解析样式 */
.explanation-toggle {
  text-align: center;
  margin-top: 16px;
}

.explanation {
  margin-top: 16px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(255, 245, 247, 0.8) 0%, rgba(240, 230, 255, 0.8) 100%);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--secondary);
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.explanation-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--secondary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.explanation-content {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }

  .action-bar {
    flex-direction: column;
    gap: 12px;
  }

  .actions {
    width: 100%;
  }

  .actions .el-button {
    flex: 1;
  }
}
</style>
