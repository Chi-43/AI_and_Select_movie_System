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
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  padding: 40px;
  width: 100%;
  max-width: 500px;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h1 {
  margin: 0;
  color: #333;
  font-size: 1.8rem;
}

.register-header p {
  margin: 10px 0 0;
  color: #666;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 5px;
  margin-bottom: 20px;
  text-align: center;
  border: 1px solid #fcc;
}

.register-form {
  margin-bottom: 30px;
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.form-row .form-group {
  flex: 1;
  margin-bottom: 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.form-hint {
  display: block;
  margin-top: 5px;
  color: #888;
  font-size: 0.85rem;
}

.register-btn {
  width: 100%;
  padding: 14px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.register-btn:hover:not(:disabled) {
  background: #45a049;
}

.register-btn:disabled {
  background: #a0aec0;
  cursor: not-allowed;
}

.register-footer {
  text-align: center;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.register-footer p {
  margin: 10px 0;
  color: #666;
}

.register-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.register-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 600px) {
  .form-row {
    flex-direction: column;
    gap: 20px;
  }

  .register-card {
    padding: 30px 20px;
  }
}
</style>
