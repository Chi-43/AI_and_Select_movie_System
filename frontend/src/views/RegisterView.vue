<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h1>🎬 电影推荐系统</h1>
        <p>创建新账户</p>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">用户名 *</label>
          <input
            type="text"
            id="username"
            v-model="registerData.username"
            required
            placeholder="请输入用户名"
          />
          <small class="form-hint">用户名必须唯一，长度3-20个字符</small>
        </div>

        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            type="email"
            id="email"
            v-model="registerData.email"
            placeholder="请输入邮箱（可选）"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="first_name">名字</label>
            <input
              type="text"
              id="first_name"
              v-model="registerData.first_name"
              placeholder="请输入名字"
            />
          </div>

          <div class="form-group">
            <label for="last_name">姓氏</label>
            <input
              type="text"
              id="last_name"
              v-model="registerData.last_name"
              placeholder="请输入姓氏"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">密码 *</label>
          <input
            type="password"
            id="password"
            v-model="registerData.password"
            required
            placeholder="请输入密码"
          />
          <small class="form-hint">密码至少8个字符，包含字母和数字</small>
        </div>

        <div class="form-group">
          <label for="password2">确认密码 *</label>
          <input
            type="password"
            id="password2"
            v-model="registerData.password2"
            required
            placeholder="请再次输入密码"
          />
        </div>

        <button type="submit" class="register-btn" :disabled="loading">
          <span v-if="loading">注册中...</span>
          <span v-else>注册</span>
        </button>
      </form>

      <div class="register-footer">
        <p>已有账户？ <router-link to="/login">立即登录</router-link></p>
        <p><router-link to="/">返回首页</router-link></p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import type { RegisterData } from "@/types/auth";

export default defineComponent({
  name: "RegisterView",
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    const registerData = ref<RegisterData>({
      username: "",
      email: "",
      password: "",
      password2: "",
      first_name: "",
      last_name: "",
    });

    const loading = ref(false);
    const error = ref("");

    const validateForm = () => {
      if (
        !registerData.value.username ||
        registerData.value.username.length < 3
      ) {
        error.value = "用户名至少需要3个字符";
        return false;
      }

      if (
        !registerData.value.password ||
        registerData.value.password.length < 8
      ) {
        error.value = "密码至少需要8个字符";
        return false;
      }

      if (registerData.value.password !== registerData.value.password2) {
        error.value = "两次输入的密码不一致";
        return false;
      }

      return true;
    };

    const handleRegister = async () => {
      if (!validateForm()) {
        return;
      }

      loading.value = true;
      error.value = "";

      try {
        await authStore.register(registerData.value);
        router.push("/");
      } catch (err: any) {
        // 处理后端返回的错误
        if (err.response?.data) {
          const errors = err.response.data;
          if (typeof errors === "object") {
            // 将对象错误转换为字符串
            const errorMessages = Object.values(errors).flat();
            error.value = errorMessages.join(", ");
          } else {
            error.value = errors.detail || errors.message || "注册失败";
          }
        } else {
          error.value = err.message || "注册失败";
        }
      } finally {
        loading.value = false;
      }
    };

    return {
      registerData,
      loading,
      error,
      handleRegister,
    };
  },
});
</script>

<style scoped>
/* ====== 背景与容器（同登录页风格） ====== */
.register-container {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 28px;

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

/* 玻璃拟态卡片 */
.register-card {
  width: 100%;
  max-width: 540px;
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
.register-card::before {
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

/* ====== 头部 ====== */
.register-header {
  text-align: center;
  margin-bottom: 22px;
}

.register-header h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 900;
  letter-spacing: 0.2px;
  color: rgba(255, 255, 255, 0.94);
}

.register-header p {
  margin: 10px 0 0;
  font-size: 13px;
  color: rgba(148, 163, 184, 0.95);
}

/* 错误提示 */
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

/* ====== 表单布局 ====== */
.register-form {
  margin-top: 8px;
  margin-bottom: 18px;
}

/* 两列：名字/姓氏 */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 14px;
}

/* 通用表单项 */
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

/* 输入框 */
.form-group input {
  width: 100%;
  padding: 12px 12px;
  border-radius: 14px;

  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(17, 24, 39, 0.65);
  color: rgba(255, 255, 255, 0.92);

  font-size: 14px;
  outline: none;

  transition: box-shadow 0.18s ease, border-color 0.18s ease;
}

.form-group input::placeholder {
  color: rgba(148, 163, 184, 0.75);
}

.form-group input:focus {
  border-color: rgba(99, 102, 241, 0.6);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2), 0 18px 50px rgba(0, 0, 0, 0.25);
}

/* 提示文字 */
.form-hint {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.9);
}

/* ====== 注册按钮（统一用紫色渐变，更一致） ====== */
.register-btn {
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

.register-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 22px 60px rgba(99, 102, 241, 0.42);
  filter: brightness(1.02);
}

.register-btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
  box-shadow: none;
}

/* ====== footer ====== */
.register-footer {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.16);
  text-align: center;
}

.register-footer p {
  margin: 10px 0;
  color: rgba(148, 163, 184, 0.95);
  font-size: 13px;
}

.register-footer a {
  color: rgba(99, 102, 241, 1);
  text-decoration: none;
  font-weight: 900;
}

.register-footer a:hover {
  text-decoration: underline;
}

/* ====== 响应式 ====== */
@media (max-width: 600px) {
  .register-card {
    padding: 28px 18px;
    border-radius: 18px;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .register-header h1 {
    font-size: 20px;
  }
}
</style>
