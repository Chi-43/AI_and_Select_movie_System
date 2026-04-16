<template>
  <div class="recommend-view">
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">智能推荐</div>
        <h1 class="hero-title">🎯 智能电影推荐中心</h1>
        <p class="hero-subtitle">
          结合协同过滤、用户画像与大模型推荐理由，为你提供更智能、更可解释的电影推荐体验。
        </p>

        <div class="hero-tags">
          <span v-for="tag in displayTags" :key="tag" class="hero-tag">
            {{ tag }}
          </span>
        </div>

        <div class="hero-actions">
          <button class="primary-btn" @click="loadPersonalizedRecommendations">
            获取个性化推荐
          </button>
          <button class="secondary-btn" @click="scrollToNaturalRecommend">
            自然语言推荐
          </button>
        </div>
      </div>

      <div class="hero-side">
        <div class="hero-stat-card">
          <div class="stat-number">
            {{ personalizedRecommendations.length }}
          </div>
          <div class="stat-label">当前推荐结果</div>
        </div>
        <div class="hero-stat-card">
          <div class="stat-number">
            {{ profileSummary.favorite_genres.length || 0 }}
          </div>
          <div class="stat-label">偏好类型</div>
        </div>
        <div class="hero-stat-card">
          <div class="stat-number">
            {{ currentUser ? currentUser.username : "访客" }}
          </div>
          <div class="stat-label">当前用户</div>
        </div>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>👤 你的推荐画像</h2>
        <p>根据用户偏好与评分行为生成的画像摘要</p>
      </div>

      <div class="profile-summary-grid">
        <div class="summary-card">
          <h3>偏好类型</h3>
          <div class="chip-group">
            <span
              v-for="item in profileSummary.favorite_genres"
              :key="item"
              class="info-chip"
            >
              {{ item }}
            </span>
            <span
              v-if="profileSummary.favorite_genres.length === 0"
              class="empty-chip"
            >
              暂无
            </span>
          </div>
        </div>

        <div class="summary-card">
          <h3>偏好国家</h3>
          <div class="chip-group">
            <span
              v-for="item in profileSummary.favorite_countries"
              :key="item"
              class="info-chip"
            >
              {{ item }}
            </span>
            <span
              v-if="profileSummary.favorite_countries.length === 0"
              class="empty-chip"
            >
              暂无
            </span>
          </div>
        </div>

        <div class="summary-card full-width">
          <h3>画像总结</h3>
          <p class="summary-text">
            {{
              profileSummary.profile_summary ||
              "当前暂无画像总结，请先进行兴趣偏好设置或评分行为积累。"
            }}
          </p>
        </div>
      </div>
    </section>

    <section class="section-card" ref="naturalRecommendRef">
      <div class="section-header">
        <h2>💬 自然语言推荐</h2>
        <p>直接告诉系统你的观影需求，例如：推荐几部适合周末看的高分科幻电影</p>
      </div>

      <div class="nl-recommend-box">
        <textarea
          v-model="naturalQuery"
          class="nl-textarea"
          rows="3"
          placeholder="请输入你的观影需求..."
        ></textarea>

        <div class="nl-actions">
          <div class="quick-prompts">
            <button
              v-for="item in quickPrompts"
              :key="item"
              class="prompt-chip"
              @click="naturalQuery = item"
            >
              {{ item }}
            </button>
          </div>

          <button
            class="primary-btn"
            @click="runNaturalLanguageRecommend"
            :disabled="naturalLoading || !naturalQuery.trim()"
          >
            {{ naturalLoading ? "推荐中..." : "开始推荐" }}
          </button>
        </div>
      </div>

      <div v-if="naturalReply" class="reply-box">
        <h3>AI 推荐说明</h3>
        <p>{{ naturalReply }}</p>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>✨ 个性化推荐</h2>
        <p>基于当前用户评分记录与画像信息生成的推荐结果</p>
      </div>

      <div class="toolbar">
        <div class="toolbar-left">
          <button
            v-for="item in recommendModes"
            :key="item.value"
            @click="setRecommendMode(item.value)"
            :class="['mode-btn', { active: recommendMode === item.value }]"
          >
            {{ item.label }}
          </button>
        </div>
        <button class="secondary-btn" @click="loadPersonalizedRecommendations">
          刷新推荐
        </button>
      </div>

      <div v-if="recommendLoading" class="loading-state">
        <div class="spinner"></div>
        <p>正在为你生成推荐结果...</p>
      </div>

      <div v-else-if="currentRecommendations.length === 0" class="empty-state">
        <div class="empty-icon">🎬</div>
        <h3>暂无推荐结果</h3>
        <p>可以先尝试自然语言推荐，或者刷新个性化推荐。</p>
      </div>

      <div v-else class="movie-grid">
        <div
          v-for="movie in currentRecommendations"
          :key="movie.movie.id"
          class="movie-card"
        >
          <div class="movie-card-header">
            <div>
              <h3 class="movie-title">{{ movie.movie.title }}</h3>
              <div class="movie-meta">
                <span>{{ movie.movie.year }}</span>
                <span>{{ movie.movie.genre }}</span>
                <span>{{ movie.movie.country }}</span>
              </div>
            </div>
            <div class="movie-rating">⭐ {{ movie.movie.rating }}</div>
          </div>

          <p class="movie-description">
            {{ movie.movie.description || "暂无简介" }}
          </p>

          <div class="movie-extra">
            <span class="meta-chip">算法：{{ movie.algorithm }}</span>
            <span class="meta-chip">分数：{{ movie.score }}</span>
          </div>

          <div class="reason-box" v-if="movie.reason">
            {{ movie.reason }}
          </div>

          <div class="movie-actions">
            <a
              v-if="movie.movie.douban_url"
              :href="movie.movie.douban_url"
              target="_blank"
              class="secondary-btn link-btn"
            >
              查看详情
            </a>
            <button
              class="primary-btn"
              @click="askAIAboutMovie(movie.movie.title)"
            >
              AI 分析
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>🔥 热门精选</h2>
        <p>系统内当前高分热门电影推荐</p>
      </div>

      <div v-if="topLoading" class="loading-state">
        <div class="spinner"></div>
        <p>正在加载热门电影...</p>
      </div>

      <div v-else class="top-grid">
        <div v-for="item in topMovies" :key="item.movie.id" class="top-card">
          <div class="top-rank">{{ item.rank }}</div>
          <div class="top-info">
            <h3>{{ item.movie.title }}</h3>
            <p>{{ item.movie.genre }}</p>
            <span>⭐ {{ item.movie.rating }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";
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

interface RecommendationItem {
  movie: MovieInfo;
  score: number;
  algorithm: string;
  reason?: string;
}

interface ProfileSummary {
  favorite_genres: string[];
  favorite_countries: string[];
  favorite_keywords: string[];
  favorite_years: { min?: number; max?: number };
  profile_summary: string;
  onboarding_completed: boolean;
}

export default defineComponent({
  name: "AboutView",
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();

    const currentUser = computed(() => authStore.user);

    const profileSummary = ref<ProfileSummary>({
      favorite_genres: [],
      favorite_countries: [],
      favorite_keywords: [],
      favorite_years: {},
      profile_summary: "",
      onboarding_completed: false,
    });

    const recommendMode = ref<"user_based" | "cold_start">("user_based");
    const recommendLoading = ref(false);
    const topLoading = ref(false);
    const naturalLoading = ref(false);

    const personalizedRecommendations = ref<RecommendationItem[]>([]);
    const naturalRecommendations = ref<RecommendationItem[]>([]);
    const topMovies = ref<any[]>([]);
    const naturalQuery = ref("");
    const naturalReply = ref("");
    const naturalRecommendRef = ref<HTMLElement | null>(null);

    const quickPrompts = [
      "推荐几部适合周末看的高分科幻电影",
      "我想看像《盗梦空间》一样烧脑的电影",
      "推荐几部不太压抑的悬疑电影",
      "推荐几部适合家庭观看的温暖电影",
    ];

    const recommendModes = [
      { label: "用户协同过滤", value: "user_based" as const },
      { label: "冷启动推荐", value: "cold_start" as const },
    ];

    const currentRecommendations = computed(() => {
      return naturalRecommendations.value.length > 0
        ? naturalRecommendations.value
        : personalizedRecommendations.value;
    });

    const displayTags = computed(() => {
      const tags = [
        ...profileSummary.value.favorite_genres.slice(0, 2),
        ...profileSummary.value.favorite_keywords.slice(0, 2),
      ];
      if (tags.length === 0) {
        return ["智能推荐", "个性化", "电影发现"];
      }
      return tags;
    });

    const authHeaders = computed(() => ({
      Authorization: `Token ${authStore.token}`,
    }));

    const loadUserProfile = async () => {
      if (!authStore.token) return;

      try {
        const response = await axios.get(`${API_BASE_URL}/user-profile/`, {
          headers: authHeaders.value,
        });
        profileSummary.value = {
          favorite_genres: response.data.favorite_genres || [],
          favorite_countries: response.data.favorite_countries || [],
          favorite_keywords: response.data.favorite_keywords || [],
          favorite_years: response.data.favorite_years || {},
          profile_summary: response.data.profile_summary || "",
          onboarding_completed: response.data.onboarding_completed || false,
        };
      } catch (error) {
        console.error("加载用户画像失败:", error);
      }
    };

    const loadPersonalizedRecommendations = async () => {
      recommendLoading.value = true;
      naturalRecommendations.value = [];
      naturalReply.value = "";

      try {
        const userId = currentUser.value?.id || 1;
        const response = await axios.get(`${API_BASE_URL}/recommendations/`, {
          params: {
            user_id: userId,
            algorithm: recommendMode.value,
            top_n: 8,
          },
        });

        personalizedRecommendations.value = response.data.recommendations || [];
      } catch (error) {
        console.error("加载个性化推荐失败:", error);
        personalizedRecommendations.value = [];
      } finally {
        recommendLoading.value = false;
      }
    };

    const loadTopMovies = async () => {
      topLoading.value = true;
      try {
        const response = await axios.get(`${API_BASE_URL}/top-movies/`);
        topMovies.value = (response.data.top_movies || []).map(
          (item: any, index: number) => ({
            ...item,
            rank: index + 1,
          })
        );
      } catch (error) {
        console.error("加载热门电影失败:", error);
        topMovies.value = [];
      } finally {
        topLoading.value = false;
      }
    };

    const runNaturalLanguageRecommend = async () => {
      if (!naturalQuery.value.trim()) return;

      naturalLoading.value = true;
      try {
        const response = await axios.post(`${API_BASE_URL}/ai/nl-recommend/`, {
          query: naturalQuery.value,
          user_id: currentUser.value?.id || 1,
          top_n: 8,
        });

        naturalReply.value = response.data.reply || "";
        naturalRecommendations.value = response.data.recommendations || [];
      } catch (error) {
        console.error("自然语言推荐失败:", error);
        naturalReply.value = "抱歉，当前推荐失败，请稍后重试。";
        naturalRecommendations.value = [];
      } finally {
        naturalLoading.value = false;
      }
    };

    const setRecommendMode = (mode: "user_based" | "cold_start") => {
      recommendMode.value = mode;
      loadPersonalizedRecommendations();
    };

    const askAIAboutMovie = (title: string) => {
      router.push({
        path: "/aichat",
        query: {
          question: `请分析一下《${title}》这部电影`,
        },
      });
    };

    const scrollToNaturalRecommend = () => {
      naturalRecommendRef.value?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    };

    onMounted(async () => {
      await loadUserProfile();
      await loadPersonalizedRecommendations();
      await loadTopMovies();
    });

    return {
      currentUser,
      profileSummary,
      recommendMode,
      recommendModes,
      recommendLoading,
      topLoading,
      naturalLoading,
      personalizedRecommendations,
      naturalRecommendations,
      currentRecommendations,
      topMovies,
      naturalQuery,
      naturalReply,
      quickPrompts,
      displayTags,
      naturalRecommendRef,
      loadPersonalizedRecommendations,
      runNaturalLanguageRecommend,
      setRecommendMode,
      askAIAboutMovie,
      scrollToNaturalRecommend,
    };
  },
});
</script>

<style scoped>
.recommend-view {
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
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 24px;
  align-items: start;
}

.hero-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.16);
  font-size: 0.9rem;
  margin-bottom: 16px;
}

.hero-title {
  margin: 0 0 12px;
  font-size: 2.4rem;
  font-weight: 800;
  color: #fff;
}

.hero-subtitle {
  margin: 0 0 18px;
  max-width: 760px;
  line-height: 1.8;
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.92);
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 22px;
}

.hero-tag {
  padding: 7px 12px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  font-size: 0.88rem;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.hero-stat-card {
  border-radius: var(--radius-md);
  padding: 18px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 800;
  color: #fff;
  word-break: break-word;
}

.stat-label {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.92rem;
}

.section-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
  padding: 28px;
}

.section-header {
  margin-bottom: 18px;
}

.section-header h2 {
  margin: 0 0 8px;
  color: var(--text-primary);
  font-size: 1.6rem;
}

.section-header p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.profile-summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.summary-card {
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  padding: 18px;
}

.summary-card.full-width {
  grid-column: 1 / -1;
}

.summary-card h3 {
  margin: 0 0 12px;
  color: var(--text-primary);
}

.summary-text {
  margin: 0;
  line-height: 1.8;
  color: var(--text-secondary);
}

.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.info-chip,
.empty-chip,
.meta-chip,
.prompt-chip {
  padding: 7px 12px;
  border-radius: var(--radius-full);
  font-size: 0.88rem;
}

.info-chip {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.empty-chip {
  background: var(--nav-hover-bg);
  color: var(--text-muted);
}

.nl-recommend-box {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.nl-textarea {
  width: 100%;
  min-height: 96px;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  resize: vertical;
  font-size: 0.98rem;
  line-height: 1.7;
}

.nl-textarea:focus {
  outline: none;
  border-color: var(--input-focus-border);
}

.nl-actions {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  flex-wrap: wrap;
}

.quick-prompts {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.prompt-chip {
  border: none;
  background: var(--nav-hover-bg);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.prompt-chip:hover {
  background: var(--nav-active-bg);
  color: var(--nav-active-text);
}

.reply-box {
  margin-top: 18px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  border: 1px dashed var(--panel-border);
}

.reply-box h3 {
  margin: 0 0 8px;
  color: var(--text-primary);
}

.reply-box p {
  margin: 0;
  line-height: 1.8;
  color: var(--text-secondary);
}

.toolbar {
  margin-bottom: 18px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.mode-btn {
  border: 1px solid var(--panel-border);
  background: var(--panel-bg);
  color: var(--text-secondary);
  border-radius: var(--radius-full);
  padding: 9px 14px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 700;
  transition: all var(--transition-fast);
}

.mode-btn.active {
  background: var(--primary-gradient);
  color: #fff;
  border-color: transparent;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 18px;
}

.movie-card,
.top-card {
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  padding: 18px;
  transition: all var(--transition-fast);
}

.movie-card:hover,
.top-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--panel-shadow);
}

.movie-card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 12px;
}

.movie-title {
  margin: 0;
  font-size: 1.08rem;
  color: var(--text-primary);
}

.movie-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.movie-meta span {
  padding: 4px 8px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.movie-rating {
  white-space: nowrap;
  font-weight: 700;
  color: #d97706;
}

.movie-description {
  margin: 0 0 12px;
  color: var(--text-secondary);
  line-height: 1.7;
  font-size: 0.92rem;
}

.movie-extra {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.meta-chip {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.reason-box {
  margin-bottom: 14px;
  padding: 12px;
  border-radius: var(--radius-sm);
  background: var(--panel-bg);
  border: 1px dashed var(--panel-border);
  color: var(--text-secondary);
  line-height: 1.7;
  font-size: 0.92rem;
}

.movie-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.top-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.top-card {
  display: flex;
  gap: 14px;
  align-items: center;
}

.top-rank {
  width: 42px;
  height: 42px;
  min-width: 42px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.top-info h3 {
  margin: 0 0 6px;
  color: var(--text-primary);
  font-size: 1rem;
}

.top-info p,
.top-info span {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 46px 24px;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 14px;
}

.spinner {
  width: 46px;
  height: 46px;
  border: 4px solid rgba(102, 126, 234, 0.14);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 18px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.primary-btn,
.secondary-btn {
  border: none;
  border-radius: var(--radius-sm);
  padding: 11px 18px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.primary-btn {
  background: var(--primary-gradient);
  color: #fff;
}

.secondary-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.link-btn {
  background: var(--nav-hover-bg);
}

.primary-btn:hover,
.secondary-btn:hover {
  transform: translateY(-1px);
}

.primary-btn:disabled,
.secondary-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 1100px) {
  .hero-section {
    grid-template-columns: 1fr;
  }

  .profile-summary-grid {
    grid-template-columns: 1fr;
  }

  .summary-card.full-width {
    grid-column: auto;
  }
}

@media (max-width: 768px) {
  .hero-section,
  .section-card {
    padding: 20px;
  }

  .hero-title {
    font-size: 2rem;
  }

  .nl-actions,
  .toolbar,
  .movie-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .movie-grid,
  .top-grid {
    grid-template-columns: 1fr;
  }
}
</style>
