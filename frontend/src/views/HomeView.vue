<template>
  <div class="home">
    <!-- 顶部横幅 -->
    <div class="hero-banner">
      <div class="hero-content">
        <h1>🎬 智能电影推荐系统</h1>
        <p class="hero-subtitle">基于豆瓣电影TOP250数据的个性化推荐</p>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-number">250</span>
            <span class="stat-label">部精选电影</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">9.0+</span>
            <span class="stat-label">平均评分</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">1994-2026</span>
            <span class="stat-label">年份跨度</span>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- 用户欢迎区域 -->
      <div class="welcome-section">
        <div v-if="currentUser" class="user-welcome">
          <div class="user-avatar">
            <span class="avatar-icon">👤</span>
          </div>
          <div class="user-info">
            <h2>欢迎回来, {{ currentUser.username }}!</h2>
            <p class="user-email">{{ currentUser.email || "未设置邮箱" }}</p>
            <p class="user-join-date">
              注册时间:
              {{
                new Date(currentUser.date_joined).toLocaleDateString("zh-CN")
              }}
            </p>
          </div>
          <div class="user-actions">
            <button @click="getPersonalizedRecommendations" class="primary-btn">
              🎯 获取个性化推荐
            </button>
            <button @click="viewFavorites" class="secondary-btn">
              ❤️ 查看收藏
            </button>
          </div>
        </div>
        <div v-else class="guest-welcome">
          <h2>👋 欢迎来到电影推荐系统</h2>
          <p>登录后可以获取个性化电影推荐、收藏喜欢的电影</p>
          <div class="auth-actions">
            <router-link to="/login" class="auth-btn login-btn"
              >登录</router-link
            >
            <router-link to="/register" class="auth-btn register-btn"
              >注册</router-link
            >
          </div>
        </div>
      </div>

      <!-- 快速推荐区域 -->
      <div class="quick-recommendations">
        <h2 class="section-title">🚀 快速推荐</h2>
        <div class="recommendation-buttons">
          <button @click="getTopRatedMovies" class="rec-btn">
            ⭐ 高分电影
          </button>
          <button @click="getRecentMovies" class="rec-btn">🆕 近期热门</button>
          <button @click="getRandomMovies" class="rec-btn">🎲 随机推荐</button>
          <button @click="getByGenre('剧情')" class="rec-btn">
            🎭 剧情电影
          </button>
          <button @click="getByGenre('喜剧')" class="rec-btn">
            😄 喜剧电影
          </button>
          <button @click="getByGenre('科幻')" class="rec-btn">
            🚀 科幻电影
          </button>
        </div>
      </div>

      <!-- 推荐结果展示 -->
      <div class="recommendations-section">
        <div class="section-header">
          <h2 class="section-title">🎬 推荐电影</h2>
          <div class="section-controls">
            <span class="result-count"
              >{{ recommendations.length }} 部电影</span
            >
            <button
              @click="clearRecommendations"
              class="clear-btn"
              v-if="recommendations.length > 0"
            >
              清空
            </button>
          </div>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>正在加载推荐...</p>
        </div>

        <div v-else-if="recommendations.length === 0" class="empty-state">
          <div class="empty-icon">🎬</div>
          <h3>暂无推荐</h3>
          <p>点击上面的按钮获取电影推荐</p>
        </div>

        <div v-else class="movies-grid">
          <div
            v-for="movie in recommendations"
            :key="movie['电影链接']"
            class="movie-card"
          >
            <div class="movie-card-header">
              <div class="movie-rating">
                <span class="rating-star">⭐</span>
                <span class="rating-value">{{ movie["评分"] }}</span>
              </div>
              <div class="movie-year">{{ movie["年份"] }}</div>
            </div>

            <h3 class="movie-title">{{ movie["电影名字"] }}</h3>

            <div class="movie-meta">
              <span class="meta-item">
                <span class="meta-label">国家:</span>
                <span class="meta-value">{{ movie["国家"] }}</span>
              </span>
              <span class="meta-item">
                <span class="meta-label">类型:</span>
                <span class="meta-value">{{ movie["类型"] }}</span>
              </span>
            </div>

            <div class="movie-crew">
              <p class="crew-item">
                <strong>导演:</strong> {{ movie["导演"] || "未知" }}
              </p>
              <p class="crew-item">
                <strong>主演:</strong> {{ movie["主演"] || "未知" }}
              </p>
            </div>

            <div class="movie-quote" v-if="movie['一句话评价']">
              <span class="quote-icon">💬</span>
              <span class="quote-text">{{ movie["一句话评价"] }}</span>
            </div>

            <div class="movie-actions">
              <button
                @click="goToMovieDetail(movie)"
                class="action-btn detail-btn"
              >
                电影详情
              </button>
              <button
                @click="toggleFavorite(movie)"
                class="action-btn favorite-btn"
              >
                {{ isFavorite(movie) ? "❤️ 已收藏" : "🤍 收藏" }}
              </button>
              <button @click="rateMovie(movie)" class="action-btn rate-btn">
                ⭐ 评分
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 热门电影排行榜 -->
      <div class="top-movies-section">
        <h2 class="section-title">🏆 豆瓣电影TOP10</h2>
        <div class="top-movies-list">
          <div
            v-for="(movie, index) in topMovies"
            :key="movie['电影链接']"
            class="top-movie-item"
            :class="{ 'top-3': index < 3 }"
          >
            <div class="rank-badge">
              <span class="rank-number">{{ index + 1 }}</span>
            </div>
            <div class="movie-info">
              <h4 class="movie-title">{{ movie["电影名字"] }}</h4>
              <div class="movie-details">
                <span class="rating">⭐ {{ movie["评分"] }}</span>
                <span class="year">{{ movie["年份"] }}</span>
                <span class="country">{{ movie["国家"] }}</span>
              </div>
              <p class="movie-quote" v-if="movie['一句话评价']">
                {{ movie["一句话评价"] }}
              </p>
            </div>
            <div class="movie-actions">
              <button @click="goToMovieDetail(movie)" class="small-btn">
                详情
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 电影分类浏览 -->
      <div class="categories-section">
        <h2 class="section-title">📂 按类型浏览</h2>
        <div class="categories-grid">
          <div
            v-for="category in movieCategories"
            :key="category.name"
            class="category-card"
            @click="getByGenre(category.name)"
          >
            <div class="category-icon">{{ category.icon }}</div>
            <h4>{{ category.name }}</h4>
            <p class="category-count">{{ category.count }} 部电影</p>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-section">
        <h2 class="section-title">📊 数据统计</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">🎬</div>
            <div class="stat-content">
              <div class="stat-number">{{ totalMovies }}</div>
              <div class="stat-label">总电影数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⭐</div>
            <div class="stat-content">
              <div class="stat-number">{{ averageRating.toFixed(1) }}</div>
              <div class="stat-label">平均评分</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🌍</div>
            <div class="stat-content">
              <div class="stat-number">{{ countries.length }}</div>
              <div class="stat-label">国家/地区</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🎭</div>
            <div class="stat-content">
              <div class="stat-number">{{ genres.length }}</div>
              <div class="stat-label">电影类型</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
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

interface MovieCategory {
  name: string;
  icon: string;
  count: number;
}

export default defineComponent({
  name: "HomeView",
  setup() {
    const authStore = useAuthStore();
    const allMovies = ref<DoubanMovie[]>([]);
    const recommendations = ref<DoubanMovie[]>([]);
    const loading = ref(false);
    const favorites = ref<Set<string>>(new Set());

    // 计算当前用户
    const currentUser = computed(() => authStore.user);

    // 计算属性
    const totalMovies = computed(() => allMovies.value.length);
    const averageRating = computed(() => {
      if (allMovies.value.length === 0) return 0;
      const sum = allMovies.value.reduce((acc, movie) => {
        return acc + parseFloat(movie["评分"] || "0");
      }, 0);
      return sum / allMovies.value.length;
    });
    const countries = computed(() => {
      const countrySet = new Set<string>();
      allMovies.value.forEach((movie) => {
        if (movie["国家"]) {
          const countries = movie["国家"].split(" ");
          countries.forEach((c) => countrySet.add(c.trim()));
        }
      });
      return Array.from(countrySet).sort();
    });
    const genres = computed(() => {
      const genreSet = new Set<string>();
      allMovies.value.forEach((movie) => {
        if (movie["类型"]) {
          const genres = movie["类型"].split(" ");
          genres.forEach((g) => genreSet.add(g.trim()));
        }
      });
      return Array.from(genreSet).sort();
    });
    const topMovies = computed(() => {
      return [...allMovies.value]
        .sort((a, b) => parseFloat(b["评分"]) - parseFloat(a["评分"]))
        .slice(0, 10);
    });
    const movieCategories = computed<MovieCategory[]>(() => {
      const categories: MovieCategory[] = [
        { name: "剧情", icon: "🎭", count: 0 },
        { name: "喜剧", icon: "😄", count: 0 },
        { name: "爱情", icon: "❤️", count: 0 },
        { name: "科幻", icon: "🚀", count: 0 },
        { name: "动作", icon: "💥", count: 0 },
        { name: "悬疑", icon: "🔍", count: 0 },
        { name: "动画", icon: "🐭", count: 0 },
        { name: "犯罪", icon: "🚔", count: 0 },
      ];

      categories.forEach((category) => {
        category.count = allMovies.value.filter((movie) =>
          movie["类型"].includes(category.name)
        ).length;
      });

      return categories.filter((cat) => cat.count > 0);
    });

    // 初始化数据
    const loadMovies = () => {
      loading.value = true;
      try {
        allMovies.value = doubanData as DoubanMovie[];
        loadFavorites();
      } catch (error) {
        console.error("加载电影数据失败:", error);
      } finally {
        loading.value = false;
      }
    };

    // 加载收藏夹
    const loadFavorites = () => {
      const saved = localStorage.getItem("movie_favorites");
      if (saved) {
        favorites.value = new Set(JSON.parse(saved));
      }
    };

    // 收藏功能
    const isFavorite = (movie: DoubanMovie) => {
      return favorites.value.has(movie["电影链接"]);
    };

    const toggleFavorite = (movie: DoubanMovie) => {
      if (favorites.value.has(movie["电影链接"])) {
        favorites.value.delete(movie["电影链接"]);
      } else {
        favorites.value.add(movie["电影链接"]);
      }
      localStorage.setItem(
        "movie_favorites",
        JSON.stringify(Array.from(favorites.value))
      );
    };

    // 查看收藏
    const viewFavorites = () => {
      const favoriteMovies = allMovies.value.filter((movie) =>
        favorites.value.has(movie["电影链接"])
      );
      recommendations.value = favoriteMovies;
    };

    // 评分电影
    const rateMovie = (movie: DoubanMovie) => {
      if (!currentUser.value) {
        alert("请先登录");
        return;
      }

      const rating = prompt(`请为《${movie["电影名字"]}》评分（1-10分）:`);
      if (rating && parseFloat(rating) >= 1 && parseFloat(rating) <= 10) {
        alert(`评分成功！您给《${movie["电影名字"]}》评分: ${rating}分`);
        // 这里可以添加API调用保存评分
      }
    };

    // 推荐算法
    const getPersonalizedRecommendations = () => {
      if (!currentUser.value) {
        alert("请先登录");
        return;
      }

      loading.value = true;
      setTimeout(() => {
        // 基于用户收藏的推荐逻辑
        const favoriteGenres = new Set<string>();
        allMovies.value.forEach((movie) => {
          if (favorites.value.has(movie["电影链接"]) && movie["类型"]) {
            const genres = movie["类型"].split(" ");
            genres.forEach((g) => favoriteGenres.add(g.trim()));
          }
        });

        let personalized = [...allMovies.value];

        if (favoriteGenres.size > 0) {
          personalized = personalized.filter((movie) => {
            const movieGenres = movie["类型"].split(" ");
            return movieGenres.some((g) => favoriteGenres.has(g.trim()));
          });
        }

        // 按评分排序并取前12部
        personalized.sort(
          (a, b) => parseFloat(b["评分"]) - parseFloat(a["评分"])
        );
        recommendations.value = personalized.slice(0, 12);
        loading.value = false;
      }, 1000);
    };

    const getTopRatedMovies = () => {
      loading.value = true;
      setTimeout(() => {
        const topRated = [...allMovies.value]
          .filter((movie) => parseFloat(movie["评分"]) >= 9.0)
          .sort((a, b) => parseFloat(b["评分"]) - parseFloat(a["评分"]));
        recommendations.value = topRated.slice(0, 12);
        loading.value = false;
      }, 800);
    };

    const getRecentMovies = () => {
      loading.value = true;
      setTimeout(() => {
        const recent = [...allMovies.value]
          .filter((movie) => {
            const year = parseInt(movie["年份"]) || 0;
            return year >= 2010;
          })
          .sort(
            (a, b) => (parseInt(b["年份"]) || 0) - (parseInt(a["年份"]) || 0)
          );
        recommendations.value = recent.slice(0, 12);
        loading.value = false;
      }, 800);
    };

    const getRandomMovies = () => {
      loading.value = true;
      setTimeout(() => {
        const shuffled = [...allMovies.value].sort(() => 0.5 - Math.random());
        recommendations.value = shuffled.slice(0, 12);
        loading.value = false;
      }, 800);
    };

    const getByGenre = (genre: string) => {
      loading.value = true;
      setTimeout(() => {
        const byGenre = allMovies.value
          .filter((movie) => movie["类型"].includes(genre))
          .sort((a, b) => parseFloat(b["评分"]) - parseFloat(a["评分"]));
        recommendations.value = byGenre.slice(0, 12);
        loading.value = false;
      }, 800);
    };

    const clearRecommendations = () => {
      recommendations.value = [];
    };

    const goToMovieDetail = (movie: DoubanMovie) => {
      sessionStorage.setItem("current_movie_detail", JSON.stringify(movie));
      window.location.href = `/movie-detail?movie_title=${encodeURIComponent(
        movie["电影名字"]
      )}&douban_url=${encodeURIComponent(movie["电影链接"])}`;
    };

    // 生命周期钩子
    onMounted(() => {
      loadMovies();
    });

    // 返回所有需要暴露给模板的属性和方法
    return {
      // 数据
      allMovies,
      recommendations,
      loading,
      favorites,

      // 计算属性
      currentUser,
      totalMovies,
      averageRating,
      countries,
      genres,
      topMovies,
      movieCategories,

      // 方法
      getPersonalizedRecommendations,
      goToMovieDetail,
      getTopRatedMovies,
      getRecentMovies,
      getRandomMovies,
      getByGenre,
      viewFavorites,
      toggleFavorite,
      isFavorite,
      rateMovie,
      clearRecommendations,
    };
  },
});
</script>

<style scoped>
.home {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

/* 英雄横幅样式 */
.hero-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 60px 20px;
  text-align: center;
  border-radius: 0 0 20px 20px;
  margin-bottom: 40px;
}

.hero-content h1 {
  margin: 0;
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 15px;
}

.hero-subtitle {
  font-size: 1.3rem;
  opacity: 0.9;
  margin-bottom: 30px;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 30px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 1rem;
  opacity: 0.8;
}

/* 容器样式 */
.container {
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* 欢迎区域样式 */
.welcome-section {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.user-welcome {
  display: flex;
  align-items: center;
  gap: 25px;
}

.user-avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  font-size: 2.5rem;
}

.user-info {
  flex: 1;
}

.user-info h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.8rem;
}

.user-email {
  color: #666;
  margin: 0 0 5px 0;
}

.user-join-date {
  color: #888;
  font-size: 0.9rem;
  margin: 0;
}

.user-actions {
  display: flex;
  gap: 15px;
}

.primary-btn,
.secondary-btn {
  padding: 12px 25px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.primary-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.secondary-btn {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.secondary-btn:hover {
  background: #667eea;
  color: white;
}

.guest-welcome {
  text-align: center;
  padding: 20px;
}

.guest-welcome h2 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 2rem;
}

.guest-welcome p {
  color: #666;
  margin-bottom: 25px;
  font-size: 1.1rem;
}

.auth-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.auth-btn {
  padding: 12px 35px;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.login-btn {
  background: #667eea;
  color: white;
}

.login-btn:hover {
  background: #5a67d8;
}

.register-btn {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.register-btn:hover {
  background: #667eea;
  color: white;
}

/* 快速推荐区域样式 */
.quick-recommendations {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.section-title {
  margin: 0 0 25px 0;
  color: #333;
  font-size: 1.8rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.recommendation-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.rec-btn {
  padding: 15px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.rec-btn:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
  transform: translateY(-3px);
}

/* 推荐结果区域样式 */
.recommendations-section {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.section-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.result-count {
  color: #666;
  font-weight: 500;
}

.clear-btn {
  padding: 8px 16px;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.clear-btn:hover {
  background: #c53030;
}

.loading-state {
  text-align: center;
  padding: 60px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.empty-state {
  text-align: center;
  padding: 60px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.empty-state p {
  color: #666;
  margin: 0;
}

/* 电影网格样式 */
.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
}

.movie-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 25px;
  background: white;
  transition: transform 0.3s, box-shadow 0.3s;
}

.movie-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.movie-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.movie-rating {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #fef3c7;
  padding: 6px 12px;
  border-radius: 20px;
}

.rating-star {
  font-size: 1.1rem;
}

.rating-value {
  font-weight: 700;
  color: #d97706;
  font-size: 1.1rem;
}

.movie-year {
  background: #f0f0f0;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #666;
}

.movie-title {
  margin: 0 0 15px 0;
  font-size: 1.4rem;
  color: #2d3748;
  line-height: 1.3;
}

.movie-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
}

.meta-label {
  color: #718096;
  font-weight: 500;
}

.meta-value {
  color: #4a5568;
  font-weight: 600;
}

.movie-crew {
  margin-bottom: 15px;
}

.crew-item {
  margin: 0 0 8px 0;
  font-size: 0.95rem;
  color: #4a5568;
  line-height: 1.4;
}

.crew-item:last-child {
  margin-bottom: 0;
}

.crew-item strong {
  color: #2d3748;
}

.movie-quote {
  margin: 15px 0;
  padding: 12px;
  background: linear-gradient(135deg, #f0f4ff 0%, #e6fffa 100%);
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.quote-icon {
  margin-right: 8px;
  font-size: 1.1rem;
}

.quote-text {
  font-style: italic;
  color: #4a5568;
  line-height: 1.5;
  font-size: 0.95rem;
}

.movie-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.action-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  text-align: center;
  text-decoration: none;
  transition: all 0.3s;
}

.detail-btn {
  background: #667eea;
  color: white;
}

.detail-btn:hover {
  background: #5a67d8;
}

.favorite-btn {
  background: #f7fafc;
  color: #e53e3e;
  border: 2px solid #e53e3e;
}

.favorite-btn:hover {
  background: #e53e3e;
  color: white;
}

.rate-btn {
  background: #fef3c7;
  color: #d97706;
  border: 2px solid #fef3c7;
}

.rate-btn:hover {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

/* 热门电影排行榜样式 */
.top-movies-section {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.top-movies-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.top-movie-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  background: white;
  transition: transform 0.3s;
}

.top-movie-item:hover {
  transform: translateX(5px);
}

.top-movie-item.top-3 {
  background: linear-gradient(135deg, #fef3c7 0%, #fef9c3 100%);
  border-color: #fbbf24;
}

.rank-badge {
  width: 40px;
  height: 40px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.top-movie-item.top-3 .rank-badge {
  background: #d97706;
}

.movie-info {
  flex: 1;
}

.movie-info .movie-title {
  margin: 0 0 10px 0;
  font-size: 1.2rem;
}

.movie-details {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  font-size: 0.9rem;
  color: #666;
}

.movie-info .movie-quote {
  margin: 10px 0 0 0;
  padding: 8px 12px;
  font-size: 0.9rem;
}

.small-btn {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  text-decoration: none;
  transition: background 0.3s;
}

.small-btn:hover {
  background: #5a67d8;
}

/* 分类浏览样式 */
.categories-section {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}

.category-card {
  padding: 25px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.category-card:hover {
  border-color: #667eea;
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.1);
}

.category-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.category-card h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.2rem;
}

.category-count {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

/* 统计信息样式 */
.stats-section {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 25px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2.2rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-content h1 {
    font-size: 2.2rem;
  }

  .hero-stats {
    flex-direction: column;
    gap: 20px;
  }

  .user-welcome {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .user-actions {
    flex-direction: column;
    width: 100%;
  }

  .primary-btn,
  .secondary-btn {
    width: 100%;
  }

  .auth-actions {
    flex-direction: column;
    width: 100%;
  }

  .auth-btn {
    width: 100%;
    text-align: center;
  }

  .recommendation-buttons {
    grid-template-columns: repeat(2, 1fr);
  }

  .movies-grid {
    grid-template-columns: 1fr;
  }

  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .top-movie-item {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }

  .movie-details {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .hero-content h1 {
    font-size: 1.8rem;
  }

  .hero-subtitle {
    font-size: 1.1rem;
  }

  .recommendation-buttons {
    grid-template-columns: 1fr;
  }

  .categories-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .section-controls {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
