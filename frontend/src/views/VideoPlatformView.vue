<template>
  <div class="video-platform-view">
    <div class="header">
      <h1>🎬 电影视频平台观看链接</h1>
      <p class="subtitle">查找电影在各大视频平台的观看链接，标注VIP/付费信息</p>
    </div>

    <div class="container">
      <div class="search-section">
        <div class="search-box">
          <input
            v-model="searchMovieTitle"
            type="text"
            placeholder="输入电影名称..."
            class="search-input"
            @keyup.enter="searchPlatformLinks"
          />
          <button @click="searchPlatformLinks" class="search-btn">
            🔍 搜索观看链接
          </button>
        </div>

        <div class="search-tips">
          <p>💡 提示：支持按电影名搜索，也支持通过豆瓣链接直接跳转到本页</p>
        </div>
      </div>

      <div v-if="currentMovie" class="movie-info-section">
        <div class="movie-card">
          <div class="movie-header">
            <h2 class="movie-title">{{ currentMovie["电影名字"] }}</h2>
            <div class="movie-rating">
              <span class="rating-star">⭐</span>
              <span class="rating-score">{{ currentMovie["评分"] }}</span>
            </div>
          </div>

          <div class="movie-details">
            <div class="detail-row">
              <span class="detail-label">年份:</span>
              <span class="detail-value">{{ currentMovie["年份"] }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">国家:</span>
              <span class="detail-value">{{ currentMovie["国家"] }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">类型:</span>
              <span class="detail-value">{{ currentMovie["类型"] }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">导演:</span>
              <span class="detail-value">{{
                currentMovie["导演"] || "未知"
              }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">主演:</span>
              <span class="detail-value">{{
                currentMovie["主演"] || "未知"
              }}</span>
            </div>
          </div>

          <div v-if="currentMovie['一句话评价']" class="movie-quote">
            <span class="quote-icon">💬</span>
            <span class="quote-text">{{ currentMovie["一句话评价"] }}</span>
          </div>

          <div class="movie-actions">
            <a
              :href="currentMovie['电影链接']"
              target="_blank"
              class="action-btn douban-link"
            >
              查看豆瓣详情
            </a>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-section">
        <div class="loading-spinner"></div>
        <p>正在搜索观看链接...</p>
      </div>

      <div v-else-if="error" class="error-section">
        <div class="error-icon">❌</div>
        <p class="error-message">{{ error }}</p>
        <button @click="searchPlatformLinks" class="retry-btn">重试</button>
      </div>

      <div
        v-else-if="platformLinks && platformLinks.total_links > 0"
        class="results-section"
      >
        <div class="results-header">
          <h3>🎯 找到 {{ platformLinks.total_platforms }} 个平台的观看链接</h3>
          <p class="results-summary">
            共 {{ platformLinks.total_links }} 个链接
            <span v-if="platformLinks.source"
              >，数据来源：{{ platformLinks.source }}</span
            >
          </p>
        </div>

        <div class="platforms-grid">
          <div
            v-for="(platformName, index) in Object.keys(
              platformLinks.platforms
            )"
            :key="index"
            class="platform-card"
          >
            <div class="platform-header">
              <div class="platform-title-wrap">
                <img
                  v-if="platformLinks.platforms[platformName][0]?.icon"
                  :src="platformLinks.platforms[platformName][0].icon"
                  :alt="platformName"
                  class="platform-icon"
                />
                <h4 class="platform-title">{{ platformName }}</h4>
              </div>

              <span class="platform-count">
                {{ platformLinks.platforms[platformName].length }} 个链接
              </span>
            </div>

            <div class="platform-links">
              <div
                v-for="(link, linkIndex) in platformLinks.platforms[
                  platformName
                ]"
                :key="linkIndex"
                class="link-item"
              >
                <div class="link-header">
                  <a
                    :href="link.platform_url"
                    target="_blank"
                    class="link-title"
                  >
                    {{
                      link.movie_title ||
                      platformLinks.movie_title ||
                      searchMovieTitle
                    }}
                  </a>

                  <span
                    :class="{
                      'vip-badge': link.vip_status === 'vip',
                      'free-badge': link.vip_status === 'free',
                      'pay-badge':
                        link.vip_status === 'pay' ||
                        link.vip_status === 'rent' ||
                        link.vip_status === 'unknown',
                    }"
                  >
                    {{ link.vip_status_display || "未知" }}
                    <span v-if="link.price" class="price-tag"
                      >¥{{ link.price }}</span
                    >
                  </span>
                </div>

                <div v-if="link.price_info" class="price-info">
                  {{ link.price_info }}
                </div>

                <div class="link-details">
                  <span v-if="link.quality" class="quality-badge">
                    {{ link.quality }}
                  </span>
                  <span v-if="link.last_checked" class="update-time">
                    更新: {{ formatDate(link.last_checked) }}
                  </span>
                  <span v-else class="update-time">实时抓取</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-else-if="searched && platformLinks && platformLinks.total_links === 0"
        class="no-results-section"
      >
        <div class="no-results-icon">😕</div>
        <h3>未找到观看链接</h3>
        <p>
          {{
            platformLinks.message || "抱歉，没有找到该电影的视频平台观看链接。"
          }}
        </p>
        <div class="suggestions">
          <p>建议：</p>
          <ul>
            <li>检查电影名称是否正确</li>
            <li>尝试从热门电影中点击进入</li>
            <li>该电影可能暂时没有在线观看资源</li>
          </ul>
        </div>
      </div>

      <div class="recommendations-section">
        <h3>🔥 热门电影推荐</h3>
        <div class="recommendations-grid">
          <div
            v-for="movie in popularMovies"
            :key="movie['电影链接']"
            class="recommendation-card"
            @click="selectMovie(movie)"
          >
            <div class="rec-header">
              <h4>{{ movie["电影名字"] }}</h4>
              <span class="rec-rating">⭐ {{ movie["评分"] }}</span>
            </div>
            <div class="rec-info">
              <span class="rec-year">{{ movie["年份"] }}</span>
              <span class="rec-country">{{ movie["国家"] }}</span>
            </div>
            <p class="rec-quote" v-if="movie['一句话评价']">
              {{ movie["一句话评价"] }}
            </p>
            <button class="rec-btn" @click.stop="selectMovie(movie)">
              查看观看链接
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import doubanData from "../data/豆瓣电影TOP250.json";

interface DoubanMovie {
  电影名字: string;
  电影链接: string;
  评分: string;
  评分人数: string;
  导演: string;
  主演: string;
  年份: string;
  国家: string;
  类型: string;
  一句话评价: string;
}

interface PlatformLink {
  id: number | null;
  movie_title: string;
  douban_url?: string;
  platform?: string;
  platform_display?: string;
  platform_url: string;
  icon?: string;
  vip_status: string;
  vip_status_display: string;
  price: number | null;
  quality: string | null;
  price_info?: string;
  available?: boolean;
  last_checked?: string | null;
  source?: string;
}

interface PlatformLinksResponse {
  movie_title: string;
  douban_url: string;
  source?: string;
  total_platforms: number;
  total_links: number;
  message?: string;
  platforms: {
    [platformName: string]: PlatformLink[];
  };
}

const API_BASE_URL = "http://localhost:8000";

export default defineComponent({
  name: "VideoPlatformView",
  setup() {
    const route = useRoute();
    const router = useRouter();

    const allMovies = ref<DoubanMovie[]>([]);
    const popularMovies = ref<DoubanMovie[]>([]);
    const currentMovie = ref<DoubanMovie | null>(null);
    const platformLinks = ref<PlatformLinksResponse | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const searched = ref(false);
    const searchMovieTitle = ref("");

    const loadMovies = () => {
      try {
        allMovies.value = doubanData as DoubanMovie[];

        popularMovies.value = [...allMovies.value]
          .sort((a, b) => parseFloat(b["评分"]) - parseFloat(a["评分"]))
          .slice(0, 6);

        const movieTitle = (route.query.movie_title as string) || "";
        const doubanUrl = (route.query.douban_url as string) || "";

        if (movieTitle) {
          searchMovieTitle.value = movieTitle;
        }

        if (movieTitle || doubanUrl) {
          const movie = allMovies.value.find(
            (m) =>
              m["电影链接"] === doubanUrl ||
              m["电影名字"].includes(movieTitle) ||
              movieTitle.includes(m["电影名字"])
          );

          if (movie) {
            currentMovie.value = movie;
            if (!searchMovieTitle.value) {
              searchMovieTitle.value = movie["电影名字"];
            }
          }

          searchPlatformLinks();
        }
      } catch (err) {
        console.error("加载电影数据失败:", err);
        error.value = "加载电影数据失败，请刷新页面重试";
      }
    };

    const searchPlatformLinks = async () => {
      const rawTitle = searchMovieTitle.value.trim();
      const routeDoubanUrl = (route.query.douban_url as string) || "";

      if (!rawTitle && !routeDoubanUrl) {
        error.value = "请输入电影名称";
        return;
      }

      loading.value = true;
      error.value = null;
      searched.value = true;
      platformLinks.value = null;

      try {
        let movie =
          allMovies.value.find(
            (m) =>
              m["电影名字"].includes(rawTitle) ||
              m["电影名字"].toLowerCase().includes(rawTitle.toLowerCase()) ||
              m["电影链接"] === routeDoubanUrl
          ) || null;

        if (movie) {
          currentMovie.value = movie;
        }

        const movieTitleForApi = movie?.["电影名字"] || rawTitle || "";
        const doubanUrlForApi = movie?.["电影链接"] || routeDoubanUrl || "";

        const params = new URLSearchParams();
        if (movieTitleForApi) params.append("movie_title", movieTitleForApi);
        if (doubanUrlForApi) params.append("douban_url", doubanUrlForApi);

        const response = await fetch(
          `${API_BASE_URL}/api/video-platform-links/?${params.toString()}`
        );

        if (!response.ok) {
          throw new Error(`API请求失败: ${response.status}`);
        }

        const data: PlatformLinksResponse = await response.json();
        platformLinks.value = data;

        if (!currentMovie.value && data.movie_title) {
          const matchedMovie = allMovies.value.find(
            (m) =>
              m["电影名字"].includes(data.movie_title) ||
              data.movie_title.includes(m["电影名字"])
          );
          if (matchedMovie) {
            currentMovie.value = matchedMovie;
          }
        }

        router.replace({
          query: {
            movie_title:
              currentMovie.value?.["电影名字"] || data.movie_title || rawTitle,
            douban_url:
              currentMovie.value?.["电影链接"] ||
              data.douban_url ||
              doubanUrlForApi,
          },
        });
      } catch (err) {
        console.error("搜索平台链接失败:", err);
        error.value = "搜索观看链接失败，请稍后重试";
      } finally {
        loading.value = false;
      }
    };

    const selectMovie = (movie: DoubanMovie) => {
      currentMovie.value = movie;
      searchMovieTitle.value = movie["电影名字"];

      router.replace({
        query: {
          movie_title: movie["电影名字"],
          douban_url: movie["电影链接"],
        },
      });

      searchPlatformLinks();
    };

    const formatDate = (dateString?: string | null) => {
      if (!dateString) return "未知";
      const date = new Date(dateString);
      if (Number.isNaN(date.getTime())) return "未知";
      return date.toLocaleDateString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });
    };

    onMounted(() => {
      loadMovies();
    });

    return {
      currentMovie,
      platformLinks,
      popularMovies,
      loading,
      error,
      searched,
      searchMovieTitle,
      searchPlatformLinks,
      selectMovie,
      formatDate,
    };
  },
});
</script>

<style scoped>
.video-platform-view {
  min-height: 100vh;
  padding: 26px;
  max-width: 1400px;
  margin: 0 auto;
  background: radial-gradient(
      900px 600px at 15% 20%,
      rgba(99, 102, 241, 0.35),
      transparent 60%
    ),
    radial-gradient(
      800px 520px at 85% 10%,
      rgba(139, 92, 246, 0.3),
      transparent 55%
    ),
    radial-gradient(
      900px 600px at 50% 95%,
      rgba(16, 185, 129, 0.18),
      transparent 55%
    ),
    linear-gradient(135deg, #0b1220 0%, #111827 55%, #0b1220 100%);
  overflow-x: hidden;

  --panel: rgba(255, 255, 255, 0.08);
  --panel-2: rgba(255, 255, 255, 0.06);
  --border: rgba(255, 255, 255, 0.14);
  --text: rgba(255, 255, 255, 0.92);
  --muted: rgba(148, 163, 184, 0.95);
  --primary: #6366f1;
  --primary2: #8b5cf6;
  --shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
  --shadow-soft: 0 16px 50px rgba(0, 0, 0, 0.25);
  color: var(--text);
}

.header {
  text-align: center;
  margin-bottom: 26px;
  padding: 26px 18px;
  border-radius: 22px;
  background: linear-gradient(
      135deg,
      rgba(99, 102, 241, 0.75),
      rgba(139, 92, 246, 0.7)
    ),
    rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.header h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 900;
  letter-spacing: 0.2px;
  color: rgba(255, 255, 255, 0.95);
}

.subtitle {
  margin: 12px 0 0;
  font-size: 13px;
  color: rgba(226, 232, 240, 0.92);
}

.container {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.search-section,
.movie-info-section,
.results-section,
.no-results-section,
.recommendations-section,
.loading-section,
.error-section {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 22px;
  padding: 18px;
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  position: relative;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
}

.search-input {
  flex: 1;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(17, 24, 39, 0.65);
  color: rgba(255, 255, 255, 0.92);
  font-size: 14px;
  outline: none;
}

.search-input::placeholder {
  color: rgba(148, 163, 184, 0.75);
}

.search-btn,
.retry-btn,
.rec-btn {
  padding: 12px 16px;
  border: none;
  border-radius: 14px;
  cursor: pointer;
  background: linear-gradient(135deg, var(--primary), var(--primary2));
  color: white;
  font-size: 14px;
  font-weight: 900;
  box-shadow: 0 18px 50px rgba(99, 102, 241, 0.35);
}

.search-tips {
  padding: 12px;
  border-radius: 14px;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: rgba(191, 219, 254, 0.95);
  font-size: 13px;
}

.movie-card,
.platform-card,
.recommendation-card {
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(17, 24, 39, 0.45);
  border-radius: 18px;
  padding: 16px;
}

.movie-header,
.platform-header,
.rec-header,
.link-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.movie-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 14px;
  margin-top: 10px;
}

.detail-row {
  display: flex;
  gap: 8px;
  align-items: baseline;
  font-size: 13px;
}

.detail-label {
  color: rgba(148, 163, 184, 0.95);
  font-weight: 800;
  min-width: 40px;
}

.movie-quote {
  margin-top: 12px;
  padding: 12px;
  border-radius: 14px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.18);
  display: flex;
  gap: 10px;
}

.movie-actions {
  margin-top: 12px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 12px;
  border-radius: 14px;
  text-decoration: none;
  font-weight: 900;
  font-size: 13px;
}

.douban-link {
  background: linear-gradient(135deg, var(--primary), var(--primary2));
  color: #fff;
}

.loading-section,
.error-section,
.no-results-section {
  text-align: center;
}

.loading-spinner {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 3px solid rgba(148, 163, 184, 0.25);
  border-top-color: rgba(99, 102, 241, 0.95);
  margin: 6px auto 10px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.results-header h3,
.recommendations-section h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 900;
}

.results-summary {
  margin: 8px 0 0;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.95);
}

.platforms-grid,
.recommendations-grid {
  display: grid;
  gap: 14px;
  margin-top: 14px;
}

.platforms-grid {
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.recommendations-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.platform-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.platform-icon {
  width: 22px;
  height: 22px;
  object-fit: contain;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.95);
  padding: 2px;
}

.platform-title {
  margin: 0;
  font-size: 14px;
  font-weight: 900;
}

.platform-count,
.rec-info,
.update-time {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.95);
}

.platform-links {
  display: grid;
  gap: 10px;
}

.link-item {
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(255, 255, 255, 0.04);
}

.link-title {
  color: rgba(226, 232, 240, 0.95);
  font-weight: 900;
  text-decoration: none;
  font-size: 13px;
  line-height: 1.3;
}

.price-info {
  margin-top: 8px;
  font-size: 12px;
  color: rgba(226, 232, 240, 0.88);
}

.vip-badge,
.free-badge,
.pay-badge,
.quality-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 900;
  font-size: 12px;
  white-space: nowrap;
}

.vip-badge {
  background: rgba(245, 158, 11, 0.14);
  border: 1px solid rgba(245, 158, 11, 0.22);
  color: rgba(245, 158, 11, 0.95);
}

.free-badge {
  background: rgba(16, 185, 129, 0.14);
  border: 1px solid rgba(16, 185, 129, 0.22);
  color: rgba(16, 185, 129, 0.95);
}

.pay-badge {
  background: rgba(239, 68, 68, 0.14);
  border: 1px solid rgba(239, 68, 68, 0.22);
  color: rgba(239, 68, 68, 0.95);
}

.quality-badge {
  border: 1px solid rgba(99, 102, 241, 0.18);
  background: rgba(99, 102, 241, 0.1);
  color: rgba(226, 232, 240, 0.95);
}

.link-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  gap: 10px;
  font-size: 12px;
}

.suggestions {
  margin-top: 12px;
  text-align: left;
  max-width: 520px;
  margin-left: auto;
  margin-right: auto;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(17, 24, 39, 0.45);
}

.suggestions ul {
  margin: 0;
  padding-left: 18px;
  color: rgba(148, 163, 184, 0.95);
}

.recommendation-card {
  cursor: pointer;
}

.rec-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 900;
}

.rec-rating {
  font-size: 12px;
  font-weight: 900;
  color: rgba(245, 158, 11, 0.95);
}

.rec-quote {
  margin-top: 10px;
  color: rgba(226, 232, 240, 0.92);
  font-size: 12px;
  line-height: 1.6;
}

.rec-btn {
  margin-top: 12px;
  width: 100%;
}

@media (max-width: 768px) {
  .video-platform-view {
    padding: 16px;
  }

  .header h1 {
    font-size: 20px;
  }

  .search-box {
    flex-direction: column;
  }

  .movie-details {
    grid-template-columns: 1fr;
  }

  .link-header,
  .platform-header,
  .movie-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
