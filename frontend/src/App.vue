<template>
  <div id="app">
    <nav v-if="!isAdminRoute">
      <div class="nav-container">
        <div class="nav-left">
          <router-link to="/" class="nav-logo"> 🎬 电影推荐系统 </router-link>
          <router-link to="/">首页</router-link>
          <router-link to="/douban">电影库</router-link>
          <router-link to="/about">智能推荐</router-link>
          <router-link to="/community">💬 社区</router-link>
          <router-link to="/ai-chat">🤖 AI机器人对话</router-link>
        </div>

        <div class="nav-search">
          <div class="search-wrap" ref="searchWrap">
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="搜索电影、导演、演员..."
              @input="onSearchInput"
              @focus="showResults = searchResults.length > 0"
              @keydown.enter="onSearchEnter"
              @blur="onSearchBlur"
            />
            <div
              class="search-dropdown"
              v-if="showResults && searchResults.length > 0"
            >
              <div
                v-for="movie in searchResults"
                :key="movie.id"
                class="search-item"
                @mousedown.prevent="goToMovie(movie)"
              >
                <div class="sr-title">{{ movie.title }}</div>
                <div class="sr-meta">
                  <span v-if="movie.year">{{ movie.year }}</span>
                  <span v-if="movie.rating">⭐ {{ movie.rating }}</span>
                  <span v-if="movie.genre">{{ movie.genre }}</span>
                </div>
              </div>
            </div>
          </div>
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
import { defineComponent, ref, computed, onMounted, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useThemeStore } from "@/stores/theme";
import { useRouter } from "vue-router";

const API_BASE_URL = "http://localhost:8000/api";

interface SearchMovie {
  id: number;
  title: string;
  year: number | null;
  rating: number | null;
  director: string;
  genre: string;
}

export default defineComponent({
  name: "App",
  setup() {
    const authStore = useAuthStore();
    const themeStore = useThemeStore();
    const router = useRouter();

    const isAdminRoute = computed(() =>
      router.currentRoute.value.path.startsWith("/admin")
    );

    const searchQuery = ref("");
    const searchResults = ref<SearchMovie[]>([]);
    const showResults = ref(false);
    let searchTimer: ReturnType<typeof setTimeout> | null = null;

    const onSearchInput = () => {
      if (searchTimer) clearTimeout(searchTimer);
      const q = searchQuery.value.trim();
      if (!q) {
        searchResults.value = [];
        showResults.value = false;
        return;
      }
      searchTimer = setTimeout(async () => {
        try {
          const res = await fetch(
            `${API_BASE_URL}/search/?q=${encodeURIComponent(q)}`
          );
          if (res.ok) {
            const data = await res.json();
            searchResults.value = data.results || [];
            showResults.value = searchResults.value.length > 0;
          }
        } catch {
          // 搜索失败静默忽略
        }
      }, 200);
    };

    const onSearchEnter = () => {
      const q = searchQuery.value.trim();
      if (!q) return;
      showResults.value = false;
      router.push({ path: "/douban", query: { search: q } });
    };

    const onSearchBlur = () => {
      setTimeout(() => {
        showResults.value = false;
      }, 200);
    };

    const goToMovie = (movie: SearchMovie) => {
      showResults.value = false;
      searchQuery.value = "";
      const detail = {
        id: movie.id,
        movie_id: movie.id,
        电影名字: movie.title,
        电影链接: "",
        评分: String(movie.rating || ""),
        评分人数: "",
        导演: movie.director || "",
        主演: "",
        年份: String(movie.year || ""),
        国家: "",
        类型: movie.genre || "",
        一句话评价: "",
      };
      sessionStorage.setItem("current_movie_detail", JSON.stringify(detail));
      router.push({
        path: "/movie-detail",
        query: { movie_id: movie.id, movie_title: movie.title },
      });
    };

    // 从电影库页搜索参数跳转时同步
    watch(
      () => router.currentRoute.value.query.search,
      (val) => {
        if (val) searchQuery.value = val as string;
      }
    );

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
      isAdminRoute,
      searchQuery,
      searchResults,
      showResults,
      onSearchInput,
      onSearchEnter,
      onSearchBlur,
      goToMovie,
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

.nav-search {
  flex: 1;
  max-width: 360px;
  margin: 0 16px;
}

.search-wrap {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 8px 14px;
  border-radius: var(--radius-full);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  font-size: 0.9rem;
  outline: none;
  transition: all var(--transition-fast);
}

.search-input:focus {
  border-color: var(--input-focus-border);
  box-shadow: var(--input-focus-shadow);
}

.search-dropdown {
  position: absolute;
  top: 42px;
  left: 0;
  right: 0;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
  z-index: 200;
  max-height: 380px;
  overflow-y: auto;
}

.search-item {
  padding: 12px 14px;
  cursor: pointer;
  border-bottom: 1px solid var(--panel-border);
  transition: background var(--transition-fast);
}

.search-item:last-child {
  border-bottom: none;
}

.search-item:hover {
  background: var(--nav-hover-bg);
}

.sr-title {
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.sr-meta {
  display: flex;
  gap: 10px;
  font-size: 0.84rem;
  color: var(--text-secondary);
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
