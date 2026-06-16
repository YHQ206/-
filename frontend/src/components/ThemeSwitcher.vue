<template>
  <div class="theme-switcher">
    <button class="theme-toggle" @click="showPanel = !showPanel" title="切换主题">
      <span class="toggle-icon">🎨</span>
    </button>

    <transition name="slide">
      <div v-if="showPanel" class="theme-panel">
        <div class="panel-header">
          <span class="panel-title">🎨 选择主题</span>
          <button class="close-btn" @click="showPanel = false">✕</button>
        </div>
        <div class="theme-list">
          <button
            v-for="(theme, key) in themes"
            :key="key"
            class="theme-option"
            :class="{ active: currentTheme === key }"
            @click="switchTheme(key)"
          >
            <span class="theme-icon">{{ theme.icon }}</span>
            <div class="theme-info">
              <span class="theme-name">{{ theme.name }}</span>
              <span class="theme-desc">{{ theme.description }}</span>
            </div>
            <span v-if="currentTheme === key" class="check-icon">✓</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- 遮罩层 -->
    <div v-if="showPanel" class="overlay" @click="showPanel = false"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { themes, getSavedTheme, saveTheme, applyTheme } from '../utils/themes'

const showPanel = ref(false)
const currentTheme = ref(getSavedTheme())

const switchTheme = (key) => {
  currentTheme.value = key
  saveTheme(key)
  applyTheme(key)
}

onMounted(() => {
  applyTheme(currentTheme.value)
})
</script>

<style scoped>
.theme-switcher {
  position: relative;
}

.theme-toggle {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: var(--card-bg, rgba(255, 255, 255, 0.85));
  backdrop-filter: blur(10px);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.theme-toggle:hover {
  transform: scale(1.1) rotate(15deg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toggle-icon {
  font-size: 20px;
}

/* 主题面板 */
.theme-panel {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  width: 280px;
  background: var(--card-bg, rgba(255, 255, 255, 0.95));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--header-border, rgba(255, 255, 255, 0.5));
  overflow: hidden;
  z-index: 1000;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(128, 128, 128, 0.1);
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: none;
  background: rgba(128, 128, 128, 0.1);
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(128, 128, 128, 0.2);
  transform: scale(1.1);
}

.theme-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  border: 2px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.theme-option:hover {
  background: var(--option-hover, rgba(0, 0, 0, 0.03));
}

.theme-option.active {
  border-color: var(--primary);
  background: var(--option-hover, rgba(0, 0, 0, 0.03));
  box-shadow: 0 0 0 1px var(--primary);
}

.theme-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.theme-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.theme-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.theme-desc {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.3;
}

.check-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--gradient-primary, linear-gradient(135deg, #FF6B9D 0%, #845EF7 100%));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

/* 遮罩层 */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 999;
}

/* 动画 */
.slide-enter-active {
  animation: slide-down 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.slide-leave-active {
  animation: slide-down 0.2s ease reverse;
}

@keyframes slide-down {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
