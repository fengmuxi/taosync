<template>
  <div class="theme-toggle" @click="toggleTheme">
    <i :class="isDarkMode ? 'el-icon-sunny' : 'el-icon-moon'" class="theme-icon"></i>
  </div>
</template>

<script>
export default {
  name: 'ThemeToggle',
  data() {
    return {
      isDarkMode: false,
      prefersDark: window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches,
    }
  },
  mounted() {
    // 初始化主题 - 检查本地存储和用户偏好
    this.initTheme();
    
    // 监听系统主题变化
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      this.prefersDark = e.matches;
      if (!localStorage.getItem('theme')) {
        this.setTheme(this.prefersDark);
      }
    });
  },
  methods: {
    initTheme() {
      // 优先从本地存储获取主题偏好
      const savedTheme = localStorage.getItem('theme');
      
      if (savedTheme) {
        this.setTheme(savedTheme === 'dark');
      } else {
        // 没有保存的主题偏好时，使用系统偏好
        this.setTheme(this.prefersDark);
      }
    },
    setTheme(dark) {
      this.isDarkMode = dark;
      const body = document.body;
      
      if (dark) {
        body.classList.remove('light');
        body.classList.add('dark');
      } else {
        body.classList.remove('dark');
        body.classList.add('light');
      }
      
      // 保存主题偏好到本地存储
      localStorage.setItem('theme', dark ? 'dark' : 'light');
    },
    toggleTheme() {
      this.setTheme(!this.isDarkMode);
    }
  }
}
</script>

<style scoped>
.theme-toggle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
}

.theme-toggle:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.theme-icon {
  font-size: 18px;
  color: var(--color-primary);
  transition: transform 0.5s ease;
}

.theme-toggle:hover .theme-icon {
  transform: rotate(360deg);
}
</style>