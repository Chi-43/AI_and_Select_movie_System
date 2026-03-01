<template>
  <div class="profile-view">
    <div class="profile-header">
      <h1>👤 个人信息管理</h1>
      <p class="subtitle">管理您的账户信息、密码和收藏夹</p>
    </div>

    <div class="profile-container">
      <!-- 左侧导航 -->
      <div class="profile-sidebar">
        <div class="user-card">
          <div class="avatar-section">
            <div class="avatar-preview" :style="avatarStyle">
              <span v-if="!avatarPreview" class="avatar-placeholder">
                {{ userInitials }}
              </span>
              <img
                v-else
                :src="avatarPreview"
                alt="用户头像"
                class="avatar-image"
              />
            </div>
            <div class="avatar-actions">
              <label for="avatar-upload" class="avatar-upload-btn">
                📷 更换头像
              </label>
              <input
                id="avatar-upload"
                type="file"
                accept="image/*"
                @change="handleAvatarUpload"
                class="avatar-input"
              />
              <button
                v-if="avatarPreview"
                @click="removeAvatar"
                class="avatar-remove-btn"
              >
                ❌ 移除
              </button>
            </div>
          </div>
          <div class="user-info-summary">
            <h3>{{ currentUser?.username || "用户" }}</h3>
            <p class="user-email">{{ currentUser?.email || "未设置邮箱" }}</p>
            <p class="user-join-date" v-if="currentUser?.date_joined">
              注册时间: {{ formatDate(currentUser.date_joined) }}
            </p>
          </div>
        </div>

        <nav class="profile-nav">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="['nav-item', { active: activeTab === tab.id }]"
          >
            <span class="nav-icon">{{ tab.icon }}</span>
            <span class="nav-text">{{ tab.name }}</span>
          </button>
        </nav>
      </div>

      <!-- 右侧内容区域 -->
      <div class="profile-content">
        <!-- 基本信息标签页 -->
        <div v-if="activeTab === 'basic'" class="tab-content">
          <div class="tab-header">
            <h2>📝 基本信息</h2>
            <p class="tab-description">更新您的个人信息</p>
          </div>

          <form @submit.prevent="updateProfile" class="profile-form">
            <div class="form-grid">
              <div class="form-group">
                <label for="username">用户名</label>
                <input
                  id="username"
                  v-model="profileForm.username"
                  type="text"
                  placeholder="请输入用户名"
                  required
                />
                <p class="form-hint">用户名用于登录，不可与其他用户重复</p>
              </div>

              <div class="form-group">
                <label for="email">邮箱地址</label>
                <input
                  id="email"
                  v-model="profileForm.email"
                  type="email"
                  placeholder="请输入邮箱地址"
                  required
                />
                <p class="form-hint">用于接收系统通知和找回密码</p>
              </div>

              <div class="form-group">
                <label for="first_name">名字</label>
                <input
                  id="first_name"
                  v-model="profileForm.first_name"
                  type="text"
                  placeholder="请输入名字"
                />
              </div>

              <div class="form-group">
                <label for="last_name">姓氏</label>
                <input
                  id="last_name"
                  v-model="profileForm.last_name"
                  type="text"
                  placeholder="请输入姓氏"
                />
              </div>
            </div>

            <div class="form-group full-width">
              <label for="bio">个人简介</label>
              <textarea
                id="bio"
                v-model="profileForm.bio"
                placeholder="介绍一下自己吧..."
                rows="4"
                maxlength="500"
              ></textarea>
              <div class="textarea-footer">
                <span class="char-count"
                  >{{ profileForm.bio?.length || 0 }}/500</span
                >
                <p class="form-hint">最多500个字符</p>
              </div>
            </div>

            <div class="form-actions">
              <button
                type="button"
                @click="resetProfileForm"
                class="secondary-btn"
                :disabled="isProfileFormChanged"
              >
                重置
              </button>
              <button
                type="submit"
                class="primary-btn"
                :disabled="!isProfileFormChanged || profileLoading"
              >
                {{ profileLoading ? "保存中..." : "保存更改" }}
              </button>
            </div>
          </form>
        </div>

        <!-- 修改密码标签页 -->
        <div v-else-if="activeTab === 'password'" class="tab-content">
          <div class="tab-header">
            <h2>🔒 修改密码</h2>
            <p class="tab-description">定期修改密码有助于保护账户安全</p>
          </div>

          <form @submit.prevent="changePassword" class="password-form">
            <div class="form-group">
              <label for="old_password">当前密码</label>
              <input
                id="old_password"
                v-model="passwordForm.old_password"
                type="password"
                placeholder="请输入当前密码"
                required
              />
            </div>

            <div class="form-group">
              <label for="new_password">新密码</label>
              <input
                id="new_password"
                v-model="passwordForm.new_password"
                type="password"
                placeholder="请输入新密码"
                required
              />
              <p class="form-hint">密码至少8位，包含字母和数字</p>
            </div>

            <div class="form-group">
              <label for="new_password2">确认新密码</label>
              <input
                id="new_password2"
                v-model="passwordForm.new_password2"
                type="password"
                placeholder="请再次输入新密码"
                required
              />
              <div
                v-if="passwordForm.new_password && passwordForm.new_password2"
                class="password-match"
              >
                <span
                  :class="[
                    'match-icon',
                    { match: passwordsMatch, mismatch: !passwordsMatch },
                  ]"
                >
                  {{ passwordsMatch ? "✓" : "✗" }}
                </span>
                <span
                  :class="[
                    'match-text',
                    { match: passwordsMatch, mismatch: !passwordsMatch },
                  ]"
                >
                  {{ passwordsMatch ? "密码匹配" : "密码不匹配" }}
                </span>
              </div>
            </div>

            <div class="password-strength" v-if="passwordForm.new_password">
              <div class="strength-label">密码强度:</div>
              <div class="strength-meter">
                <div
                  class="strength-bar"
                  :class="passwordStrengthClass"
                  :style="{ width: passwordStrength + '%' }"
                ></div>
              </div>
              <div class="strength-text">{{ passwordStrengthText }}</div>
            </div>

            <div class="form-actions">
              <button
                type="button"
                @click="resetPasswordForm"
                class="secondary-btn"
              >
                重置
              </button>
              <button
                type="submit"
                class="primary-btn"
                :disabled="!isPasswordFormValid || passwordLoading"
              >
                {{ passwordLoading ? "修改中..." : "修改密码" }}
              </button>
            </div>
          </form>
        </div>

        <!-- 收藏夹标签页 -->
        <div v-else-if="activeTab === 'favorites'" class="tab-content">
          <div class="tab-header">
            <h2>❤️ 我的收藏夹</h2>
            <p class="tab-description">您收藏的电影列表</p>
            <div class="favorites-stats">
              <span class="stat-item">
                <span class="stat-number">{{ favorites.length }}</span>
                <span class="stat-label">部收藏</span>
              </span>
              <span class="stat-item">
                <span class="stat-number">{{ favoriteGenres.length }}</span>
                <span class="stat-label">种类型</span>
              </span>
              <span class="stat-item">
                <span class="stat-number">{{
                  averageFavoriteRating.toFixed(1)
                }}</span>
                <span class="stat-label">平均评分</span>
              </span>
            </div>
          </div>

          <div v-if="favoritesLoading" class="loading-state">
            <div class="spinner"></div>
            <p>加载收藏夹中...</p>
          </div>

          <div v-else-if="favorites.length === 0" class="empty-state">
            <div class="empty-icon">🎬</div>
            <h3>暂无收藏</h3>
            <p>您还没有收藏任何电影</p>
            <router-link to="/douban" class="browse-btn">
              去浏览电影
            </router-link>
          </div>

          <div v-else class="favorites-content">
            <div class="favorites-controls">
              <div class="sort-controls">
                <label>排序方式:</label>
                <select v-model="favoritesSortBy" @change="sortFavorites">
                  <option value="rating">评分从高到低</option>
                  <option value="rating_asc">评分从低到高</option>
                  <option value="year">年份从新到旧</option>
                  <option value="year_asc">年份从旧到新</option>
                  <option value="name">电影名称A-Z</option>
                </select>
              </div>
              <button @click="clearAllFavorites" class="danger-btn">
                🗑️ 清空收藏夹
              </button>
            </div>

            <div class="favorites-grid">
              <div
                v-for="movie in sortedFavorites"
                :key="movie['电影链接']"
                class="favorite-card"
              >
                <div class="favorite-header">
                  <h4 class="movie-title">{{ movie["电影名字"] }}</h4>
                  <div class="movie-rating">
                    <span class="rating-star">⭐</span>
                    <span class="rating-value">{{ movie["评分"] }}</span>
                  </div>
                </div>

                <div class="movie-meta">
                  <span class="meta-item">
                    <span class="meta-label">年份:</span>
                    <span class="meta-value">{{ movie["年份"] }}</span>
                  </span>
                  <span class="meta-item">
                    <span class="meta-label">国家:</span>
                    <span class="meta-value">{{ movie["国家"] }}</span>
                  </span>
                  <span class="meta-item">
                    <span class="meta-label">类型:</span>
                    <span class="meta-value">{{ movie["类型"] }}</span>
                  </span>
                </div>

                <div class="movie-quote" v-if="movie['一句话评价']">
                  <span class="quote-icon">💬</span>
                  <span class="quote-text">{{ movie["一句话评价"] }}</span>
                </div>

                <div class="favorite-actions">
                  <a
                    :href="movie['电影链接']"
                    target="_blank"
                    class="action-btn small-btn"
                  >
                    查看豆瓣
                  </a>
                  <button
                    @click="removeFromFavorites(movie)"
                    class="action-btn danger-btn small-btn"
                  >
                    取消收藏
                  </button>
                </div>
              </div>
            </div>

            <!-- 收藏分析 -->
            <div class="favorites-analysis">
              <h3>📊 收藏分析</h3>
              <div class="analysis-grid">
                <div class="analysis-card">
                  <h4>最常收藏的类型</h4>
                  <div class="genre-tags">
                    <span
                      v-for="genre in topFavoriteGenres"
                      :key="genre.name"
                      class="genre-tag"
                    >
                      {{ genre.name }} ({{ genre.count }})
                    </span>
                  </div>
                </div>
                <div class="analysis-card">
                  <h4>年份分布</h4>
                  <div class="year-distribution">
                    <div
                      v-for="year in favoriteYears"
                      :key="year.year"
                      class="year-item"
                    >
                      <span class="year-label">{{ year.year }}</span>
                      <div class="year-bar">
                        <div
                          class="bar-fill"
                          :style="{ width: year.percentage + '%' }"
                        ></div>
                      </div>
                      <span class="year-count">{{ year.count }}部</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 账户设置标签页 -->
        <div v-else-if="activeTab === 'settings'" class="tab-content">
          <div class="tab-header">
            <h2>⚙️ 账户设置</h2>
            <p class="tab-description">管理您的账户偏好设置</p>
          </div>

          <div class="settings-list">
            <div class="setting-item">
              <div class="setting-info">
                <h4>邮箱通知</h4>
                <p>接收系统通知和推荐邮件</p>
              </div>
              <div class="setting-control">
                <label class="switch">
                  <input
                    type="checkbox"
                    v-model="settings.emailNotifications"
                  />
                  <span class="slider"></span>
                </label>
              </div>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h4>个性化推荐</h4>
                <p>基于您的观看历史和收藏推荐电影</p>
              </div>
              <div class="setting-control">
                <label class="switch">
                  <input
                    type="checkbox"
                    v-model="settings.personalizedRecommendations"
                  />
                  <span class="slider"></span>
                </label>
              </div>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h4>公开收藏夹</h4>
                <p>允许其他用户查看您的收藏</p>
              </div>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.publicFavorites" />
                  <span class="slider"></span>
                </label>
              </div>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h4>深色模式</h4>
                <p>切换到深色主题</p>
              </div>
              <div class="setting-control">
                <label class="switch">
                  <input
                    type="checkbox"
                    v-model="settings.darkMode"
                    @change="toggleDarkMode"
                  />
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>

          <div class="settings-actions">
            <button
              @click="saveSettings"
              class="primary-btn"
              :disabled="settingsLoading"
            >
              {{ settingsLoading ? "保存中..." : "保存设置" }}
            </button>
            <button @click="resetSettings" class="secondary-btn">
              恢复默认
            </button>
          </div>

          <div class="danger-zone">
            <h3>⚠️ 危险区域</h3>
            <p class="danger-warning">这些操作不可撤销，请谨慎操作</p>

            <div class="danger-actions">
              <button @click="exportData" class="secondary-btn">
                📥 导出个人数据
              </button>
              <button @click="deleteAccount" class="danger-btn">
                🗑️ 删除账户
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import doubanData from "../data/豆瓣电影TOP250.json";

interface DoubanMovie {
  电影名字: string;
  电影链接: string;
  评分: string;
  评分人数: string;
  导演: string;
  主演: string;
  年份: string;
  国家: string;
  类型: string;
  一句话评价: string;
}

interface Tab {
  id: string;
  name: string;
  icon: string;
}

interface ProfileForm {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  bio: string;
}

interface PasswordForm {
  old_password: string;
  new_password: string;
  new_password2: string;
}

interface Settings {
  emailNotifications: boolean;
  personalizedRecommendations: boolean;
  publicFavorites: boolean;
  darkMode: boolean;
}

interface GenreStat {
  name: string;
  count: number;
}

interface YearStat {
  year: string;
  count: number;
  percentage: number;
}

export default defineComponent({
  name: "ProfileView",
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    const allMovies = ref<DoubanMovie[]>([]);

    // 标签页状态
    const tabs: Tab[] = [
      { id: "basic", name: "基本信息", icon: "📝" },
      { id: "password", name: "修改密码", icon: "🔒" },
      { id: "favorites", name: "收藏夹", icon: "❤️" },
      { id: "settings", name: "账户设置", icon: "⚙️" },
    ];
    const activeTab = ref("basic");

    // 用户信息
    const currentUser = computed(() => authStore.user);
    const userInitials = computed(() => {
      if (!currentUser.value) return "?";
      const firstName = currentUser.value.first_name || "";
      const lastName = currentUser.value.last_name || "";
      if (firstName || lastName) {
        return (firstName.charAt(0) + lastName.charAt(0)).toUpperCase();
      }
      return currentUser.value.username.charAt(0).toUpperCase();
    });

    // 头像相关状态
    const avatarPreview = ref<string | null>(null);
    const avatarFile = ref<File | null>(null);
    const avatarStyle = computed(() => {
      if (avatarPreview.value) {
        return { backgroundImage: `url(${avatarPreview.value})` };
      }
      // 生成基于用户名的颜色
      const colors = [
        "#667eea",
        "#764ba2",
        "#f56565",
        "#ed8936",
        "#ecc94b",
        "#48bb78",
        "#38b2ac",
      ];
      const colorIndex = currentUser.value?.username?.length || 0;
      const color = colors[colorIndex % colors.length];
      return { backgroundColor: color };
    });

    // 表单状态
    const profileForm = ref<ProfileForm>({
      username: "",
      email: "",
      first_name: "",
      last_name: "",
      bio: "",
    });

    const passwordForm = ref<PasswordForm>({
      old_password: "",
      new_password: "",
      new_password2: "",
    });

    const settings = ref<Settings>({
      emailNotifications: true,
      personalizedRecommendations: true,
      publicFavorites: false,
      darkMode: false,
    });

    // 加载状态
    const profileLoading = ref(false);
    const passwordLoading = ref(false);
    const favoritesLoading = ref(false);
    const settingsLoading = ref(false);

    // 收藏夹相关状态
    const favorites = ref<DoubanMovie[]>([]);
    const favoritesSortBy = ref("rating");

    // 计算属性
    const isProfileFormChanged = computed(() => {
      const original = currentUser.value;
      if (!original) return false;

      return (
        profileForm.value.username !== original.username ||
        profileForm.value.email !== original.email ||
        profileForm.value.first_name !== original.first_name ||
        profileForm.value.last_name !== original.last_name ||
        profileForm.value.bio !== (original.bio || "")
      );
    });

    const passwordsMatch = computed(() => {
      return (
        passwordForm.value.new_password === passwordForm.value.new_password2
      );
    });

    const passwordStrength = computed(() => {
      const password = passwordForm.value.new_password;
      if (!password) return 0;

      let strength = 0;
      if (password.length >= 8) strength += 25;
      if (/[a-z]/.test(password)) strength += 25;
      if (/[A-Z]/.test(password)) strength += 25;
      if (/[0-9]/.test(password)) strength += 25;

      return Math.min(strength, 100);
    });

    const passwordStrengthClass = computed(() => {
      const strength = passwordStrength.value;
      if (strength < 50) return "weak";
      if (strength < 75) return "medium";
      return "strong";
    });

    const passwordStrengthText = computed(() => {
      const strength = passwordStrength.value;
      if (strength < 50) return "弱";
      if (strength < 75) return "中等";
      return "强";
    });

    const isPasswordFormValid = computed(() => {
      return (
        passwordForm.value.old_password &&
        passwordForm.value.new_password &&
        passwordForm.value.new_password2 &&
        passwordsMatch.value &&
        passwordStrength.value >= 50
      );
    });

    const favoriteGenres = computed(() => {
      const genreSet = new Set<string>();
      favorites.value.forEach((movie) => {
        if (movie["类型"]) {
          const genres = movie["类型"].split(" ");
          genres.forEach((g) => genreSet.add(g.trim()));
        }
      });
      return Array.from(genreSet);
    });

    const averageFavoriteRating = computed(() => {
      if (favorites.value.length === 0) return 0;
      const sum = favorites.value.reduce((acc, movie) => {
        return acc + parseFloat(movie["评分"] || "0");
      }, 0);
      return sum / favorites.value.length;
    });

    const sortedFavorites = computed(() => {
      const sorted = [...favorites.value];
      switch (favoritesSortBy.value) {
        case "rating":
          return sorted.sort(
            (a, b) => parseFloat(b["评分"]) - parseFloat(a["评分"])
          );
        case "rating_asc":
          return sorted.sort(
            (a, b) => parseFloat(a["评分"]) - parseFloat(b["评分"])
          );
        case "year":
          return sorted.sort(
            (a, b) => (parseInt(b["年份"]) || 0) - (parseInt(a["年份"]) || 0)
          );
        case "year_asc":
          return sorted.sort(
            (a, b) => (parseInt(a["年份"]) || 0) - (parseInt(b["年份"]) || 0)
          );
        case "name":
          return sorted.sort((a, b) =>
            a["电影名字"].localeCompare(b["电影名字"])
          );
        default:
          return sorted;
      }
    });

    const topFavoriteGenres = computed<GenreStat[]>(() => {
      const genreCounts: Record<string, number> = {};
      favorites.value.forEach((movie) => {
        if (movie["类型"]) {
          const genres = movie["类型"].split(" ");
          genres.forEach((g) => {
            const genre = g.trim();
            genreCounts[genre] = (genreCounts[genre] || 0) + 1;
          });
        }
      });

      return Object.entries(genreCounts)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);
    });

    const favoriteYears = computed<YearStat[]>(() => {
      const yearCounts: Record<string, number> = {};
      favorites.value.forEach((movie) => {
        const year = movie["年份"];
        if (year) {
          yearCounts[year] = (yearCounts[year] || 0) + 1;
        }
      });

      const total = favorites.value.length;
      return Object.entries(yearCounts)
        .map(([year, count]) => ({
          year,
          count,
          percentage: Math.round((count / total) * 100),
        }))
        .sort((a, b) => parseInt(b.year) - parseInt(a.year))
        .slice(0, 5);
    });

    // 方法
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleDateString("zh-CN", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    };

    const handleAvatarUpload = (event: Event) => {
      const input = event.target as HTMLInputElement;
      if (input.files && input.files[0]) {
        const file = input.files[0];
        if (file.size > 5 * 1024 * 1024) {
          alert("头像文件大小不能超过5MB");
          return;
        }

        avatarFile.value = file;
        const reader = new FileReader();
        reader.onload = (e) => {
          avatarPreview.value = e.target?.result as string;
        };
        reader.readAsDataURL(file);
      }
    };

    const removeAvatar = () => {
      avatarPreview.value = null;
      avatarFile.value = null;
      const input = document.getElementById(
        "avatar-upload"
      ) as HTMLInputElement;
      if (input) input.value = "";
    };

    const resetProfileForm = () => {
      if (currentUser.value) {
        profileForm.value = {
          username: currentUser.value.username,
          email: currentUser.value.email,
          first_name: currentUser.value.first_name || "",
          last_name: currentUser.value.last_name || "",
          bio: currentUser.value.bio || "",
        };
      }
    };

    const updateProfile = async () => {
      if (!currentUser.value) return;

      profileLoading.value = true;
      try {
        await authStore.updateProfile(profileForm.value);
        alert("个人信息更新成功！");
      } catch (error) {
        console.error("更新个人信息失败:", error);
        alert("更新失败，请重试");
      } finally {
        profileLoading.value = false;
      }
    };

    const resetPasswordForm = () => {
      passwordForm.value = {
        old_password: "",
        new_password: "",
        new_password2: "",
      };
    };

    const changePassword = async () => {
      if (!isPasswordFormValid.value) return;

      passwordLoading.value = true;
      try {
        await authStore.changePassword(
          passwordForm.value.old_password,
          passwordForm.value.new_password,
          passwordForm.value.new_password2
        );
        alert("密码修改成功！");
        resetPasswordForm();
      } catch (error) {
        console.error("修改密码失败:", error);
        alert("修改失败，请检查当前密码是否正确");
      } finally {
        passwordLoading.value = false;
      }
    };

    const loadFavorites = () => {
      favoritesLoading.value = true;
      try {
        const saved = localStorage.getItem("movie_favorites");
        if (saved) {
          const favoriteUrls = JSON.parse(saved) as string[];
          favorites.value = allMovies.value.filter((movie) =>
            favoriteUrls.includes(movie["电影链接"])
          );
        }
      } catch (error) {
        console.error("加载收藏夹失败:", error);
      } finally {
        favoritesLoading.value = false;
      }
    };

    const sortFavorites = () => {
      // sortedFavorites computed property handles sorting
    };

    const removeFromFavorites = (movie: DoubanMovie) => {
      const saved = localStorage.getItem("movie_favorites");
      if (saved) {
        const favoriteUrls = JSON.parse(saved) as string[];
        const updated = favoriteUrls.filter((url) => url !== movie["电影链接"]);
        localStorage.setItem("movie_favorites", JSON.stringify(updated));
        loadFavorites();
        alert("已取消收藏");
      }
    };

    const clearAllFavorites = () => {
      if (confirm("确定要清空所有收藏吗？此操作不可撤销。")) {
        localStorage.removeItem("movie_favorites");
        favorites.value = [];
        alert("收藏夹已清空");
      }
    };

    const toggleDarkMode = () => {
      if (settings.value.darkMode) {
        document.documentElement.classList.add("dark-mode");
      } else {
        document.documentElement.classList.remove("dark-mode");
      }
    };

    const saveSettings = () => {
      settingsLoading.value = true;
      setTimeout(() => {
        localStorage.setItem("user_settings", JSON.stringify(settings.value));
        settingsLoading.value = false;
        alert("设置已保存");
      }, 500);
    };

    const resetSettings = () => {
      settings.value = {
        emailNotifications: true,
        personalizedRecommendations: true,
        publicFavorites: false,
        darkMode: false,
      };
      document.documentElement.classList.remove("dark-mode");
    };

    const exportData = () => {
      const data = {
        user: currentUser.value,
        favorites: favorites.value,
        settings: settings.value,
        exportDate: new Date().toISOString(),
      };

      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `movie_recommendation_data_${new Date().getTime()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      alert("数据导出成功！");
    };

    const deleteAccount = () => {
      if (
        confirm("确定要删除账户吗？此操作将永久删除您的所有数据，且不可恢复。")
      ) {
        alert("账户删除功能需要后端API支持");
        // 这里可以添加调用后端API删除账户的逻辑
      }
    };

    // 初始化
    const init = () => {
      allMovies.value = doubanData as DoubanMovie[];

      // 初始化表单数据
      if (currentUser.value) {
        resetProfileForm();
      }

      // 加载收藏夹
      loadFavorites();

      // 加载设置
      const savedSettings = localStorage.getItem("user_settings");
      if (savedSettings) {
        try {
          settings.value = JSON.parse(savedSettings);
          if (settings.value.darkMode) {
            document.documentElement.classList.add("dark-mode");
          }
        } catch (error) {
          console.error("加载设置失败:", error);
        }
      }
    };

    // 生命周期钩子
    onMounted(() => {
      init();
    });

    // 返回所有需要暴露给模板的属性和方法
    return {
      // 数据
      tabs,
      activeTab,
      currentUser,
      avatarStyle,
      avatarPreview,
      userInitials,
      profileForm,
      passwordForm,
      settings,
      favorites,
      favoritesSortBy,

      // 计算属性
      isProfileFormChanged,
      passwordsMatch,
      passwordStrength,
      passwordStrengthClass,
      passwordStrengthText,
      isPasswordFormValid,
      favoriteGenres,
      averageFavoriteRating,
      sortedFavorites,
      topFavoriteGenres,
      favoriteYears,

      // 加载状态
      profileLoading,
      passwordLoading,
      favoritesLoading,
      settingsLoading,

      // 方法
      formatDate,
      handleAvatarUpload,
      removeAvatar,
      resetProfileForm,
      updateProfile,
      resetPasswordForm,
      changePassword,
      sortFavorites,
      removeFromFavorites,
      clearAllFavorites,
      toggleDarkMode,
      saveSettings,
      resetSettings,
      exportData,
      deleteAccount,
    };
  },
});
</script>

<style scoped>
.profile-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.profile-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 15px;
}

.profile-header h1 {
  margin: 0;
  font-size: 2.8rem;
  font-weight: 700;
}

.subtitle {
  margin: 15px 0 0;
  font-size: 1.3rem;
  opacity: 0.9;
}

.profile-container {
  display: flex;
  gap: 30px;
  min-height: 600px;
}

/* 侧边栏样式 */
.profile-sidebar {
  flex: 0 0 300px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.avatar-section {
  text-align: center;
  margin-bottom: 20px;
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin: 0 auto 15px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.avatar-placeholder {
  font-size: 3rem;
  font-weight: 700;
  color: white;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.avatar-upload-btn {
  padding: 10px 15px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.3s;
}

.avatar-upload-btn:hover {
  background: #5a67d8;
}

.avatar-input {
  display: none;
}

.avatar-remove-btn {
  padding: 8px 12px;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.3s;
}

.avatar-remove-btn:hover {
  background: #c53030;
}

.user-info-summary {
  text-align: center;
}

.user-info-summary h3 {
  margin: 0 0 10px;
  color: #333;
  font-size: 1.5rem;
}

.user-email {
  color: #666;
  margin: 0 0 5px;
  font-size: 0.95rem;
}

.user-join-date {
  color: #888;
  font-size: 0.85rem;
  margin: 0;
}

.profile-nav {
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
  padding: 15px;
  border: none;
  background: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  color: #4a5568;
  transition: all 0.3s;
  text-align: left;
}

.nav-item:hover {
  background: #f7fafc;
  color: #667eea;
}

.nav-item.active {
  background: #667eea;
  color: white;
}

.nav-icon {
  font-size: 1.2rem;
}

.nav-text {
  flex: 1;
}

/* 右侧内容区域样式 */
.profile-content {
  flex: 1;
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.tab-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.tab-header h2 {
  margin: 0 0 10px;
  color: #333;
  font-size: 1.8rem;
}

.tab-description {
  color: #666;
  margin: 0;
  font-size: 1rem;
}

/* 表单样式 */
.profile-form,
.password-form {
  max-width: 800px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 600;
  color: #4a5568;
  font-size: 0.95rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 12px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-hint {
  color: #718096;
  font-size: 0.85rem;
  margin: 5px 0 0;
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 5px;
}

.char-count {
  font-size: 0.85rem;
  color: #718096;
}

/* 密码匹配指示器 */
.password-match {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 5px;
}

.match-icon {
  font-size: 1rem;
  font-weight: bold;
}

.match-icon.match {
  color: #48bb78;
}

.match-icon.mismatch {
  color: #e53e3e;
}

.match-text {
  font-size: 0.9rem;
}

.match-text.match {
  color: #48bb78;
}

.match-text.mismatch {
  color: #e53e3e;
}

/* 密码强度指示器 */
.password-strength {
  margin: 20px 0;
  padding: 15px;
  background: #f7fafc;
  border-radius: 8px;
}

.strength-label {
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 10px;
}

.strength-meter {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.strength-bar {
  height: 100%;
  transition: width 0.3s;
}

.strength-bar.weak {
  background: #e53e3e;
}

.strength-bar.medium {
  background: #ed8936;
}

.strength-bar.strong {
  background: #48bb78;
}

.strength-text {
  font-size: 0.9rem;
  font-weight: 600;
}

.strength-bar.weak + .strength-text {
  color: #e53e3e;
}

.strength-bar.medium + .strength-text {
  color: #ed8936;
}

.strength-bar.strong + .strength-text {
  color: #48bb78;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.primary-btn,
.secondary-btn,
.danger-btn {
  padding: 12px 25px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.primary-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.secondary-btn {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.secondary-btn:hover:not(:disabled) {
  background: #667eea;
  color: white;
}

.secondary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.danger-btn {
  background: #e53e3e;
  color: white;
}

.danger-btn:hover:not(:disabled) {
  background: #c53030;
}

.danger-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 收藏夹样式 */
.favorites-stats {
  display: flex;
  gap: 30px;
  margin-top: 20px;
}

.favorites-stats .stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.favorites-stats .stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 5px;
}

.favorites-stats .stat-label {
  color: #666;
  font-size: 0.9rem;
}

.loading-state {
  text-align: center;
  padding: 60px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.empty-state {
  text-align: center;
  padding: 60px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px;
  color: #333;
}

.empty-state p {
  color: #666;
  margin: 0 0 20px;
}

.browse-btn {
  display: inline-block;
  padding: 12px 25px;
  background: #667eea;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.3s;
}

.browse-btn:hover {
  background: #5a67d8;
}

.favorites-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding: 15px;
  background: #f7fafc;
  border-radius: 8px;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sort-controls label {
  font-weight: 600;
  color: #4a5568;
}

.sort-controls select {
  padding: 8px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.95rem;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.favorite-card {
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 20px;
  background: white;
  transition: transform 0.3s;
}

.favorite-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.favorite-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.favorite-header .movie-title {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
  flex: 1;
  margin-right: 15px;
}

.movie-rating {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #fef3c7;
  padding: 4px 10px;
  border-radius: 15px;
}

.rating-star {
  font-size: 1rem;
}

.rating-value {
  font-weight: 600;
  color: #d97706;
  font-size: 1rem;
}

.movie-meta {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.85rem;
}

.meta-label {
  color: #718096;
  font-weight: 500;
}

.meta-value {
  color: #4a5568;
  font-weight: 600;
}

.movie-quote {
  margin: 15px 0;
  padding: 10px;
  background: #f0f4ff;
  border-radius: 6px;
  border-left: 3px solid #667eea;
}

.quote-icon {
  margin-right: 8px;
  font-size: 1rem;
}

.quote-text {
  font-style: italic;
  color: #4a5568;
  font-size: 0.9rem;
  line-height: 1.4;
}

.favorite-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.small-btn {
  padding: 8px 15px;
  font-size: 0.85rem;
}

/* 收藏分析样式 */
.favorites-analysis {
  margin-top: 40px;
  padding: 25px;
  background: #f7fafc;
  border-radius: 10px;
}

.favorites-analysis h3 {
  margin: 0 0 20px;
  color: #333;
  font-size: 1.5rem;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.analysis-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.analysis-card h4 {
  margin: 0 0 15px;
  color: #333;
  font-size: 1.2rem;
}

.genre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.genre-tag {
  padding: 6px 12px;
  background: #667eea;
  color: white;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 500;
}

.year-distribution {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.year-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.year-label {
  width: 50px;
  font-size: 0.9rem;
  color: #4a5568;
  font-weight: 600;
}

.year-bar {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s;
}

.year-count {
  width: 50px;
  text-align: right;
  font-size: 0.85rem;
  color: #718096;
}

/* 设置样式 */
.settings-list {
  margin-bottom: 30px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info h4 {
  margin: 0 0 5px;
  color: #333;
  font-size: 1.1rem;
}

.setting-info p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 34px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #667eea;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.settings-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 40px;
}

/* 危险区域样式 */
.danger-zone {
  padding: 25px;
  background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
  border: 2px solid #fc8181;
  border-radius: 10px;
}

.danger-zone h3 {
  margin: 0 0 10px;
  color: #c53030;
  font-size: 1.5rem;
}

.danger-warning {
  color: #e53e3e;
  margin: 0 0 20px;
  font-size: 0.95rem;
}

.danger-actions {
  display: flex;
  gap: 15px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .profile-container {
    flex-direction: column;
  }

  .profile-sidebar {
    flex: none;
    width: 100%;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .profile-header h1 {
    font-size: 2.2rem;
  }

  .favorites-controls {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .sort-controls {
    flex-direction: column;
    align-items: flex-start;
  }

  .favorites-grid {
    grid-template-columns: 1fr;
  }

  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .danger-actions {
    flex-direction: column;
  }

  .form-actions,
  .settings-actions {
    flex-direction: column;
  }

  .primary-btn,
  .secondary-btn,
  .danger-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .profile-header {
    padding: 20px;
  }

  .profile-header h1 {
    font-size: 1.8rem;
  }

  .subtitle {
    font-size: 1.1rem;
  }

  .profile-content {
    padding: 20px;
  }

  .favorites-stats {
    flex-direction: column;
    gap: 15px;
  }

  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

/* 深色模式样式 */
:global(.dark-mode) .profile-view {
  background: #1a202c;
  color: #e2e8f0;
}

:global(.dark-mode) .profile-header {
  background: linear-gradient(135deg, #4c51bf 0%, #6b46c1 100%);
}

:global(.dark-mode) .user-card,
:global(.dark-mode) .profile-nav,
:global(.dark-mode) .profile-content,
:global(.dark-mode) .favorite-card,
:global(.dark-mode) .analysis-card {
  background: #2d3748;
  color: #e2e8f0;
}

:global(.dark-mode) .user-info-summary h3,
:global(.dark-mode) .tab-header h2,
:global(.dark-mode) .analysis-card h4,
:global(.dark-mode) .favorite-header .movie-title {
  color: #e2e8f0;
}

:global(.dark-mode) .user-email,
:global(.dark-mode) .user-join-date,
:global(.dark-mode) .tab-description,
:global(.dark-mode) .form-hint,
:global(.dark-mode) .meta-label,
:global(.dark-mode) .quote-text {
  color: #a0aec0;
}

:global(.dark-mode) .form-group input,
:global(.dark-mode) .form-group textarea,
:global(.dark-mode) .form-group select {
  background: #4a5568;
  border-color: #718096;
  color: #e2e8f0;
}

:global(.dark-mode) .form-group input:focus,
:global(.dark-mode) .form-group textarea:focus,
:global(.dark-mode) .form-group select:focus {
  border-color: #667eea;
}

:global(.dark-mode) .nav-item:hover {
  background: #4a5568;
}

:global(.dark-mode) .favorites-controls,
:global(.dark-mode) .password-strength,
:global(.dark-mode) .favorites-analysis {
  background: #4a5568;
}

:global(.dark-mode) .movie-quote {
  background: #4a5568;
  border-left-color: #667eea;
}

:global(.dark-mode) .year-bar {
  background: #4a5568;
}

:global(.dark-mode) .danger-zone {
  background: linear-gradient(135deg, #742a2a 0%, #9b2c2c 100%);
  border-color: #c53030;
}
</style>
