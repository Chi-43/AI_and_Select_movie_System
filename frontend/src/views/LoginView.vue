<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>🎬 电影推荐系统</h1>
        <p>登录您的账户</p>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            id="username"
            v-model="loginData.username"
            required
            placeholder="请输入用户名"
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
          <span v-if="loading">登录中...</span>
          <span v-else>登录</span>
        </button>
      </form>

      <div class="login-footer">
        <p>还没有账户？ <router-link to="/register">立即注册</router-link></p>
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

    const handleLogin = async () => {
      if (!loginData.value.username || !loginData.value.password) {
        error.value = "请输入用户名和密码";
        return;
      }

      loading.value = true;
      error.value = "";

      try {
        await authStore.login(loginData.value);
        router.push("/");
      } catch (err: any) {
        error.value = err.response?.data?.detail || err.message || "登录失败";
      } finally {
        loading.value = false;
      }
    };

    return {
      loginData,
      loading,
      error,
      handleLogin,
    };
  },
});
</script>

<style scoped>
/* ====== 基础：更柔和的字体与布局 ====== */
.login-container {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 28px;

  /* 背景：渐变 + 光斑 */
  background: radial-gradient(
      900px 600px at 15% 20%,
      rgba(99, 102, 241, 0.35),
      transparent 60%
    ),
    radial-gradient(
      800px 520px at 85% 10%,
      rgba(139, 92, 246, 0.3),
      transparent 55%
    ),
    radial-gradient(
      900px 600px at 50% 95%,
      rgba(16, 185, 129, 0.18),
      transparent 55%
    ),
    linear-gradient(135deg, #0b1220 0%, #111827 55%, #0b1220 100%);
  overflow: hidden;
}

/* 外层卡片：玻璃拟态 */
.login-card {
  width: 100%;
  max-width: 420px;
  padding: 34px 28px;
  border-radius: 22px;

  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);

  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);

  position: relative;
}

/* 卡片顶部细光 */
.login-card::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 22px;
  pointer-events: none;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.14),
    rgba(255, 255, 255, 0.02)
  );
  mask: linear-gradient(#000, transparent 55%);
}

/* 头部 */
.login-header {
  text-align: center;
  margin-bottom: 22px;
}

.login-header h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 900;
  letter-spacing: 0.2px;
  color: rgba(255, 255, 255, 0.94);
}

.login-header p {
  margin: 10px 0 0;
  font-size: 13px;
  color: rgba(148, 163, 184, 0.95);
}

/* 错误提示：更像 toast 卡片 */
.error-message {
  margin: 14px 0 18px;
  padding: 12px 12px;
  border-radius: 14px;

  color: rgba(254, 226, 226, 0.95);
  background: rgba(239, 68, 68, 0.18);
  border: 1px solid rgba(239, 68, 68, 0.28);

  font-weight: 700;
  font-size: 13px;
}

/* 表单间距 */
.login-form {
  margin-top: 8px;
}

/* 表单项 */
.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 800;
  color: rgba(226, 232, 240, 0.92);
  letter-spacing: 0.2px;
}

/* 输入框：更现代 */
.form-group input {
  width: 100%;
  padding: 12px 12px;
  border-radius: 14px;

  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(17, 24, 39, 0.65);
  color: rgba(255, 255, 255, 0.92);

  font-size: 14px;
  outline: none;

  transition: box-shadow 0.18s ease, border-color 0.18s ease,
    transform 0.18s ease;
}

.form-group input::placeholder {
  color: rgba(148, 163, 184, 0.75);
}

/* focus：紫蓝光圈 */
.form-group input:focus {
  border-color: rgba(99, 102, 241, 0.6);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2), 0 18px 50px rgba(0, 0, 0, 0.25);
}

/* 登录按钮：渐变 + 立体 */
.login-btn {
  width: 100%;
  margin-top: 6px;
  padding: 12px 14px;

  border-radius: 14px;
  border: none;

  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;

  font-size: 14px;
  font-weight: 900;
  cursor: pointer;

  box-shadow: 0 18px 50px rgba(99, 102, 241, 0.35);
  transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 22px 60px rgba(99, 102, 241, 0.42);
  filter: brightness(1.02);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0px);
}

.login-btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
  box-shadow: none;
}

/* footer：更简洁 */
.login-footer {
  margin-top: 22px;
  padding-top: 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.16);
  text-align: center;
}

.login-footer p {
  margin: 10px 0;
  color: rgba(148, 163, 184, 0.95);
  font-size: 13px;
}

/* 链接：像按钮文字 */
.login-footer a {
  color: rgba(99, 102, 241, 1);
  text-decoration: none;
  font-weight: 900;
}

.login-footer a:hover {
  text-decoration: underline;
}

/* 移动端适配 */
@media (max-width: 480px) {
  .login-card {
    padding: 28px 18px;
    border-radius: 18px;
  }

  .login-header h1 {
    font-size: 20px;
  }
}
</style>
