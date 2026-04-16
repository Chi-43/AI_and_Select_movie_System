<template>
  <div id="app">
    <nav>
      <div class="nav-container">
        <div class="nav-left">
          <router-link to="/" class="nav-logo"> 🎬 电影推荐系统 </router-link>
          <router-link to="/">首页</router-link>
          <router-link to="/douban">电影库</router-link>
          <router-link to="/about">智能推荐</router-link>
          <router-link to="/ai-chat">🤖 AI机器人对话</router-link>
        </div>

        <div class="nav-right">
          <button @click="themeStore.toggleTheme()" class="theme-toggle-btn">
            {{ themeStore.isDark ? "☀️" : "🌙" }}
          </button>

          <div v-if="authStore.isAuthenticated" class="user-info">
            <router-link to="/profile" class="profile-link">
              👤 {{ authStore.user?.username }}
            </router-link>
            <button @click="handleLogout" class="logout-btn">退出</button>
          </div>
          <div v-else class="auth-links">
            <router-link to="/login">登录</router-link>
            <router-link to="/register" class="register-link">注册</router-link>
          </div>
        </div>
      </div>
    </nav>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useThemeStore } from "@/stores/theme";
import { useRouter } from "vue-router";

export default defineComponent({
  name: "App",
  setup() {
    const authStore = useAuthStore();
    const themeStore = useThemeStore();
    const router = useRouter();

    onMounted(() => {
      authStore.initialize();
      themeStore.initialize();
    });

    const handleLogout = async () => {
      await authStore.logout();
      router.push("/login");
    };

    return {
      authStore,
      themeStore,
      handleLogout,
    };
  },
});
</script>

<style>
#app {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-primary);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

nav {
  background: var(--nav-bg);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
  border-bottom: 1px solid var(--nav-border);
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 100;
  transition: background var(--transition-normal),
    border-color var(--transition-normal);
}

.nav-container {
  max-width: var(--max-width);
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-logo {
  font-weight: 800;
  font-size: 1.1rem;
  color: var(--primary) !important;
  text-decoration: none;
  margin-right: 10px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

nav a {
  font-weight: 500;
  color: var(--nav-text);
  text-decoration: none;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  font-size: var(--font-base);
}

nav a:hover {
  color: var(--nav-active-text);
  background: var(--nav-hover-bg);
}

nav a.router-link-exact-active {
  color: var(--nav-active-text);
  background: var(--nav-active-bg);
}

.theme-toggle-btn {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-full);
  border: 1px solid var(--panel-border);
  background: var(--panel-bg);
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.theme-toggle-btn:hover {
  background: var(--nav-hover-bg);
  transform: rotate(15deg);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-link {
  color: var(--nav-text) !important;
  font-weight: 600;
}

.logout-btn {
  padding: 6px 14px;
  background: var(--danger);
  color: var(--text-inverse);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--font-sm);
  font-weight: 600;
  transition: all var(--transition-fast);
}

.logout-btn:hover {
  opacity: 0.85;
  transform: translateY(-1px);
}

.auth-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

.register-link {
  background: var(--primary-gradient) !important;
  color: #fff !important;
  padding: 8px 16px !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
}

.register-link:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

main {
  flex: 1;
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 20px;
  width: 100%;
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    height: auto;
    padding: 10px 0;
  }

  .nav-left,
  .nav-right {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  main {
    padding: 10px;
  }
}
</style>
