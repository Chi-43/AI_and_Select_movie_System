<template>
  <div id="app">
    <nav>
      <div class="nav-container">
        <div class="nav-left">
          <router-link to="/" class="nav-logo"> 🎬 电影推荐系统 </router-link>
          <router-link to="/">首页</router-link>
          <router-link to="/douban">豆瓣电影TOP250</router-link>
          <router-link to="/ai-chat">🤖 AI对话</router-link>
          <router-link to="/about">关于</router-link>
        </div>

        <div class="nav-right">
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
import { useRouter } from "vue-router";

export default defineComponent({
  name: "App",
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();

    // 初始化认证状态
    onMounted(() => {
      authStore.initialize();
    });

    const handleLogout = async () => {
      await authStore.logout();
      router.push("/login");
    };

    return {
      authStore,
      handleLogout,
    };
  },
});
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

nav {
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-logo {
  font-weight: bold;
  font-size: 1.2rem;
  color: #667eea;
  text-decoration: none;
  margin-right: 10px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

nav a {
  font-weight: 500;
  color: #4a5568;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s;
}

nav a:hover {
  color: #667eea;
  background: #f7fafc;
}

nav a.router-link-exact-active {
  color: #667eea;
  background: #edf2f7;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.username {
  color: #4a5568;
  font-weight: 500;
}

.logout-btn {
  padding: 6px 12px;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: #c53030;
}

.register-link {
  background: #667eea;
  color: white !important;
}

.register-link:hover {
  background: #5a67d8 !important;
}

main {
  flex: 1;
  max-width: 1200px;
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
    gap: 10px;
  }

  main {
    padding: 10px;
  }
}
</style>
