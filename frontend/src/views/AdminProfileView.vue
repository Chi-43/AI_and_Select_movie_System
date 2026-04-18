<template>
  <div class="admin-profile-page">
    <section class="profile-card">
      <div class="profile-header">
        <div class="avatar-wrap">
          <div class="avatar-circle">👑</div>
          <div>
            <h2>管理员个人信息</h2>
            <p>查看并修改管理员个人资料。</p>
          </div>
        </div>
      </div>

      <div v-if="errorMessage" class="error-box">
        {{ errorMessage }}
      </div>

      <div class="form-grid">
        <div class="form-item">
          <label>用户名</label>
          <input v-model="form.username" class="form-input" />
        </div>

        <div class="form-item">
          <label>邮箱</label>
          <input v-model="form.email" class="form-input" />
        </div>

        <div class="form-item">
          <label>姓</label>
          <input v-model="form.first_name" class="form-input" />
        </div>

        <div class="form-item">
          <label>名</label>
          <input v-model="form.last_name" class="form-input" />
        </div>

        <div class="form-item full">
          <label>个人简介</label>
          <textarea v-model="form.bio" class="form-textarea"></textarea>
        </div>
      </div>

      <div class="info-row">
        <div class="info-card">
          <div class="info-label">管理员角色</div>
          <div class="info-value">系统管理员</div>
        </div>
        <div class="info-card">
          <div class="info-label">注册时间</div>
          <div class="info-value">{{ formatDate(form.date_joined) }}</div>
        </div>
      </div>

      <div class="action-row">
        <button class="save-btn" @click="saveProfile" :disabled="saving">
          {{ saving ? "保存中..." : "保存修改" }}
        </button>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, onMounted } from "vue";

const API_BASE_URL = "http://127.0.0.1:8000";

export default defineComponent({
  name: "AdminProfileView",
  setup() {
    const saving = ref(false);
    const errorMessage = ref("");

    const form = reactive({
      username: "",
      email: "",
      first_name: "",
      last_name: "",
      bio: "",
      date_joined: "",
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

    const fetchProfile = async () => {
      errorMessage.value = "";

      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/profile/`, {
          method: "GET",
          headers: getTokenHeaders(),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.detail || "获取管理员信息失败");
        }

        form.username = data.username || "";
        form.email = data.email || "";
        form.first_name = data.first_name || "";
        form.last_name = data.last_name || "";
        form.bio = data.bio || "";
        form.date_joined = data.date_joined || "";
      } catch (error: any) {
        errorMessage.value = error.message || "加载管理员信息失败";
      }
    };

    const saveProfile = async () => {
      if (!form.username.trim()) {
        alert("用户名不能为空");
        return;
      }

      saving.value = true;
      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/profile/`, {
          method: "PUT",
          headers: getJsonHeaders(),
          body: JSON.stringify({
            username: form.username.trim(),
            email: form.email.trim(),
            first_name: form.first_name.trim(),
            last_name: form.last_name.trim(),
            bio: form.bio.trim(),
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.detail || "保存管理员信息失败");
        }

        if (data.admin) {
          localStorage.setItem("admin_user", JSON.stringify(data.admin));
        }

        alert("管理员信息更新成功");
        await fetchProfile();
      } catch (error: any) {
        alert(error.message || "保存失败");
      } finally {
        saving.value = false;
      }
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
      fetchProfile();
    });

    return {
      form,
      saving,
      errorMessage,
      saveProfile,
      formatDate,
    };
  },
});
</script>

<style scoped>
.admin-profile-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-card,
.info-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
}

.profile-card {
  padding: 24px;
}

.profile-header {
  margin-bottom: 24px;
}

.avatar-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-circle {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  color: white;
  font-size: 28px;
  box-shadow: var(--shadow-glow);
}

.avatar-wrap h2 {
  margin: 0;
  color: var(--text-primary);
}

.avatar-wrap p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}

.error-box {
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
  font-weight: 600;
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

.info-row {
  margin-top: 22px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.info-card {
  padding: 18px 20px;
}

.info-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.info-value {
  margin-top: 8px;
  color: var(--text-primary);
  font-weight: 800;
  font-size: 1.05rem;
}

.action-row {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.save-btn {
  border: none;
  border-radius: var(--radius-md);
  padding: 12px 18px;
  background: var(--primary-gradient);
  color: white;
  font-weight: 800;
  cursor: pointer;
  box-shadow: var(--shadow-glow);
}

@media (max-width: 900px) {
  .form-grid,
  .info-row {
    grid-template-columns: 1fr;
  }
}
</style>
