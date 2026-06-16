<template>
  <div class="random-quiz">
    <el-page-header @back="$router.push('/')" title="返回首页">
      <template #content>
        <span class="page-title">随机刷题</span>
      </template>
    </el-page-header>

    <!-- 设置 -->
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
              @click="settings.subject = subject.value"
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

    <!-- 题目列表 -->
    <div v-if="questions.length > 0" class="questions-area">
      <div
        v-for="(q, index) in questions"
        :key="q.id"
        class="question-card"
        :style="{ animationDelay: `${index * 0.1}s` }"
      >
        <div class="question-header">
          <span class="q-index">第 {{ index + 1 }} 题</span>
          <span class="type-tag" :class="q.type">{{ getTypeText(q.type) }}</span>
        </div>

        <div class="question-content">{{ q.content }}</div>

        <!-- 选项 -->
        <div v-if="q.type === 'single' || q.type === 'multiple'" class="options">
          <div
            v-for="opt in q.options"
            :key="opt.key"
            class="option-item"
            :class="{
              selected: isOptionSelected(q, opt.key),
              correct: submitted && isOptionCorrect(q, opt.key),
              wrong: submitted && isOptionSelected(q, opt.key) && !isOptionCorrect(q, opt.key)
            }"
            @click="selectOption(q.id, opt.key)"
          >
            <span class="option-key">{{ opt.key }}</span>
            <span class="option-text">{{ opt.text }}</span>
          </div>
        </div>

        <div v-if="q.type === 'judge'" class="judge-options">
          <button
            class="judge-btn"
            :class="{ selected: answers[q.id] === '√', correct: submitted && q.answer === '√', wrong: submitted && answers[q.id] === '√' && q.answer !== '√' }"
            @click="selectOption(q.id, '√')"
            :disabled="submitted"
          >
            <span class="judge-icon">√</span>
            <span>正确</span>
          </button>
          <button
            class="judge-btn"
            :class="{ selected: answers[q.id] === '×', correct: submitted && q.answer === '×', wrong: submitted && answers[q.id] === '×' && q.answer !== '×' }"
            @click="selectOption(q.id, '×')"
            :disabled="submitted"
          >
            <span class="judge-icon">×</span>
            <span>错误</span>
          </button>
        </div>

        <div v-if="q.type === 'blank'" class="blank-input">
          <input
            v-model="answers[q.id]"
            placeholder="请输入答案"
            :disabled="submitted"
            class="blank-field"
          />
        </div>

        <!-- 答案结果 -->
        <div v-if="submitted" class="answer-result" :class="results[q.id] ? 'correct' : 'wrong'">
          <div class="result-icon">{{ results[q.id] ? '✅' : '❌' }}</div>
          <div class="result-info">
            <div class="result-text">{{ results[q.id] ? '回答正确！' : '回答错误' }}</div>
            <div class="result-answer">正确答案：{{ q.answer }}</div>
          </div>
        </div>
      </div>

      <!-- 提交按钮 -->
      <div class="submit-area">
        <button v-if="!submitted" class="submit-btn" @click="submitAll">
          <span class="btn-icon">📝</span>
          <span>提交全部答案</span>
        </button>
        <button v-else class="submit-btn restart" @click="startRandom">
          <span class="btn-icon">🔄</span>
          <span>再来一轮</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSubjects, getRandomQuestions, submitAnswer } from '../api'

const subjectOptions = [
  { value: '习概', label: '习概', icon: '🇨🇳' },
  { value: '马原', label: '马原', icon: '📕' }
]

const settings = reactive({
  subject: '习概',
  subjectId: null,
  count: 10,
  onlyUnanswered: false
})

const questions = ref([])
const answers = reactive({})
const results = reactive({})
const submitted = ref(false)

const onSubjectChange = async () => {
  const { data } = await getSubjects()
  const subject = data.data.find(s => s.name === settings.subject)
  if (subject) {
    settings.subjectId = subject.id
  }
}

const startRandom = async () => {
  if (!settings.subjectId) {
    await onSubjectChange()
  }

  const { data } = await getRandomQuestions({
    subject_id: settings.subjectId,
    count: settings.count,
    only_unanswered: settings.onlyUnanswered
  })

  questions.value = data.data
  submitted.value = false

  Object.keys(answers).forEach(key => delete answers[key])
  Object.keys(results).forEach(key => delete results[key])
}

const selectOption = (qId, key) => {
  if (submitted.value) return
  const q = questions.value.find(x => x.id === qId)
  if (q && q.type === 'multiple') {
    const current = (answers[qId] || '').toUpperCase()
    if (current.includes(key.toUpperCase())) {
      answers[qId] = current.replace(key.toUpperCase(), '').split('').sort().join('')
    } else {
      answers[qId] = (current + key.toUpperCase()).split('').sort().join('')
    }
  } else {
    answers[qId] = key
  }
}

const isOptionSelected = (q, key) => {
  const ans = (answers[q.id] || '').toUpperCase()
  if (q.type === 'multiple') {
    return ans.includes(key.toUpperCase())
  }
  return ans === key.toUpperCase()
}

const isOptionCorrect = (q, key) => {
  if (!q.answer) return false
  if (q.type === 'multiple') {
    return q.answer.toUpperCase().includes(key.toUpperCase())
  }
  return q.answer.toUpperCase() === key.toUpperCase()
}

const submitAll = async () => {
  const unanswered = questions.value.filter(q => !answers[q.id])
  if (unanswered.length > 0) {
    ElMessage.warning(`还有 ${unanswered.length} 题未作答`)
    return
  }

  for (const q of questions.value) {
    const { data } = await submitAnswer(q.id, answers[q.id])
    results[q.id] = data.data.is_correct
  }

  submitted.value = true

  const correctCount = Object.values(results).filter(v => v).length
  ElMessage.success(`答对 ${correctCount}/${questions.value.length} 题`)
}

const getTypeText = (type) => {
  const map = { single: '单选', multiple: '多选', blank: '填空', judge: '判断' }
  return map[type] || ''
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
.settings-card {
  margin-top: 20px;
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  padding: 24px;
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
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.settings-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.settings-form {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: flex-end;
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
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.6);
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.3s ease;
}

.subject-option:hover {
  border-color: var(--primary-light);
}

.subject-option.active {
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.1) 0%, rgba(132, 94, 247, 0.1) 100%);
  border-color: var(--primary);
}

.subject-icon {
  font-size: 20px;
}

/* 题数输入 */
.count-input {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.6);
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-sm);
  padding: 4px;
}

.count-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 18px;
  font-weight: 700;
  transition: all 0.3s ease;
}

.count-btn:hover {
  transform: scale(1.1);
}

.count-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  min-width: 40px;
  text-align: center;
}

/* 复选框 */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
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
  font-size: 14px;
  color: var(--text-primary);
}

/* 开始按钮 */
.start-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 32px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
  margin-left: auto;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 157, 0.4);
}

.btn-icon {
  font-size: 20px;
}

/* 题目区域 */
.questions-area {
  margin-top: 24px;
}

.question-card {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(255, 255, 255, 0.6);
  animation: slideIn 0.5s ease backwards;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(255, 107, 157, 0.1);
}

.q-index {
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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

.question-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-primary);
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(255, 245, 247, 0.5) 0%, rgba(240, 230, 255, 0.5) 100%);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--primary);
}

/* 选项 */
.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  line-height: 1.5;
  color: var(--text-primary);
}

/* 判断题 */
.judge-options {
  display: flex;
  gap: 20px;
}

.judge-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.6);
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.judge-btn:hover:not(:disabled) {
  border-color: var(--primary-light);
  transform: translateY(-2px);
}

.judge-btn.selected {
  border-color: var(--primary);
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.1) 0%, rgba(132, 94, 247, 0.1) 100%);
}

.judge-btn.correct {
  border-color: var(--accent);
  background: linear-gradient(135deg, rgba(32, 201, 151, 0.1) 0%, rgba(150, 242, 215, 0.1) 100%);
}

.judge-btn.wrong {
  border-color: var(--danger);
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 150, 150, 0.1) 100%);
}

.judge-icon {
  font-size: 32px;
  font-weight: 700;
}

/* 填空题 */
.blank-input {
  max-width: 100%;
}

.blank-field {
  width: 100%;
  padding: 14px 20px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-md);
  font-size: 16px;
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
  outline: none;
}

.blank-field:focus {
  border-color: var(--primary);
  box-shadow: 0 4px 15px rgba(255, 107, 157, 0.15);
}

.blank-field:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 答案结果 */
.answer-result {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding: 20px;
  border-radius: var(--radius-md);
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

.answer-result.correct {
  background: linear-gradient(135deg, rgba(32, 201, 151, 0.1) 0%, rgba(150, 242, 215, 0.1) 100%);
  border: 2px solid rgba(32, 201, 151, 0.2);
}

.answer-result.wrong {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 150, 150, 0.1) 100%);
  border: 2px solid rgba(255, 107, 107, 0.2);
}

.result-icon {
  font-size: 36px;
}

.result-text {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
}

.answer-result.correct .result-text {
  color: var(--accent);
}

.answer-result.wrong .result-text {
  color: var(--danger);
}

.result-answer {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 提交区域 */
.submit-area {
  margin-top: 24px;
  text-align: center;
}

.submit-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 48px;
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

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 157, 0.4);
}

.submit-btn.restart {
  background: linear-gradient(135deg, var(--accent) 0%, #38D9A9 100%);
  box-shadow: 0 4px 15px rgba(32, 201, 151, 0.3);
}

.submit-btn.restart:hover {
  box-shadow: 0 6px 20px rgba(32, 201, 151, 0.4);
}

/* 响应式 */
@media (max-width: 768px) {
  .settings-form {
    flex-direction: column;
    align-items: stretch;
  }

  .start-btn {
    margin-left: 0;
    justify-content: center;
  }

  .judge-options {
    flex-direction: column;
  }
}
</style>
