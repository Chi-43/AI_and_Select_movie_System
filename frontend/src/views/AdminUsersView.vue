<template>
  <div class="admin-users-page">
    <section class="toolbar-card">
      <div class="toolbar-left">
        <h2>用户管理</h2>
        <p>查看系统中的普通用户，并支持修改或删除用户信息。</p>
      </div>

      <div class="toolbar-right">
        <input
          v-model="keyword"
          type="text"
          class="search-input"
          placeholder="搜索用户名 / 邮箱 / 姓名"
        />
        <button class="refresh-btn" @click="fetchUsers" :disabled="loading">
          {{ loading ? "刷新中..." : "刷新列表" }}
        </button>
      </div>
    </section>

    <section class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ filteredUsers.length }}</div>
        <div class="stat-label">当前显示用户</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ users.length }}</div>
        <div class="stat-label">系统用户总数</div>
      </div>
    </section>

    <section class="table-card">
      <div v-if="errorMessage" class="error-box">
        {{ errorMessage }}
      </div>

      <div v-if="loading" class="loading-box">正在加载用户列表...</div>

      <div v-else-if="filteredUsers.length === 0" class="empty-box">
        暂无符合条件的用户数据。
      </div>

      <div v-else class="table-wrapper">
        <table class="user-table">
          <thead>
            <tr>
              <th>用户名</th>
              <th>邮箱</th>
              <th>姓名</th>
              <th>注册时间</th>
              <th>简介</th>
              <th>操作</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td class="username-cell">
                <div class="avatar-badge">
                  {{ getUserInitial(user.username) }}
                </div>
                <span>{{ user.username }}</span>
              </td>
              <td>{{ user.email || "未填写" }}</td>
              <td>{{ formatName(user.first_name, user.last_name) }}</td>
              <td>{{ formatDate(user.date_joined) }}</td>
              <td class="bio-cell">
                {{ user.bio || "暂无简介" }}
              </td>
              <td>
                <div class="action-group">
                  <button class="action-btn edit" @click="openEditModal(user)">
                    编辑
                  </button>
                  <button class="action-btn delete" @click="deleteUser(user)">
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 编辑弹窗 -->
    <div v-if="showEditModal" class="modal-mask" @click.self="closeEditModal">
      <div class="modal-card">
        <div class="modal-header">
          <h3>编辑用户信息</h3>
          <button class="close-btn" @click="closeEditModal">×</button>
        </div>

        <div class="form-grid">
          <div class="form-item">
            <label>用户名</label>
            <input v-model="editForm.username" class="form-input" />
          </div>

          <div class="form-item">
            <label>邮箱</label>
            <input v-model="editForm.email" class="form-input" />
          </div>

          <div class="form-item">
            <label>姓</label>
            <input v-model="editForm.first_name" class="form-input" />
          </div>

          <div class="form-item">
            <label>名</label>
            <input v-model="editForm.last_name" class="form-input" />
          </div>

          <div class="form-item full">
            <label>个人简介</label>
            <textarea v-model="editForm.bio" class="form-textarea"></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button class="cancel-btn" @click="closeEditModal">取消</button>
          <button class="save-btn" @click="submitEdit" :disabled="submitting">
            {{ submitting ? "保存中..." : "保存修改" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, reactive, onMounted } from "vue";

const API_BASE_URL = "http://127.0.0.1:8000";

interface UserItem {
  id: number;
  username: string;
  email: string | null;
  first_name: string;
  last_name: string;
  bio: string | null;
  avatar?: string | null;
  avatar_url?: string | null;
  date_joined: string;
  profile?: any;
}

export default defineComponent({
  name: "AdminUsersView",
  setup() {
    const users = ref<UserItem[]>([]);
    const keyword = ref("");
    const loading = ref(false);
    const submitting = ref(false);
    const errorMessage = ref("");

    const showEditModal = ref(false);
    const currentEditUserId = ref<number | null>(null);

    const editForm = reactive({
      username: "",
      email: "",
      first_name: "",
      last_name: "",
      bio: "",
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

    const fetchUsers = async () => {
      loading.value = true;
      errorMessage.value = "";

      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/users/`, {
          method: "GET",
          headers: getTokenHeaders(),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.detail || "获取用户列表失败");
        }

        users.value = data.users || [];
      } catch (error: any) {
        errorMessage.value = error.message || "加载用户列表失败";
      } finally {
        loading.value = false;
      }
    };

    const filteredUsers = computed(() => {
      const key = keyword.value.trim().toLowerCase();
      if (!key) return users.value;

      return users.value.filter((user) => {
        const fullName = `${user.first_name || ""}${
          user.last_name || ""
        }`.toLowerCase();
        return (
          user.username?.toLowerCase().includes(key) ||
          (user.email || "").toLowerCase().includes(key) ||
          fullName.includes(key)
        );
      });
    });

    const openEditModal = (user: UserItem) => {
      currentEditUserId.value = user.id;
      editForm.username = user.username || "";
      editForm.email = user.email || "";
      editForm.first_name = user.first_name || "";
      editForm.last_name = user.last_name || "";
      editForm.bio = user.bio || "";
      showEditModal.value = true;
    };

    const closeEditModal = () => {
      showEditModal.value = false;
      currentEditUserId.value = null;
      editForm.username = "";
      editForm.email = "";
      editForm.first_name = "";
      editForm.last_name = "";
      editForm.bio = "";
    };

    const submitEdit = async () => {
      if (!currentEditUserId.value) return;

      if (!editForm.username.trim()) {
        alert("用户名不能为空");
        return;
      }

      submitting.value = true;
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/admin/users/${currentEditUserId.value}/`,
          {
            method: "PUT",
            headers: getJsonHeaders(),
            body: JSON.stringify({
              username: editForm.username.trim(),
              email: editForm.email.trim(),
              first_name: editForm.first_name.trim(),
              last_name: editForm.last_name.trim(),
              bio: editForm.bio.trim(),
            }),
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.detail || "更新用户失败");
        }

        alert("用户信息更新成功");
        closeEditModal();
        await fetchUsers();
      } catch (error: any) {
        alert(error.message || "更新用户失败");
      } finally {
        submitting.value = false;
      }
    };

    const deleteUser = async (user: UserItem) => {
      const ok = window.confirm(`确定要删除用户“${user.username}”吗？`);
      if (!ok) return;

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/admin/users/${user.id}/`,
          {
            method: "DELETE",
            headers: getTokenHeaders(),
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.detail || "删除用户失败");
        }

        alert("用户删除成功");
        await fetchUsers();
      } catch (error: any) {
        alert(error.message || "删除用户失败");
      }
    };

    const getUserInitial = (username: string) => {
      return username ? username.charAt(0).toUpperCase() : "?";
    };

    const formatName = (firstName: string, lastName: string) => {
      const name = `${firstName || ""}${lastName || ""}`.trim();
      return name || "未填写";
    };

    const formatDate = (dateStr: string) => {
      if (!dateStr) return "未知";
      return new Date(dateStr).toLocaleDateString("zh-CN");
    };

    onMounted(() => {
      const token = localStorage.getItem("admin_token");
      if (!token) {
        window.location.href = "/admin/login";
        return;
      }
      fetchUsers();
    });

    return {
      users,
      keyword,
      loading,
      submitting,
      errorMessage,
      filteredUsers,
      showEditModal,
      editForm,
      fetchUsers,
      openEditModal,
      closeEditModal,
      submitEdit,
      deleteUser,
      getUserInitial,
      formatName,
      formatDate,
    };
  },
});
</script>

<style scoped>
.admin-users-page {
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
  width: 280px;
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

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th {
  text-align: left;
  padding: 14px 12px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--panel-border);
  font-size: 0.95rem;
}

.user-table td {
  padding: 14px 12px;
  color: var(--text-secondary);
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  vertical-align: middle;
}

.username-cell {
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
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  color: white;
  font-weight: 800;
}

.bio-cell {
  max-width: 260px;
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
  max-width: 720px;
  padding: 24px;
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
  min-height: 120px;
  resize: vertical;
}

.modal-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 900px) {
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
