<template>
  <div class="dashboard-home">
    <section class="hero-card">
      <div class="hero-left">
        <div class="hero-badge">后台概览</div>
        <h2>欢迎进入管理员控制台</h2>
        <p>
          你可以在这里管理用户信息、电影信息、评论内容，并维护系统的基础数据。
        </p>
      </div>
      <div class="hero-right">
        <div class="stat-card">
          <div class="stat-value">用户</div>
          <div class="stat-label">用户管理</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">电影</div>
          <div class="stat-label">电影管理</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">评论</div>
          <div class="stat-label">评论管理</div>
        </div>
      </div>
    </section>

    <section class="quick-grid">
      <router-link to="/admin/users" class="quick-card">
        <div class="quick-icon">👤</div>
        <h3>用户管理</h3>
        <p>查看用户列表，修改或删除用户信息。</p>
      </router-link>

      <router-link to="/admin/movies" class="quick-card">
        <div class="quick-icon">🎞️</div>
        <h3>电影管理</h3>
        <p>新增、修改或删除系统中的电影数据。</p>
      </router-link>

      <router-link to="/admin/comments" class="quick-card">
        <div class="quick-icon">💬</div>
        <h3>评论管理</h3>
        <p>查看评论内容并删除不合规评论。</p>
      </router-link>

      <router-link to="/admin/profile" class="quick-card">
        <div class="quick-icon">⚙️</div>
        <h3>个人信息</h3>
        <p>查看并修改管理员个人资料。</p>
      </router-link>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "AdminDashboardHome",
});
</script>

<style scoped>
.dashboard-home {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-card {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 20px;
  padding: 26px;
  border-radius: var(--radius-lg);
  background: var(--bg-hero);
  color: white;
  box-shadow: var(--panel-shadow);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.14);
  margin-bottom: 12px;
  font-weight: 700;
}

.hero-left h2 {
  margin: 0;
  font-size: 2rem;
}

.hero-left p {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.8;
}

.hero-right {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.stat-card {
  padding: 18px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.12);
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 900;
}

.stat-label {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.88);
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.quick-card {
  display: block;
  text-decoration: none;
  padding: 22px;
  border-radius: var(--radius-lg);
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  box-shadow: var(--panel-shadow);
  color: inherit;
  transition: all var(--transition-fast);
}

.quick-card:hover {
  transform: translateY(-2px);
  border-color: rgba(99, 102, 241, 0.3);
}

.quick-icon {
  font-size: 2rem;
  margin-bottom: 12px;
}

.quick-card h3 {
  margin: 0;
  color: var(--text-primary);
}

.quick-card p {
  margin: 8px 0 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

@media (max-width: 960px) {
  .hero-card,
  .quick-grid {
    grid-template-columns: 1fr;
  }
}
</style>
