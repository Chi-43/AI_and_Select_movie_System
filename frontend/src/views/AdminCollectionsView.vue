<template>
  <div class="admin-coll">
    <table>
      <thead>
        <tr>
          <th>片单名称</th>
          <th>创建者</th>
          <th>可见</th>
          <th>电影</th>
          <th>赞</th>
          <th>时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in collections" :key="c.id">
          <td class="title-cell">{{ c.title }}</td>
          <td>{{ c.created_by }}</td>
          <td>{{ c.is_public ? "🌐 公开" : "🔒 私密" }}</td>
          <td>{{ c.movie_count }}</td>
          <td>{{ c.like_count }}</td>
          <td>{{ formatDate(c.created_at) }}</td>
          <td class="actions">
            <button class="danger" @click="del(c.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
const API = "http://127.0.0.1:8000";
export default defineComponent({
  name: "AdminCollectionsView",
  setup() {
    const collections = ref<any[]>([]);
    const headers = () => ({
      Authorization: `Token ${localStorage.getItem("admin_token")}`,
    });

    const load = async () => {
      const r = await fetch(`${API}/api/admin/collections/`, {
        headers: headers(),
      });
      if (r.ok) {
        const d = await r.json();
        collections.value = d.collections || [];
      }
    };

    const del = async (id: number) => {
      if (!confirm("确定删除该片单？")) return;
      const r = await fetch(
        `${API}/api/admin/collections/?collection_id=${id}`,
        { method: "DELETE", headers: headers() }
      );
      if (r.ok) await load();
    };

    const formatDate = (d: string) => new Date(d).toLocaleDateString("zh-CN");
    onMounted(load);
    return { collections, del, formatDate };
  },
});
</script>

<style scoped>
.admin-coll {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
table {
  width: 100%;
  border-collapse: collapse;
  background: var(--panel-bg);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
th {
  text-align: left;
  padding: 12px 14px;
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  font-size: 0.85rem;
}
td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--panel-border);
  color: var(--text-primary);
  font-size: 0.9rem;
}
.title-cell {
  max-width: 220px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.actions button {
  border: none;
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
}
.actions button.danger {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}
</style>
