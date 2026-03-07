<template>
  <div class="video-platform-view">
    <div class="header">
      <h1>🎬 电影视频平台观看链接</h1>
      <p class="subtitle">查找电影在各大视频平台的观看链接，标注VIP/付费信息</p>
    </div>

    <div class="container">
      <!-- 搜索区域 -->
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
          <p>💡 提示：您也可以从豆瓣电影页面点击"查看观看链接"跳转到此页面</p>
        </div>
      </div>

      <!-- 电影信息 -->
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

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-section">
        <div class="loading-spinner"></div>
        <p>正在搜索观看链接...</p>
      </div>

      <!-- 错误信息 -->
      <div v-else-if="error" class="error-section">
        <div class="error-icon">❌</div>
        <p class="error-message">{{ error }}</p>
        <button @click="searchPlatformLinks" class="retry-btn">重试</button>
      </div>

      <!-- 平台链接结果 -->
      <div
        v-else-if="platformLinks && platformLinks.total_links > 0"
        class="results-section"
      >
        <div class="results-header">
          <h3>🎯 找到 {{ platformLinks.total_platforms }} 个平台的观看链接</h3>
          <p class="results-summary">
            共 {{ platformLinks.total_links }} 个链接，最后更新:
            {{
              formatDate(
                platformLinks.platforms[
                  Object.keys(platformLinks.platforms)[0]
                ][0].last_checked
              )
            }}
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
              <h4 class="platform-title">{{ platformName }}</h4>
              <span class="platform-count"
                >{{ platformLinks.platforms[platformName].length }} 个链接</span
              >
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
                    {{ link.movie_title }}
                  </a>
                  <span
                    :class="{
                      'vip-badge': link.vip_status === 'vip',
                      'free-badge': link.vip_status === 'free',
                      'pay-badge':
                        link.vip_status === 'pay' || link.vip_status === 'rent',
                    }"
                  >
                    {{ link.vip_status_display }}
                    <span v-if="link.price" class="price-tag">
                      ¥{{ link.price }}
                    </span>
                  </span>
                </div>

                <div class="link-details">
                  <span v-if="link.quality" class="quality-badge">
                    {{ link.quality }}
                  </span>
                  <span class="update-time">
                    更新: {{ formatDate(link.last_checked) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 无结果 -->
      <div
        v-else-if="searched && platformLinks && platformLinks.total_links === 0"
        class="no-results-section"
      >
        <div class="no-results-icon">😕</div>
        <h3>未找到观看链接</h3>
        <p>抱歉，没有找到该电影的视频平台观看链接。</p>
        <div class="suggestions">
          <p>建议：</p>
          <ul>
            <li>检查电影名称是否正确</li>
            <li>尝试搜索其他电影</li>
            <li>该电影可能暂时没有在线观看资源</li>
          </ul>
        </div>
      </div>

      <!-- 热门电影推荐 -->
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
  id: number;
  movie_title: string;
  platform_url: string;
  vip_status: string;
  vip_status_display: string;
  price: number | null;
  quality: string | null;
  last_checked: string;
}

interface PlatformLinksResponse {
  movie_title: string;
  douban_url: string;
  total_platforms: number;
  total_links: number;
  platforms: {
    [platformName: string]: PlatformLink[];
  };
}

export default defineComponent({
  name: "VideoPlatformView",
  setup() {
    const route = useRoute();
    const router = useRouter();

    // 数据状态
    const allMovies = ref<DoubanMovie[]>([]);
    const popularMovies = ref<DoubanMovie[]>([]);
    const currentMovie = ref<DoubanMovie | null>(null);
    const platformLinks = ref<PlatformLinksResponse | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const searched = ref(false);

    // 搜索状态
    const searchMovieTitle = ref("");

    // 初始化数据
    const loadMovies = () => {
      try {
        allMovies.value = doubanData as DoubanMovie[];

        // 获取热门电影（评分最高的6部）
        popularMovies.value = [...allMovies.value]
          .sort((a, b) => parseFloat(b["评分"]) - parseFloat(a["评分"]))
          .slice(0, 6);

        // 检查URL参数
        const movieTitle = route.query.movie_title as string;
        const doubanUrl = route.query.douban_url as string;

        if (movieTitle) {
          searchMovieTitle.value = movieTitle;
          // 查找电影
          const movie = allMovies.value.find(
            (m) =>
              m["电影名字"].includes(movieTitle) || m["电影链接"] === doubanUrl
          );
          if (movie) {
            currentMovie.value = movie;
            searchPlatformLinks();
          }
        }
      } catch (err) {
        console.error("加载电影数据失败:", err);
        error.value = "加载电影数据失败，请刷新页面重试";
      }
    };

    // 搜索平台链接
    const searchPlatformLinks = async () => {
      if (!searchMovieTitle.value.trim()) {
        error.value = "请输入电影名称";
        return;
      }

      loading.value = true;
      error.value = null;
      searched.value = true;

      try {
        // 首先在本地数据中查找电影
        const movie = allMovies.value.find(
          (m) =>
            m["电影名字"].includes(searchMovieTitle.value) ||
            m["电影名字"]
              .toLowerCase()
              .includes(searchMovieTitle.value.toLowerCase())
        );

        if (!movie) {
          error.value = "未找到该电影，请检查电影名称";
          loading.value = false;
          return;
        }

        currentMovie.value = movie;

        // 调用API获取平台链接
        const response = await fetch(
          `http://localhost:8000/api/video-platform-links/?movie_title=${encodeURIComponent(
            movie["电影名字"]
          )}&douban_url=${encodeURIComponent(movie["电影链接"])}`
        );

        if (!response.ok) {
          throw new Error(`API请求失败: ${response.status}`);
        }

        const data = await response.json();
        platformLinks.value = data;

        // 更新URL参数
        router.replace({
          query: {
            movie_title: movie["电影名字"],
            douban_url: movie["电影链接"],
          },
        });
      } catch (err) {
        console.error("搜索平台链接失败:", err);
        error.value = "搜索观看链接失败，请稍后重试";

        // 模拟数据用于演示
        platformLinks.value = {
          movie_title: searchMovieTitle.value,
          douban_url: currentMovie.value?.["电影链接"] || "",
          total_platforms: 3,
          total_links: 4,
          platforms: {
            爱奇艺: [
              {
                id: 1,
                movie_title:
                  currentMovie.value?.["电影名字"] || searchMovieTitle.value,
                platform_url: "https://www.iqiyi.com/v_19rrho3x8w.html",
                vip_status: "vip",
                vip_status_display: "VIP可看",
                price: null,
                quality: "高清",
                last_checked: new Date().toISOString(),
              },
            ],
            腾讯视频: [
              {
                id: 2,
                movie_title:
                  currentMovie.value?.["电影名字"] || searchMovieTitle.value,
                platform_url: "https://v.qq.com/x/cover/mzc00200mp8vo7h.html",
                vip_status: "free",
                vip_status_display: "免费观看",
                price: null,
                quality: "超清",
                last_checked: new Date().toISOString(),
              },
            ],
            哔哩哔哩: [
              {
                id: 3,
                movie_title:
                  currentMovie.value?.["电影名字"] || searchMovieTitle.value,
                platform_url: "https://www.bilibili.com/bangumi/play/ss12044",
                vip_status: "vip",
                vip_status_display: "VIP可看",
                price: null,
                quality: "1080P",
                last_checked: new Date().toISOString(),
              },
              {
                id: 4,
                movie_title:
                  currentMovie.value?.["电影名字"] || searchMovieTitle.value,
                platform_url: "https://www.bilibili.com/bangumi/play/ep12045",
                vip_status: "free",
                vip_status_display: "免费观看",
                price: null,
                quality: "720P",
                last_checked: new Date().toISOString(),
              },
            ],
          },
        };
      } finally {
        loading.value = false;
      }
    };

    // 选择电影
    const selectMovie = (movie: DoubanMovie) => {
      currentMovie.value = movie;
      searchMovieTitle.value = movie["电影名字"];
      searchPlatformLinks();
    };

    // 格式化日期
    const formatDate = (dateString: string) => {
      const date = new Date(dateString);
      return date.toLocaleDateString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });
    };

    // 生命周期钩子
    onMounted(() => {
      loadMovies();
    });

    return {
      // 数据
      currentMovie,
      platformLinks,
      popularMovies,
      loading,
      error,
      searched,

      // 搜索状态
      searchMovieTitle,

      // 方法
      searchPlatformLinks,
      selectMovie,
      formatDate,
    };
  },
});
</script>

<style scoped>
/* ====== 全局容器：深色渐变 + 光斑 ====== */
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

  /* 统一色变量 */
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

/* ====== 顶部 Header：玻璃卡 + 渐变标题条 ====== */
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
  opacity: 0.95;
}

/* ====== 主容器 ====== */
.container {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* ====== 通用“玻璃卡片” ====== */
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

/* 卡片上沿微光 */
.search-section::before,
.movie-info-section::before,
.results-section::before,
.no-results-section::before,
.recommendations-section::before,
.loading-section::before,
.error-section::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 22px;
  pointer-events: none;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.14),
    rgba(255, 255, 255, 0.02)
  );
  mask: linear-gradient(#000, transparent 55%);
}

/* ====== 搜索区域 ====== */
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
  transition: box-shadow 0.18s ease, border-color 0.18s ease;
}

.search-input::placeholder {
  color: rgba(148, 163, 184, 0.75);
}

.search-input:focus {
  border-color: rgba(99, 102, 241, 0.6);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
}

.search-btn {
  padding: 12px 16px;
  border: none;
  border-radius: 14px;
  cursor: pointer;

  background: linear-gradient(135deg, var(--primary), var(--primary2));
  color: white;

  font-size: 14px;
  font-weight: 900;
  box-shadow: 0 18px 50px rgba(99, 102, 241, 0.35);
  transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
}

.search-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 22px 60px rgba(99, 102, 241, 0.42);
  filter: brightness(1.02);
}

.search-tips {
  padding: 12px 12px;
  border-radius: 14px;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: rgba(191, 219, 254, 0.95);
  font-size: 13px;
}

.search-tips p {
  margin: 0;
}

/* ====== 电影信息卡 ====== */
.movie-card {
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(17, 24, 39, 0.45);
  border-radius: 18px;
  padding: 16px;
}

.movie-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.movie-title {
  margin: 0;
  font-size: 18px;
  font-weight: 900;
}

.movie-rating {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.14);
  border: 1px solid rgba(245, 158, 11, 0.22);
  color: rgba(245, 158, 11, 0.95);
  font-weight: 900;
  font-size: 12px;
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

.detail-value {
  color: rgba(226, 232, 240, 0.95);
  font-weight: 700;
}

.movie-quote {
  margin-top: 12px;
  padding: 12px;
  border-radius: 14px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.18);
  color: rgba(226, 232, 240, 0.95);
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.quote-icon {
  opacity: 0.95;
}

.movie-actions {
  margin-top: 12px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 14px;
  text-decoration: none;
  font-weight: 900;
  font-size: 13px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(17, 24, 39, 0.55);
  color: rgba(226, 232, 240, 0.95);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.25);
}

.douban-link {
  border: none;
  background: linear-gradient(135deg, var(--primary), var(--primary2));
  box-shadow: 0 18px 50px rgba(99, 102, 241, 0.35);
  color: #fff;
}

/* ====== Loading / Error ====== */
.loading-section,
.error-section {
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

.error-icon {
  font-size: 26px;
  margin-bottom: 6px;
}

.error-message {
  margin: 0 0 12px 0;
  color: rgba(254, 226, 226, 0.95);
}

.retry-btn {
  padding: 10px 14px;
  border-radius: 14px;
  border: none;
  cursor: pointer;
  font-weight: 900;
  background: linear-gradient(135deg, var(--primary), var(--primary2));
  color: #fff;
  box-shadow: 0 18px 50px rgba(99, 102, 241, 0.35);
}

.retry-btn:hover {
  transform: translateY(-1px);
}

/* ====== 结果区域 ====== */
.results-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 900;
}

.results-summary {
  margin: 8px 0 0;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.95);
}

/* 平台网格 */
.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 14px;
  margin-top: 14px;
}

.platform-card {
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(17, 24, 39, 0.45);
  padding: 14px;
}

.platform-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 10px;
}

.platform-title {
  margin: 0;
  font-size: 14px;
  font-weight: 900;
}

.platform-count {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 800;
}

/* 链接项 */
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

.link-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
}

.link-title {
  color: rgba(226, 232, 240, 0.95);
  font-weight: 900;
  text-decoration: none;
  font-size: 13px;
  line-height: 1.3;
}

.link-title:hover {
  text-decoration: underline;
}

/* vip/free/pay 标签 */
.vip-badge,
.free-badge,
.pay-badge {
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

.price-tag {
  opacity: 0.95;
}

/* 细节行 */
.link-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  gap: 10px;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.95);
}

.quality-badge {
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid rgba(99, 102, 241, 0.18);
  background: rgba(99, 102, 241, 0.1);
  color: rgba(226, 232, 240, 0.95);
  font-weight: 900;
}

.update-time {
  opacity: 0.9;
}

/* ====== 无结果 ====== */
.no-results-section {
  text-align: center;
}

.no-results-icon {
  font-size: 28px;
  margin-bottom: 10px;
}

.no-results-section h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 900;
}

.no-results-section p {
  margin: 10px 0 0;
  color: rgba(148, 163, 184, 0.95);
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

.suggestions p {
  margin: 0 0 8px 0;
  font-weight: 900;
  color: rgba(226, 232, 240, 0.95);
}

.suggestions ul {
  margin: 0;
  padding-left: 18px;
  color: rgba(148, 163, 184, 0.95);
}

/* ====== 热门推荐 ====== */
.recommendations-section h3 {
  margin: 0 0 14px 0;
  font-size: 16px;
  font-weight: 900;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

.recommendation-card {
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(17, 24, 39, 0.45);
  padding: 14px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 22px 60px rgba(0, 0, 0, 0.35);
}

.rec-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
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

.rec-info {
  margin-top: 8px;
  display: flex;
  gap: 10px;
  color: rgba(148, 163, 184, 0.95);
  font-size: 12px;
  font-weight: 800;
}

.rec-quote {
  margin-top: 10px;
  color: rgba(226, 232, 240, 0.92);
  opacity: 0.9;
  font-size: 12px;
  line-height: 1.6;
}

.rec-btn {
  margin-top: 12px;
  width: 100%;
  padding: 10px 12px;
  border-radius: 14px;
  border: none;
  cursor: pointer;
  font-weight: 900;
  color: #fff;
  background: linear-gradient(135deg, var(--primary), var(--primary2));
  box-shadow: 0 18px 50px rgba(99, 102, 241, 0.35);
}

.rec-btn:hover {
  transform: translateY(-1px);
}

/* ====== 响应式 ====== */
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
}
</style>
