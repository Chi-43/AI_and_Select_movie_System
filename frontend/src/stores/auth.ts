import { defineStore } from "pinia";
import { ref, computed } from "vue";
import axios from "axios";
import type {
  LoginData,
  RegisterData,
  User,
  AuthResponse,
  AuthState,
} from "@/types/auth";

const API_BASE_URL = "http://localhost:8000/api";

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem("token"),
    isAuthenticated: !!localStorage.getItem("token"),
    loading: false,
    error: null,
  }),

  actions: {
    async login(loginData: LoginData) {
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.post<AuthResponse>(
          `${API_BASE_URL}/auth/login/`,
          loginData
        );

        this.user = response.data.user;
        this.token = response.data.token;
        this.isAuthenticated = true;

        // 保存token到localStorage
        localStorage.setItem("token", response.data.token);
        localStorage.setItem("user", JSON.stringify(response.data.user));

        // 设置axios默认头部
        axios.defaults.headers.common[
          "Authorization"
        ] = `Token ${response.data.token}`;

        return response.data;
      } catch (error: any) {
        this.error =
          error.response?.data?.detail || error.message || "登录失败";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async register(registerData: RegisterData) {
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.post<AuthResponse>(
          `${API_BASE_URL}/auth/register/`,
          registerData
        );

        this.user = response.data.user;
        this.token = response.data.token;
        this.isAuthenticated = true;

        // 保存token到localStorage
        localStorage.setItem("token", response.data.token);
        localStorage.setItem("user", JSON.stringify(response.data.user));

        // 设置axios默认头部
        axios.defaults.headers.common[
          "Authorization"
        ] = `Token ${response.data.token}`;

        return response.data;
      } catch (error: any) {
        this.error = error.response?.data || error.message || "注册失败";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      this.loading = true;

      try {
        if (this.token) {
          await axios.post(
            `${API_BASE_URL}/auth/logout/`,
            {},
            {
              headers: {
                Authorization: `Token ${this.token}`,
              },
            }
          );
        }
      } catch (error) {
        console.error("注销时出错:", error);
      } finally {
        // 清除本地状态
        this.user = null;
        this.token = null;
        this.isAuthenticated = false;

        // 清除localStorage
        localStorage.removeItem("token");
        localStorage.removeItem("user");

        // 清除axios头部
        delete axios.defaults.headers.common["Authorization"];

        this.loading = false;
      }
    },

    async checkAuth() {
      if (!this.token) {
        return false;
      }

      this.loading = true;

      try {
        const response = await axios.get(`${API_BASE_URL}/auth/check/`, {
          headers: {
            Authorization: `Token ${this.token}`,
          },
        });

        if (response.data.authenticated) {
          this.user = response.data.user;
          this.isAuthenticated = true;
          return true;
        } else {
          this.logout();
          return false;
        }
      } catch (error) {
        console.error("检查认证状态时出错:", error);
        this.logout();
        return false;
      } finally {
        this.loading = false;
      }
    },

    async updateProfile(userData: Partial<User>) {
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.put(
          `${API_BASE_URL}/auth/profile/`,
          userData,
          {
            headers: {
              Authorization: `Token ${this.token}`,
            },
          }
        );

        this.user = response.data;
        localStorage.setItem("user", JSON.stringify(response.data));

        return response.data;
      } catch (error: any) {
        this.error = error.response?.data || error.message || "更新资料失败";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async changePassword(
      oldPassword: string,
      newPassword: string,
      newPassword2: string
    ) {
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.post(
          `${API_BASE_URL}/auth/change-password/`,
          {
            old_password: oldPassword,
            new_password: newPassword,
            new_password2: newPassword2,
          },
          {
            headers: {
              Authorization: `Token ${this.token}`,
            },
          }
        );

        // 更新token
        this.token = response.data.token;
        localStorage.setItem("token", response.data.token);
        axios.defaults.headers.common[
          "Authorization"
        ] = `Token ${response.data.token}`;

        return response.data;
      } catch (error: any) {
        this.error = error.response?.data || error.message || "修改密码失败";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    initialize() {
      // 从localStorage恢复用户信息
      const savedUser = localStorage.getItem("user");
      if (savedUser) {
        try {
          this.user = JSON.parse(savedUser);
        } catch (error) {
          console.error("解析用户信息失败:", error);
          localStorage.removeItem("user");
        }
      }

      // 设置axios默认头部
      if (this.token) {
        axios.defaults.headers.common["Authorization"] = `Token ${this.token}`;
      }

      // 检查认证状态
      if (this.token) {
        this.checkAuth();
      }
    },
  },

  getters: {
    fullName: (state) => {
      if (!state.user) return "";
      return (
        `${state.user.first_name} ${state.user.last_name}`.trim() ||
        state.user.username
      );
    },

    isAdmin: (state) => {
      return state.user?.username === "admin";
    },
  },
});
