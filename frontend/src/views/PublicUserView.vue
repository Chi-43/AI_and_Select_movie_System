<template>
  <div class="public-user-view">
    <div v-if="errorMsg" class="error-section panel-card">
      <p>{{ errorMsg }}</p>
      <router-link to="/" class="primary-btn">返回首页</router-link>
    </div>

    <template v-else>
      <section class="hero-section">
        <div class="hero-content">
          <div class="avatar-wrap">
            <div class="avatar" :style="avatarStyle">
              {{ userInitial }}
            </div>
          </div>
          <div class="hero-info">
            <h1 class="username">{{ userData?.username }}</h1>
            <p class="bio" v-if="userData?.bio">{{ userData.bio }}</p>
            <p class="join-date">
              注册于 {{ formatDate(userData?.date_joined) }}
            </p>
          </div>

          <div class="hero-stats">
            <div class="stat-item">
              <div class="stat-num">{{ ratings.length }}</div>
              <div class="stat-label">评分</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">{{ comments.length }}</div>
              <div class="stat-label">评论</div>
            </div>
            <div class="stat-item" v-if="profileData">
              <div class="stat-num">
                {{ profileData.onboarding_completed ? "已设置" : "未设置" }}
              </div>
              <div class="stat-label">兴趣偏好</div>
            </div>
          </div>
        </div>
      </section>

      <section class="content-grid">
        <div class="main-column">
          <div class="panel-card" v-if="ratings.length > 0">
            <h2>最近评分</h2>
            <div class="rating-list">
              <div
                v-for="r in ratings"
                :key="r.movie.id"
                class="rating-item"
                @click="goToMovie(r.movie)"
              >
                <div class="rating-movie-info">
                  <span class="rm-title">{{ r.movie.title }}</span>
                  <span class="rm-year">{{ r.movie.year }}</span>
                </div>
                <div class="rating-stars">⭐ {{ r.rating }}</div>
              </div>
            </div>
          </div>

          <div class="panel-card" v-if="comments.length > 0">
            <h2>最近评论</h2>
            <div class="comment-list">
              <div
                v-for="c in comments"
                :key="c.id"
                class="comment-item"
                @click="goToMovie(c.movie)"
              >
                <div class="comment-movie-title">评《{{ c.movie.title }}》</div>
                <p class="comment-text">{{ c.content }}</p>
                <span class="comment-time">{{
                  formatDateTime(c.created_at)
                }}</span>
              </div>
            </div>
          </div>

          <div class="panel-card" v-if="favorites && favorites.length > 0">
            <h2>❤️ 喜欢的电影</h2>
            <div class="favorite-grid">
              <div
                v-for="f in favorites"
                :key="f.id"
                class="fav-card"
                @click="goToMovie(f)"
              >
                <div class="fav-title">{{ f.title }}</div>
                <div class="fav-meta">
                  <span>⭐ {{ f.rating }}</span>
                  <span>{{ f.year }}</span>
                  <span>{{ f.genre }}</span>
                </div>
              </div>
            </div>
          </div>

          <div
            v-if="
              ratings.length === 0 &&
              comments.length === 0 &&
              (!favorites || favorites.length === 0)
            "
            class="panel-card empty-card"
          >
            <p>该用户暂无评分和评论记录</p>
          </div>
        </div>

        <div class="side-column">
          <div class="panel-card" v-if="profileData">
            <h3>偏好类型</h3>
            <div class="chip-group">
              <span
                v-for="g in profileData.favorite_genres"
                :key="g"
                class="info-chip"
                >{{ g }}</span
              >
              <span
                v-if="!profileData.favorite_genres?.length"
                class="empty-chip"
                >暂无</span
              >
            </div>
          </div>

          <div class="panel-card" v-if="profileData">
            <h3>偏好国家/地区</h3>
            <div class="chip-group">
              <span
                v-for="c in profileData.favorite_countries"
                :key="c"
                class="info-chip"
                >{{ c }}</span
              >
              <span
                v-if="!profileData.favorite_countries?.length"
                class="empty-chip"
                >暂无</span
              >
            </div>
          </div>

          <div class="panel-card" v-if="profileData?.profile_summary">
            <h3>画像总结</h3>
            <p class="summary-text">{{ profileData.profile_summary }}</p>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const API_BASE_URL = "http://localhost:8000/api";

interface UserData {
  id: number;
  username: string;
  bio?: string;
  date_joined: string;
  avatar_url?: string;
}

interface ProfileData {
  favorite_genres: string[];
  favorite_countries: string[];
  favorite_keywords: string[];
  onboarding_completed: boolean;
  profile_summary: string;
}

interface RatingItem {
  movie: any;
  rating: number;
  timestamp: string;
}

interface CommentItem {
  id: number;
  movie: any;
  content: string;
  created_at: string;
}

export default defineComponent({
  name: "PublicUserView",
  setup() {
    const route = useRoute();
    const router = useRouter();

    const loading = ref(true);
    const errorMsg = ref("");
    const userData = ref<UserData | null>(null);
    const profileData = ref<ProfileData | null>(null);
    const ratings = ref<RatingItem[]>([]);
    const comments = ref<CommentItem[]>([]);
    const favorites = ref<any[] | null>(null);

    const userInitial = computed(
      () => userData.value?.username?.charAt(0).toUpperCase() || "?"
    );

    const avatarStyle = computed(() => {
      const colors = [
        "#667eea",
        "#764ba2",
        "#f56565",
        "#ed8936",
        "#48bb78",
        "#38b2ac",
      ];
      const idx = (userData.value?.username?.length || 0) % colors.length;
      return { backgroundColor: colors[idx] };
    });

    const formatDate = (d?: string) => {
      if (!d) return "";
      return new Date(d).toLocaleDateString("zh-CN");
    };

    const formatDateTime = (d: string) => {
      return new Date(d).toLocaleString("zh-CN");
    };

    const goToMovie = (movie: any) => {
      const detail = {
        id: movie.id,
        movie_id: movie.id,
        电影名字: movie.title,
        电影链接: movie.douban_url || "",
        评分: String(movie.rating || ""),
        评分人数: "",
        导演: movie.director || "",
        主演: movie.actors || "",
        年份: String(movie.year || ""),
        国家: movie.country || "",
        类型: movie.genre || "",
        一句话评价: movie.quote || "",
      };
      sessionStorage.setItem("current_movie_detail", JSON.stringify(detail));
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
      const userId = route.params.user_id;
      if (!userId) {
        errorMsg.value = "缺少用户ID";
        return;
      }

      try {
        const res = await fetch(`${API_BASE_URL}/users/${userId}/profile/`);
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error((err as any).error || "获取用户信息失败");
        }
        const data = await res.json();
        userData.value = data.user;
        profileData.value = data.profile;
        ratings.value = data.ratings || [];
        comments.value = data.comments || [];
        favorites.value = data.favorites;
      } catch (e: any) {
        errorMsg.value = e.message || "加载失败";
      } finally {
        loading.value = false;
      }
    });

    return {
      loading,
      errorMsg,
      userData,
      profileData,
      ratings,
      comments,
      favorites,
      userInitial,
      avatarStyle,
      formatDate,
      formatDateTime,
      goToMovie,
    };
  },
});
</script>

<style scoped>
.public-user-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: var(--max-width);
  margin: 0 auto;
}

.hero-section {
  background: var(--bg-hero);
  border-radius: var(--radius-lg);
  padding: 32px;
  color: #fff;
}

.hero-content {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.avatar-wrap {
  flex-shrink: 0;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 800;
  color: #fff;
  border: 3px solid rgba(255, 255, 255, 0.5);
}

.username {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 800;
}

.bio {
  margin: 8px 0 4px;
  color: rgba(255, 255, 255, 0.85);
}

.join-date {
  margin: 0;
  color: rgba(255, 255, 255, 0.65);
  font-size: 0.9rem;
}

.hero-stats {
  display: flex;
  gap: 18px;
  margin-left: auto;
}

.stat-item {
  text-align: center;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.12);
  min-width: 80px;
}

.stat-num {
  font-size: 1.5rem;
  font-weight: 800;
}

.stat-label {
  margin-top: 4px;
  font-size: 0.84rem;
  color: rgba(255, 255, 255, 0.8);
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.main-column,
.side-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 22px;
}

.panel-card h2,
.panel-card h3 {
  margin: 0 0 14px;
  color: var(--text-primary);
}

.rating-list,
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rating-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.rating-item:hover {
  background: var(--nav-hover-bg);
}

.rm-title {
  font-weight: 700;
  color: var(--text-primary);
}

.rm-year {
  margin-left: 8px;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.rating-stars {
  font-weight: 700;
  color: #d97706;
}

.comment-item {
  padding: 12px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.comment-item:hover {
  background: var(--nav-hover-bg);
}

.comment-movie-title {
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.comment-text {
  margin: 0 0 8px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.comment-time {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.info-chip {
  padding: 6px 12px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-primary);
  font-size: 0.86rem;
}

.empty-chip {
  padding: 6px 12px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-muted);
  font-size: 0.86rem;
}

.summary-text {
  color: var(--text-secondary);
  line-height: 1.8;
  margin: 0;
}

.favorite-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.fav-card {
  padding: 12px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.fav-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--panel-shadow);
}

.fav-title {
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.fav-meta {
  display: flex;
  gap: 8px;
  font-size: 0.84rem;
  color: var(--text-secondary);
}

.empty-card {
  text-align: center;
  color: var(--text-muted);
}

.error-section {
  text-align: center;
  padding: 60px 20px;
}

.primary-btn {
  display: inline-block;
  margin-top: 14px;
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  background: var(--primary-gradient);
  color: #fff;
  text-decoration: none;
  font-weight: 700;
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .hero-content {
    flex-direction: column;
    text-align: center;
  }

  .hero-stats {
    margin-left: 0;
    justify-content: center;
  }
}
</style>
