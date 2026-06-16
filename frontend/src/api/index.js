import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 全局错误拦截
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg = error.response?.data?.message || error.message || '请求失败'
    // 不重复弹导入相关的错误（Home.vue 自己处理）
    if (!error.config?.url?.includes('/import')) {
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

// 科目相关
export const getSubjects = () => api.get('/subjects')
export const getChapters = (subjectId) => api.get(`/subjects/${subjectId}/chapters`)

// 题目相关
export const getChapterQuestions = (chapterId) => api.get(`/chapters/${chapterId}/questions`)
export const getQuestionDetail = (questionId) => api.get(`/questions/${questionId}`)
export const getRandomQuestions = (params) => api.get('/questions/random', { params })
export const submitAnswer = (questionId, answer) => api.post(`/questions/${questionId}/answer`, { answer })

// 收藏相关
export const getFavorites = (subjectId) => api.get('/favorites', { params: { subject_id: subjectId } })
export const addFavorite = (questionId) => api.post(`/favorites/${questionId}`)
export const removeFavorite = (questionId) => api.delete(`/favorites/${questionId}`)

// 错题相关
export const getWrongQuestions = (subjectId) => api.get('/records/wrong', { params: { subject_id: subjectId } })

// 统计相关
export const getStatsOverview = (subjectId) => api.get('/stats/overview', { params: { subject_id: subjectId } })
export const getChapterStats = (subjectId) => api.get('/stats/chapters', { params: { subject_id: subjectId } })

// 进度相关
export const getLastPosition = (subjectId) => api.get('/progress/last', { params: { subject_id: subjectId } })
export const savePosition = (data) => api.post('/progress/save', data)
export const clearAllProgress = () => api.delete('/progress')

// 导入题库（单独超时 120s）
export const importQuestions = (mode) => api.post('/import', { mode }, { timeout: 120000 })

export default api
