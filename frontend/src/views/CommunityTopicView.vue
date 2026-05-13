<template>
  <div class="topic-page">
    <router-link to="/community" class="back-link">← 返回社区</router-link>

    <section class="hero-section">
      <h1>{{ topic.icon }} {{ topic.name }}</h1>
      <p>{{ topic.description }}</p>
      <button
        class="new-post-btn"
        @click="showForm = true"
        v-if="authStore.isAuthenticated"
      >
        + 发新帖
      </button>
    </section>

    <div v-if="showForm" class="post-form-card">
      <input v-model="form.title" placeholder="帖子标题" class="form-input" />
      <textarea
        v-model="form.content"
        placeholder="写下你的想法..."
        class="form-textarea"
        rows="5"
      ></textarea>
      <div class="form-actions">
        <button class="cancel-btn" @click="showForm = false">取消</button>
        <button
          class="submit-btn"
          @click="createPost"
          :disabled="submitting || !form.title.trim() || !form.content.trim()"
        >
          {{ submitting ? "发布中..." : "发布" }}
        </button>
      </div>
    </div>

    <div class="post-list">
      <div
        v-for="p in posts"
        :key="p.id"
        class="post-card"
        @click="$router.push(`/community/post/${p.id}`)"
      >
        <div class="post-avatar">
          {{ getUserInitial(p.created_by?.username) }}
        </div>
        <div class="post-body">
          <h3 class="post-title">{{ p.title }}</h3>
          <p class="post-excerpt">{{ p.content }}</p>
          <div class="post-meta">
            <span>{{ p.created_by?.username }}</span>
            <span>{{ formatDate(p.created_at) }}</span>
            <span>👁 {{ p.view_count }}</span>
            <span>💬 {{ p.reply_count }}</span>
            <span>👍 {{ p.like_count }}</span>
          </div>
        </div>
      </div>
      <div v-if="posts.length === 0 && !loading" class="empty-card">
        暂无帖子，快来发第一帖
      </div>
    </div>

    <div class="pagination-bar" v-if="nextUrl || prevUrl">
      <button :disabled="!prevUrl" @click="fetchPosts(prevUrl)">上一页</button>
      <span>共 {{ totalCount }} 条</span>
      <button :disabled="!nextUrl" @click="fetchPosts(nextUrl)">下一页</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
const API = "http://localhost:8000/api";
export default defineComponent({
  name: "CommunityTopicView",
  setup() {
    const route = useRoute();
    const authStore = useAuthStore();
    const topic = ref<any>({});
    const posts = ref<any[]>([]);
    const loading = ref(false);
    const showForm = ref(false);
    const submitting = ref(false);
    const totalCount = ref(0);
    const nextUrl = ref<string | null>(null);
    const prevUrl = ref<string | null>(null);
    const form = ref({ title: "", content: "" });

    const fetchPosts = async (url?: string) => {
      loading.value = true;
      try {
        const r = await fetch(
          url || `${API}/community/posts/?topic_id=${route.params.topic_id}`
        );
        if (r.ok) {
          const d = await r.json();
          posts.value = d.results || [];
          totalCount.value = d.count || 0;
          nextUrl.value = d.next;
          prevUrl.value = d.previous;
        }
      } catch {
        /* 加载失败 */
      } finally {
        loading.value = false;
      }
    };

    const createPost = async () => {
      submitting.value = true;
      try {
        const r = await fetch(`${API}/community/posts/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${authStore.token}`,
          },
          body: JSON.stringify({
            title: form.value.title,
            content: form.value.content,
            topic_id: route.params.topic_id,
          }),
        });
        if (r.ok) {
          showForm.value = false;
          form.value = { title: "", content: "" };
          await fetchPosts();
        } else alert("发帖失败");
      } catch {
        /* 发帖失败 */
      } finally {
        submitting.value = false;
      }
    };

    const getUserInitial = (u?: string) => u?.charAt(0)?.toUpperCase() || "?";
    const formatDate = (d: string) => new Date(d).toLocaleDateString("zh-CN");

    onMounted(async () => {
      try {
        const r = await fetch(`${API}/community/topics/`);
        if (r.ok) {
          const d = await r.json();
          topic.value =
            d.topics?.find((t: any) => t.id == route.params.topic_id) || {};
        }
      } catch {
        /* 加载话题失败 */
      }
      await fetchPosts();
    });
    return {
      topic,
      posts,
      loading,
      showForm,
      submitting,
      form,
      fetchPosts,
      createPost,
      getUserInitial,
      formatDate,
      totalCount,
      nextUrl,
      prevUrl,
      authStore,
    };
  },
});
</script>

<style scoped>
.topic-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.back-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
}
.hero-section {
  background: var(--bg-hero);
  border-radius: var(--radius-lg);
  padding: 28px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.hero-section h1 {
  margin: 0;
  font-size: 1.6rem;
  flex: 1;
}
.hero-section p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
}
.new-post-btn {
  border: none;
  padding: 10px 18px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}
.post-form-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.form-input,
.form-textarea {
  width: 100%;
  padding: 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
  font-family: inherit;
}
.form-textarea {
  resize: vertical;
  min-height: 100px;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.submit-btn,
.cancel-btn {
  border: none;
  border-radius: var(--radius-sm);
  padding: 10px 18px;
  font-weight: 700;
  cursor: pointer;
}
.submit-btn {
  background: var(--primary-gradient);
  color: #fff;
}
.cancel-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}
.post-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.post-card {
  display: flex;
  gap: 14px;
  padding: 20px;
  border-radius: var(--radius-lg);
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--panel-shadow);
}
.post-card:hover {
  transform: translateY(-2px);
}
.post-avatar {
  width: 40px;
  height: 40px;
  min-width: 40px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}
.post-title {
  margin: 0 0 6px;
  color: var(--text-primary);
  font-size: 1.05rem;
}
.post-excerpt {
  margin: 0 0 8px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.post-meta {
  display: flex;
  gap: 12px;
  font-size: 0.82rem;
  color: var(--text-muted);
  flex-wrap: wrap;
}
.pagination-bar {
  display: flex;
  justify-content: center;
  gap: 16px;
  align-items: center;
  padding: 16px;
}
.pagination-bar button {
  border: 1px solid var(--panel-border);
  background: var(--panel-bg);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 600;
}
.pagination-bar button:disabled {
  opacity: 0.4;
  cursor: default;
}
.empty-card {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}
</style>
