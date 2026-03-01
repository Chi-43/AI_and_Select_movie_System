<template>
  <div class="douban-view">
    <div class="header">
      <h1>🎬 豆瓣电影TOP250推荐系统</h1>
      <p class="subtitle">基于豆瓣电影TOP250数据的智能推荐</p>
    </div>

    <div class="container">
      <!-- 搜索和筛选部分 -->
      <div class="filter-section">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索电影名称、导演、主演..."
            class="search-input"
            @input="filterMovies"
          />
          <button @click="filterMovies" class="search-btn">搜索</button>
        </div>

        <div class="filter-controls">
          <div class="filter-group">
            <label>年份范围:</label>
            <div class="range-inputs">
              <input
                v-model="yearRange[0]"
                type="number"
                placeholder="起始年份"
                min="1900"
                max="2026"
                @change="filterMovies"
              />
              <span>至</span>
              <input
                v-model="yearRange[1]"
                type="number"
                placeholder="结束年份"
                min="1900"
                max="2026"
                @change="filterMovies"
              />
            </div>
          </div>

          <div class="filter-group">
            <label>评分范围:</label>
            <div class="range-inputs">
              <input
                v-model="ratingRange[0]"
                type="number"
                placeholder="最低评分"
                min="0"
                max="10"
                step="0.1"
                @change="filterMovies"
              />
              <span>至</span>
              <input
                v-model="ratingRange[1]"
                type="number"
                placeholder="最高评分"
                min="0"
                max="10"
                step="0.1"
                @change="filterMovies"
              />
            </div>
          </div>

          <div class="filter-group">
            <label>国家/地区:</label>
            <select
              v-model="selectedCountry"
              @change="filterMovies"
              class="country-select"
            >
              <option value="">全部</option>
              <option
                v-for="country in countries"
                :key="country"
                :value="country"
              >
                {{ country }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label>类型:</label>
            <select
              v-model="selectedType"
              @change="filterMovies"
              class="type-select"
            >
              <option value="">全部</option>
              <option v-for="type in types" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>

          <button @click="resetFilters" class="reset-btn">重置筛选</button>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-section">
        <div class="stat-card">
          <div class="stat-number">{{ totalMovies }}</div>
          <div class="stat-label">总电影数</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ filteredMovies.length }}</div>
          <div class="stat-label">筛选结果</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ averageRating.toFixed(1) }}</div>
          <div class="stat-label">平均评分</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ yearRangeText }}</div>
          <div class="stat-label">年份跨度</div>
        </div>
      </div>

      <!-- 排序控制 -->
      <div class="sort-section">
        <div class="sort-controls">
          <label>排序方式:</label>
          <select v-model="sortBy" @change="sortMovies" class="sort-select">
            <option value="rating">评分从高到低</option>
            <option value="rating_asc">评分从低到高</option>
            <option value="year">年份从新到旧</option>
            <option value="year_asc">年份从旧到新</option>
            <option value="name">电影名称A-Z</option>
            <option value="name_desc">电影名称Z-A</option>
          </select>
        </div>
      </div>

      <!-- 电影列表 -->
      <div class="movies-section">
        <div v-if="loading" class="loading">加载电影数据中...</div>

        <div v-else-if="filteredMovies.length === 0" class="no-results">
          <p>没有找到符合条件的电影</p>
          <button @click="resetFilters" class="reset-btn">重置筛选条件</button>
        </div>

        <div v-else class="movies-grid">
          <div
            v-for="movie in filteredMovies"
            :key="movie['电影链接']"
            class="movie-card"
          >
            <div class="movie-header">
              <h3 class="movie-title">{{ movie["电影名字"] }}</h3>
              <div class="movie-rating">
                <span class="rating-star">⭐</span>
                <span class="rating-score">{{ movie["评分"] }}</span>
              </div>
            </div>

            <div class="movie-meta">
              <div class="meta-item">
                <span class="meta-label">年份:</span>
                <span class="meta-value">{{ movie["年份"] }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">国家:</span>
                <span class="meta-value">{{ movie["国家"] }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">类型:</span>
                <span class="meta-value">{{ movie["类型"] }}</span>
              </div>
            </div>

            <div class="movie-crew">
              <div class="crew-item">
                <span class="crew-label">导演:</span>
                <span class="crew-value">{{ movie["导演"] || "未知" }}</span>
              </div>
              <div class="crew-item">
                <span class="crew-label">主演:</span>
                <span class="crew-value">{{ movie["主演"] || "未知" }}</span>
              </div>
            </div>

            <div class="movie-quote" v-if="movie['一句话评价']">
              <span class="quote-icon">💬</span>
              <span class="quote-text">{{ movie["一句话评价"] }}</span>
            </div>

            <div class="movie-actions">
              <a
                :href="movie['电影链接']"
                target="_blank"
                class="action-btn douban-link"
              >
                查看豆瓣详情
              </a>
              <button
                @click="addToFavorites(movie)"
                class="action-btn favorite-btn"
              >
                {{ isFavorite(movie) ? "❤️ 已收藏" : "🤍 收藏" }}
              </button>
            </div>
          </div>
        </div>

        <!-- 分页控制 -->
        <div v-if="filteredMovies.length > 0" class="pagination">
          <button
            @click="prevPage"
            :disabled="currentPage === 1"
            class="page-btn"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ currentPage }} 页 / 共 {{ totalPages }} 页 ({{
              filteredMovies.length
            }}
            部电影)
          </span>
          <button
            @click="nextPage"
            :disabled="currentPage === totalPages"
            class="page-btn"
          >
            下一页
          </button>
        </div>
      </div>

      <!-- 推荐算法部分 -->
      <div class="recommendation-section">
        <h2>🎯 智能推荐</h2>
        <div class="recommendation-controls">
          <button @click="getRandomRecommendations" class="recommend-btn">
            🎲 随机推荐
          </button>
          <button @click="getHighRatingRecommendations" class="recommend-btn">
            ⭐ 高分推荐
          </button>
          <button @click="getRecentRecommendations" class="recommend-btn">
            🆕 近期推荐
          </button>
          <button @click="getByGenreRecommendations" class="recommend-btn">
            🎭 类型推荐
          </button>
        </div>

        <div v-if="recommendations.length > 0" class="recommendations-grid">
          <div
            v-for="movie in recommendations"
            :key="movie['电影链接']"
            class="recommendation-card"
          >
            <div class="rec-header">
              <h4>{{ movie["电影名字"] }}</h4>
              <span class="rec-rating">⭐ {{ movie["评分"] }}</span>
            </div>
            <div class="rec-info">
              <span class="rec-year">{{ movie["年份"] }}</span>
              <span class="rec-country">{{ movie["国家"] }}</span>
              <span class="rec-genre">{{ movie["类型"] }}</span>
            </div>
            <p class="rec-quote" v-if="movie['一句话评价']">
              {{ movie["一句话评价"] }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";
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

export default defineComponent({
  name: "DoubanView",
  setup() {
    // 数据状态
    const allMovies = ref<DoubanMovie[]>([]);
    const filteredMovies = ref<DoubanMovie[]>([]);
    const recommendations = ref<DoubanMovie[]>([]);
    const loading = ref(true);
    const favorites = ref<Set<string>>(new Set());

    // 筛选状态
    const searchQuery = ref("");
    const yearRange = ref([1900, 2026]);
    const ratingRange = ref([0, 10]);
    const selectedCountry = ref("");
    const selectedType = ref("");
    const sortBy = ref("rating");
    const currentPage = ref(1);
    const itemsPerPage = 20;

    // 计算属性
    const totalMovies = computed(() => allMovies.value.length);
    const averageRating = computed(() => {
      if (allMovies.value.length === 0) return 0;
      const sum = allMovies.value.reduce((acc, movie) => {
        return acc + parseFloat(movie["评分"] || "0");
      }, 0);
      return sum / allMovies.value.length;
    });
    const yearRangeText = computed(() => {
      const years = allMovies.value
        .map((m) => parseInt(m["年份"]) || 0)
        .filter((y) => y > 0);
      if (years.length === 0) return "未知";
      const min = Math.min(...years);
      const max = Math.max(...years);
      return `${min} - ${max}`;
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
    const types = computed(() => {
      const typeSet = new Set<string>();
      allMovies.value.forEach((movie) => {
        if (movie["类型"]) {
          const types = movie["类型"].split(" ");
          types.forEach((t) => typeSet.add(t.trim()));
        }
      });
      return Array.from(typeSet).sort();
    });
    const totalPages = computed(() =>
      Math.ceil(filteredMovies.value.length / itemsPerPage)
    );
    const paginatedMovies = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      const end = start + itemsPerPage;
      return filteredMovies.value.slice(start, end);
    });

    // 初始化数据
    const loadMovies = () => {
      loading.value = true;
      try {
        allMovies.value = doubanData as DoubanMovie[];
        filteredMovies.value = [...allMovies.value];

        // 自动设置年份范围
        const years = allMovies.value
          .map((m) => parseInt(m["年份"]) || 0)
          .filter((y) => y > 0);
        if (years.length > 0) {
          yearRange.value = [Math.min(...years), Math.max(...years)];
        }

        // 自动设置评分范围
        const ratings = allMovies.value
          .map((m) => parseFloat(m["评分"]) || 0)
          .filter((r) => r > 0);
        if (ratings.length > 0) {
          ratingRange.value = [Math.min(...ratings), Math.max(...ratings)];
        }

        sortMovies();
      } catch (error) {
        console.error("加载电影数据失败:", error);
      } finally {
        loading.value = false;
      }
    };

    // 筛选电影
    const filterMovies = () => {
      let filtered = [...allMovies.value];

      // 搜索筛选
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter(
          (movie) =>
            movie["电影名字"].toLowerCase().includes(query) ||
            movie["导演"].toLowerCase().includes(query) ||
            movie["主演"].toLowerCase().includes(query) ||
            movie["类型"].toLowerCase().includes(query)
        );
      }

      // 年份筛选
      filtered = filtered.filter((movie) => {
        const year = parseInt(movie["年份"]) || 0;
        return year >= yearRange.value[0] && year <= yearRange.value[1];
      });

      // 评分筛选
      filtered = filtered.filter((movie) => {
        const rating = parseFloat(movie["评分"]) || 0;
        return rating >= ratingRange.value[0] && rating <= ratingRange.value[1];
      });

      // 国家筛选
      if (selectedCountry.value) {
        filtered = filtered.filter((movie) =>
          movie["国家"].includes(selectedCountry.value)
        );
      }

      // 类型筛选
      if (selectedType.value) {
        filtered = filtered.filter((movie) =>
          movie["类型"].includes(selectedType.value)
        );
      }

      filteredMovies.value = filtered;
      currentPage.value = 1;
      sortMovies();
    };

    // 排序电影
    const sortMovies = () => {
      filteredMovies.value.sort((a, b) => {
        switch (sortBy.value) {
          case "rating":
            return parseFloat(b["评分"] || "0") - parseFloat(a["评分"] || "0");
          case "rating_asc":
            return parseFloat(a["评分"] || "0") - parseFloat(b["评分"] || "0");
          case "year":
            return (parseInt(b["年份"]) || 0) - (parseInt(a["年份"]) || 0);
          case "year_asc":
            return (parseInt(a["年份"]) || 0) - (parseInt(b["年份"]) || 0);
          case "name":
            return a["电影名字"].localeCompare(b["电影名字"]);
          case "name_desc":
            return b["电影名字"].localeCompare(a["电影名字"]);
          default:
            return 0;
        }
      });
    };

    // 重置筛选
    const resetFilters = () => {
      searchQuery.value = "";
      selectedCountry.value = "";
      selectedType.value = "";
      sortBy.value = "rating";

      // 重置年份范围
      const years = allMovies.value
        .map((m) => parseInt(m["年份"]) || 0)
        .filter((y) => y > 0);
      if (years.length > 0) {
        yearRange.value = [Math.min(...years), Math.max(...years)];
      }

      // 重置评分范围
      const ratings = allMovies.value
        .map((m) => parseFloat(m["评分"]) || 0)
        .filter((r) => r > 0);
      if (ratings.length > 0) {
        ratingRange.value = [Math.min(...ratings), Math.max(...ratings)];
      }

      filterMovies();
    };

    // 分页控制
    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
      }
    };

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
      }
    };

    // 收藏功能
    const isFavorite = (movie: DoubanMovie) => {
      return favorites.value.has(movie["电影链接"]);
    };

    const addToFavorites = (movie: DoubanMovie) => {
      if (favorites.value.has(movie["电影链接"])) {
        favorites.value.delete(movie["电影链接"]);
      } else {
        favorites.value.add(movie["电影链接"]);
      }
      // 保存到localStorage
      localStorage.setItem(
        "movie_favorites",
        JSON.stringify(Array.from(favorites.value))
      );
    };

    // 推荐算法
    const getRandomRecommendations = () => {
      const shuffled = [...allMovies.value].sort(() => 0.5 - Math.random());
      recommendations.value = shuffled.slice(0, 6);
    };

    const getHighRatingRecommendations = () => {
      const highRated = [...allMovies.value]
        .filter((movie) => parseFloat(movie["评分"]) >= 9.0)
        .sort((a, b) => parseFloat(b["评分"]) - parseFloat(a["评分"]));
      recommendations.value = highRated.slice(0, 6);
    };

    const getRecentRecommendations = () => {
      const recent = [...allMovies.value]
        .filter((movie) => {
          const year = parseInt(movie["年份"]) || 0;
          return year >= 2000;
        })
        .sort(
          (a, b) => (parseInt(b["年份"]) || 0) - (parseInt(a["年份"]) || 0)
        );
      recommendations.value = recent.slice(0, 6);
    };

    const getByGenreRecommendations = () => {
      // 获取最常见的类型
      const genreCounts: Record<string, number> = {};
      allMovies.value.forEach((movie) => {
        if (movie["类型"]) {
          const genres = movie["类型"].split(" ");
          genres.forEach((genre) => {
            genreCounts[genre] = (genreCounts[genre] || 0) + 1;
          });
        }
      });

      // 找到最常见的类型
      const mostCommonGenre = Object.entries(genreCounts).sort(
        (a, b) => b[1] - a[1]
      )[0]?.[0];

      if (mostCommonGenre) {
        const byGenre = allMovies.value
          .filter((movie) => movie["类型"].includes(mostCommonGenre))
          .sort((a, b) => parseFloat(b["评分"]) - parseFloat(a["评分"]));
        recommendations.value = byGenre.slice(0, 6);
      }
    };

    // 初始化收藏夹
    const loadFavorites = () => {
      const saved = localStorage.getItem("movie_favorites");
      if (saved) {
        favorites.value = new Set(JSON.parse(saved));
      }
    };

    // 生命周期钩子
    onMounted(() => {
      loadMovies();
      loadFavorites();
    });

    // 返回所有需要暴露给模板的属性和方法
    return {
      // 数据
      allMovies,
      filteredMovies: paginatedMovies,
      recommendations,
      loading,
      favorites,

      // 筛选状态
      searchQuery,
      yearRange,
      ratingRange,
      selectedCountry,
      selectedType,
      sortBy,
      currentPage,

      // 计算属性
      totalMovies,
      averageRating,
      yearRangeText,
      countries,
      types,
      totalPages,

      // 方法
      filterMovies,
      sortMovies,
      resetFilters,
      prevPage,
      nextPage,
      isFavorite,
      addToFavorites,
      getRandomRecommendations,
      getHighRatingRecommendations,
      getRecentRecommendations,
      getByGenreRecommendations,
    };
  },
});
</script>

<style scoped>
.douban-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  font-size: 2.8rem;
  font-weight: 700;
}

.subtitle {
  margin: 15px 0 0;
  font-size: 1.3rem;
  opacity: 0.9;
}

.container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 筛选部分样式 */
.filter-section {
  background: white;
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 25px;
}

.search-input {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

.search-btn {
  padding: 12px 30px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background 0.3s;
}

.search-btn:hover {
  background: #5a67d8;
}

.filter-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-weight: 600;
  color: #4a5568;
  font-size: 0.95rem;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.range-inputs input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.95rem;
}

.range-inputs span {
  color: #718096;
  font-size: 0.9rem;
}

.country-select,
.type-select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.95rem;
  background: white;
}

.reset-btn {
  align-self: flex-end;
  padding: 10px 20px;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  transition: background 0.3s;
}

.reset-btn:hover {
  background: #c53030;
}

/* 统计信息样式 */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 1rem;
  color: #718096;
  font-weight: 500;
}

/* 排序部分样式 */
.sort-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.sort-controls label {
  font-weight: 600;
  color: #4a5568;
}

.sort-select {
  padding: 8px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  background: white;
  min-width: 200px;
}

/* 电影列表样式 */
.movies-section {
  background: white;
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.loading {
  text-align: center;
  padding: 60px;
  font-size: 1.3rem;
  color: #667eea;
}

.no-results {
  text-align: center;
  padding: 60px;
}

.no-results p {
  font-size: 1.2rem;
  color: #718096;
  margin-bottom: 20px;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
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

.movie-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.movie-title {
  margin: 0;
  font-size: 1.4rem;
  color: #2d3748;
  line-height: 1.3;
  flex: 1;
  margin-right: 15px;
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

.rating-score {
  font-weight: 700;
  color: #d97706;
  font-size: 1.1rem;
}

.movie-meta {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f7fafc;
  border-radius: 8px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-size: 0.85rem;
  color: #718096;
  font-weight: 500;
}

.meta-value {
  font-size: 0.95rem;
  color: #4a5568;
  font-weight: 600;
}

.movie-crew {
  margin-bottom: 20px;
}

.crew-item {
  margin-bottom: 12px;
}

.crew-item:last-child {
  margin-bottom: 0;
}

.crew-label {
  display: inline-block;
  width: 50px;
  font-size: 0.9rem;
  color: #718096;
  font-weight: 500;
}

.crew-value {
  font-size: 0.95rem;
  color: #4a5568;
  line-height: 1.4;
}

.movie-quote {
  margin: 20px 0;
  padding: 15px;
  background: linear-gradient(135deg, #f0f4ff 0%, #e6fffa 100%);
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.quote-icon {
  margin-right: 10px;
  font-size: 1.2rem;
}

.quote-text {
  font-style: italic;
  color: #4a5568;
  line-height: 1.5;
}

.movie-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.action-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  text-align: center;
  text-decoration: none;
  transition: all 0.3s;
}

.douban-link {
  background: #667eea;
  color: white;
}

.douban-link:hover {
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

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.page-btn {
  padding: 10px 25px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background 0.3s;
}

.page-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.page-btn:not(:disabled):hover {
  background: #5a67d8;
}

.page-info {
  font-size: 1rem;
  color: #4a5568;
  font-weight: 500;
}

/* 推荐部分样式 */
.recommendation-section {
  background: white;
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.recommendation-section h2 {
  margin-top: 0;
  margin-bottom: 25px;
  color: #2d3748;
  font-size: 1.8rem;
}

.recommendation-controls {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.recommend-btn {
  padding: 12px 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: transform 0.3s, box-shadow 0.3s;
}

.recommend-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(102, 126, 234, 0.3);
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.recommendation-card {
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 20px;
  background: white;
  transition: transform 0.3s;
}

.recommendation-card:hover {
  transform: translateY(-5px);
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.rec-header h4 {
  margin: 0;
  font-size: 1.2rem;
  color: #2d3748;
  flex: 1;
  margin-right: 15px;
}

.rec-rating {
  background: #fef3c7;
  color: #d97706;
  padding: 4px 10px;
  border-radius: 15px;
  font-weight: 600;
  font-size: 0.9rem;
}

.rec-info {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.rec-year,
.rec-country,
.rec-genre {
  font-size: 0.85rem;
  padding: 4px 10px;
  border-radius: 12px;
  background: #f7fafc;
  color: #4a5568;
}

.rec-quote {
  margin: 0;
  font-style: italic;
  color: #718096;
  font-size: 0.95rem;
  line-height: 1.5;
  border-left: 3px solid #667eea;
  padding-left: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header h1 {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 1.1rem;
  }

  .movies-grid {
    grid-template-columns: 1fr;
  }

  .filter-controls {
    grid-template-columns: 1fr;
  }

  .movie-meta {
    grid-template-columns: 1fr;
  }

  .recommendation-controls {
    flex-direction: column;
  }

  .recommend-btn {
    width: 100%;
  }

  .pagination {
    flex-direction: column;
    gap: 15px;
  }

  .page-info {
    order: -1;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 20px;
  }

  .header h1 {
    font-size: 1.6rem;
  }

  .movie-card {
    padding: 20px;
  }

  .movie-actions {
    flex-direction: column;
  }
}
</style>
