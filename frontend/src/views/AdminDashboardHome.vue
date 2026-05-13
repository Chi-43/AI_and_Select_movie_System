<template>
  <div class="dashboard-home">
    <section class="stats-row">
      <div class="stat-card">
        <div class="stat-icon">👤</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.total_users }}</div>
          <div class="stat-label">用户总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🎬</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.total_movies }}</div>
          <div class="stat-label">电影总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.total_ratings }}</div>
          <div class="stat-label">评分总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💬</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.total_comments }}</div>
          <div class="stat-label">评论总数</div>
        </div>
      </div>
    </section>

    <section class="recent-row">
      <div class="panel-card">
        <h3>近 7 天新增</h3>
        <div class="recent-grid">
          <div class="recent-item">
            <span class="recent-num">{{
              stats.recent?.new_users_7d || 0
            }}</span>
            <span class="recent-label">新用户</span>
          </div>
          <div class="recent-item">
            <span class="recent-num">{{
              stats.recent?.new_ratings_7d || 0
            }}</span>
            <span class="recent-label">新评分</span>
          </div>
          <div class="recent-item">
            <span class="recent-num">{{
              stats.recent?.new_comments_7d || 0
            }}</span>
            <span class="recent-label">新评论</span>
          </div>
        </div>
      </div>
    </section>

    <section class="charts-row">
      <div class="panel-card">
        <h3>热门电影类型</h3>
        <div class="genre-chart" v-if="stats.top_genres?.length">
          <div
            v-for="g in stats.top_genres"
            :key="g.name"
            class="genre-bar-wrap"
          >
            <span class="genre-name">{{ g.name }}</span>
            <div class="genre-bar-bg">
              <div
                class="genre-bar-fill"
                :style="{ width: barWidth(g.count) + '%' }"
              ></div>
            </div>
            <span class="genre-count">{{ g.count }}</span>
          </div>
        </div>
      </div>

      <div class="panel-card">
        <h3>评分分布</h3>
        <div class="rating-dist" v-if="stats.rating_distribution">
          <div v-for="star in [5, 4, 3, 2, 1]" :key="star" class="rating-row">
            <span class="star-label">{{ star }} 星</span>
            <div class="rating-bar-bg">
              <div
                class="rating-bar-fill"
                :style="{ width: ratingBarWidth(star) + '%' }"
              ></div>
            </div>
            <span class="rating-count-val">{{
              stats.rating_distribution[String(star)] || 0
            }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="quick-grid">
      <router-link to="/admin/users" class="quick-card">
        <span class="quick-icon">👤</span>
        <h3>用户管理</h3>
        <p>查看、编辑和删除系统中的用户</p>
      </router-link>
      <router-link to="/admin/movies" class="quick-card">
        <span class="quick-icon">🎞️</span>
        <h3>电影管理</h3>
        <p>新增、修改或删除电影数据</p>
      </router-link>
      <router-link to="/admin/comments" class="quick-card">
        <span class="quick-icon">💬</span>
        <h3>评论管理</h3>
        <p>查看并删除不合规评论</p>
      </router-link>
      <router-link to="/admin/profile" class="quick-card">
        <span class="quick-icon">⚙️</span>
        <h3>个人信息</h3>
        <p>查看并修改管理员资料</p>
      </router-link>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";

const API_BASE_URL = "http://127.0.0.1:8000";

interface DashboardStats {
  total_users: number;
  total_movies: number;
  total_comments: number;
  total_ratings: number;
  recent: {
    new_users_7d: number;
    new_comments_7d: number;
    new_ratings_7d: number;
  };
  top_genres: { name: string; count: number }[];
  rating_distribution: Record<string, number>;
}

export default defineComponent({
  name: "AdminDashboardHome",
  setup() {
    const stats = ref<DashboardStats>({
      total_users: 0,
      total_movies: 0,
      total_comments: 0,
      total_ratings: 0,
      recent: { new_users_7d: 0, new_comments_7d: 0, new_ratings_7d: 0 },
      top_genres: [],
      rating_distribution: {},
    });

    const maxGenre = ref(1);
    const maxRating = ref(1);

    const barWidth = (count: number) =>
      Math.round((count / maxGenre.value) * 100);
    const ratingBarWidth = (star: number) => {
      const val = stats.value.rating_distribution[String(star)] || 0;
      return Math.round((val / maxRating.value) * 100);
    };

    const fetchStats = async () => {
      const token = localStorage.getItem("admin_token");
      try {
        const res = await fetch(`${API_BASE_URL}/api/admin/dashboard/`, {
          headers: token ? { Authorization: `Token ${token}` } : {},
        });
        if (res.ok) {
          const data = await res.json();
          stats.value = data;
          maxGenre.value = Math.max(
            1,
            ...(data.top_genres || []).map((g: any) => g.count)
          );
          const dist = data.rating_distribution || {};
          maxRating.value = Math.max(1, ...(Object.values(dist) as number[]));
        }
      } catch (e) {
        console.error("加载仪表盘失败:", e);
      }
    };

    onMounted(fetchStats);

    return { stats, barWidth, ratingBarWidth };
  },
});
</script>

<style scoped>
.dashboard-home {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  border-radius: var(--radius-lg);
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  box-shadow: var(--panel-shadow);
}

.stat-icon {
  font-size: 2rem;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--text-primary);
}

.stat-label {
  margin-top: 4px;
  color: var(--text-secondary);
  font-size: 0.88rem;
}

.recent-row {
  display: grid;
  gap: 16px;
}

.recent-grid {
  display: flex;
  gap: 28px;
}

.recent-item {
  text-align: center;
}

.recent-num {
  display: block;
  font-size: 1.6rem;
  font-weight: 900;
  color: var(--primary);
}

.recent-label {
  color: var(--text-secondary);
  font-size: 0.86rem;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.panel-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 22px;
  box-shadow: var(--panel-shadow);
}

.panel-card h3 {
  margin: 0 0 16px;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.genre-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.genre-bar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.genre-name {
  width: 56px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  text-align: right;
  flex-shrink: 0;
}

.genre-bar-bg,
.rating-bar-bg {
  flex: 1;
  height: 10px;
  border-radius: 5px;
  background: var(--nav-hover-bg);
  overflow: hidden;
}

.genre-bar-fill {
  height: 100%;
  border-radius: 5px;
  background: var(--primary-gradient);
  transition: width 0.6s ease;
}

.genre-count {
  width: 32px;
  font-size: 0.85rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.rating-dist {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rating-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.star-label {
  width: 36px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.rating-bar-fill {
  height: 100%;
  border-radius: 5px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  transition: width 0.6s ease;
}

.rating-count-val {
  width: 32px;
  font-size: 0.85rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.quick-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px;
  border-radius: var(--radius-md);
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  text-decoration: none;
  color: inherit;
  transition: all var(--transition-fast);
}

.quick-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--panel-shadow);
}

.quick-icon {
  font-size: 1.5rem;
}

.quick-card h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
}

.quick-card p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

@media (max-width: 900px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    grid-template-columns: 1fr;
  }
  .quick-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
