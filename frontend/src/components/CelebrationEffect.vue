<template>
  <div class="celebration-container" v-if="show">
    <!-- 烟花粒子 -->
    <div
      v-for="(particle, index) in particles"
      :key="index"
      class="particle"
      :style="particle.style"
    >
      {{ particle.emoji }}
    </div>

    <!-- 连胜文字 -->
    <div class="streak-text" v-if="streak >= 3">
      🔥 连续答对 {{ streak }} 题！
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  streak: {
    type: Number,
    default: 0
  }
})

const particles = ref([])
let animationTimer = null

const emojis = ['🎉', '✨', '🌟', '💫', '🎊', '⭐', '💖', '🎈', '🦋', '🌸', '🎆', '🎇']

const createParticles = () => {
  const newParticles = []
  const count = props.streak >= 10 ? 30 : props.streak >= 5 ? 20 : 12

  for (let i = 0; i < count; i++) {
    const emoji = emojis[Math.floor(Math.random() * emojis.length)]
    const startX = 50 + (Math.random() - 0.5) * 60
    const startY = 100
    const endX = startX + (Math.random() - 0.5) * 80
    const endY = -20 - Math.random() * 80
    const duration = 1 + Math.random() * 1.5
    const delay = Math.random() * 0.5
    const rotation = (Math.random() - 0.5) * 720
    const scale = 0.5 + Math.random() * 1.5

    newParticles.push({
      emoji,
      style: {
        '--start-x': `${startX}%`,
        '--start-y': `${startY}%`,
        '--end-x': `${endX}%`,
        '--end-y': `${endY}%`,
        '--rotation': `${rotation}deg`,
        '--scale': scale,
        '--duration': `${duration}s`,
        '--delay': `${delay}s`,
        left: `${startX}%`,
        top: `${startY}%`,
        animation: `particle-float ${duration}s ease-out ${delay}s forwards`
      }
    })
  }

  particles.value = newParticles
}

watch(() => props.show, (newVal) => {
  if (newVal && props.streak >= 3) {
    createParticles()
    animationTimer = setTimeout(() => {
      particles.value = []
    }, 3000)
  } else {
    particles.value = []
  }
})

onUnmounted(() => {
  if (animationTimer) {
    clearTimeout(animationTimer)
  }
})
</script>

<style scoped>
.celebration-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9999;
  overflow: hidden;
}

.particle {
  position: absolute;
  font-size: 24px;
  animation-fill-mode: forwards;
  will-change: transform, opacity;
}

.streak-text {
  position: fixed;
  top: 20%;
  left: 50%;
  transform: translateX(-50%);
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #FF6B6B 0%, #FFD93D 50%, #6BCB77 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 4px 20px rgba(255, 107, 107, 0.3);
  animation: streak-pop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
  white-space: nowrap;
}

@keyframes particle-float {
  0% {
    transform: translate(0, 0) scale(var(--scale)) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translate(
      calc(var(--end-x) - var(--start-x)),
      calc(var(--end-y) - var(--start-y))
    ) scale(0) rotate(var(--rotation));
    opacity: 0;
  }
}

@keyframes streak-pop {
  0% {
    transform: translateX(-50%) scale(0) rotate(-10deg);
    opacity: 0;
  }
  50% {
    transform: translateX(-50%) scale(1.2) rotate(5deg);
    opacity: 1;
  }
  100% {
    transform: translateX(-50%) scale(1) rotate(0deg);
    opacity: 1;
  }
}
</style>
