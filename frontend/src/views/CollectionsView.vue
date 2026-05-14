<template>
  <div class="collections-page">
    <section class="hero-section">
      <div>
        <h1>📚 电影片单</h1>
        <p>发现精选片单，或创建你自己的电影合集</p>
      </div>
      <button
        class="create-btn"
        @click="showForm = true"
        v-if="authStore.isAuthenticated"
      >
        + 创建片单
      </button>
    </section>

    <div v-if="showForm" class="form-card">
      <input v-model="form.title" placeholder="片单名称" class="form-input" />
      <textarea
        v-model="form.description"
        placeholder="描述这个片单..."
        class="form-textarea"
        rows="2"
      ></textarea>
      <input
        type="file"
        accept="image/*"
        @change="onCoverChange"
        class="file-input"
      />
      <img v-if="coverPreview" :src="coverPreview" class="preview-img" />

      <!-- 创建时添加电影 -->
      <div class="movie-search-bar">
        <input
          v-model="movieSearchQ"
          placeholder="搜索电影添加到片单..."
          @input="searchCreateMovies"
          class="form-input"
        />
        <div class="search-results" v-if="createSearchResults.length">
          <div
            v-for="m in createSearchResults"
            :key="m.id"
            class="search-item"
            @click="selectMovie(m)"
          >
            + {{ m.title }}（⭐ {{ m.rating }}）
          </div>
        </div>
      </div>
      <div v-if="selectedMovies.length" class="selected-movies">
        <span v-for="m in selectedMovies" :key="m.id" class="selected-chip"
          >{{ m.title }} <button @click="removeSelected(m.id)">×</button></span
        >
      </div>

      <label class="checkbox-label"
        ><input type="checkbox" v-model="form.isPublic" checked />
        公开片单（其他人可见）</label
      >
      <div class="form-actions">
        <button
          class="cancel-btn"
          @click="
            showForm = false;
            coverPreview = null;
          "
        >
          取消
        </button>
        <button
          class="submit-btn"
          @click="createCollection"
          :disabled="!form.title.trim() || submitting"
        >
          {{ submitting ? "创建中..." : "创建" }}
        </button>
      </div>
    </div>

    <div class="collection-grid">
      <div
        v-for="c in collections"
        :key="c.id"
        class="collection-card"
        @click="$router.push(`/collections/${c.id}`)"
      >
        <div
          class="cc-cover"
          :style="c.cover ? { backgroundImage: `url(${c.cover})` } : {}"
        >
          <span v-if="!c.cover" class="cc-icon">🎬</span>
        </div>
        <div class="cc-body">
          <h3>{{ c.is_public ? "" : "🔒 " }}{{ c.title }}</h3>
          <p>{{ c.description || "暂无描述" }}</p>
          <div class="cc-meta">
            <span>{{ c.created_by?.username }}</span>
            <span>🎬 {{ c.movie_count }} 部</span>
            <span>👍 {{ c.like_count }}</span>
          </div>
        </div>
      </div>
      <div v-if="collections.length === 0" class="empty-card">
        暂无片单，快来创建第一个吧
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
const API = "http://localhost:8000/api";
export default defineComponent({
  name: "CollectionsView",
  setup() {
    const authStore = useAuthStore();
    const collections = ref<any[]>([]);
    const showForm = ref(false);
    const submitting = ref(false);
    const form = ref({ title: "", description: "", isPublic: true });
    const coverFile = ref<File | null>(null);
    const coverPreview = ref<string | null>(null);
    const movieSearchQ = ref("");
    const createSearchResults = ref<any[]>([]);
    const selectedMovies = ref<any[]>([]);
    let createSearchTimer: any = null;

    const searchCreateMovies = () => {
      if (createSearchTimer) clearTimeout(createSearchTimer);
      const q = movieSearchQ.value.trim();
      if (!q) {
        createSearchResults.value = [];
        return;
      }
      createSearchTimer = setTimeout(async () => {
        const r = await fetch(`${API}/search/?q=${encodeURIComponent(q)}`);
        if (r.ok) {
          const d = await r.json();
          createSearchResults.value = d.results || [];
        }
      }, 300);
    };

    const selectMovie = (m: any) => {
      if (!selectedMovies.value.find((x) => x.id === m.id)) {
        selectedMovies.value.push(m);
      }
      movieSearchQ.value = "";
      createSearchResults.value = [];
    };

    const removeSelected = (id: number) => {
      selectedMovies.value = selectedMovies.value.filter((m) => m.id !== id);
    };

    const onCoverChange = (e: Event) => {
      const input = e.target as HTMLInputElement;
      if (input.files?.[0]) {
        coverFile.value = input.files[0];
        coverPreview.value = URL.createObjectURL(input.files[0]);
      }
    };

    const fetchList = async () => {
      const headers: any = {};
      if (authStore.token) headers.Authorization = `Token ${authStore.token}`;
      const r = await fetch(`${API}/collections/`, { headers });
      if (r.ok) {
        const d = await r.json();
        collections.value = d.results || [];
      }
    };

    const createCollection = async () => {
      submitting.value = true;
      const fd = new FormData();
      fd.append("title", form.value.title);
      fd.append("description", form.value.description);
      fd.append("is_public", String(form.value.isPublic));
      if (coverFile.value) fd.append("cover", coverFile.value);
      if (selectedMovies.value.length) {
        fd.append(
          "movie_ids",
          JSON.stringify(selectedMovies.value.map((m) => m.id))
        );
      }
      const r = await fetch(`${API}/collections/`, {
        method: "POST",
        headers: { Authorization: `Token ${authStore.token}` },
        body: fd,
      });
      if (r.ok) {
        showForm.value = false;
        form.value = { title: "", description: "", isPublic: true };
        coverFile.value = null;
        coverPreview.value = null;
        selectedMovies.value = [];
        movieSearchQ.value = "";
        await fetchList();
      }
      submitting.value = false;
    };

    onMounted(fetchList);
    return {
      authStore,
      collections,
      showForm,
      submitting,
      form,
      onCoverChange,
      coverPreview,
      movieSearchQ,
      createSearchResults,
      selectedMovies,
      searchCreateMovies,
      selectMovie,
      removeSelected,
      createCollection,
    };
  },
});
</script>

<style scoped>
.collections-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.hero-section {
  background: var(--bg-hero);
  border-radius: var(--radius-lg);
  padding: 28px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
}
.hero-section h1 {
  margin: 0;
  font-size: 1.6rem;
}
.hero-section p {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.8);
}
.create-btn {
  border: none;
  padding: 10px 18px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}
.form-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
  font-family: inherit;
}
.form-textarea {
  resize: vertical;
  min-height: 60px;
}
.file-input {
  font-size: 0.9rem;
  color: var(--text-secondary);
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  cursor: pointer;
}
.movie-search-bar {
  position: relative;
}
.search-results {
  position: absolute;
  top: 42px;
  left: 0;
  right: 0;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  z-index: 20;
  max-height: 200px;
  overflow-y: auto;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}
.search-item {
  padding: 10px 14px;
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--panel-border);
  transition: background var(--transition-fast);
}
.search-item:hover {
  background: var(--nav-hover-bg);
}
.selected-movies {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.selected-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  border-radius: var(--radius-full);
  background: var(--primary-gradient);
  color: #fff;
  font-size: 0.85rem;
  font-weight: 600;
}
.selected-chip button {
  border: none;
  background: rgba(255, 255, 255, 0.3);
  color: #fff;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  cursor: pointer;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-img {
  max-width: 160px;
  max-height: 120px;
  border-radius: var(--radius-md);
  object-fit: cover;
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
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
}
.submit-btn {
  background: var(--primary-gradient);
  color: #fff;
}
.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.cancel-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}
.collection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
.collection-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--panel-shadow);
}
.collection-card:hover {
  transform: translateY(-2px);
}
.cc-cover {
  height: 140px;
  background-size: cover;
  background-position: center;
  background-color: var(--nav-hover-bg);
  display: flex;
  align-items: center;
  justify-content: center;
}
.cc-icon {
  font-size: 2.5rem;
}
.cc-body {
  padding: 16px;
}
.cc-body h3 {
  margin: 0 0 6px;
  color: var(--text-primary);
  font-size: 1.05rem;
}
.cc-body p {
  margin: 0 0 8px;
  color: var(--text-secondary);
  font-size: 0.88rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.cc-meta {
  display: flex;
  gap: 12px;
  font-size: 0.82rem;
  color: var(--text-muted);
}
.empty-card {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}
</style>
