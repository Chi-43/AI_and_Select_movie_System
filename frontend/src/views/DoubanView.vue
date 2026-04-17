<template>
  <div class="douban-view">
    <!-- Hero -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">电影发现</div>
        <h1 class="hero-title">🎬 豆瓣电影 TOP250</h1>
        <p class="hero-subtitle">
          浏览高分电影、按条件筛选、查看详情、收藏影片，并基于当前电影库获取智能推荐。
        </p>

        <div class="hero-tags">
          <span class="hero-tag">高分电影</span>
          <span class="hero-tag">多维筛选</span>
          <span class="hero-tag">智能推荐</span>
          <span class="hero-tag">收藏管理</span>
        </div>
      </div>

      <div class="hero-stats">
        <div class="hero-stat-card">
          <div class="stat-number">{{ totalMovies }}</div>
          <div class="stat-label">总电影数</div>
        </div>
        <div class="hero-stat-card">
          <div class="stat-number">{{ averageRating.toFixed(1) }}</div>
          <div class="stat-label">平均评分</div>
        </div>
        <div class="hero-stat-card">
          <div class="stat-number">{{ yearRangeText }}</div>
          <div class="stat-label">年份跨度</div>
        </div>
      </div>
    </section>

    <!-- 搜索筛选 -->
    <section class="panel-card filter-panel">
      <div class="panel-header">
        <h2>🔍 搜索与筛选</h2>
        <p>
          根据电影名称、导演、主演、年份、评分、国家和类型快速定位目标电影。
        </p>
      </div>

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
          <label>年份范围</label>
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
          <label>评分范围</label>
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
          <label>国家/地区</label>
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
          <label>类型</label>
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

        <div class="filter-actions">
          <button @click="resetFilters" class="reset-btn">重置筛选</button>
        </div>
      </div>
    </section>

    <!-- 数据统计 -->
    <section class="stats-grid">
      <div class="stat-card">
        <div class="stat-number">{{ totalMovies }}</div>
        <div class="stat-label dark">总电影数</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ filteredMovies.length }}</div>
        <div class="stat-label dark">当前结果</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ averageRating.toFixed(1) }}</div>
        <div class="stat-label dark">平均评分</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ favorites.size }}</div>
        <div class="stat-label dark">收藏数量</div>
      </div>
    </section>

    <!-- 排序 -->
    <section class="panel-card sort-panel">
      <div class="sort-controls">
        <label>排序方式</label>
        <select v-model="sortBy" @change="sortMovies" class="sort-select">
          <option value="rating">评分从高到低</option>
          <option value="rating_asc">评分从低到高</option>
          <option value="year">年份从新到旧</option>
          <option value="year_asc">年份从旧到新</option>
          <option value="name">电影名称 A-Z</option>
          <option value="name_desc">电影名称 Z-A</option>
        </select>
      </div>
    </section>

    <!-- 电影列表 -->
    <section class="panel-card movies-section">
      <div class="panel-header">
        <h2>🎞️ 电影列表</h2>
        <p>当前按筛选条件与排序方式显示的电影结果。</p>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载电影数据中...</p>
      </div>

      <div v-else-if="filteredMovies.length === 0" class="empty-state">
        <div class="empty-icon">🎬</div>
        <h3>没有找到符合条件的电影</h3>
        <p>你可以调整筛选条件或重置筛选重新查看。</p>
        <button @click="resetFilters" class="reset-btn">重置筛选条件</button>
      </div>

      <div v-else class="movies-grid">
        <div
          v-for="movie in filteredMovies"
          :key="movie['电影链接']"
          class="movie-card"
        >
          <div class="movie-header">
            <div class="movie-title-wrap">
              <h3 class="movie-title">{{ movie["电影名字"] }}</h3>
              <div class="movie-tags">
                <span class="meta-chip">{{ movie["年份"] }}</span>
                <span class="meta-chip">{{ movie["国家"] }}</span>
              </div>
            </div>

            <div class="movie-rating">
              <span class="rating-star">⭐</span>
              <span class="rating-score">{{ movie["评分"] }}</span>
            </div>
          </div>

          <div class="movie-meta">
            <div class="meta-row">
              <span class="meta-label">类型</span>
              <span class="meta-value">{{ movie["类型"] }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">导演</span>
              <span class="meta-value">{{ movie["导演"] || "未知" }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">主演</span>
              <span class="meta-value">{{ movie["主演"] || "未知" }}</span>
            </div>
          </div>

          <div class="movie-quote" v-if="movie['一句话评价']">
            <span class="quote-icon">💬</span>
            <span class="quote-text">{{ movie["一句话评价"] }}</span>
          </div>

          <div class="movie-actions">
            <button
              @click="goToMovieDetail(movie)"
              class="action-btn detail-link"
            >
              电影详情
            </button>

            <button
              @click="addToFavorites(movie)"
              class="action-btn favorite-btn"
            >
              {{ isFavorite(movie) ? "❤️ 已收藏" : "🤍 收藏" }}
            </button>

            <router-link
              :to="{
                name: 'video-platform',
                query: {
                  movie_title: movie['电影名字'],
                  douban_url: movie['电影链接'],
                },
              }"
              class="action-btn watch-link"
            >
              📺 观看链接
            </router-link>
          </div>
        </div>
      </div>

      <div v-if="filteredMovies.length > 0" class="pagination">
        <button
          @click="prevPage"
          :disabled="currentPage === 1"
          class="page-btn"
        >
          上一页
        </button>

        <span class="page-info">
          第 {{ currentPage }} 页 / 共 {{ totalPages }} 页（{{
            filteredMovies.length
          }}
          部）
        </span>

        <button
          @click="nextPage"
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          下一页
        </button>
      </div>
    </section>

    <!-- 智能推荐 -->
    <section class="panel-card recommendation-section">
      <div class="panel-header">
        <h2>🎯 智能推荐</h2>
        <p>基于当前电影库快速生成不同风格的推荐结果。</p>
      </div>

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
            <span class="rec-chip">{{ movie["年份"] }}</span>
            <span class="rec-chip">{{ movie["国家"] }}</span>
            <span class="rec-chip">{{ movie["类型"] }}</span>
          </div>
          <p class="rec-quote" v-if="movie['一句话评价']">
            {{ movie["一句话评价"] }}
          </p>
        </div>
      </div>

      <div v-else class="recommend-placeholder">
        <p>点击上方按钮生成推荐结果</p>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";
import doubanData from "../data/豆瓣电影TOP250.json";

interface DoubanMovie {
  id?: number;
  movie_id?: number;
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

    const goToMovieDetail = (movie: DoubanMovie) => {
      if (!movie.id) {
        alert("当前电影还没有匹配到数据库ID，请确认后端电影数据是否已导入。");
        return;
      }

      const movieWithId = {
        ...movie,
        id: movie.id,
        movie_id: movie.id,
      };

      sessionStorage.setItem(
        "current_movie_detail",
        JSON.stringify(movieWithId)
      );

      window.location.href = `/movie-detail?movie_id=${
        movie.id
      }&movie_title=${encodeURIComponent(
        movie["电影名字"]
      )}&douban_url=${encodeURIComponent(movie["电影链接"])}`;
    };

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
    const normalizeUrl = (url: string) => {
      return (url || "").trim().replace(/\/+$/, "");
    };

    const mergeMovieIdsFromBackend = async (localMovies: DoubanMovie[]) => {
      try {
        const response = await fetch("http://localhost:8000/api/movies/");
        if (!response.ok) {
          throw new Error(`获取后端电影列表失败: ${response.status}`);
        }

        const backendMovies = await response.json();

        const urlToIdMap = new Map<string, number>();
        const titleYearToIdMap = new Map<string, number>();

        backendMovies.forEach((item: any) => {
          if (item.douban_url) {
            urlToIdMap.set(normalizeUrl(item.douban_url), item.id);
          }

          const key = `${(item.title || "").trim()}__${item.year || ""}`;
          titleYearToIdMap.set(key, item.id);
        });

        return localMovies.map((movie) => {
          const normalizedLocalUrl = normalizeUrl(movie["电影链接"]);
          const localKey = `${(movie["电影名字"] || "").trim()}__${
            movie["年份"] || ""
          }`;

          const id =
            urlToIdMap.get(normalizedLocalUrl) ||
            titleYearToIdMap.get(localKey) ||
            undefined;

          return {
            ...movie,
            id,
            movie_id: id,
          };
        });
      } catch (error) {
        console.error("合并后端电影ID失败:", error);
        return localMovies;
      }
    };
    // 初始化数据
    const loadMovies = async () => {
      loading.value = true;
      try {
        const localMovies = doubanData as DoubanMovie[];
        const mergedMovies = await mergeMovieIdsFromBackend(localMovies);

        allMovies.value = mergedMovies;
        filteredMovies.value = [...mergedMovies];

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
    onMounted(async () => {
      await loadMovies();
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
      goToMovieDetail,
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
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 24px;
}

.hero-section {
  background: var(--bg-hero);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  padding: 36px;
  color: #fff;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
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
  margin: 0 0 20px;
  line-height: 1.8;
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.92);
  max-width: 760px;
}

.hero-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.hero-tag {
  padding: 7px 12px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  font-size: 0.88rem;
}

.hero-stats {
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

.panel-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
  padding: 24px;
}

.panel-header {
  margin-bottom: 18px;
}

.panel-header h2 {
  margin: 0 0 8px;
  color: var(--text-primary);
  font-size: 1.5rem;
}

.panel-header p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--input-border);
  border-radius: var(--radius-md);
  font-size: 1rem;
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
}

.search-input::placeholder {
  color: var(--input-placeholder);
}

.search-input:focus {
  border-color: var(--input-focus-border);
  box-shadow: var(--input-focus-shadow);
}

.search-btn,
.recommend-btn,
.page-btn,
.reset-btn {
  border: none;
  cursor: pointer;
  font-weight: 700;
  transition: all var(--transition-fast);
}

.search-btn,
.recommend-btn,
.page-btn {
  background: var(--primary-gradient);
  color: #fff;
}

.search-btn {
  padding: 12px 24px;
  border-radius: var(--radius-md);
}

.search-btn:hover,
.recommend-btn:hover,
.page-btn:not(:disabled):hover {
  transform: translateY(-1px);
}

.filter-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-weight: 700;
  color: var(--text-secondary);
  font-size: 0.92rem;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.range-inputs input,
.country-select,
.type-select,
.sort-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--input-border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
}

.range-inputs input:focus,
.country-select:focus,
.type-select:focus,
.sort-select:focus {
  border-color: var(--input-focus-border);
}

.range-inputs span {
  color: var(--text-muted);
  font-size: 0.88rem;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
}

.reset-btn {
  padding: 10px 18px;
  background: #ef4444;
  color: #fff;
  border-radius: var(--radius-sm);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.stat-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  padding: 22px;
  border-radius: var(--radius-md);
  text-align: center;
  box-shadow: var(--panel-shadow);
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: var(--primary);
  margin-bottom: 8px;
  word-break: break-word;
}

.stat-label {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.9);
}

.stat-label.dark {
  color: var(--text-secondary);
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sort-controls label {
  font-weight: 700;
  color: var(--text-secondary);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 48px 24px;
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

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.movie-card {
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  background: var(--panel-bg);
  transition: all var(--transition-fast);
}

.movie-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--panel-shadow);
}

.movie-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.movie-title-wrap {
  flex: 1;
}

.movie-title {
  margin: 0 0 10px;
  font-size: 1.2rem;
  color: var(--text-primary);
  line-height: 1.4;
}

.movie-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-chip {
  padding: 5px 10px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.movie-rating {
  display: flex;
  align-items: center;
  gap: 5px;
  background: var(--rating-bg);
  padding: 6px 12px;
  border-radius: var(--radius-full);
}

.rating-score {
  font-weight: 700;
  color: var(--rating-text);
  font-size: 1rem;
}

.movie-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 14px;
  padding: 14px;
  background: var(--primary-bg);
  border-radius: var(--radius-sm);
}

.meta-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-size: 0.82rem;
  color: var(--text-muted);
  font-weight: 700;
}

.meta-value {
  font-size: 0.92rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.movie-quote {
  margin: 14px 0;
  padding: 14px;
  background: var(--quote-bg);
  border-radius: var(--radius-sm);
  border-left: 4px solid var(--quote-border);
}

.quote-text {
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 0.92rem;
}

.movie-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.action-btn {
  flex: 1;
  min-width: 100px;
  padding: 11px 12px;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.92rem;
  font-weight: 700;
  text-align: center;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.detail-link {
  background: var(--primary-gradient);
  color: #fff;
}

.favorite-btn {
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

.favorite-btn:hover {
  background: var(--danger);
  color: #fff;
}

.watch-link {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 18px;
  margin-top: 10px;
  padding-top: 20px;
  border-top: 1px solid var(--panel-border);
}

.page-btn {
  padding: 10px 20px;
  border-radius: var(--radius-sm);
}

.page-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
}

.page-info {
  color: var(--text-secondary);
  font-weight: 600;
}

.recommendation-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 22px;
}

.recommend-btn {
  padding: 11px 18px;
  border-radius: var(--radius-sm);
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}

.recommendation-card {
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  padding: 18px;
  background: var(--primary-bg);
  transition: all var(--transition-fast);
}

.recommendation-card:hover {
  transform: translateY(-3px);
}

.rec-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
  margin-bottom: 12px;
}

.rec-header h4 {
  margin: 0;
  font-size: 1.05rem;
  color: var(--text-primary);
}

.rec-rating {
  background: var(--rating-bg);
  color: var(--rating-text);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-weight: 700;
  font-size: 0.85rem;
  white-space: nowrap;
}

.rec-info {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.rec-chip {
  font-size: 0.82rem;
  padding: 5px 10px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
}

.rec-quote {
  margin: 0;
  line-height: 1.6;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.recommend-placeholder {
  text-align: center;
  padding: 30px 12px;
  color: var(--text-muted);
}

@media (max-width: 1100px) {
  .hero-section {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .douban-view {
    padding: 16px;
  }

  .hero-section,
  .panel-card {
    padding: 20px;
  }

  .hero-title {
    font-size: 2rem;
  }

  .search-box,
  .sort-controls,
  .pagination,
  .movie-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-controls,
  .stats-grid,
  .movies-grid,
  .recommendations-grid {
    grid-template-columns: 1fr;
  }

  .page-info {
    text-align: center;
  }
}
</style>
