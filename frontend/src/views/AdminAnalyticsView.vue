<template>
  <div class="analytics-page">
    <div class="stats-top">
      <div class="stat-card">
        <div class="n">{{ data.total_users }}</div>
        <div class="l">用户总数</div>
      </div>
      <div class="stat-card">
        <div class="n">{{ data.total_movies }}</div>
        <div class="l">电影总数</div>
      </div>
      <div class="stat-card">
        <div class="n">{{ data.total_ratings }}</div>
        <div class="l">评分总数</div>
      </div>
      <div class="stat-card">
        <div class="n">{{ data.total_comments }}</div>
        <div class="l">评论总数</div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card wide">
        <h3>用户增长趋势（近30天）</h3>
        <svg
          viewBox="0 0 600 180"
          class="line-chart"
          v-if="userGrowthPoints.length"
        >
          <polyline
            :points="userGrowthPoints"
            fill="none"
            stroke="#667eea"
            stroke-width="2.5"
          />
          <circle
            v-for="(p, i) in userGrowthDots"
            :key="'u' + i"
            :cx="p.x"
            :cy="p.y"
            r="3"
            fill="#667eea"
          />
        </svg>
        <div v-else class="no-data">暂无数据</div>
      </div>

      <div class="chart-card wide">
        <h3>每日活跃趋势（评分+评论）</h3>
        <svg
          viewBox="0 0 600 180"
          class="line-chart"
          v-if="activePoints.length"
        >
          <polyline
            :points="activePoints"
            fill="none"
            stroke="#f59e0b"
            stroke-width="2.5"
          />
          <circle
            v-for="(p, i) in activeDots"
            :key="'a' + i"
            :cx="p.x"
            :cy="p.y"
            r="3"
            fill="#f59e0b"
          />
        </svg>
        <div v-else class="no-data">暂无数据</div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3>电影类型分布</h3>
        <div class="bar-chart" v-if="data.genre_distribution?.length">
          <div
            v-for="g in data.genre_distribution"
            :key="g.name"
            class="bar-row"
          >
            <span class="bar-label">{{ g.name }}</span>
            <div class="bar-bg">
              <div
                class="bar-fill"
                :style="{ width: barPct(g.count, maxGenre) + '%' }"
              ></div>
            </div>
            <span class="bar-val">{{ g.count }}</span>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <h3>评分分布（1-5星）</h3>
        <div class="bar-chart" v-if="data.rating_distribution">
          <div v-for="star in [5, 4, 3, 2, 1]" :key="star" class="bar-row">
            <span class="bar-label">{{ star }} 星</span>
            <div class="bar-bg">
              <div
                class="bar-fill star"
                :style="{
                  width:
                    barPct(
                      data.rating_distribution[String(star)] || 0,
                      maxRating
                    ) + '%',
                }"
              ></div>
            </div>
            <span class="bar-val">{{
              data.rating_distribution[String(star)] || 0
            }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="chart-card">
      <h3>社区活跃</h3>
      <div class="community-stats">
        <div class="cs-item">
          <span class="cs-num">{{ data.community_posts || 0 }}</span
          ><span>帖子</span>
        </div>
        <div class="cs-item">
          <span class="cs-num">{{ data.community_replies || 0 }}</span
          ><span>回复</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";
const API = "http://127.0.0.1:8000";
export default defineComponent({
  name: "AdminAnalyticsView",
  setup() {
    const data = ref<any>({});
    const maxGenre = ref(1);
    const maxRating = ref(1);

    const barPct = (v: number, max: number) => Math.round((v / max) * 100);

    const userGrowthDots = computed(() => {
      if (!data.value.user_growth?.length) return [];
      const max = Math.max(
        ...data.value.user_growth.map((d: any) => d.count),
        1
      );
      return data.value.user_growth.map((d: any, i: number) => ({
        x: (i / (data.value.user_growth.length - 1 || 1)) * 580 + 10,
        y: 170 - (d.count / max) * 150,
      }));
    });

    const userGrowthPoints = computed(() =>
      userGrowthDots.value.map((p: any) => `${p.x},${p.y}`).join(" ")
    );

    const activeDots = computed(() => {
      const ratings = data.value.rating_trend || [];
      const comments = data.value.comment_trend || [];
      const merged: Record<string, number> = {};
      ratings.forEach(
        (r: any) => (merged[r.day] = (merged[r.day] || 0) + r.count)
      );
      comments.forEach(
        (c: any) => (merged[c.day] = (merged[c.day] || 0) + c.count)
      );
      const days = Object.keys(merged).sort();
      if (!days.length) return [];
      const max = Math.max(...Object.values(merged), 1);
      return days.map((day, i) => ({
        x: (i / (days.length - 1 || 1)) * 580 + 10,
        y: 170 - (merged[day] / max) * 150,
      }));
    });

    const activePoints = computed(() =>
      activeDots.value.map((p: any) => `${p.x},${p.y}`).join(" ")
    );

    onMounted(async () => {
      const token = localStorage.getItem("admin_token");
      try {
        const r = await fetch(`${API}/api/admin/analytics/`, {
          headers: { Authorization: `Token ${token}` },
        });
        if (r.ok) {
          data.value = await r.json();
          maxGenre.value = Math.max(
            1,
            ...(data.value.genre_distribution || []).map((g: any) => g.count)
          );
          const dist = data.value.rating_distribution || {};
          maxRating.value = Math.max(1, ...(Object.values(dist) as number[]));
        }
      } catch {
        /* 加载失败 */
      }
    });

    return {
      data,
      maxGenre,
      maxRating,
      barPct,
      userGrowthPoints,
      userGrowthDots,
      activePoints,
      activeDots,
    };
  },
});
</script>

<style scoped>
.analytics-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.stats-top {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.stat-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 22px;
  text-align: center;
  box-shadow: var(--panel-shadow);
}
.n {
  font-size: 2rem;
  font-weight: 900;
  color: var(--primary);
}
.l {
  margin-top: 6px;
  color: var(--text-secondary);
  font-size: 0.88rem;
}
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.chart-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 22px;
  box-shadow: var(--panel-shadow);
}
.chart-card.wide {
  grid-column: 1 / -1;
}
.chart-card h3 {
  margin: 0 0 16px;
  color: var(--text-primary);
  font-size: 1.05rem;
}
.line-chart {
  width: 100%;
  height: 180px;
}
.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.bar-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.bar-label {
  width: 48px;
  font-size: 0.82rem;
  color: var(--text-secondary);
  text-align: right;
  flex-shrink: 0;
}
.bar-bg {
  flex: 1;
  height: 10px;
  border-radius: 5px;
  background: var(--nav-hover-bg);
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 5px;
  background: var(--primary-gradient);
  transition: width 0.6s;
}
.bar-fill.star {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}
.bar-val {
  width: 36px;
  font-size: 0.82rem;
  color: var(--text-muted);
  flex-shrink: 0;
}
.community-stats {
  display: flex;
  gap: 40px;
}
.cs-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
}
.cs-num {
  font-size: 1.6rem;
  font-weight: 900;
  color: var(--primary);
}
.no-data {
  text-align: center;
  color: var(--text-muted);
  padding: 40px;
}

@media (max-width: 900px) {
  .stats-top {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
