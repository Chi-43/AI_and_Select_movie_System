<template>
  <div class="coll-detail">
    <router-link to="/collections" class="back-link"
      >← 返回片单广场</router-link
    >

    <div v-if="err" class="error-card">{{ err }}</div>

    <template v-else>
      <section class="hero-section">
        <div
          class="hero-cover"
          :style="coll.cover ? { backgroundImage: `url(${coll.cover})` } : {}"
        >
          <span v-if="!coll.cover">🎬</span>
        </div>
        <div class="hero-info">
          <h1>{{ coll.title }}</h1>
          <p>{{ coll.description || "暂无描述" }}</p>
          <div class="hero-meta">
            <span>{{ coll.created_by?.username }}</span>
            <span>🎬 {{ coll.movie_count }} 部</span>
            <span>👍 {{ coll.like_count }}</span>
          </div>
        </div>
        <div class="hero-actions">
          <button
            class="fb-btn"
            :class="{ active: coll.user_liked }"
            @click="likeColl('like')"
          >
            👍 {{ coll.like_count }}
          </button>
          <button
            class="fb-btn"
            :class="{ active: coll.user_disliked }"
            @click="likeColl('dislike')"
          >
            👎 {{ coll.dislike_count || 0 }}
          </button>
        </div>
        <button v-if="isOwner" class="toggle-btn" @click="togglePublic">
          {{ coll.is_public ? "🌐 公开" : "🔒 私密" }}
        </button>
        <button v-if="isOwner" class="del-btn" @click="deleteCollection">
          删除片单
        </button>
      </section>

      <div class="add-movie-bar" v-if="isOwner">
        <div class="search-wrap">
          <input
            v-model="searchQ"
            placeholder="搜索电影名添加..."
            @input="searchMovies"
            class="search-input"
          />
          <div class="search-results" v-if="searchResults.length">
            <div
              v-for="m in searchResults"
              :key="m.id"
              class="search-item"
              @click="addMovie(m.id)"
            >
              <span class="sr-title">{{ m.title }}</span>
              <span class="sr-meta"
                >⭐ {{ m.rating }} · {{ m.year }} · {{ m.genre }}</span
              >
            </div>
          </div>
        </div>
      </div>

      <div class="movie-list">
        <div
          v-for="item in movies"
          :key="item.id"
          class="movie-row"
          @click="goToMovie(item.movie)"
        >
          <span class="mr-index">{{ item.order || "·" }}</span>
          <div class="mr-info">
            <div class="mr-title">{{ item.movie.title }}</div>
            <div class="mr-meta">
              ⭐ {{ item.movie.rating }} · {{ item.movie.year }} ·
              {{ item.movie.genre }}
            </div>
            <div class="mr-note" v-if="item.note">💬 {{ item.note }}</div>
          </div>
          <button
            v-if="isOwner"
            class="remove-btn"
            @click.stop="removeMovie(item.movie.id)"
          >
            ×
          </button>
        </div>
        <div v-if="movies.length === 0" class="empty-card">片单中暂无电影</div>
      </div>

      <div class="comments-section">
        <h3>讨论 ({{ comments.length }})</h3>
        <div v-if="authStore.isAuthenticated" class="comment-form">
          <textarea
            v-model="commentText"
            placeholder="对这个片单说点什么..."
            rows="2"
          ></textarea>
          <button @click="postComment()" :disabled="!commentText.trim()">
            发表
          </button>
        </div>

        <!-- 一级评论 -->
        <div v-for="c in comments" :key="c.id" class="comment-item">
          <div class="cmt-user">
            <router-link :to="'/user/' + c.user?.id">{{
              c.user?.username
            }}</router-link>
            <span>{{ formatDate(c.created_at) }}</span>
          </div>
          <p>{{ c.content }}</p>
          <div class="cmt-actions">
            <button
              :class="{ active: c.user_liked }"
              @click="commentLike(c.id, 'like')"
            >
              👍 {{ c.like_count }}
            </button>
            <button
              :class="{ active: c.user_disliked }"
              @click="commentLike(c.id, 'dislike')"
            >
              👎 {{ c.dislike_count }}
            </button>
            <button
              v-if="authStore.isAuthenticated"
              class="reply-btn"
              @click="replyingTo = replyingTo === c.id ? null : c.id"
            >
              💬 回复
            </button>
          </div>

          <!-- 回复框 -->
          <div v-if="replyingTo === c.id" class="reply-form">
            <textarea
              v-model="replyText"
              placeholder="写下你的回复..."
              rows="1"
            ></textarea>
            <button @click="postComment(c.id)" :disabled="!replyText.trim()">
              发送
            </button>
            <button
              class="cancel-btn"
              @click="
                replyingTo = null;
                replyText = '';
              "
            >
              取消
            </button>
          </div>

          <!-- 二级回复 -->
          <div v-if="c.replies?.length" class="replies-list">
            <div v-for="r in c.replies" :key="r.id" class="reply-item">
              <div class="cmt-user sm">
                <router-link :to="'/user/' + r.user?.id">{{
                  r.user?.username
                }}</router-link>
                <span>{{ formatDate(r.created_at) }}</span>
              </div>
              <p>{{ r.content }}</p>
              <div class="cmt-actions sm">
                <button
                  :class="{ active: r.user_liked }"
                  @click="commentLike(r.id, 'like')"
                >
                  👍 {{ r.like_count }}
                </button>
                <button
                  :class="{ active: r.user_disliked }"
                  @click="commentLike(r.id, 'dislike')"
                >
                  👎 {{ r.dislike_count }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
const API = "http://localhost:8000/api";
export default defineComponent({
  name: "CollectionDetailView",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();
    const coll = ref<any>({});
    const movies = ref<any[]>([]);
    const err = ref("");
    const searchQ = ref("");
    const searchResults = ref<any[]>([]);
    let searchTimer: any = null;
    const commentText = ref("");
    const comments = ref<any[]>([]);

    const fetchComments = async () => {
      const r = await fetch(
        `${API}/collections/comments/?collection_id=${route.params.id}`
      );
      if (r.ok) {
        const d = await r.json();
        comments.value = d.comments || [];
      }
    };

    const postComment = async (parentId?: number | null) => {
      const content = (parentId ? replyText.value : commentText.value).trim();
      if (!content || !authStore.token) return;
      const r = await fetch(`${API}/collections/comments/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${authStore.token}`,
        },
        body: JSON.stringify({
          collection_id: route.params.id,
          content,
          parent_id: parentId || undefined,
        }),
      });
      if (r.ok) {
        commentText.value = "";
        replyText.value = "";
        replyingTo.value = null;
        await fetchComments();
      }
    };

    const commentLike = async (commentId: number, type: string) => {
      if (!authStore.token) return alert("请先登录");
      await fetch(`${API}/collections/comments/likes/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${authStore.token}`,
        },
        body: JSON.stringify({ comment_id: commentId, feedback_type: type }),
      });
      await fetchComments();
    };

    const replyingTo = ref<number | null>(null);
    const replyText = ref("");

    const likeColl = async (type: string) => {
      if (!authStore.token) return alert("请先登录");
      if (
        (type === "like" && coll.value.user_liked) ||
        (type === "dislike" && coll.value.user_disliked)
      ) {
        await fetch(
          `${API}/collections/likes/?collection_id=${route.params.id}`,
          {
            method: "DELETE",
            headers: { Authorization: `Token ${authStore.token}` },
          }
        );
      } else {
        await fetch(`${API}/collections/likes/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${authStore.token}`,
          },
          body: JSON.stringify({
            collection_id: route.params.id,
            feedback_type: type,
          }),
        });
      }
      await fetchDetail();
      await fetchComments();
    };

    const searchMovies = () => {
      if (searchTimer) clearTimeout(searchTimer);
      const q = searchQ.value.trim();
      if (!q) {
        searchResults.value = [];
        return;
      }
      searchTimer = setTimeout(async () => {
        const r = await fetch(`${API}/search/?q=${encodeURIComponent(q)}`);
        if (r.ok) {
          const d = await r.json();
          searchResults.value = d.results || [];
        }
      }, 300);
    };

    const addMovie = async (movieId: number) => {
      const r = await fetch(`${API}/collections/movies/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${authStore.token}`,
        },
        body: JSON.stringify({
          collection_id: route.params.id,
          movie_id: movieId,
        }),
      });
      if (r.ok) {
        searchQ.value = "";
        searchResults.value = [];
        await fetchDetail();
      } else {
        const d = await r.json().catch(() => ({}));
        alert((d as any).error || "添加失败");
      }
    };

    const togglePublic = async () => {
      const r = await fetch(`${API}/collections/${route.params.id}/`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${authStore.token}`,
        },
        body: JSON.stringify({ is_public: !coll.value.is_public }),
      });
      if (r.ok) await fetchDetail();
    };

    const isOwner = computed(
      () => authStore.user?.id === coll.value.created_by?.id
    );

    const fetchDetail = async () => {
      try {
        const headers: any = {};
        if (authStore.token) headers.Authorization = `Token ${authStore.token}`;
        const r = await fetch(`${API}/collections/${route.params.id}/`, {
          headers,
        });
        if (r.ok) {
          const d = await r.json();
          coll.value = d;
          movies.value = d.movies || [];
          comments.value = d.comments || [];
        } else {
          const ed = await r.json().catch(() => ({}));
          err.value = (ed as any).error || `请求失败 (${r.status})`;
        }
      } catch {
        err.value = "加载失败";
      }
    };

    const removeMovie = async (movieId: number) => {
      await fetch(
        `${API}/collections/movies/?collection_id=${route.params.id}&movie_id=${movieId}`,
        {
          method: "DELETE",
          headers: { Authorization: `Token ${authStore.token}` },
        }
      );
      await fetchDetail();
    };

    const deleteCollection = async () => {
      if (!confirm("确定删除这个片单？")) return;
      await fetch(`${API}/collections/${route.params.id}/`, {
        method: "DELETE",
        headers: { Authorization: `Token ${authStore.token}` },
      });
      router.push("/collections");
    };

    const goToMovie = (m: any) => {
      const detail = {
        id: m.id,
        movie_id: m.id,
        电影名字: m.title,
        电影链接: m.douban_url || "",
        评分: String(m.rating || ""),
        评分人数: "",
        导演: m.director || "",
        主演: m.actors || "",
        年份: String(m.year || ""),
        国家: m.country || "",
        类型: m.genre || "",
        一句话评价: m.quote || "",
      };
      sessionStorage.setItem("current_movie_detail", JSON.stringify(detail));
      router.push({
        path: "/movie-detail",
        query: { movie_id: m.id, movie_title: m.title },
      });
    };

    onMounted(fetchDetail);
    return {
      coll,
      movies,
      err,
      authStore,
      searchQ,
      searchResults,
      searchMovies,
      addMovie,
      isOwner,
      togglePublic,
      commentText,
      comments,
      postComment,
      commentLike,
      replyingTo,
      replyText,
      likeColl,
      formatDate: (d: string) => new Date(d).toLocaleDateString("zh-CN"),
      removeMovie,
      deleteCollection,
      goToMovie,
    };
  },
});
</script>

<style scoped>
.coll-detail {
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
.hero-section {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  gap: 20px;
  align-items: center;
  box-shadow: var(--panel-shadow);
}
.hero-cover {
  width: 120px;
  height: 120px;
  min-width: 120px;
  border-radius: var(--radius-md);
  background-size: cover;
  background-position: center;
  background-color: var(--nav-hover-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}
.hero-info h1 {
  margin: 0 0 8px;
  color: var(--text-primary);
  font-size: 1.4rem;
}
.hero-info p {
  margin: 0 0 8px;
  color: var(--text-secondary);
  line-height: 1.6;
}
.hero-meta {
  display: flex;
  gap: 12px;
  color: var(--text-muted);
  font-size: 0.86rem;
}
.hero-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}
.fb-btn {
  border: 1px solid var(--panel-border);
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  padding: 8px 14px;
  cursor: pointer;
  font-weight: 600;
  transition: all var(--transition-fast);
}
.fb-btn.active {
  background: rgba(102, 126, 234, 0.15);
  color: var(--primary);
  border-color: var(--primary);
}
.toggle-btn {
  border: 1px solid var(--panel-border);
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  padding: 8px 14px;
  cursor: pointer;
  font-weight: 600;
  transition: all var(--transition-fast);
}
.toggle-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}
.del-btn {
  border: none;
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: 600;
}
.movie-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.movie-row {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 14px 16px;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--panel-shadow);
}
.movie-row:hover {
  transform: translateY(-1px);
}
.mr-index {
  width: 28px;
  text-align: center;
  color: var(--text-muted);
  font-weight: 700;
}
.mr-title {
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}
.mr-meta {
  font-size: 0.84rem;
  color: var(--text-secondary);
}
.mr-note {
  margin-top: 6px;
  font-size: 0.86rem;
  color: var(--text-muted);
  font-style: italic;
}
.remove-btn {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}
.remove-btn:hover {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}
.add-movie-bar {
  margin-bottom: 4px;
}
.search-wrap {
  position: relative;
}
.search-input {
  width: 100%;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
}
.search-results {
  position: absolute;
  top: 44px;
  left: 0;
  right: 0;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  z-index: 10;
  max-height: 260px;
  overflow-y: auto;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}
.search-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  cursor: pointer;
  border-bottom: 1px solid var(--panel-border);
  transition: background var(--transition-fast);
}
.search-item:hover {
  background: var(--nav-hover-bg);
}
.sr-title {
  font-weight: 600;
  color: var(--text-primary);
}
.sr-meta {
  font-size: 0.84rem;
  color: var(--text-secondary);
}

.comments-section {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 22px;
  box-shadow: var(--panel-shadow);
}
.comments-section h3 {
  margin: 0 0 14px;
  color: var(--text-primary);
}
.comment-form {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.comment-form textarea {
  flex: 1;
  padding: 10px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
  font-family: inherit;
  resize: vertical;
  min-height: 50px;
}
.comment-form button {
  border: none;
  border-radius: var(--radius-sm);
  padding: 10px 16px;
  background: var(--primary-gradient);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}
.comment-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--panel-border);
}
.comment-item:last-child {
  border-bottom: none;
}
.cmt-user {
  display: flex;
  gap: 10px;
  margin-bottom: 6px;
  font-size: 0.86rem;
}
.cmt-user a {
  font-weight: 700;
  color: var(--text-primary);
  text-decoration: none;
}
.cmt-user a:hover {
  color: var(--primary);
}
.cmt-user span {
  color: var(--text-muted);
}
.comment-item p {
  margin: 6px 0;
  color: var(--text-secondary);
  line-height: 1.6;
}
.cmt-actions {
  display: flex;
  gap: 8px;
  margin-top: 6px;
}
.cmt-actions button {
  border: 1px solid var(--panel-border);
  background: var(--nav-hover-bg);
  color: var(--text-muted);
  border-radius: 12px;
  padding: 4px 10px;
  font-size: 0.82rem;
  cursor: pointer;
  font-weight: 600;
  transition: all var(--transition-fast);
}
.cmt-actions button.active {
  background: rgba(102, 126, 234, 0.15);
  color: var(--primary);
  border-color: var(--primary);
}
.cmt-actions button:hover {
  border-color: var(--primary);
}
.cmt-actions.sm button {
  font-size: 0.78rem;
  padding: 3px 8px;
}
.reply-btn {
  border: none !important;
  background: transparent !important;
  color: var(--text-muted) !important;
  font-size: 0.82rem;
}
.reply-btn:hover {
  color: var(--primary) !important;
}
.reply-form {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  margin-left: 20px;
}
.reply-form textarea {
  flex: 1;
  padding: 8px 10px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
  font-family: inherit;
  font-size: 0.9rem;
  resize: vertical;
  min-height: 36px;
}
.reply-form button {
  border: none;
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.85rem;
}
.reply-form button:first-of-type {
  background: var(--primary-gradient);
  color: #fff;
}
.reply-form .cancel-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}
.replies-list {
  margin-top: 10px;
  margin-left: 24px;
  padding-left: 12px;
  border-left: 2px solid var(--panel-border);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.reply-item {
  padding: 8px 12px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
}
.reply-item p {
  margin: 4px 0;
  font-size: 0.9rem;
}
.cmt-user.sm {
  font-size: 0.82rem;
}

.empty-card {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}
</style>
