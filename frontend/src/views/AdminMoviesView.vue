<template>
  <div class="admin-movies-page">
    <section class="toolbar-card">
      <div class="toolbar-left">
        <h2>电影管理</h2>
        <p>查看、新增、修改和删除系统中的电影信息。</p>
      </div>

      <div class="toolbar-right">
        <input
          v-model="keyword"
          type="text"
          class="search-input"
          placeholder="搜索电影名 / 类型 / 国家 / 导演"
        />
        <button class="primary-btn" @click="openCreateModal">新增电影</button>
        <button class="refresh-btn" @click="fetchMovies" :disabled="loading">
          {{ loading ? "刷新中..." : "刷新列表" }}
        </button>
      </div>
    </section>

    <section class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ filteredMovies.length }}</div>
        <div class="stat-label">当前显示电影</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ movies.length }}</div>
        <div class="stat-label">系统电影总数</div>
      </div>
    </section>

    <section class="table-card">
      <div v-if="errorMessage" class="error-box">
        {{ errorMessage }}
      </div>

      <div v-if="loading" class="loading-box">正在加载电影列表...</div>

      <div v-else-if="filteredMovies.length === 0" class="empty-box">
        暂无符合条件的电影数据。
      </div>

      <div v-else class="table-wrapper">
        <table class="movie-table">
          <thead>
            <tr>
              <th>电影名称</th>
              <th>类型</th>
              <th>年份</th>
              <th>国家/地区</th>
              <th>评分</th>
              <th>导演</th>
              <th>操作</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="movie in filteredMovies" :key="movie.id">
              <td class="title-cell">
                <div class="movie-badge">🎬</div>
                <div class="title-content">
                  <div class="movie-title">{{ movie.title }}</div>
                  <div class="movie-sub" v-if="movie.douban_url">
                    豆瓣链接已配置
                  </div>
                </div>
              </td>
              <td>{{ movie.genre || "未填写" }}</td>
              <td>{{ movie.year || "未知" }}</td>
              <td>{{ movie.country || "未填写" }}</td>
              <td>{{ movie.rating || "暂无" }}</td>
              <td class="director-cell">{{ movie.director || "未填写" }}</td>
              <td>
                <div class="action-group">
                  <button class="action-btn edit" @click="openEditModal(movie)">
                    编辑
                  </button>
                  <button class="action-btn delete" @click="deleteMovie(movie)">
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 新增 / 编辑弹窗 -->
    <div v-if="showModal" class="modal-mask" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-header">
          <h3>{{ isEditMode ? "编辑电影信息" : "新增电影" }}</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>

        <div class="form-grid">
          <div class="form-item">
            <label>电影名称</label>
            <input v-model="form.title" class="form-input" />
          </div>

          <div class="form-item">
            <label>类型</label>
            <input
              v-model="form.genre"
              class="form-input"
              placeholder="如：剧情 / 科幻"
            />
          </div>

          <div class="form-item">
            <label>年份</label>
            <input v-model="form.year" type="number" class="form-input" />
          </div>

          <div class="form-item">
            <label>国家/地区</label>
            <input v-model="form.country" class="form-input" />
          </div>

          <div class="form-item">
            <label>豆瓣评分</label>
            <input
              v-model="form.rating"
              type="number"
              step="0.1"
              class="form-input"
            />
          </div>

          <div class="form-item">
            <label>评分人数</label>
            <input
              v-model="form.rating_count"
              type="number"
              class="form-input"
            />
          </div>

          <div class="form-item full">
            <label>豆瓣链接</label>
            <input v-model="form.douban_url" class="form-input" />
          </div>

          <div class="form-item">
            <label>导演</label>
            <input v-model="form.director" class="form-input" />
          </div>

          <div class="form-item">
            <label>主演</label>
            <input v-model="form.actors" class="form-input" />
          </div>

          <div class="form-item full">
            <label>一句话评价</label>
            <input v-model="form.quote" class="form-input" />
          </div>

          <div class="form-item full">
            <label>简介</label>
            <textarea
              v-model="form.description"
              class="form-textarea"
            ></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button class="cancel-btn" @click="closeModal">取消</button>
          <button class="save-btn" @click="submitMovie" :disabled="submitting">
            {{
              submitting ? "保存中..." : isEditMode ? "保存修改" : "新增电影"
            }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, reactive, onMounted } from "vue";

const API_BASE_URL = "http://127.0.0.1:8000";

interface MovieItem {
  id: number;
  title: string;
  genre: string;
  year: number | null;
  description: string;
  country: string;
  rating: number | null;
  rating_count: number | null;
  douban_url: string | null;
  quote: string;
  director: string;
  actors: string;
  created_at?: string;
}

export default defineComponent({
  name: "AdminMoviesView",
  setup() {
    const movies = ref<MovieItem[]>([]);
    const keyword = ref("");
    const loading = ref(false);
    const submitting = ref(false);
    const errorMessage = ref("");

    const showModal = ref(false);
    const isEditMode = ref(false);
    const currentMovieId = ref<number | null>(null);

    const form = reactive({
      title: "",
      genre: "",
      year: "",
      description: "",
      country: "",
      rating: "",
      rating_count: "",
      douban_url: "",
      quote: "",
      director: "",
      actors: "",
    });

    const getTokenHeaders = (): Record<string, string> => {
      const token = localStorage.getItem("admin_token");
      const headers: Record<string, string> = {};
      if (token) {
        headers.Authorization = `Token ${token}`;
      }
      return headers;
    };

    const getJsonHeaders = (): Record<string, string> => {
      const token = localStorage.getItem("admin_token");
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (token) {
        headers.Authorization = `Token ${token}`;
      }
      return headers;
    };

    const fetchMovies = async () => {
      loading.value = true;
      errorMessage.value = "";

      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/movies/`, {
          method: "GET",
          headers: getTokenHeaders(),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.detail || "获取电影列表失败");
        }

        movies.value = data.movies || [];
      } catch (error: any) {
        errorMessage.value = error.message || "加载电影列表失败";
      } finally {
        loading.value = false;
      }
    };

    const filteredMovies = computed(() => {
      const key = keyword.value.trim().toLowerCase();
      if (!key) return movies.value;

      return movies.value.filter((movie) => {
        return (
          (movie.title || "").toLowerCase().includes(key) ||
          (movie.genre || "").toLowerCase().includes(key) ||
          (movie.country || "").toLowerCase().includes(key) ||
          (movie.director || "").toLowerCase().includes(key)
        );
      });
    });

    const resetForm = () => {
      form.title = "";
      form.genre = "";
      form.year = "";
      form.description = "";
      form.country = "";
      form.rating = "";
      form.rating_count = "";
      form.douban_url = "";
      form.quote = "";
      form.director = "";
      form.actors = "";
    };

    const openCreateModal = () => {
      resetForm();
      isEditMode.value = false;
      currentMovieId.value = null;
      showModal.value = true;
    };

    const openEditModal = (movie: MovieItem) => {
      isEditMode.value = true;
      currentMovieId.value = movie.id;

      form.title = movie.title || "";
      form.genre = movie.genre || "";
      form.year = movie.year ? String(movie.year) : "";
      form.description = movie.description || "";
      form.country = movie.country || "";
      form.rating =
        movie.rating !== null && movie.rating !== undefined
          ? String(movie.rating)
          : "";
      form.rating_count =
        movie.rating_count !== null && movie.rating_count !== undefined
          ? String(movie.rating_count)
          : "";
      form.douban_url = movie.douban_url || "";
      form.quote = movie.quote || "";
      form.director = movie.director || "";
      form.actors = movie.actors || "";

      showModal.value = true;
    };

    const closeModal = () => {
      showModal.value = false;
      isEditMode.value = false;
      currentMovieId.value = null;
      resetForm();
    };

    const submitMovie = async () => {
      if (!form.title.trim()) {
        alert("电影名称不能为空");
        return;
      }

      submitting.value = true;

      try {
        const payload = {
          title: form.title.trim(),
          genre: form.genre.trim(),
          year: form.year ? Number(form.year) : null,
          description: form.description.trim(),
          country: form.country.trim(),
          rating: form.rating ? Number(form.rating) : null,
          rating_count: form.rating_count ? Number(form.rating_count) : null,
          douban_url: form.douban_url.trim() || null,
          quote: form.quote.trim(),
          director: form.director.trim(),
          actors: form.actors.trim(),
        };

        const url = isEditMode.value
          ? `${API_BASE_URL}/api/admin/movies/${currentMovieId.value}/`
          : `${API_BASE_URL}/api/admin/movies/`;

        const method = isEditMode.value ? "PUT" : "POST";

        const response = await fetch(url, {
          method,
          headers: getJsonHeaders(),
          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.detail || "保存电影失败");
        }

        alert(isEditMode.value ? "电影信息更新成功" : "电影新增成功");
        closeModal();
        await fetchMovies();
      } catch (error: any) {
        alert(error.message || "保存电影失败");
      } finally {
        submitting.value = false;
      }
    };

    const deleteMovie = async (movie: MovieItem) => {
      const ok = window.confirm(`确定要删除电影“${movie.title}”吗？`);
      if (!ok) return;

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/admin/movies/${movie.id}/`,
          {
            method: "DELETE",
            headers: getTokenHeaders(),
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.detail || "删除电影失败");
        }

        alert("电影删除成功");
        await fetchMovies();
      } catch (error: any) {
        alert(error.message || "删除电影失败");
      }
    };

    onMounted(() => {
      const token = localStorage.getItem("admin_token");
      if (!token) {
        window.location.href = "/admin/login";
        return;
      }
      fetchMovies();
    });

    return {
      movies,
      keyword,
      loading,
      submitting,
      errorMessage,
      filteredMovies,
      showModal,
      isEditMode,
      form,
      fetchMovies,
      openCreateModal,
      openEditModal,
      closeModal,
      submitMovie,
      deleteMovie,
    };
  },
});
</script>

<style scoped>
.admin-movies-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.toolbar-card,
.table-card,
.stat-card,
.modal-card {
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

.primary-btn,
.refresh-btn,
.save-btn,
.cancel-btn,
.action-btn {
  border: none;
  border-radius: var(--radius-md);
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 700;
  transition: all var(--transition-fast);
}

.primary-btn,
.refresh-btn,
.save-btn {
  background: var(--primary-gradient);
  color: white;
}

.cancel-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
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

.movie-table {
  width: 100%;
  border-collapse: collapse;
}

.movie-table th {
  text-align: left;
  padding: 14px 12px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--panel-border);
  font-size: 0.95rem;
}

.movie-table td {
  padding: 14px 12px;
  color: var(--text-secondary);
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  vertical-align: middle;
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.movie-badge {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
}

.title-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.movie-title {
  color: var(--text-primary);
  font-weight: 800;
}

.movie-sub {
  font-size: 0.84rem;
  color: var(--text-muted);
}

.director-cell {
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-group {
  display: flex;
  gap: 8px;
}

.action-btn.edit {
  background: rgba(99, 102, 241, 0.14);
  color: var(--primary);
}

.action-btn.delete {
  background: rgba(239, 68, 68, 0.14);
  color: #ef4444;
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.58);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 20px;
}

.modal-card {
  width: 100%;
  max-width: 680px;
  max-height: 85vh;
  overflow-y: auto;
  padding: 22px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 1.5rem;
  cursor: pointer;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item.full {
  grid-column: 1 / -1;
}

.form-item label {
  color: var(--text-primary);
  font-weight: 700;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
}

.form-input:focus,
.form-textarea:focus {
  border-color: var(--input-focus-border);
  box-shadow: var(--input-focus-shadow);
}

.form-textarea {
  min-height: 90px;
  resize: vertical;
}

.modal-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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

  .stats-row,
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
