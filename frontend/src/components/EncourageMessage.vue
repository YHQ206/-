<template>
  <transition name="fade-up">
    <div v-if="show" class="encourage-message" :class="type">
      <span class="encourage-emoji">{{ emoji }}</span>
      <span class="encourage-text">{{ message }}</span>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'correct', // 'correct' or 'wrong'
    validator: (value) => ['correct', 'wrong'].includes(value)
  },
  streak: {
    type: Number,
    default: 0
  }
})

const correctMessages = [
  { emoji: '🎉', text: '太棒了！' },
  { emoji: '✨', text: '你真聪明！' },
  { emoji: '🌟', text: '答对啦！' },
  { emoji: '💪', text: '厉害！' },
  { emoji: '🎯', text: '完美！' },
  { emoji: '👏', text: '真厉害！' },
  { emoji: '💖', text: '太优秀了！' },
  { emoji: '🏆', text: '你是学霸！' },
  { emoji: '🥳', text: '答对了耶！' },
  { emoji: '😎', text: '轻松拿下！' }
]

const wrongMessages = [
  { emoji: '💪', text: '加油哦～' },
  { emoji: '🌈', text: '下次一定行！' },
  { emoji: '💝', text: '别灰心～' },
  { emoji: '🌸', text: '继续努力！' },
  { emoji: '💫', text: '你可以的！' },
  { emoji: '🍀', text: '再试一次！' },
  { emoji: '🧸', text: '没关系哦～' },
  { emoji: '🌻', text: '加油加油！' },
  { emoji: '⭐', text: '不要放弃！' },
  { emoji: '🎀', text: '慢慢来～' }
]

const streakMessages = {
  3: { emoji: '🔥', text: '连续3题！继续保持！' },
  5: { emoji: '🔥🔥', text: '连对5题！太强了！' },
  10: { emoji: '🔥🔥🔥', text: '连对10题！神了！' },
  15: { emoji: '⚡', text: '15连对！无敌！' },
  20: { emoji: '👑', text: '20连对！王者！' }
}

const getRandomMessage = (messages) => {
  return messages[Math.floor(Math.random() * messages.length)]
}

const message = computed(() => {
  // 检查是否有连胜消息
  if (props.type === 'correct' && props.streak >= 3) {
    const streakKey = Object.keys(streakMessages)
      .reverse()
      .find(k => props.streak >= parseInt(k))
    if (streakKey) {
      return streakMessages[streakKey].text
    }
  }

  const messages = props.type === 'correct' ? correctMessages : wrongMessages
  return getRandomMessage(messages).text
})

const emoji = computed(() => {
  // 检查是否有连胜emoji
  if (props.type === 'correct' && props.streak >= 3) {
    const streakKey = Object.keys(streakMessages)
      .reverse()
      .find(k => props.streak >= parseInt(k))
    if (streakKey) {
      return streakMessages[streakKey].emoji
    }
  }

  const messages = props.type === 'correct' ? correctMessages : wrongMessages
  return getRandomMessage(messages).emoji
})
</script>

<style scoped>
.encourage-message {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  margin-top: 8px;
}

.encourage-message.correct {
  background: linear-gradient(135deg, rgba(32, 201, 151, 0.15) 0%, rgba(150, 242, 215, 0.15) 100%);
  color: #388E3C;
  border: 1px solid rgba(32, 201, 151, 0.3);
}

.encourage-message.wrong {
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.15) 0%, rgba(132, 94, 247, 0.15) 100%);
  color: #D32F2F;
  border: 1px solid rgba(255, 107, 157, 0.3);
}

.encourage-emoji {
  font-size: 18px;
  animation: bounce 0.6s ease infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

.encourage-text {
  letter-spacing: 0.5px;
}

/* 过渡动画 */
.fade-up-enter-active {
  animation: fade-up 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.fade-up-leave-active {
  animation: fade-up 0.3s ease reverse;
}

@keyframes fade-up {
  0% {
    opacity: 0;
    transform: translateY(10px) scale(0.9);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
