import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/chapter/:id',
    name: 'Chapter',
    component: () => import('../views/Chapter.vue')
  },
  {
    path: '/quiz/:chapterId/:index?',
    name: 'Quiz',
    component: () => import('../views/Quiz.vue')
  },
  {
    path: '/wrong',
    name: 'WrongBook',
    component: () => import('../views/WrongBook.vue')
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('../views/Favorites.vue')
  },
  {
    path: '/random',
    name: 'RandomQuiz',
    component: () => import('../views/RandomQuiz.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
