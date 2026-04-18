<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>🎬 电影推荐系统</h1>
        <p>{{ isAdminMode ? "管理员后台登录" : "登录您的账户" }}</p>
      </div>

      <div class="mode-switch">
        <button
          class="mode-btn"
          :class="{ active: !isAdminMode }"
          @click="switchMode(false)"
        >
          用户登录
        </button>
        <button
          class="mode-btn"
          :class="{ active: isAdminMode }"
          @click="switchMode(true)"
        >
          管理员登录
        </button>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">{{
            isAdminMode ? "管理员账号" : "用户名"
          }}</label>
          <input
            type="text"
            id="username"
            v-model="loginData.username"
            required
            :placeholder="isAdminMode ? '请输入管理员账号' : '请输入用户名'"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="loginData.password"
            required
            placeholder="请输入密码"
          />
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          <span v-if="loading">{{
            isAdminMode ? "登录后台中..." : "登录中..."
          }}</span>
          <span v-else>{{ isAdminMode ? "进入管理员后台" : "登录" }}</span>
        </button>
      </form>

      <div class="login-footer">
        <template v-if="!isAdminMode">
          <p>还没有账户？ <router-link to="/register">立即注册</router-link></p>
        </template>
        <p><router-link to="/">返回首页</router-link></p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import type { LoginData } from "@/types/auth";

const API_BASE_URL = "http://127.0.0.1:8000";

export default defineComponent({
  name: "LoginView",
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    const loginData = ref<LoginData>({
      username: "",
      password: "",
    });

    const loading = ref(false);
    const error = ref("");
    const isAdminMode = ref(false);

    const switchMode = (adminMode: boolean) => {
      isAdminMode.value = adminMode;
      error.value = "";
      loginData.value.username = "";
      loginData.value.password = "";
    };

    const handleUserLogin = async () => {
      await authStore.login(loginData.value);
      router.push("/");
    };

    const handleAdminLogin = async () => {
      const response = await fetch(`${API_BASE_URL}/api/admin/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: loginData.value.username,
          password: loginData.value.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.detail || "管理员登录失败");
      }

      localStorage.setItem("admin_token", data.token);
      localStorage.setItem("admin_user", JSON.stringify(data.user));

      router.push("/admin/dashboard");
    };

    const handleLogin = async () => {
      if (!loginData.value.username || !loginData.value.password) {
        error.value = isAdminMode.value
          ? "请输入管理员账号和密码"
          : "请输入用户名和密码";
        return;
      }

      loading.value = true;
      error.value = "";

      try {
        if (isAdminMode.value) {
          await handleAdminLogin();
        } else {
          await handleUserLogin();
        }
      } catch (err: any) {
        error.value =
          err.response?.data?.detail ||
          err.message ||
          (isAdminMode.value ? "管理员登录失败" : "登录失败");
      } finally {
        loading.value = false;
      }
    };

    return {
      loginData,
      loading,
      error,
      isAdminMode,
      switchMode,
      handleLogin,
    };
  },
});
</script>

<style scoped>
/* ====== 登录页 ====== */
.login-container {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 28px;
  background: var(--bg-glow);
  overflow: hidden;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 34px 28px;
  border-radius: var(--radius-lg);
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  box-shadow: var(--panel-shadow);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
  position: relative;
}

.login-card::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: var(--radius-lg);
  pointer-events: none;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.14),
    rgba(255, 255, 255, 0.02)
  );
  mask: linear-gradient(#000, transparent 55%);
}

.login-header {
  text-align: center;
  margin-bottom: 18px;
}

.login-header h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 900;
  letter-spacing: 0.2px;
  color: var(--text-primary);
}

.login-header p {
  margin: 10px 0 0;
  font-size: var(--font-sm);
  color: var(--text-muted);
}

.mode-switch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 18px;
  padding: 6px;
  border-radius: var(--radius-md);
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid var(--panel-border);
}

.mode-btn {
  border: none;
  border-radius: var(--radius-md);
  padding: 10px 12px;
  background: transparent;
  color: var(--text-secondary);
  font-weight: 800;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.mode-btn.active {
  background: var(--primary-gradient);
  color: #fff;
  box-shadow: var(--primary-shadow);
}

.error-message {
  margin: 14px 0 18px;
  padding: 12px;
  border-radius: var(--radius-md);
  color: var(--danger-text);
  background: var(--danger-bg);
  border: 1px solid var(--danger-border);
  font-weight: 700;
  font-size: var(--font-sm);
}

.login-form {
  margin-top: 8px;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: var(--font-xs);
  font-weight: 800;
  color: var(--text-secondary);
  letter-spacing: 0.2px;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  font-size: var(--font-base);
  outline: none;
  transition: box-shadow var(--transition-fast),
    border-color var(--transition-fast);
}

.form-group input::placeholder {
  color: var(--input-placeholder);
}

.form-group input:focus {
  border-color: var(--input-focus-border);
  box-shadow: var(--input-focus-shadow);
}

.login-btn {
  width: 100%;
  margin-top: 6px;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  border: none;
  background: var(--primary-gradient);
  color: #fff;
  font-size: var(--font-base);
  font-weight: 900;
  cursor: pointer;
  box-shadow: var(--primary-shadow);
  transition: transform var(--transition-fast),
    box-shadow var(--transition-fast), filter var(--transition-fast);
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.05);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0px);
}

.login-btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
  box-shadow: none;
}

.login-footer {
  margin-top: 22px;
  padding-top: 16px;
  border-top: 1px solid var(--panel-border);
  text-align: center;
}

.login-footer p {
  margin: 10px 0;
  color: var(--text-muted);
  font-size: var(--font-sm);
}

.login-footer a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 900;
}

.login-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-card {
    padding: 28px 18px;
    border-radius: var(--radius-lg);
  }

  .login-header h1 {
    font-size: 20px;
  }
}
</style>
