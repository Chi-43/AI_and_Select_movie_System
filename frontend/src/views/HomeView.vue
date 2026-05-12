<template>
  <div class="home-view">
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title" v-if="authStore.isAuthenticated">
          欢迎回来，{{ authStore.user?.username }}
        </h1>
        <h1 class="hero-title" v-else>发现你的下一部心仪电影</h1>
        <p class="hero-subtitle" v-if="authStore.isAuthenticated">
          基于你的评分记录与兴趣偏好，为你精选推荐
        </p>
        <p class="hero-subtitle" v-else>
          登录后获取个性化推荐，探索更多符合你口味的电影
        </p>
        <div class="hero-actions" v-if="!authStore.isAuthenticated">
          <router-link to="/login" class="primary-btn">立即登录</router-link>
          <router-link to="/register" class="secondary-btn"
            >注册账号</router-link
          >
        </div>
      </div>
      <div class="hero-stats">
        <div class="hero-stat-card">
          <div class="stat-number">{{ personalizedRecs.length }}</div>
          <div class="stat-label">为你推荐</div>
        </div>
        <div class="hero-stat-card">
          <div class="stat-number">{{ topMovies.length }}</div>
          <div class="stat-label">热门精选</div>
        </div>
      </div>
    </section>

    <section class="section-card" v-if="authStore.isAuthenticated">
      <div class="section-header">
        <h2>✨ 为你推荐</h2>
        <button
          class="refresh-btn"
          @click="refreshRecommendations"
          :disabled="recsLoading"
        >
          {{ recsLoading ? "加载中..." : "换一批" }}
        </button>
      </div>

      <div v-if="recsLoading" class="loading-state">
        <div class="spinner"></div>
        <p>正在为你生成推荐...</p>
      </div>

      <div v-else-if="personalizedRecs.length === 0" class="empty-state">
        <p>暂无个性化推荐，去电影库评几部电影再来看看吧。</p>
        <router-link to="/douban" class="primary-btn">前往电影库</router-link>
      </div>

      <div v-else class="movie-grid">
        <div
          v-for="item in personalizedRecs"
          :key="item.movie.id"
          class="movie-card"
          @click="goToDetail(item.movie)"
        >
          <div class="card-header">
            <h3 class="movie-title">{{ item.movie.title }}</h3>
            <span class="movie-rating">⭐ {{ item.movie.rating }}</span>
          </div>
          <div class="movie-meta">
            <span>{{ item.movie.year }}</span>
            <span>{{ item.movie.genre }}</span>
            <span>{{ item.movie.country }}</span>
          </div>
          <p class="movie-desc">{{ item.movie.description || "暂无简介" }}</p>
          <div class="reason-box" v-if="item.reason">{{ item.reason }}</div>
          <div class="card-footer">
            <span class="algo-chip">{{ algoLabel(item.algorithm) }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="cta-card" v-if="!authStore.isAuthenticated">
      <div class="cta-content">
        <h2>想要更精准的个性化推荐？</h2>
        <p>注册账号，选择你的兴趣偏好，系统将为你量身推荐电影。</p>
      </div>
      <router-link to="/register" class="primary-btn">免费注册</router-link>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>🔥 热门精选</h2>
        <span class="section-sub">系统内高分热门电影</span>
      </div>

      <div v-if="topLoading" class="loading-state">
        <div class="spinner"></div>
      </div>

      <div v-else class="top-grid">
        <div
          v-for="(item, index) in topMovies"
          :key="item.movie.id"
          class="top-card"
          @click="goToDetail(item.movie)"
        >
          <div class="top-rank" :class="index < 3 ? 'top3' : ''">
            {{ index + 1 }}
          </div>
          <div class="top-info">
            <h3>{{ item.movie.title }}</h3>
            <div class="top-meta">
              <span>{{ item.movie.year }}</span>
              <span>{{ item.movie.genre }}</span>
            </div>
          </div>
          <div class="top-rating">⭐ {{ item.movie.rating }}</div>
        </div>
      </div>
    </section>

    <section class="section-card quick-links">
      <h2>快速探索</h2>
      <div class="link-grid">
        <router-link to="/about" class="link-card">
          <span class="link-icon">🎯</span>
          <span class="link-label">智能推荐</span>
          <span class="link-desc">自然语言描述你的观影需求</span>
        </router-link>
        <router-link to="/douban" class="link-card">
          <span class="link-icon">🎬</span>
          <span class="link-label">电影库</span>
          <span class="link-desc">浏览全部高分电影</span>
        </router-link>
        <router-link to="/ai-chat" class="link-card">
          <span class="link-icon">🤖</span>
          <span class="link-label">AI 对话</span>
          <span class="link-desc">和 AI 聊聊电影</span>
        </router-link>
        <router-link to="/profile" class="link-card">
          <span class="link-icon">👤</span>
          <span class="link-label">个人中心</span>
          <span class="link-desc">管理你的偏好与画像</span>
        </router-link>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch } from "vue";
import axios from "axios";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

const API_BASE_URL = "http://localhost:8000/api";

interface MovieInfo {
  id: number;
  title: string;
  genre: string;
  year: number;
  description: string;
  country: string;
  rating: number;
  douban_url?: string;
}

interface RecItem {
  movie: MovieInfo;
  score: number;
  algorithm: string;
  reason?: string;
}

export default defineComponent({
  name: "HomeView",
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();

    const personalizedRecs = ref<RecItem[]>([]);
    const topMovies = ref<any[]>([]);
    const recsLoading = ref(false);
    const topLoading = ref(false);

    const loadSavedRecommendations = async () => {
      if (!authStore.isAuthenticated || !authStore.token) return;

      recsLoading.value = true;
      try {
        const response = await axios.get(
          `${API_BASE_URL}/my-recommendations/`,
          {
            headers: { Authorization: `Token ${authStore.token}` },
          }
        );
        personalizedRecs.value = response.data.recommendations || [];
      } catch (error) {
        console.error("加载已保存推荐失败:", error);
      } finally {
        recsLoading.value = false;
      }
    };

    const refreshRecommendations = async () => {
      if (!authStore.isAuthenticated || !authStore.user) return;

      recsLoading.value = true;
      try {
        await axios.get(`${API_BASE_URL}/recommendations/`, {
          params: {
            user_id: authStore.user.id,
            algorithm: "user_based",
            top_n: 8,
          },
        });
        // 生成完成后重新读取已保存的推荐
        await loadSavedRecommendations();
      } catch (error) {
        console.error("刷新推荐失败:", error);
      } finally {
        recsLoading.value = false;
      }
    };

    const loadTopMovies = async () => {
      topLoading.value = true;
      try {
        const response = await axios.get(`${API_BASE_URL}/top-movies/`);
        topMovies.value = (response.data.top_movies || []).slice(0, 10);
      } catch (error) {
        console.error("加载热门电影失败:", error);
      } finally {
        topLoading.value = false;
      }
    };

    const algoLabel = (algo: string) => {
      const map: Record<string, string> = {
        user_based: "协同过滤",
        item_based: "基于物品",
        cold_start: "兴趣匹配",
        top: "热门推荐",
        hybrid: "混合推荐",
        nl_query: "自然语言推荐",
      };
      return map[algo] || algo;
    };

    const goToDetail = (movie: MovieInfo) => {
      const detailMovie = {
        id: movie.id,
        movie_id: movie.id,
        电影名字: movie.title,
        电影链接: movie.douban_url || "",
        评分: String(movie.rating || ""),
        评分人数: "",
        导演: "",
        主演: "",
        年份: String(movie.year || ""),
        国家: movie.country || "",
        类型: movie.genre || "",
        一句话评价: "",
      };
      sessionStorage.setItem(
        "current_movie_detail",
        JSON.stringify(detailMovie)
      );
      router.push({
        path: "/movie-detail",
        query: {
          movie_id: movie.id,
          movie_title: movie.title,
          douban_url: movie.douban_url || "",
        },
      });
    };

    onMounted(async () => {
      await loadTopMovies();
    });

    watch(
      () => authStore.isAuthenticated && !!authStore.user,
      (ready) => {
        if (ready) loadSavedRecommendations();
      },
      { immediate: true }
    );

    return {
      authStore,
      personalizedRecs,
      topMovies,
      recsLoading,
      topLoading,
      loadSavedRecommendations,
      refreshRecommendations,
      algoLabel,
      goToDetail,
    };
  },
});
</script>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-section {
  background: var(--bg-hero);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  padding: 36px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.hero-title {
  margin: 0 0 10px;
  font-size: 2rem;
  font-weight: 800;
}

.hero-subtitle {
  margin: 0 0 18px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.hero-stats {
  display: flex;
  gap: 14px;
}

.hero-stat-card {
  padding: 16px 22px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.12);
  text-align: center;
  min-width: 100px;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 800;
}

.stat-label {
  margin-top: 4px;
  font-size: 0.88rem;
  color: rgba(255, 255, 255, 0.88);
}

.section-card,
.cta-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  padding: 28px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.section-header h2 {
  margin: 0;
  font-size: 1.4rem;
  color: var(--text-primary);
}

.section-sub {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.cta-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.08),
    rgba(118, 75, 162, 0.08)
  );
  border-color: rgba(102, 126, 234, 0.2);
}

.cta-content h2 {
  margin: 0 0 6px;
  color: var(--text-primary);
}

.cta-content p {
  margin: 0;
  color: var(--text-secondary);
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.movie-card {
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  padding: 18px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.movie-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--panel-shadow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
}

.movie-title {
  margin: 0;
  font-size: 1.05rem;
  color: var(--text-primary);
}

.movie-rating {
  font-weight: 700;
  color: #d97706;
  white-space: nowrap;
}

.movie-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.movie-meta span {
  padding: 3px 8px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.movie-desc {
  margin: 0 0 10px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.reason-box {
  margin-bottom: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: var(--panel-bg);
  border: 1px dashed var(--panel-border);
  color: var(--text-secondary);
  font-size: 0.88rem;
  line-height: 1.6;
}

.card-footer {
  display: flex;
  gap: 8px;
}

.algo-chip {
  padding: 4px 10px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-muted);
  font-size: 0.78rem;
}

.top-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.top-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.top-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--panel-shadow);
}

.top-rank {
  width: 40px;
  height: 40px;
  min-width: 40px;
  border-radius: 50%;
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.top-rank.top3 {
  background: var(--primary-gradient);
  color: #fff;
}

.top-info {
  flex: 1;
  min-width: 0;
}

.top-info h3 {
  margin: 0 0 4px;
  font-size: 0.98rem;
  color: var(--text-primary);
}

.top-meta {
  display: flex;
  gap: 8px;
}

.top-meta span {
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.top-rating {
  font-weight: 700;
  color: #d97706;
  white-space: nowrap;
}

.quick-links h2 {
  margin: 0 0 16px;
  color: var(--text-primary);
}

.link-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.link-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 18px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.link-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--panel-shadow);
}

.link-icon {
  font-size: 1.5rem;
}

.link-label {
  font-weight: 700;
  color: var(--text-primary);
}

.link-desc {
  font-size: 0.84rem;
  color: var(--text-secondary);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(102, 126, 234, 0.14);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 14px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.primary-btn,
.secondary-btn,
.refresh-btn {
  border: none;
  border-radius: var(--radius-sm);
  padding: 10px 18px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.primary-btn {
  background: var(--primary-gradient);
  color: #fff;
}

.secondary-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.refresh-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
  font-size: 0.85rem;
  padding: 8px 14px;
}

.primary-btn:hover,
.secondary-btn:hover,
.refresh-btn:hover {
  transform: translateY(-1px);
}

@media (max-width: 900px) {
  .hero-section {
    flex-direction: column;
    text-align: center;
  }

  .hero-actions {
    justify-content: center;
  }

  .link-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .movie-grid,
  .top-grid,
  .link-grid {
    grid-template-columns: 1fr;
  }
}
</style>
