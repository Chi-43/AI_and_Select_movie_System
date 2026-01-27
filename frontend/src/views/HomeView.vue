<template>
  <div class="home">
    <div class="header">
      <h1>🎬 基于协同过滤的电影推荐系统</h1>
      <p class="subtitle">使用协同过滤算法为您推荐喜欢的电影</p>
    </div>

    <div class="container">
      <!-- 用户信息部分 -->
      <div class="user-section" v-if="currentUser">
        <h2>👤 欢迎, {{ currentUser.username }}</h2>
        <div class="user-info">
          <p><strong>邮箱:</strong> {{ currentUser.email || "未设置" }}</p>
          <p>
            <strong>注册时间:</strong>
            {{ new Date(currentUser.date_joined).toLocaleDateString() }}
          </p>
        </div>

        <div class="user-actions">
          <button @click="getRecommendations('user_based')" class="action-btn">
            基于用户的推荐
          </button>
          <button @click="getRecommendations('item_based')" class="action-btn">
            基于电影的推荐
          </button>
          <button @click="getTopMovies" class="action-btn">热门电影</button>
        </div>
      </div>

      <div class="user-section" v-else>
        <h2>👤 请先登录</h2>
        <p>登录后可以获取个性化电影推荐</p>
        <div class="user-actions">
          <router-link to="/login" class="action-btn">登录</router-link>
          <router-link to="/register" class="action-btn">注册</router-link>
        </div>
      </div>

      <!-- 推荐结果部分 -->
      <div class="recommendations-section">
        <h2>🎯 推荐结果</h2>
        <div v-if="loading" class="loading">加载中...</div>

        <div v-if="recommendations.length > 0" class="recommendations">
          <div class="algorithm-info">
            <span class="algorithm-badge">{{
              algorithm === "user_based"
                ? "基于用户"
                : algorithm === "item_based"
                ? "基于电影"
                : "热门电影"
            }}</span>
            <span class="count">共 {{ recommendations.length }} 部电影</span>
          </div>

          <div class="movies-grid">
            <div
              v-for="movie in recommendations"
              :key="movie.id"
              class="movie-card"
            >
              <div class="movie-header">
                <h3>{{ movie.title }}</h3>
                <span class="year">{{ movie.year }}</span>
              </div>
              <div class="movie-genre">{{ movie.genre }}</div>
              <p class="movie-description">{{ movie.description }}</p>
              <div class="movie-actions">
                <button @click="getSimilarMovies(movie.id)" class="similar-btn">
                  相似电影
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!loading && currentUser" class="no-recommendations">
          <p>请点击上面的按钮获取推荐</p>
        </div>
        <div v-else-if="!loading && !currentUser" class="no-recommendations">
          <p>请先登录以获取个性化推荐</p>
        </div>
      </div>

      <!-- 相似电影部分 -->
      <div v-if="similarMovies.length > 0" class="similar-section">
        <h2>🎭 相似电影</h2>
        <div class="similar-movies">
          <div
            v-for="movie in similarMovies"
            :key="movie.id"
            class="similar-movie-card"
          >
            <h4>{{ movie.title }}</h4>
            <div class="similar-movie-info">
              <span class="genre">{{ movie.genre }}</span>
              <span class="year">{{ movie.year }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 电影列表部分 -->
      <div class="movies-section">
        <h2>📽️ 所有电影</h2>
        <div class="movies-list">
          <div v-for="movie in allMovies" :key="movie.id" class="movie-item">
            <div class="movie-item-header">
              <h4>{{ movie.title }}</h4>
              <span class="movie-year">{{ movie.year }}</span>
            </div>
            <div class="movie-item-genre">{{ movie.genre }}</div>
            <button @click="rateMovie(movie)" class="rate-btn">评分</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from "vue";
import axios from "axios";
import { useAuthStore } from "@/stores/auth";

interface Movie {
  id: number;
  title: string;
  genre: string;
  year: number;
  description: string;
}

interface RecommendationResponse {
  user_id: number;
  username: string;
  algorithm: string;
  recommendations: Movie[];
}

export default defineComponent({
  name: "HomeView",
  setup() {
    const authStore = useAuthStore();
    const allMovies = ref<Movie[]>([]);
    const recommendations = ref<Movie[]>([]);
    const similarMovies = ref<Movie[]>([]);
    const loading = ref(false);
    const algorithm = ref<string>("");

    // API基础URL
    const API_BASE_URL = "http://localhost:8000/api";

    // 计算当前用户
    const currentUser = computed(() => authStore.user);

    // 获取所有电影
    const fetchMovies = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/movies/`);
        allMovies.value = response.data;
      } catch (error) {
        console.error("获取电影失败:", error);
      }
    };

    // 获取推荐
    const getRecommendations = async (algo: string) => {
      if (!currentUser.value) {
        alert("请先登录");
        return;
      }

      loading.value = true;
      algorithm.value = algo;

      try {
        const response = await axios.get<RecommendationResponse>(
          `${API_BASE_URL}/recommendations/`,
          {
            params: {
              user_id: currentUser.value.id,
              algorithm: algo,
              top_n: 10,
            },
            headers: {
              Authorization: `Token ${authStore.token}`,
            },
          }
        );

        recommendations.value = response.data.recommendations;
        similarMovies.value = [];
      } catch (error) {
        console.error("获取推荐失败:", error);
        alert("获取推荐失败，请检查后端服务是否运行");
      } finally {
        loading.value = false;
      }
    };

    // 获取热门电影
    const getTopMovies = async () => {
      loading.value = true;
      algorithm.value = "top_movies";

      try {
        const response = await axios.get(`${API_BASE_URL}/top-movies/`, {
          params: { top_n: 10 },
        });

        recommendations.value = response.data.top_movies;
        similarMovies.value = [];
      } catch (error) {
        console.error("获取热门电影失败:", error);
      } finally {
        loading.value = false;
      }
    };

    // 获取相似电影
    const getSimilarMovies = async (movieId: number) => {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/similar-movies/${movieId}/`,
          {
            params: { top_n: 5 },
          }
        );

        similarMovies.value = response.data.similar_movies;
      } catch (error) {
        console.error("获取相似电影失败:", error);
      }
    };

    // 评分电影
    const rateMovie = async (movie: Movie) => {
      if (!currentUser.value) {
        alert("请先登录");
        return;
      }

      const rating = prompt(`请为《${movie.title}》评分（1-5分）:`);
      if (rating && parseInt(rating) >= 1 && parseInt(rating) <= 5) {
        try {
          await axios.post(
            `${API_BASE_URL}/ratings/`,
            {
              user: currentUser.value.id,
              movie: movie.id,
              rating: parseFloat(rating),
            },
            {
              headers: {
                Authorization: `Token ${authStore.token}`,
              },
            }
          );
          alert(`评分成功！您给《${movie.title}》评分: ${rating}分`);
        } catch (error) {
          console.error("评分失败:", error);
          alert("评分失败，请重试");
        }
      }
    };

    // 初始化
    onMounted(() => {
      fetchMovies();
    });

    return {
      currentUser,
      allMovies,
      recommendations,
      similarMovies,
      loading,
      algorithm,
      getRecommendations,
      getTopMovies,
      getSimilarMovies,
      rateMovie,
    };
  },
});
</script>

<style scoped>
.home {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
}

.header h1 {
  margin: 0;
  font-size: 2.5rem;
}

.subtitle {
  margin: 10px 0 0;
  font-size: 1.2rem;
  opacity: 0.9;
}

.container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.user-section,
.recommendations-section,
.similar-section,
.movies-section {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
}

.user-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 20px 0;
}

.user-btn {
  padding: 10px 20px;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
}

.user-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.user-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.selected-user {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.user-actions {
  display: flex;
  gap: 15px;
  margin-top: 15px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 24px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s;
}

.action-btn:hover {
  background: #45a049;
}

.action-btn:nth-child(2) {
  background: #2196f3;
}

.action-btn:nth-child(2):hover {
  background: #0b7dda;
}

.action-btn:nth-child(3) {
  background: #ff9800;
}

.action-btn:nth-child(3):hover {
  background: #e68a00;
}

.loading {
  text-align: center;
  padding: 40px;
  font-size: 1.2rem;
  color: #666;
}

.algorithm-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px;
  background: #f0f0f0;
  border-radius: 5px;
}

.algorithm-badge {
  background: #667eea;
  color: white;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
}

.count {
  color: #666;
  font-size: 0.9rem;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.movie-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.movie-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.movie-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.year {
  background: #f0f0f0;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.9rem;
  color: #666;
}

.movie-genre {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.movie-description {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 10px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.movie-actions {
  margin-top: 15px;
}

.similar-btn {
  padding: 8px 16px;
  background: #9c27b0;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.similar-btn:hover {
  background: #7b1fa2;
}

.similar-movies {
  display: flex;
  gap: 15px;
  overflow-x: auto;
  padding: 10px 0;
}

.similar-movie-card {
  flex: 0 0 auto;
  width: 200px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
}

.similar-movie-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 0.9rem;
  color: #666;
}

.movies-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.movie-item {
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #f9f9f9;
}

.movie-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.movie-item-header h4 {
  margin: 0;
  font-size: 1rem;
}

.movie-year {
  font-size: 0.9rem;
  color: #666;
}

.movie-item-genre {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 10px;
}

.rate-btn {
  width: 100%;
  padding: 8px;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.rate-btn:hover {
  background: #e68a00;
}

.no-recommendations {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .movies-grid {
    grid-template-columns: 1fr;
  }

  .user-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }
}
</style>
