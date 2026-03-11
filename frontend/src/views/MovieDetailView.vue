<template>
  <div class="movie-detail-view">
    <div v-if="!movie" class="error-section">
      <div class="error-icon">⚠️</div>
      <h2>未找到电影信息</h2>
      <p>请从首页或电影库重新进入电影详情页。</p>
      <router-link to="/" class="primary-btn">返回首页</router-link>
    </div>

    <template v-else>
      <!-- 顶部电影英雄区 -->
      <section class="hero-section">
        <div class="poster-wrap">
          <img
            v-if="extraDetail?.poster"
            :src="extraDetail.poster"
            :alt="movie['电影名字']"
            class="poster"
          />
          <div v-else class="poster-placeholder">
            <span class="poster-icon">🎬</span>
            <span class="poster-text">电影海报</span>
          </div>
        </div>

        <div class="hero-content">
          <div class="title-row">
            <h1 class="movie-title">{{ movie["电影名字"] }}</h1>
            <span class="year-badge">{{ movie["年份"] || "未知年份" }}</span>
          </div>

          <p class="sub-title">
            {{ movie["国家"] || "未知国家" }} ·
            {{ movie["类型"] || "未知类型" }}
          </p>

          <div class="rating-row">
            <div class="rating-card">
              <span class="rating-star">⭐</span>
              <span class="rating-value">{{
                movie["评分"] || "暂无评分"
              }}</span>
              <span class="rating-count" v-if="movie['评分人数']">
                {{ movie["评分人数"] }} 人评分
              </span>
            </div>
          </div>

          <div class="tag-row">
            <span v-for="tag in movieTypes" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>

          <div class="meta-grid">
            <div class="meta-item">
              <span class="meta-label">导演</span>
              <span class="meta-value">{{ movie["导演"] || "未知" }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">主演</span>
              <span class="meta-value">{{ movie["主演"] || "未知" }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">年份</span>
              <span class="meta-value">{{ movie["年份"] || "未知" }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">国家/地区</span>
              <span class="meta-value">{{ movie["国家"] || "未知" }}</span>
            </div>
          </div>

          <div class="action-row">
            <router-link
              :to="{
                name: 'video-platform',
                query: {
                  movie_title: movie['电影名字'],
                  douban_url: movie['电影链接'],
                },
              }"
              class="action-btn primary"
            >
              📺 查看观看链接
            </router-link>

            <button class="action-btn secondary" @click="handleFavorite">
              ❤️ 收藏
            </button>

            <button class="action-btn secondary" @click="handleLike">
              👍 点赞
            </button>

            <button class="action-btn secondary" @click="handleDislike">
              👎 点踩
            </button>
          </div>
        </div>
      </section>

      <!-- 主内容区 -->
      <section class="content-grid">
        <div class="main-column">
          <div class="panel">
            <h2>一句话评价</h2>
            <p class="summary">
              {{ movie["一句话评价"] || "暂无一句话评价" }}
            </p>
          </div>

          <div class="panel">
            <div class="panel-header">
              <h2>剧情简介</h2>
              <span v-if="extraLoading" class="loading-badge">加载中...</span>
            </div>

            <p v-if="extraLoading" class="summary placeholder-text">
              正在加载剧情简介...
            </p>

            <p v-else-if="extraDetail?.summary" class="summary">
              {{ extraDetail.summary }}
            </p>

            <p v-else class="summary placeholder-text">暂无剧情简介</p>
          </div>

          <div class="panel">
            <h2>用户评论（预留）</h2>

            <div class="comment-box">
              <textarea
                v-model="commentText"
                placeholder="写下你对这部电影的看法..."
                class="comment-input"
              ></textarea>
              <button class="primary-btn" @click="submitComment">
                发表评论
              </button>
            </div>

            <div class="comment-empty">
              暂无评论。后续接入你自己的评论接口后，这里就可以展示真实评论。
            </div>
          </div>
        </div>

        <div class="side-column">
          <div class="panel">
            <h3>基础信息</h3>
            <ul class="side-list">
              <li>
                <strong>电影名:</strong> {{ movie["电影名字"] || "未知" }}
              </li>
              <li><strong>评分:</strong> {{ movie["评分"] || "暂无" }}</li>
              <li><strong>年份:</strong> {{ movie["年份"] || "未知" }}</li>
              <li><strong>国家:</strong> {{ movie["国家"] || "未知" }}</li>
              <li><strong>类型:</strong> {{ movie["类型"] || "未知" }}</li>
            </ul>
          </div>

          <div class="panel">
            <div class="panel-header">
              <h3>扩展信息</h3>
              <span v-if="extraLoading" class="loading-badge">加载中...</span>
            </div>

            <div v-if="extraError" class="placeholder-text">
              {{ extraError }}
            </div>

            <ul v-else-if="extraDetail" class="side-list">
              <li>
                <strong>英文名:</strong>
                {{ extraDetail.english_title || "暂无" }}
              </li>
              <li>
                <strong>IMDb:</strong>
                {{ extraDetail.imdb || "暂无" }}
              </li>
              <li>
                <strong>上映日期:</strong>
                {{ joinList(extraDetail.release_dates) }}
              </li>
              <li>
                <strong>片长:</strong>
                {{ joinList(extraDetail.runtime) }}
              </li>
              <li>
                <strong>语言:</strong>
                {{ joinList(extraDetail.languages) }}
              </li>
              <li>
                <strong>又名:</strong>
                {{ joinList(extraDetail.aka) }}
              </li>
              <li>
                <strong>编剧:</strong>
                {{ joinList(extraDetail.writer) }}
              </li>
              <li>
                <strong>主演:</strong>
                {{ joinList(extraDetail.actors) }}
              </li>
            </ul>

            <div v-else class="placeholder-text">暂无扩展信息</div>
          </div>

          <div class="panel">
            <h3>外部入口</h3>
            <a
              :href="movie['电影链接']"
              target="_blank"
              rel="noopener noreferrer"
              class="external-link"
            >
              打开原始豆瓣页
            </a>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";

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

interface MovieExtraDetail {
  movie_title?: string;
  english_title?: string;
  douban_url?: string;
  poster?: string;
  rating?: string;
  rating_count?: string;
  director?: string[];
  writer?: string[];
  actors?: string[];
  genres?: string[];
  countries?: string[];
  languages?: string[];
  release_dates?: string[];
  runtime?: string[];
  aka?: string[];
  imdb?: string;
  summary?: string;
  year?: string;
  source?: string;
}

const API_BASE_URL = "http://localhost:8000";

export default defineComponent({
  name: "MovieDetailView",
  setup() {
    const movie = ref<DoubanMovie | null>(null);
    const commentText = ref("");

    const extraDetail = ref<MovieExtraDetail | null>(null);
    const extraLoading = ref(false);
    const extraError = ref("");

    const movieTypes = computed(() => {
      if (!movie.value?.["类型"]) return [];
      return movie.value["类型"]
        .split(" ")
        .map((item) => item.trim())
        .filter(Boolean);
    });

    const joinList = (arr?: string[]) => {
      if (!arr || arr.length === 0) return "暂无";
      return arr.join(" / ");
    };

    const loadMovieFromSession = () => {
      const saved = sessionStorage.getItem("current_movie_detail");
      if (!saved) return;

      try {
        movie.value = JSON.parse(saved);
      } catch (error) {
        console.error("解析 sessionStorage 电影详情失败:", error);
      }
    };

    const fetchExtraDetail = async () => {
      if (!movie.value?.["电影链接"]) return;

      extraLoading.value = true;
      extraError.value = "";

      try {
        const params = new URLSearchParams();
        params.append("douban_url", movie.value["电影链接"]);
        params.append("movie_title", movie.value["电影名字"]);

        const response = await fetch(
          `${API_BASE_URL}/api/movie-detail/?${params.toString()}`
        );

        if (!response.ok) {
          throw new Error(`请求失败: ${response.status}`);
        }

        extraDetail.value = await response.json();
      } catch (err: any) {
        console.error("获取扩展详情失败:", err);
        extraError.value = "扩展详情加载失败，当前已显示基础信息";
      } finally {
        extraLoading.value = false;
      }
    };

    const submitComment = () => {
      if (!commentText.value.trim()) {
        alert("请输入评论内容");
        return;
      }
      alert("评论功能下一步接后端接口");
      commentText.value = "";
    };

    const handleFavorite = () => {
      if (!movie.value) return;

      const saved = localStorage.getItem("movie_favorites");
      const favorites: string[] = saved ? JSON.parse(saved) : [];

      const movieLink = movie.value["电影链接"];
      const exists = favorites.includes(movieLink);

      const newFavorites = exists
        ? favorites.filter((item) => item !== movieLink)
        : [...favorites, movieLink];

      localStorage.setItem("movie_favorites", JSON.stringify(newFavorites));
      alert(exists ? "已取消收藏" : "收藏成功");
    };

    const handleLike = () => {
      alert("点赞功能下一步接后端接口");
    };

    const handleDislike = () => {
      alert("点踩功能下一步接后端接口");
    };

    onMounted(() => {
      loadMovieFromSession();
      fetchExtraDetail();
    });

    return {
      movie,
      commentText,
      extraDetail,
      extraLoading,
      extraError,
      movieTypes,
      joinList,
      submitComment,
      handleFavorite,
      handleLike,
      handleDislike,
    };
  },
});
</script>

<style scoped>
.movie-detail-view {
  min-height: 100vh;
  padding: 24px;
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
    linear-gradient(135deg, #0b1220 0%, #111827 55%, #0b1220 100%);
  color: rgba(255, 255, 255, 0.92);

  --panel: rgba(255, 255, 255, 0.08);
  --border: rgba(255, 255, 255, 0.14);
  --primary: #6366f1;
  --primary2: #8b5cf6;
  --shadow: 0 16px 50px rgba(0, 0, 0, 0.28);
}

.error-section {
  text-align: center;
  padding: 80px 20px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 24px;
  backdrop-filter: blur(14px);
}

.error-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.hero-section {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 28px;
  padding: 24px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 28px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
}

.poster-wrap {
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.poster {
  width: 100%;
  max-width: 280px;
  border-radius: 20px;
  object-fit: cover;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
}

.poster-placeholder {
  width: 280px;
  height: 400px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
}

.poster-icon {
  font-size: 48px;
}

.poster-text {
  color: rgba(226, 232, 240, 0.85);
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.movie-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 900;
}

.sub-title {
  margin: 10px 0 0;
  color: rgba(226, 232, 240, 0.85);
}

.year-badge,
.tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.year-badge {
  background: rgba(245, 158, 11, 0.16);
  color: #fbbf24;
}

.rating-row {
  margin-top: 16px;
}

.rating-card {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 16px;
  background: rgba(245, 158, 11, 0.16);
  color: #fcd34d;
  font-weight: 900;
}

.rating-value {
  font-size: 1.2rem;
}

.rating-count {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
}

.tag-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.tag {
  background: rgba(99, 102, 241, 0.16);
  color: rgba(255, 255, 255, 0.92);
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 20px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
}

.meta-label {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.95);
  font-weight: 700;
}

.meta-value {
  font-size: 14px;
  line-height: 1.6;
}

.action-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 20px;
}

.action-btn,
.primary-btn,
.external-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  border: none;
  cursor: pointer;
  border-radius: 14px;
  padding: 10px 16px;
  font-weight: 900;
}

.action-btn.primary,
.primary-btn {
  background: linear-gradient(135deg, var(--primary), var(--primary2));
  color: white;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.08);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.14);
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 20px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
}

.panel h2,
.panel h3 {
  margin-top: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.loading-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  background: rgba(99, 102, 241, 0.16);
  color: rgba(255, 255, 255, 0.92);
}

.summary {
  line-height: 1.9;
  color: rgba(226, 232, 240, 0.92);
}

.placeholder-text {
  color: rgba(148, 163, 184, 0.95);
}

.comment-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-input {
  min-height: 120px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 14px;
  padding: 14px;
  resize: vertical;
  background: rgba(17, 24, 39, 0.55);
  color: white;
}

.comment-empty {
  margin-top: 16px;
  color: rgba(148, 163, 184, 0.95);
}

.side-list {
  margin: 0;
  padding-left: 18px;
  line-height: 1.9;
}

.external-link {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}

@media (max-width: 900px) {
  .hero-section {
    grid-template-columns: 1fr;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
