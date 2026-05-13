<template>
  <div class="community-page">
    <section class="hero-section">
      <h1>💬 社区讨论区</h1>
      <p>和影迷一起聊聊电影、分享观点、发现好片</p>
    </section>

    <section class="topic-grid">
      <div
        v-for="t in topics"
        :key="t.id"
        class="topic-card"
        @click="$router.push(`/community/topic/${t.id}`)"
      >
        <span class="topic-icon">{{ t.icon }}</span>
        <div class="topic-info">
          <h3>{{ t.name }}</h3>
          <p>{{ t.description }}</p>
          <span class="topic-count">{{ t.post_count }} 个帖子</span>
        </div>
      </div>
      <div v-if="topics.length === 0" class="empty-card">暂无讨论话题</div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
const API = "http://localhost:8000/api";
export default defineComponent({
  name: "CommunityView",
  setup() {
    const topics = ref<any[]>([]);
    onMounted(async () => {
      try {
        const r = await fetch(`${API}/community/topics/`);
        if (r.ok) {
          const d = await r.json();
          topics.value = d.topics || [];
        }
      } catch {
        /* 加载失败静默忽略 */
      }
    });
    return { topics };
  },
});
</script>

<style scoped>
.community-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.hero-section {
  background: var(--bg-hero);
  border-radius: var(--radius-lg);
  padding: 32px;
  color: #fff;
}
.hero-section h1 {
  margin: 0 0 8px;
  font-size: 1.8rem;
}
.hero-section p {
  margin: 0;
  color: rgba(255, 255, 255, 0.85);
}
.topic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.topic-card {
  display: flex;
  gap: 16px;
  padding: 22px;
  border-radius: var(--radius-lg);
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  box-shadow: var(--panel-shadow);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.topic-card:hover {
  transform: translateY(-2px);
  border-color: var(--primary);
}
.topic-icon {
  font-size: 2.2rem;
}
.topic-info h3 {
  margin: 0 0 6px;
  color: var(--text-primary);
  font-size: 1.1rem;
}
.topic-info p {
  margin: 0 0 8px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
}
.topic-count {
  font-size: 0.82rem;
  color: var(--text-muted);
}
.empty-card {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}
</style>
