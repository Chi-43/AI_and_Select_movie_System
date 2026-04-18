<template>
  <div class="admin-login-page">
    <div class="admin-login-card">
      <div class="brand-row">
        <div class="brand-icon">🛠️</div>
        <div>
          <h1>管理员后台</h1>
          <p>电影推荐系统 · 后台登录</p>
        </div>
      </div>

      <div class="login-form">
        <div class="form-group">
          <label>管理员账号</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入管理员账号"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            class="form-input"
            @keyup.enter="handleLogin"
          />
        </div>

        <div v-if="errorMessage" class="error-box">
          {{ errorMessage }}
        </div>

        <button class="login-btn" @click="handleLogin" :disabled="loading">
          {{ loading ? "登录中..." : "登录后台" }}
        </button>

        <div class="extra-actions">
          <router-link to="/" class="back-link">返回前台首页</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref } from "vue";

const API_BASE_URL = "http://127.0.0.1:8000";

export default defineComponent({
  name: "AdminLoginView",
  setup() {
    const loading = ref(false);
    const errorMessage = ref("");

    const form = reactive({
      username: "",
      password: "",
    });

    const handleLogin = async () => {
      errorMessage.value = "";

      if (!form.username.trim() || !form.password.trim()) {
        errorMessage.value = "请输入管理员账号和密码";
        return;
      }

      loading.value = true;
      try {
        const response = await fetch(`${API_BASE_URL}/api/admin/login/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: form.username.trim(),
            password: form.password,
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.detail || "管理员登录失败");
        }

        localStorage.setItem("admin_token", data.token);
        localStorage.setItem("admin_user", JSON.stringify(data.user));

        window.location.href = "/admin/dashboard";
      } catch (error: any) {
        errorMessage.value = error.message || "登录失败，请稍后重试";
      } finally {
        loading.value = false;
      }
    };

    return {
      form,
      loading,
      errorMessage,
      handleLogin,
    };
  },
});
</script>

<style scoped>
.admin-login-page {
  min-height: calc(100vh - 80px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  background: var(--bg-main);
}

.admin-login-card {
  width: 100%;
  max-width: 460px;
  padding: 32px;
  border-radius: var(--radius-lg);
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  box-shadow: var(--panel-shadow);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}

.brand-icon {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  background: var(--primary-gradient);
  box-shadow: var(--shadow-glow);
}

.brand-row h1 {
  margin: 0;
  font-size: 1.8rem;
  color: var(--text-primary);
}

.brand-row p {
  margin: 6px 0 0;
  color: var(--text-secondary);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 700;
  color: var(--text-primary);
}

.form-input {
  width: 100%;
  padding: 13px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
  transition: all var(--transition-fast);
}

.form-input:focus {
  border-color: var(--input-focus-border);
  box-shadow: var(--input-focus-shadow);
}

.error-box {
  padding: 12px 14px;
  border-radius: var(--radius-md);
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
  font-size: 0.95rem;
}

.login-btn {
  width: 100%;
  padding: 13px 16px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--primary-gradient);
  color: white;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
  transition: transform var(--transition-fast),
    box-shadow var(--transition-fast);
  box-shadow: var(--shadow-glow);
}

.login-btn:hover {
  transform: translateY(-1px);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.extra-actions {
  display: flex;
  justify-content: center;
}

.back-link {
  color: var(--primary);
  font-weight: 700;
  text-decoration: none;
}

.back-link:hover {
  text-decoration: underline;
}
</style>
