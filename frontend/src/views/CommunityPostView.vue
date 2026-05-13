<template>
  <div class="post-page">
    <router-link :to="`/community/topic/${post.topic?.id}`" class="back-link"
      >← 返回话题</router-link
    >

    <div v-if="errorMsg" class="error-card">{{ errorMsg }}</div>

    <template v-else>
      <section class="post-hero">
        <div class="post-avatar">
          {{ getUserInitial(post.created_by?.username) }}
        </div>
        <div class="post-main">
          <h1>{{ post.title }}</h1>
          <div class="post-meta-row">
            <span>{{ post.created_by?.username }}</span>
            <span>{{ formatDate(post.created_at) }}</span>
            <span>👁 {{ post.view_count }}</span>
            <span>💬 {{ post.reply_count }}</span>
          </div>
          <img v-if="post.image" :src="post.image" class="post-image" />
          <div class="post-content" v-html="renderMarkdown(post.content)"></div>
          <div class="post-actions">
            <button
              class="like-btn"
              :class="{ liked: post.liked }"
              @click="toggleLike"
              v-if="authStore.isAuthenticated"
            >
              {{ post.liked ? "👍 已赞" : "👍 点赞" }} {{ post.like_count }}
            </button>
            <span v-else>👍 {{ post.like_count }}</span>
          </div>
        </div>
      </section>

      <section class="replies-card">
        <h2>回复 ({{ replies.length }})</h2>

        <div v-for="r in replies" :key="r.id" class="reply-item">
          <div class="reply-avatar">
            {{ getUserInitial(r.created_by?.username) }}
          </div>
          <div class="reply-body">
            <div class="reply-meta">
              <router-link
                :to="'/user/' + r.created_by?.id"
                class="reply-user"
                >{{ r.created_by?.username }}</router-link
              >
              <span class="reply-time">{{ formatDate(r.created_at) }}</span>
            </div>
            <p class="reply-text">{{ r.content }}</p>
            <button
              class="reply-toggle"
              @click="replyingTo = replyingTo === r.id ? null : r.id"
              v-if="authStore.isAuthenticated"
            >
              回复
            </button>

            <div v-if="replyingTo === r.id" class="reply-form">
              <input
                v-model="replyText"
                placeholder="写下你的回复..."
                @keyup.enter="submitReply(r.id)"
              />
              <button @click="submitReply(r.id)">发送</button>
              <button class="cancel-btn" @click="replyingTo = null">
                取消
              </button>
            </div>
          </div>
        </div>

        <div v-if="authStore.isAuthenticated" class="main-reply-form">
          <textarea
            v-model="mainReplyText"
            placeholder="写下你的回复..."
            rows="2"
          ></textarea>
          <button @click="submitReply()" :disabled="!mainReplyText.trim()">
            发表回复
          </button>
        </div>
      </section>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { marked } from "marked";
const API = "http://localhost:8000/api";
export default defineComponent({
  name: "CommunityPostView",
  setup() {
    const route = useRoute();
    const authStore = useAuthStore();
    const post = ref<any>({});
    const replies = ref<any[]>([]);
    const errorMsg = ref("");
    const replyingTo = ref<number | null>(null);
    const replyText = ref("");
    const mainReplyText = ref("");

    const fetchPost = async () => {
      const headers: any = {};
      if (authStore.token) headers.Authorization = `Token ${authStore.token}`;
      try {
        const r = await fetch(
          `${API}/community/posts/${route.params.post_id}/`,
          { headers }
        );
        if (r.ok) {
          const d = await r.json();
          post.value = d;
          replies.value = d.replies || [];
        } else errorMsg.value = "帖子不存在";
      } catch {
        errorMsg.value = "加载失败";
      }
    };

    const toggleLike = async () => {
      if (!authStore.token) return;
      try {
        const r = await fetch(`${API}/community/likes/`, {
          method: post.value.liked ? "DELETE" : "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${authStore.token}`,
          },
          body: JSON.stringify({ post_id: post.value.id }),
        });
        if (r.ok) {
          const d = await r.json();
          post.value.liked = d.liked;
          post.value.like_count = d.like_count;
        }
      } catch {
        /* 操作失败 */
      }
    };

    const submitReply = async (parentId?: number | null) => {
      const content = (parentId ? replyText.value : mainReplyText.value).trim();
      if (!content || !authStore.token) return;
      try {
        const r = await fetch(`${API}/community/replies/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${authStore.token}`,
          },
          body: JSON.stringify({
            post_id: post.value.id,
            content,
            parent_id: parentId || undefined,
          }),
        });
        if (r.ok) {
          replyText.value = "";
          mainReplyText.value = "";
          replyingTo.value = null;
          await fetchPost();
        }
      } catch {
        /* 操作失败 */
      }
    };

    const renderMarkdown = (text: string) => marked(text || "");

    const getUserInitial = (u?: string) => u?.charAt(0)?.toUpperCase() || "?";
    const formatDate = (d: string) => new Date(d).toLocaleDateString("zh-CN");

    onMounted(fetchPost);
    return {
      post,
      replies,
      errorMsg,
      replyingTo,
      replyText,
      mainReplyText,
      toggleLike,
      submitReply,
      getUserInitial,
      formatDate,
      renderMarkdown,
      authStore,
    };
  },
});
</script>

<style scoped>
.post-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.back-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
}
.error-card {
  text-align: center;
  padding: 60px;
  color: var(--text-muted);
}
.post-hero {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 28px;
  display: flex;
  gap: 16px;
  box-shadow: var(--panel-shadow);
}
.post-avatar {
  width: 48px;
  height: 48px;
  min-width: 48px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.2rem;
}
.post-main h1 {
  margin: 0 0 8px;
  color: var(--text-primary);
  font-size: 1.5rem;
}
.post-meta-row {
  display: flex;
  gap: 14px;
  color: var(--text-muted);
  font-size: 0.86rem;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.post-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: var(--radius-md);
  margin-bottom: 16px;
  object-fit: contain;
}
.post-content {
  color: var(--text-primary);
  line-height: 1.9;
  margin: 0 0 16px;
}
.post-content :deep(h1),
.post-content :deep(h2),
.post-content :deep(h3) {
  margin: 14px 0 8px;
}
.post-content :deep(h2) {
  font-size: 1.2rem;
  border-bottom: 1px solid var(--panel-border);
  padding-bottom: 6px;
}
.post-content :deep(p) {
  margin: 8px 0;
}
.post-content :deep(code) {
  background: var(--nav-hover-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
.post-content :deep(pre) {
  background: var(--nav-hover-bg);
  padding: 14px;
  border-radius: var(--radius-md);
  overflow-x: auto;
}
.post-content :deep(pre code) {
  background: none;
  padding: 0;
}
.post-content :deep(blockquote) {
  border-left: 3px solid var(--primary);
  padding-left: 12px;
  color: var(--text-secondary);
  margin: 10px 0;
}
.post-content :deep(ul),
.post-content :deep(ol) {
  padding-left: 20px;
}
.post-content :deep(a) {
  color: var(--primary);
}
.post-content :deep(img) {
  max-width: 100%;
  border-radius: var(--radius-md);
}
.post-actions {
  display: flex;
  gap: 10px;
}
.like-btn {
  border: 1px solid var(--panel-border);
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  padding: 8px 14px;
  cursor: pointer;
  font-weight: 600;
  transition: all var(--transition-fast);
}
.like-btn.liked {
  background: rgba(102, 126, 234, 0.15);
  color: var(--primary);
  border-color: var(--primary);
}
.replies-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--panel-shadow);
}
.replies-card h2 {
  margin: 0 0 18px;
  color: var(--text-primary);
}
.reply-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--panel-border);
}
.reply-avatar {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 50%;
  background: var(--nav-hover-bg);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
}
.reply-user {
  font-weight: 700;
  color: var(--text-primary);
  text-decoration: none;
}
.reply-user:hover {
  color: var(--primary);
}
.reply-time {
  color: var(--text-muted);
  font-size: 0.82rem;
  margin-left: 8px;
}
.reply-text {
  margin: 6px 0;
  color: var(--text-secondary);
  line-height: 1.7;
}
.reply-toggle {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.82rem;
  cursor: pointer;
  padding: 0;
}
.reply-form,
.main-reply-form {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.reply-form input,
.main-reply-form textarea {
  flex: 1;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
  font-family: inherit;
}
.main-reply-form textarea {
  resize: vertical;
  min-height: 60px;
}
.reply-form button,
.main-reply-form button {
  border: none;
  border-radius: var(--radius-sm);
  padding: 8px 14px;
  background: var(--primary-gradient);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}
.cancel-btn {
  background: var(--nav-hover-bg) !important;
  color: var(--text-primary) !important;
}
</style>
