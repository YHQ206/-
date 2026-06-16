<template>
  <div id="app">
    <div class="app-bg">
      <!-- 装饰性浮动元素（只在可爱主题显示） -->
      <div class="floating-shapes theme-cute-only">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
        <div class="shape shape-5"></div>
      </div>

      <el-container>
        <el-header>
          <div class="header-content">
            <div class="logo" @click="$router.push('/')">
              <span class="logo-icon">📚</span>
              <span class="logo-text">刷题助手</span>
            </div>
            <div class="header-right">
              <el-menu mode="horizontal" :router="true" :default-active="$route.path">
                <el-menu-item index="/">
                  <el-icon><HomeFilled /></el-icon>
                  首页
                </el-menu-item>
                <el-menu-item index="/wrong">
                  <el-icon><Notebook /></el-icon>
                  错题本
                </el-menu-item>
                <el-menu-item index="/favorites">
                  <el-icon><Star /></el-icon>
                  收藏夹
                </el-menu-item>
                <el-menu-item index="/random">
                  <el-icon><Refresh /></el-icon>
                  随机刷题
                </el-menu-item>
              </el-menu>
              <ThemeSwitcher />
            </div>
          </div>
        </el-header>
        <el-main>
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </div>
  </div>
</template>

<script setup>
import { HomeFilled, Notebook, Star, Refresh } from '@element-plus/icons-vue'
import ThemeSwitcher from './components/ThemeSwitcher.vue'
</script>

<style>
/* 导入可爱字体 */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  /* 默认主题变量（会被JS覆盖） */
  --primary: #FF6B9D;
  --primary-light: #FFB3D0;
  --secondary: #845EF7;
  --secondary-light: #B197FC;
  --accent: #20C997;
  --accent-light: #96F2D7;
  --warning: #FFC078;
  --danger: #FF6B6B;

  --bg-gradient: linear-gradient(135deg, #FFF5F7 0%, #F0E6FF 50%, #E6F9FF 100%);
  --card-bg: rgba(255, 255, 255, 0.85);
  --card-shadow: 0 8px 32px rgba(255, 107, 157, 0.1);
  --card-hover-shadow: 0 12px 40px rgba(255, 107, 157, 0.2);

  --text-primary: #2D3436;
  --text-secondary: #636E72;
  --text-light: #B2BEC3;

  --radius-sm: 12px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-xl: 32px;

  --header-bg: rgba(255, 255, 255, 0.9);
  --header-border: rgba(255, 255, 255, 0.5);
  --input-bg: rgba(255, 255, 255, 0.6);
  --option-hover: rgba(255, 107, 157, 0.05);
  --gradient-primary: linear-gradient(135deg, #FF6B9D 0%, #845EF7 100%);
  --gradient-accent: linear-gradient(135deg, #20C997 0%, #38D9A9 100%);
}

body {
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-gradient);
  min-height: 100vh;
  overflow-x: hidden;
  transition: background 0.5s ease;
}

/* 背景容器 */
.app-bg {
  min-height: 100vh;
  position: relative;
}

/* 浮动装饰元素（只在可爱主题显示） */
.theme-cute-only {
  display: none;
}

.theme-cute .theme-cute-only {
  display: block;
}

.floating-shapes {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
  animation: float 20s ease-in-out infinite;
}

.shape-1 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, var(--primary-light) 0%, transparent 70%);
  top: -50px;
  right: -50px;
  animation-delay: 0s;
}

.shape-2 {
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, var(--secondary-light) 0%, transparent 70%);
  bottom: 10%;
  left: -30px;
  animation-delay: -5s;
}

.shape-3 {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, var(--accent-light) 0%, transparent 70%);
  top: 40%;
  right: 10%;
  animation-delay: -10s;
}

.shape-4 {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--warning) 0%, transparent 70%);
  top: 60%;
  left: 15%;
  animation-delay: -15s;
}

.shape-5 {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, var(--primary-light) 0%, transparent 70%);
  bottom: -30px;
  right: 20%;
  animation-delay: -8s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(20px, -30px) rotate(5deg);
  }
  50% {
    transform: translate(-10px, 20px) rotate(-3deg);
  }
  75% {
    transform: translate(15px, 10px) rotate(2deg);
  }
}

/* 头部导航 */
.el-header {
  background: var(--header-bg) !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.08) !important;
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid var(--header-border);
  transition: all 0.3s ease;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: transform 0.3s;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 28px;
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

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 菜单样式 */
.el-menu {
  border-bottom: none !important;
  background: transparent !important;
}

.el-menu--horizontal {
  border-bottom: none !important;
}

.el-menu-item {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary) !important;
  border-radius: var(--radius-sm) !important;
  margin: 0 4px;
  transition: all 0.3s !important;
}

.el-menu-item:hover {
  background: var(--option-hover) !important;
  color: var(--primary) !important;
}

.el-menu-item.is-active {
  background: var(--gradient-primary) !important;
  color: #fff !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

.el-menu-item .el-icon {
  margin-right: 6px;
}

/* 主内容区 */
.el-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
  min-height: calc(100vh - 60px);
  position: relative;
  z-index: 1;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Element Plus 组件美化 */
.el-card {
  background: var(--card-bg) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--header-border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--card-shadow) !important;
  transition: all 0.3s ease !important;
}

.el-card:hover {
  box-shadow: var(--card-hover-shadow) !important;
  transform: translateY(-2px);
}

.el-card__header {
  border-bottom: 1px solid rgba(128, 128, 128, 0.1) !important;
  font-weight: 600;
  color: var(--text-primary);
}

/* 按钮美化 */
.el-button--primary {
  background: var(--gradient-primary) !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease !important;
}

.el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.el-button--primary:active {
  transform: translateY(0);
}

/* 输入框美化 */
.el-input__wrapper {
  border-radius: var(--radius-sm) !important;
  background: var(--input-bg) !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04) !important;
  transition: all 0.3s ease !important;
}

.el-input__wrapper:hover,
.el-input__wrapper.is-focus {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
}

/* 标签页美化 */
.el-tabs__item {
  font-weight: 500;
  transition: all 0.3s ease !important;
}

.el-tabs__item.is-active {
  color: var(--primary) !important;
  font-weight: 600;
}

.el-tabs__active-bar {
  background: var(--gradient-primary) !important;
  height: 3px !important;
  border-radius: 2px !important;
}

/* 进度条美化 */
.el-progress-bar__outer {
  border-radius: 10px !important;
  background: rgba(128, 128, 128, 0.1) !important;
}

.el-progress-bar__inner {
  border-radius: 10px !important;
  background: var(--gradient-accent) !important;
}

/* 空状态美化 */
.el-empty__description p {
  color: var(--text-secondary);
  font-size: 15px;
}

/* 消息提示美化 */
.el-message {
  border-radius: var(--radius-sm) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
}

/* 对话框美化 */
.el-dialog {
  border-radius: var(--radius-lg) !important;
  overflow: hidden;
  background: var(--card-bg) !important;
}

.el-dialog__header {
  background: var(--gradient-primary);
  padding: 20px 24px !important;
}

.el-dialog__title {
  color: #fff;
  font-weight: 600;
}

.el-dialog__body {
  padding: 24px !important;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(128, 128, 128, 0.05);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--primary-light);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary);
}

/* 暗黑主题特殊样式 */
.theme-dark .el-menu-item.is-active {
  color: #000 !important;
}

.theme-dark .el-dialog__header {
  background: linear-gradient(135deg, #00D4FF 0%, #FF00FF 100%);
}

.theme-dark .el-dialog__title {
  color: #000;
}

/* 玻璃主题特殊样式 */
.theme-glass .el-menu-item.is-active {
  color: #fff !important;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}
</style>
