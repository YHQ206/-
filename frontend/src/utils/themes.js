// 主题配置
export const themes = {
  cute: {
    name: '清新可爱',
    icon: '🌸',
    description: '温暖渐变色，圆润卡片，柔和阴影',
    vars: {
      // 主色调
      '--primary': '#FF6B9D',
      '--primary-light': '#FFB3D0',
      '--secondary': '#845EF7',
      '--secondary-light': '#B197FC',
      '--accent': '#20C997',
      '--accent-light': '#96F2D7',
      '--warning': '#FFC078',
      '--danger': '#FF6B6B',

      // 背景
      '--bg-gradient': 'linear-gradient(135deg, #FFF5F7 0%, #F0E6FF 50%, #E6F9FF 100%)',
      '--card-bg': 'rgba(255, 255, 255, 0.85)',
      '--card-shadow': '0 8px 32px rgba(255, 107, 157, 0.1)',
      '--card-hover-shadow': '0 12px 40px rgba(255, 107, 157, 0.2)',

      // 文字
      '--text-primary': '#2D3436',
      '--text-secondary': '#636E72',
      '--text-light': '#B2BEC3',

      // 圆角
      '--radius-sm': '12px',
      '--radius-md': '16px',
      '--radius-lg': '24px',
      '--radius-xl': '32px',

      // 特殊
      '--header-bg': 'rgba(255, 255, 255, 0.9)',
      '--header-border': 'rgba(255, 255, 255, 0.5)',
      '--input-bg': 'rgba(255, 255, 255, 0.6)',
      '--option-hover': 'rgba(255, 107, 157, 0.05)',
      '--gradient-primary': 'linear-gradient(135deg, #FF6B9D 0%, #845EF7 100%)',
      '--gradient-accent': 'linear-gradient(135deg, #20C997 0%, #38D9A9 100%)',
      '--el-color-primary': '#FF6B9D',
    }
  },

  dark: {
    name: '暗黑酷炫',
    icon: '🌙',
    description: '深色背景，霓虹渐变，科技感十足',
    vars: {
      '--primary': '#00D4FF',
      '--primary-light': '#00A3CC',
      '--secondary': '#FF00FF',
      '--secondary-light': '#CC00CC',
      '--accent': '#00FF88',
      '--accent-light': '#00CC6A',
      '--warning': '#FFD700',
      '--danger': '#FF4444',

      '--bg-gradient': 'linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0d0d2b 100%)',
      '--card-bg': 'rgba(20, 20, 50, 0.9)',
      '--card-shadow': '0 8px 32px rgba(0, 212, 255, 0.15)',
      '--card-hover-shadow': '0 12px 40px rgba(0, 212, 255, 0.25)',

      '--text-primary': '#E8E8FF',
      '--text-secondary': '#A0A0CC',
      '--text-light': '#666699',

      '--radius-sm': '8px',
      '--radius-md': '12px',
      '--radius-lg': '16px',
      '--radius-xl': '24px',

      '--header-bg': 'rgba(15, 15, 40, 0.95)',
      '--header-border': 'rgba(0, 212, 255, 0.2)',
      '--input-bg': 'rgba(30, 30, 60, 0.8)',
      '--option-hover': 'rgba(0, 212, 255, 0.1)',
      '--gradient-primary': 'linear-gradient(135deg, #00D4FF 0%, #FF00FF 100%)',
      '--gradient-accent': 'linear-gradient(135deg, #00FF88 0%, #00D4FF 100%)',
      '--el-color-primary': '#00D4FF',
    }
  },

  glass: {
    name: '玻璃拟态',
    icon: '✨',
    description: '毛玻璃效果，半透明卡片，很有质感',
    vars: {
      '--primary': '#6366F1',
      '--primary-light': '#818CF8',
      '--secondary': '#EC4899',
      '--secondary-light': '#F472B6',
      '--accent': '#14B8A6',
      '--accent-light': '#2DD4BF',
      '--warning': '#F59E0B',
      '--danger': '#EF4444',

      '--bg-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
      '--card-bg': 'rgba(255, 255, 255, 0.2)',
      '--card-shadow': '0 8px 32px rgba(0, 0, 0, 0.15)',
      '--card-hover-shadow': '0 12px 40px rgba(0, 0, 0, 0.2)',

      '--text-primary': '#FFFFFF',
      '--text-secondary': 'rgba(255, 255, 255, 0.8)',
      '--text-light': 'rgba(255, 255, 255, 0.6)',

      '--radius-sm': '12px',
      '--radius-md': '20px',
      '--radius-lg': '28px',
      '--radius-xl': '36px',

      '--header-bg': 'rgba(255, 255, 255, 0.15)',
      '--header-border': 'rgba(255, 255, 255, 0.2)',
      '--input-bg': 'rgba(255, 255, 255, 0.15)',
      '--option-hover': 'rgba(255, 255, 255, 0.1)',
      '--gradient-primary': 'linear-gradient(135deg, #6366F1 0%, #EC4899 100%)',
      '--gradient-accent': 'linear-gradient(135deg, #14B8A6 0%, #6366F1 100%)',
      '--el-color-primary': '#6366F1',
    }
  },

  minimal: {
    name: '简约精致',
    icon: '🎨',
    description: '保持干净但加点颜色和动效，不会太花',
    vars: {
      '--primary': '#3B82F6',
      '--primary-light': '#60A5FA',
      '--secondary': '#8B5CF6',
      '--secondary-light': '#A78BFA',
      '--accent': '#10B981',
      '--accent-light': '#34D399',
      '--warning': '#F59E0B',
      '--danger': '#EF4444',

      '--bg-gradient': 'linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%)',
      '--card-bg': 'rgba(255, 255, 255, 0.95)',
      '--card-shadow': '0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06)',
      '--card-hover-shadow': '0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)',

      '--text-primary': '#111827',
      '--text-secondary': '#6B7280',
      '--text-light': '#9CA3AF',

      '--radius-sm': '8px',
      '--radius-md': '12px',
      '--radius-lg': '16px',
      '--radius-xl': '20px',

      '--header-bg': 'rgba(255, 255, 255, 0.98)',
      '--header-border': 'rgba(0, 0, 0, 0.05)',
      '--input-bg': 'rgba(255, 255, 255, 0.9)',
      '--option-hover': 'rgba(59, 130, 246, 0.05)',
      '--gradient-primary': 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
      '--gradient-accent': 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
      '--el-color-primary': '#3B82F6',
    }
  }
}

// 获取保存的主题或默认主题
export const getSavedTheme = () => {
  return localStorage.getItem('shuti-theme') || 'cute'
}

// 保存主题
export const saveTheme = (themeKey) => {
  localStorage.setItem('shuti-theme', themeKey)
}

// 应用主题到DOM
export const applyTheme = (themeKey) => {
  const theme = themes[themeKey]
  if (!theme) return

  const root = document.documentElement
  Object.entries(theme.vars).forEach(([key, value]) => {
    root.style.setProperty(key, value)
  })

  // 添加主题类名
  root.className = `theme-${themeKey}`

  // 更新 Element Plus 主题色
  const style = document.getElementById('theme-style') || document.createElement('style')
  style.id = 'theme-style'

  const primaryColor = theme.vars['--primary']
  const primaryLight = theme.vars['--primary-light']

  style.textContent = `
    .theme-${themeKey} .el-button--primary {
      --el-button-bg-color: ${primaryColor};
      --el-button-border-color: ${primaryColor};
    }
    .theme-${themeKey} .el-radio-button__inner:hover {
      color: ${primaryColor};
    }
    .theme-${themeKey} .el-checkbox__input.is-checked .el-checkbox__inner {
      background-color: ${primaryColor};
      border-color: ${primaryColor};
    }
    .theme-${themeKey} .el-switch.is-checked .el-switch__core {
      background-color: ${primaryColor};
      border-color: ${primaryColor};
    }
    .theme-${themeKey} .el-tag--primary {
      --el-tag-bg-color: ${primaryLight}33;
      --el-tag-border-color: ${primaryLight}66;
      --el-tag-text-color: ${primaryColor};
    }
    .theme-${themeKey} .el-pagination.is-background .el-pager li:not(.is-disabled).is-active {
      background-color: ${primaryColor};
    }
  `

  if (!document.getElementById('theme-style')) {
    document.head.appendChild(style)
  }
}
