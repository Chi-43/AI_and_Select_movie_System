<template>
  <div class="admin-comments-page">
    <section class="toolbar-card">
      <div class="toolbar-left">
        <h2>评论管理</h2>
        <p>查看系统评论内容，并删除不合规评论。</p>
      </div>

      <div class="toolbar-right">
        <input
          v-model="keyword"
          type="text"
          class="search-input"
          placeholder="搜索用户名 / 电影名 / 评论内容"
        />
        <button class="refresh-btn" @click="fetchComments" :disabled="loading">
          {{ loading ? "刷新中..." : "刷新列表" }}
        </button>
      </div>
    </section>

    <section class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ filteredComments.length }}</div>
        <div class="stat-label">当前显示评论</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ comments.length }}</div>
        <div class="stat-label">评论总数</div>
      </div>
    </section>

    <section class="table-card">
      <div v-if="errorMessage" class="error-box">
        {{ errorMessage }}
      </div>

      <div v-if="loading" class="loading-box">正在加载评论列表...</div>

      <div v-else-if="filteredComments.length === 0" class="empty-box">
        暂无符合条件的评论数据。
      </div>

      <div v-else class="table-wrapper">
        <table class="comment-table">
          <thead>
            <tr>
              <th>用户</th>
              <th>电影</th>
              <th>评论内容</th>
              <th>发布时间</th>
              <th>操作</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="comment in filteredComments" :key="comment.id">
              <td class="user-cell">
                <div class="avatar-badge">
                  {{ getUserInitial(comment.user?.username) }}
                </div>
                <span>{{ comment.user?.username || "未知用户" }}</span>
              </td>

              <td class="movie-cell">
                {{ comment.movie?.title || "未知电影" }}
              </td>

              <td class="content-cell">
                {{ comment.content }}
              </td>

              <td>{{ formatDate(comment.created_at) }}</td>

              <td>
                <div class="action-group">
                  <button
                    class="action-btn danger"
                    @click="deleteComment(comment)"
                  >
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";

const API_BASE_URL = "http://127.0.0.1:8000";

interface CommentUser {
  id: number;
  username: string;
}

interface CommentMovie {
  id: number;
  title: string;
}

interface CommentItem {
  id: number;
  user?: CommentUser;
  movie?: CommentMovie;
  content: string;
  created_at: string;
  updated_at: string;
}

export default defineComponent({
  name: "AdminCommentsView",
  setup() {
    const comments = ref<CommentItem[]>([]);
    const keyword = ref("");
    const loading = ref(false);
    const errorMessage = ref("");

    const getTokenHeaders = (): Record<string, string> => {
      const token = localStorage.getItem("admin_token");
      const headers: Record<string, string> = {};
      if (token) {
        headers.Authorization = `Token ${token}`;
      }
      return headers;
    };

    const fetchComments = async () => {
      loading.value = true;
      errorMessage.value = "";

      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/comments/`, {
          method: "GET",
          headers: getTokenHeaders(),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.detail || "获取评论列表失败");
        }

        comments.value = data.comments || [];
      } catch (error: any) {
        errorMessage.value = error.message || "加载评论列表失败";
      } finally {
        loading.value = false;
      }
    };

    const filteredComments = computed(() => {
      const key = keyword.value.trim().toLowerCase();
      if (!key) return comments.value;

      return comments.value.filter((comment) => {
        return (
          (comment.user?.username || "").toLowerCase().includes(key) ||
          (comment.movie?.title || "").toLowerCase().includes(key) ||
          (comment.content || "").toLowerCase().includes(key)
        );
      });
    });

    const deleteComment = async (comment: CommentItem) => {
      const ok = window.confirm(
        `确定要删除用户“${comment.user?.username || "未知"}”对电影“${
          comment.movie?.title || "未知电影"
        }”的评论吗？`
      );
      if (!ok) return;

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/admin/comments/${comment.id}/`,
          {
            method: "DELETE",
            headers: getTokenHeaders(),
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.detail || "删除评论失败");
        }

        alert("评论删除成功");
        await fetchComments();
      } catch (error: any) {
        alert(error.message || "删除评论失败");
      }
    };

    const getUserInitial = (username?: string) => {
      return username ? username.charAt(0).toUpperCase() : "?";
    };

    const formatDate = (dateStr: string) => {
      if (!dateStr) return "未知";
      return new Date(dateStr).toLocaleString("zh-CN");
    };

    onMounted(() => {
      const token = localStorage.getItem("admin_token");
      if (!token) {
        window.location.href = "/admin/login";
        return;
      }
      fetchComments();
    });

    return {
      comments,
      keyword,
      loading,
      errorMessage,
      filteredComments,
      fetchComments,
      deleteComment,
      getUserInitial,
      formatDate,
    };
  },
});
</script>

<style scoped>
.admin-comments-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.toolbar-card,
.table-card,
.stat-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
}

.toolbar-card {
  padding: 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.toolbar-left h2 {
  margin: 0;
  color: var(--text-primary);
}

.toolbar-left p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 320px;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
}

.search-input:focus {
  border-color: var(--input-focus-border);
  box-shadow: var(--input-focus-shadow);
}

.refresh-btn,
.action-btn {
  border: none;
  border-radius: var(--radius-md);
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 700;
  transition: all var(--transition-fast);
}

.refresh-btn {
  background: var(--primary-gradient);
  color: white;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  padding: 18px 20px;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--primary);
}

.stat-label {
  margin-top: 6px;
  color: var(--text-secondary);
}

.table-card {
  padding: 20px;
}

.error-box,
.loading-box,
.empty-box {
  padding: 16px;
  border-radius: var(--radius-md);
  font-weight: 600;
}

.error-box {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

.loading-box,
.empty-box {
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
}

.table-wrapper {
  overflow-x: auto;
}

.comment-table {
  width: 100%;
  border-collapse: collapse;
}

.comment-table th {
  text-align: left;
  padding: 14px 12px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--panel-border);
  font-size: 0.95rem;
}

.comment-table td {
  padding: 14px 12px;
  color: var(--text-secondary);
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  vertical-align: middle;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
  font-weight: 700;
}

.avatar-badge {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 800;
}

.movie-cell {
  max-width: 220px;
  color: var(--text-primary);
  font-weight: 700;
}

.content-cell {
  max-width: 420px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-group {
  display: flex;
  gap: 8px;
}

.action-btn.danger {
  background: rgba(239, 68, 68, 0.14);
  color: #ef4444;
}

@media (max-width: 980px) {
  .toolbar-card {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-right {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
