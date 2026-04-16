<template>
  <div class="profile-view">
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">个人中心</div>
        <h1 class="hero-title">👤 用户管理与画像中心</h1>
        <p class="hero-subtitle">
          管理账户资料、安全设置、兴趣偏好、用户画像与收藏内容，让推荐结果更贴合你的观影习惯。
        </p>

        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-number">{{ favorites.length }}</div>
            <div class="stat-label">收藏电影</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">
              {{ profileData.favorite_genres.length }}
            </div>
            <div class="stat-label">偏好类型</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">
              {{ profileData.onboarding_completed ? "已完成" : "未完成" }}
            </div>
            <div class="stat-label">冷启动偏好</div>
          </div>
        </div>
      </div>

      <div class="hero-actions">
        <button
          class="header-btn"
          @click="reloadAllData"
          :disabled="profileLoading || preferenceLoading"
        >
          {{
            profileLoading || preferenceLoading ? "刷新中..." : "🔄 刷新数据"
          }}
        </button>
      </div>
    </section>

    <div class="profile-container">
      <!-- 左侧 -->
      <aside class="profile-sidebar">
        <div class="panel-card user-card">
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
              <label for="avatar-upload" class="small-primary-btn">
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
                class="small-danger-btn"
              >
                ❌ 移除头像
              </button>
            </div>
          </div>

          <div class="user-info-summary">
            <h3>{{ currentUser?.username || "用户" }}</h3>
            <p class="user-email">{{ currentUser?.email || "未设置邮箱" }}</p>
            <p class="user-join-date" v-if="currentUser?.date_joined">
              注册时间：{{ formatDate(currentUser.date_joined) }}
            </p>
          </div>

          <div class="summary-tags">
            <span class="summary-chip" v-if="profileData.onboarding_completed">
              已完成兴趣初始化
            </span>
            <span class="summary-chip" v-else>未设置兴趣偏好</span>
            <span class="summary-chip">
              收藏 {{ favorites.length }} 部电影
            </span>
          </div>
        </div>

        <div class="panel-card profile-quick-card">
          <h3 class="card-title">🎯 画像速览</h3>
          <div class="quick-block">
            <div class="quick-label">偏好类型</div>
            <div class="chip-group">
              <span
                v-for="item in profileData.favorite_genres.slice(0, 4)"
                :key="item"
                class="info-chip"
              >
                {{ item }}
              </span>
              <span
                v-if="profileData.favorite_genres.length === 0"
                class="empty-chip"
              >
                暂无
              </span>
            </div>
          </div>

          <div class="quick-block">
            <div class="quick-label">偏好国家/地区</div>
            <div class="chip-group">
              <span
                v-for="item in profileData.favorite_countries.slice(0, 4)"
                :key="item"
                class="info-chip"
              >
                {{ item }}
              </span>
              <span
                v-if="profileData.favorite_countries.length === 0"
                class="empty-chip"
              >
                暂无
              </span>
            </div>
          </div>

          <div class="quick-block">
            <div class="quick-label">关键词</div>
            <div class="chip-group">
              <span
                v-for="item in profileData.favorite_keywords.slice(0, 4)"
                :key="item"
                class="info-chip muted"
              >
                {{ item }}
              </span>
              <span
                v-if="profileData.favorite_keywords.length === 0"
                class="empty-chip"
              >
                暂无
              </span>
            </div>
          </div>
        </div>

        <div class="panel-card nav-card">
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
      </aside>

      <!-- 右侧 -->
      <section class="profile-content panel-card">
        <!-- 基本信息 -->
        <div v-if="activeTab === 'basic'" class="tab-content">
          <div class="tab-header">
            <h2>📝 基本信息</h2>
            <p class="tab-description">更新你的账户资料与个人简介</p>
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
                <span class="char-count">
                  {{ profileForm.bio?.length || 0 }}/500
                </span>
                <p class="form-hint">最多 500 个字符</p>
              </div>
            </div>

            <div class="form-actions">
              <button
                type="button"
                @click="resetProfileForm"
                class="secondary-btn"
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

        <!-- 修改密码 -->
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
              <p class="form-hint">密码至少 8 位，建议包含大小写字母和数字</p>
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
              <div class="strength-label">密码强度</div>
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

        <!-- 兴趣偏好 -->
        <div v-else-if="activeTab === 'preferences'" class="tab-content">
          <div class="tab-header">
            <h2>🎯 兴趣偏好</h2>
            <p class="tab-description">
              这些偏好会影响你的冷启动推荐结果，也会参与个性化推荐解释。
            </p>
          </div>

          <div class="two-column-layout">
            <div class="sub-card">
              <h3 class="section-title">喜欢的电影类型</h3>
              <div class="chip-selector">
                <button
                  v-for="genre in genreOptions"
                  :key="genre"
                  @click="
                    togglePreferenceItem(preferenceForm.favorite_genres, genre)
                  "
                  :class="[
                    'selector-chip',
                    { active: preferenceForm.favorite_genres.includes(genre) },
                  ]"
                >
                  {{ genre }}
                </button>
              </div>
            </div>

            <div class="sub-card">
              <h3 class="section-title">喜欢的国家/地区</h3>
              <div class="chip-selector">
                <button
                  v-for="country in countryOptions"
                  :key="country"
                  @click="
                    togglePreferenceItem(
                      preferenceForm.favorite_countries,
                      country
                    )
                  "
                  :class="[
                    'selector-chip',
                    {
                      active:
                        preferenceForm.favorite_countries.includes(country),
                    },
                  ]"
                >
                  {{ country }}
                </button>
              </div>
            </div>
          </div>

          <div class="sub-card">
            <h3 class="section-title">兴趣关键词</h3>
            <div class="chip-selector">
              <button
                v-for="keyword in keywordOptions"
                :key="keyword"
                @click="
                  togglePreferenceItem(
                    preferenceForm.favorite_keywords,
                    keyword
                  )
                "
                :class="[
                  'selector-chip',
                  {
                    active: preferenceForm.favorite_keywords.includes(keyword),
                  },
                ]"
              >
                {{ keyword }}
              </button>
            </div>
          </div>

          <div class="sub-card">
            <h3 class="section-title">偏好年份区间</h3>
            <div class="year-range-grid">
              <div class="form-group">
                <label>开始年份</label>
                <input
                  v-model.number="preferenceForm.favorite_years.min"
                  type="number"
                  min="1900"
                  max="2100"
                  placeholder="如 2000"
                />
              </div>
              <div class="form-group">
                <label>结束年份</label>
                <input
                  v-model.number="preferenceForm.favorite_years.max"
                  type="number"
                  min="1900"
                  max="2100"
                  placeholder="如 2024"
                />
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button
              type="button"
              class="secondary-btn"
              @click="loadOnboardingPreferences"
            >
              重载偏好
            </button>
            <button
              type="button"
              class="primary-btn"
              @click="saveOnboardingPreferences"
              :disabled="preferenceLoading"
            >
              {{ preferenceLoading ? "保存中..." : "保存兴趣偏好" }}
            </button>
          </div>
        </div>

        <!-- 用户画像 -->
        <div v-else-if="activeTab === 'profile'" class="tab-content">
          <div class="tab-header">
            <h2>🧠 用户画像</h2>
            <p class="tab-description">
              用户画像会根据你的兴趣偏好和评分行为动态更新，用于个性化推荐与推荐理由生成。
            </p>
          </div>

          <div class="profile-overview-grid">
            <div class="sub-card">
              <h3 class="section-title">偏好类型</h3>
              <div class="chip-group">
                <span
                  v-for="item in profileData.favorite_genres"
                  :key="item"
                  class="info-chip"
                >
                  {{ item }}
                </span>
                <span
                  v-if="profileData.favorite_genres.length === 0"
                  class="empty-chip"
                >
                  暂无数据
                </span>
              </div>
            </div>

            <div class="sub-card">
              <h3 class="section-title">偏好国家/地区</h3>
              <div class="chip-group">
                <span
                  v-for="item in profileData.favorite_countries"
                  :key="item"
                  class="info-chip"
                >
                  {{ item }}
                </span>
                <span
                  v-if="profileData.favorite_countries.length === 0"
                  class="empty-chip"
                >
                  暂无数据
                </span>
              </div>
            </div>

            <div class="sub-card">
              <h3 class="section-title">偏好关键词</h3>
              <div class="chip-group">
                <span
                  v-for="item in profileData.favorite_keywords"
                  :key="item"
                  class="info-chip muted"
                >
                  {{ item }}
                </span>
                <span
                  v-if="profileData.favorite_keywords.length === 0"
                  class="empty-chip"
                >
                  暂无数据
                </span>
              </div>
            </div>

            <div class="sub-card">
              <h3 class="section-title">偏好年份</h3>
              <div class="year-range-display">
                <template
                  v-if="
                    profileData.favorite_years &&
                    profileData.favorite_years.min &&
                    profileData.favorite_years.max
                  "
                >
                  {{ profileData.favorite_years.min }} -
                  {{ profileData.favorite_years.max }}
                </template>
                <template v-else>暂无数据</template>
              </div>
            </div>
          </div>

          <div class="sub-card summary-card">
            <h3 class="section-title">画像总结</h3>
            <p class="profile-summary-text">
              {{
                profileData.profile_summary ||
                "当前暂无画像总结，请先设置偏好或进行评分。"
              }}
            </p>
            <div class="meta-row">
              <span class="meta-badge">
                冷启动状态：{{
                  profileData.onboarding_completed ? "已完成" : "未完成"
                }}
              </span>
              <span class="meta-badge" v-if="profileData.updated_at">
                更新时间：{{ formatDateTime(profileData.updated_at) }}
              </span>
            </div>
          </div>

          <div class="form-actions">
            <button
              type="button"
              class="secondary-btn"
              @click="loadUserProfile"
            >
              刷新画像
            </button>
            <button
              type="button"
              class="primary-btn"
              @click="refreshUserProfile"
              :disabled="profileRefreshLoading"
            >
              {{ profileRefreshLoading ? "生成中..." : "根据评分重新生成画像" }}
            </button>
          </div>
        </div>

        <!-- 收藏夹 -->
        <div v-else-if="activeTab === 'favorites'" class="tab-content">
          <div class="tab-header">
            <h2>❤️ 我的收藏夹</h2>
            <p class="tab-description">你收藏的电影列表与收藏偏好分析</p>

            <div class="favorites-stats">
              <span class="stat-inline">
                <span class="stat-number small">{{ favorites.length }}</span>
                <span class="stat-label dark">部收藏</span>
              </span>
              <span class="stat-inline">
                <span class="stat-number small">{{
                  favoriteGenres.length
                }}</span>
                <span class="stat-label dark">种类型</span>
              </span>
              <span class="stat-inline">
                <span class="stat-number small">
                  {{ averageFavoriteRating.toFixed(1) }}
                </span>
                <span class="stat-label dark">平均评分</span>
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
            <p>你还没有收藏任何电影</p>
            <router-link to="/douban" class="browse-btn">
              去浏览电影
            </router-link>
          </div>

          <div v-else class="favorites-content">
            <div class="favorites-controls">
              <div class="sort-controls">
                <label>排序方式</label>
                <select v-model="favoritesSortBy">
                  <option value="rating">评分从高到低</option>
                  <option value="rating_asc">评分从低到高</option>
                  <option value="year">年份从新到旧</option>
                  <option value="year_asc">年份从旧到新</option>
                  <option value="name">电影名称 A-Z</option>
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
                  <span class="meta-item">{{ movie["年份"] }}</span>
                  <span class="meta-item">{{ movie["国家"] }}</span>
                  <span class="meta-item">{{ movie["类型"] }}</span>
                </div>

                <div class="movie-quote" v-if="movie['一句话评价']">
                  <span class="quote-text">{{ movie["一句话评价"] }}</span>
                </div>

                <div class="favorite-actions">
                  <a
                    :href="movie['电影链接']"
                    target="_blank"
                    class="action-btn link-btn"
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

            <div class="favorites-analysis">
              <h3 class="section-title">📊 收藏分析</h3>
              <div class="analysis-grid">
                <div class="sub-card">
                  <h4>最常收藏的类型</h4>
                  <div class="chip-group">
                    <span
                      v-for="genre in topFavoriteGenres"
                      :key="genre.name"
                      class="info-chip"
                    >
                      {{ genre.name }}（{{ genre.count }}）
                    </span>
                  </div>
                </div>

                <div class="sub-card">
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
                      <span class="year-count">{{ year.count }} 部</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 账户设置 -->
        <div v-else-if="activeTab === 'settings'" class="tab-content">
          <div class="tab-header">
            <h2>⚙️ 账户设置</h2>
            <p class="tab-description">管理你的账户偏好与功能开关</p>
          </div>

          <div class="settings-list">
            <div class="setting-item">
              <div class="setting-info">
                <h4>邮箱通知</h4>
                <p>接收系统通知和推荐邮件</p>
              </div>
              <label class="switch">
                <input type="checkbox" v-model="settings.emailNotifications" />
                <span class="slider"></span>
              </label>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h4>个性化推荐</h4>
                <p>基于你的观看历史和偏好提供个性化推荐</p>
              </div>
              <label class="switch">
                <input
                  type="checkbox"
                  v-model="settings.personalizedRecommendations"
                />
                <span class="slider"></span>
              </label>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h4>公开收藏夹</h4>
                <p>允许其他用户查看你的收藏内容</p>
              </div>
              <label class="switch">
                <input type="checkbox" v-model="settings.publicFavorites" />
                <span class="slider"></span>
              </label>
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
            <p class="danger-warning">以下操作不可撤销，请谨慎执行。</p>

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
      </section>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import axios from "axios";
import doubanData from "../data/豆瓣电影TOP250.json";

const API_BASE_URL = "http://localhost:8000/api";

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

interface UserProfileData {
  favorite_genres: string[];
  favorite_countries: string[];
  favorite_years: { min?: number; max?: number };
  favorite_keywords: string[];
  onboarding_completed: boolean;
  profile_summary: string;
  updated_at: string;
}

interface PreferenceForm {
  favorite_genres: string[];
  favorite_countries: string[];
  favorite_keywords: string[];
  favorite_years: { min?: number; max?: number };
}

export default defineComponent({
  name: "ProfileView",
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    const allMovies = ref<DoubanMovie[]>([]);

    const tabs: Tab[] = [
      { id: "basic", name: "基本信息", icon: "📝" },
      { id: "password", name: "修改密码", icon: "🔒" },
      { id: "preferences", name: "兴趣偏好", icon: "🎯" },
      { id: "profile", name: "用户画像", icon: "🧠" },
      { id: "favorites", name: "收藏夹", icon: "❤️" },
      { id: "settings", name: "账户设置", icon: "⚙️" },
    ];

    const activeTab = ref("basic");

    const genreOptions = [
      "剧情",
      "喜剧",
      "爱情",
      "科幻",
      "悬疑",
      "犯罪",
      "动作",
      "冒险",
      "动画",
      "战争",
      "家庭",
      "奇幻",
      "历史",
      "音乐",
      "传记",
    ];

    const countryOptions = [
      "美国",
      "英国",
      "中国大陆",
      "中国香港",
      "日本",
      "韩国",
      "法国",
      "德国",
      "意大利",
      "印度",
    ];

    const keywordOptions = [
      "高分",
      "烧脑",
      "温暖",
      "治愈",
      "经典",
      "悬疑",
      "热血",
      "家庭",
      "成长",
      "史诗",
      "黑色幽默",
      "周末",
      "轻松",
      "不压抑",
    ];

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

    const avatarPreview = ref<string | null>(null);
    const avatarFile = ref<File | null>(null);

    const avatarStyle = computed(() => {
      if (avatarPreview.value) {
        return { backgroundImage: `url(${avatarPreview.value})` };
      }
      const colors = [
        "#667eea",
        "#764ba2",
        "#f56565",
        "#ed8936",
        "#48bb78",
        "#38b2ac",
      ];
      const colorIndex = currentUser.value?.username?.length || 0;
      const color = colors[colorIndex % colors.length];
      return { backgroundColor: color };
    });

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
    });

    const profileData = ref<UserProfileData>({
      favorite_genres: [],
      favorite_countries: [],
      favorite_years: {},
      favorite_keywords: [],
      onboarding_completed: false,
      profile_summary: "",
      updated_at: "",
    });

    const preferenceForm = ref<PreferenceForm>({
      favorite_genres: [],
      favorite_countries: [],
      favorite_keywords: [],
      favorite_years: {},
    });

    const profileLoading = ref(false);
    const passwordLoading = ref(false);
    const favoritesLoading = ref(false);
    const settingsLoading = ref(false);
    const preferenceLoading = ref(false);
    const profileRefreshLoading = ref(false);

    const favorites = ref<DoubanMovie[]>([]);
    const favoritesSortBy = ref("rating");

    const isProfileFormChanged = computed(() => {
      const original = currentUser.value;
      if (!original) return false;

      return (
        profileForm.value.username !== original.username ||
        profileForm.value.email !== original.email ||
        profileForm.value.first_name !== (original.first_name || "") ||
        profileForm.value.last_name !== (original.last_name || "") ||
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
          movie["类型"]
            .split(/[ /、,，]+/)
            .filter(Boolean)
            .forEach((g) => genreSet.add(g.trim()));
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
          movie["类型"]
            .split(/[ /、,，]+/)
            .filter(Boolean)
            .forEach((g) => {
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

      const total = favorites.value.length || 1;
      return Object.entries(yearCounts)
        .map(([year, count]) => ({
          year,
          count,
          percentage: Math.round((count / total) * 100),
        }))
        .sort((a, b) => parseInt(b.year) - parseInt(a.year))
        .slice(0, 5);
    });

    const authHeaders = computed(() => ({
      Authorization: `Token ${authStore.token}`,
    }));

    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleDateString("zh-CN", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    };

    const formatDateTime = (dateString: string) => {
      return new Date(dateString).toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    const togglePreferenceItem = (targetList: string[], value: string) => {
      const index = targetList.indexOf(value);
      if (index >= 0) {
        targetList.splice(index, 1);
      } else {
        targetList.push(value);
      }
    };

    const handleAvatarUpload = async (event: Event) => {
      const input = event.target as HTMLInputElement;
      if (input.files && input.files[0]) {
        const file = input.files[0];
        if (file.size > 5 * 1024 * 1024) {
          alert("头像文件大小不能超过5MB");
          return;
        }

        avatarFile.value = file;

        const formData = new FormData();
        formData.append("avatar", file);

        try {
          const response = await axios.put(
            `${API_BASE_URL}/auth/profile/`,
            formData,
            {
              headers: {
                ...authHeaders.value,
                "Content-Type": "multipart/form-data",
              },
            }
          );

          authStore.user = response.data;
          localStorage.setItem("user", JSON.stringify(response.data));

          const reader = new FileReader();
          reader.onload = (e) => {
            avatarPreview.value = e.target?.result as string;
          };
          reader.readAsDataURL(file);

          alert("头像上传成功！");
        } catch (error) {
          console.error("头像上传失败:", error);
          alert("头像上传失败，请重试");
        }
      }
    };

    const removeAvatar = async () => {
      if (!confirm("确定要移除头像吗？")) return;

      try {
        const response = await axios.put(
          `${API_BASE_URL}/auth/profile/`,
          { avatar: null },
          {
            headers: authHeaders.value,
          }
        );

        authStore.user = response.data;
        localStorage.setItem("user", JSON.stringify(response.data));

        avatarPreview.value = null;
        avatarFile.value = null;
        const input = document.getElementById(
          "avatar-upload"
        ) as HTMLInputElement;
        if (input) input.value = "";

        alert("头像已移除！");
      } catch (error) {
        console.error("移除头像失败:", error);
        alert("移除头像失败，请重试");
      }
    };

    const resetProfileForm = () => {
      if (currentUser.value) {
        profileForm.value = {
          username: currentUser.value.username || "",
          email: currentUser.value.email || "",
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
        } else {
          favorites.value = [];
        }
      } catch (error) {
        console.error("加载收藏夹失败:", error);
        favorites.value = [];
      } finally {
        favoritesLoading.value = false;
      }
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
      if (!confirm("确定要清空所有收藏吗？此操作不可撤销。")) return;
      localStorage.removeItem("movie_favorites");
      favorites.value = [];
      alert("收藏夹已清空");
    };

    const loadOnboardingPreferences = async () => {
      if (!authStore.token) return;

      preferenceLoading.value = true;
      try {
        const response = await axios.get(
          `${API_BASE_URL}/onboarding-preferences/`,
          {
            headers: authHeaders.value,
          }
        );

        const data = response.data || {};
        preferenceForm.value = {
          favorite_genres: data.favorite_genres || [],
          favorite_countries: data.favorite_countries || [],
          favorite_keywords: data.favorite_keywords || [],
          favorite_years: data.favorite_years || {},
        };
      } catch (error) {
        console.error("加载兴趣偏好失败:", error);
      } finally {
        preferenceLoading.value = false;
      }
    };

    const saveOnboardingPreferences = async () => {
      if (!authStore.token) return;

      preferenceLoading.value = true;
      try {
        await axios.post(
          `${API_BASE_URL}/onboarding-preferences/`,
          preferenceForm.value,
          {
            headers: {
              ...authHeaders.value,
              "Content-Type": "application/json",
            },
          }
        );

        alert("兴趣偏好保存成功！");
        await loadOnboardingPreferences();
        await loadUserProfile();
      } catch (error) {
        console.error("保存兴趣偏好失败:", error);
        alert("保存兴趣偏好失败，请重试");
      } finally {
        preferenceLoading.value = false;
      }
    };

    const loadUserProfile = async () => {
      if (!authStore.token) return;

      try {
        const response = await axios.get(`${API_BASE_URL}/user-profile/`, {
          headers: authHeaders.value,
        });

        profileData.value = {
          favorite_genres: response.data.favorite_genres || [],
          favorite_countries: response.data.favorite_countries || [],
          favorite_years: response.data.favorite_years || {},
          favorite_keywords: response.data.favorite_keywords || [],
          onboarding_completed: response.data.onboarding_completed || false,
          profile_summary: response.data.profile_summary || "",
          updated_at: response.data.updated_at || "",
        };
      } catch (error) {
        console.error("加载用户画像失败:", error);
      }
    };

    const refreshUserProfile = async () => {
      if (!authStore.token) return;

      profileRefreshLoading.value = true;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/user-profile/`,
          {},
          {
            headers: authHeaders.value,
          }
        );

        const data = response.data.profile || response.data || {};
        profileData.value = {
          favorite_genres: data.favorite_genres || [],
          favorite_countries: data.favorite_countries || [],
          favorite_years: data.favorite_years || {},
          favorite_keywords: data.favorite_keywords || [],
          onboarding_completed: data.onboarding_completed || false,
          profile_summary: data.profile_summary || "",
          updated_at: data.updated_at || "",
        };

        alert("用户画像已重新生成！");
      } catch (error) {
        console.error("重新生成用户画像失败:", error);
        alert("重新生成画像失败，请重试");
      } finally {
        profileRefreshLoading.value = false;
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
      };
    };

    const exportData = () => {
      const data = {
        user: currentUser.value,
        favorites: favorites.value,
        settings: settings.value,
        profile: profileData.value,
        preferences: preferenceForm.value,
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
        alert("账户删除功能需要后端 API 支持");
      }
    };

    const reloadAllData = async () => {
      await Promise.all([loadOnboardingPreferences(), loadUserProfile()]);
      loadFavorites();
    };

    const init = async () => {
      allMovies.value = doubanData as DoubanMovie[];

      if (currentUser.value) {
        resetProfileForm();
        if (currentUser.value.avatar_url) {
          avatarPreview.value = currentUser.value.avatar_url;
        }
      }

      loadFavorites();

      const savedSettings = localStorage.getItem("user_settings");
      if (savedSettings) {
        try {
          settings.value = JSON.parse(savedSettings);
        } catch (error) {
          console.error("加载设置失败:", error);
        }
      }

      if (authStore.token) {
        await loadOnboardingPreferences();
        await loadUserProfile();
      }
    };

    onMounted(() => {
      init();
    });

    return {
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
      profileData,
      preferenceForm,
      genreOptions,
      countryOptions,
      keywordOptions,
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
      profileLoading,
      passwordLoading,
      favoritesLoading,
      settingsLoading,
      preferenceLoading,
      profileRefreshLoading,
      formatDate,
      formatDateTime,
      handleAvatarUpload,
      removeAvatar,
      resetProfileForm,
      updateProfile,
      resetPasswordForm,
      changePassword,
      removeFromFavorites,
      clearAllFavorites,
      saveSettings,
      resetSettings,
      exportData,
      deleteAccount,
      loadOnboardingPreferences,
      saveOnboardingPreferences,
      loadUserProfile,
      refreshUserProfile,
      reloadAllData,
      togglePreferenceItem,
      router,
    };
  },
});
</script>

<style scoped>
.profile-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-section {
  background: var(--bg-hero);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  padding: 36px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
}

.hero-content {
  flex: 1;
}

.hero-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.16);
  font-size: 0.9rem;
  margin-bottom: 16px;
}

.hero-title {
  margin: 0 0 12px;
  font-size: 2.3rem;
  font-weight: 800;
  color: #fff;
}

.hero-subtitle {
  margin: 0 0 24px;
  font-size: 1.05rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.92);
  max-width: 760px;
}

.hero-stats {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
}

.stat-item {
  min-width: 120px;
  padding: 16px 18px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 800;
  color: #fff;
}

.stat-number.small {
  font-size: 1.4rem;
  color: var(--primary);
}

.stat-label {
  margin-top: 6px;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.88);
}

.stat-label.dark {
  color: var(--text-secondary);
}

.hero-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.header-btn {
  border: none;
  border-radius: var(--radius-sm);
  padding: 12px 18px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  transition: all var(--transition-fast);
}

.header-btn:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.2);
}

.header-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.profile-container {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}

.panel-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
}

.profile-sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-card,
.profile-quick-card,
.nav-card {
  padding: 20px;
}

.profile-content {
  padding: 28px;
}

.avatar-section {
  text-align: center;
  margin-bottom: 18px;
}

.avatar-preview {
  width: 110px;
  height: 110px;
  border-radius: 50%;
  margin: 0 auto 14px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid rgba(255, 255, 255, 0.9);
  box-shadow: var(--panel-shadow);
}

.avatar-placeholder {
  font-size: 2.6rem;
  font-weight: 800;
  color: #fff;
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

.avatar-input {
  display: none;
}

.small-primary-btn,
.small-danger-btn {
  border: none;
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: center;
}

.small-primary-btn {
  background: var(--primary-gradient);
  color: #fff;
}

.small-danger-btn {
  background: #ef4444;
  color: #fff;
}

.user-info-summary {
  text-align: center;
}

.user-info-summary h3 {
  margin: 0 0 8px;
  color: var(--text-primary);
  font-size: 1.35rem;
}

.user-email,
.user-join-date {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.92rem;
}

.user-join-date {
  margin-top: 6px;
}

.summary-tags {
  margin-top: 18px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.summary-chip {
  padding: 6px 10px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.card-title,
.section-title {
  margin: 0 0 14px;
  color: var(--text-primary);
}

.quick-block {
  margin-bottom: 16px;
}

.quick-block:last-child {
  margin-bottom: 0;
}

.quick-label {
  margin-bottom: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.profile-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 13px 14px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.96rem;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  text-align: left;
}

.nav-item:hover {
  background: var(--nav-hover-bg);
  color: var(--primary);
}

.nav-item.active {
  background: var(--primary-gradient);
  color: #fff;
}

.tab-header {
  margin-bottom: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--panel-border);
}

.tab-header h2 {
  margin: 0 0 8px;
  color: var(--text-primary);
  font-size: 1.7rem;
}

.tab-description {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.profile-form,
.password-form {
  max-width: 920px;
}

.form-grid,
.year-range-grid,
.two-column-layout,
.analysis-grid,
.profile-overview-grid {
  display: grid;
  gap: 20px;
}

.form-grid,
.two-column-layout,
.analysis-grid,
.profile-overview-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.year-range-grid {
  grid-template-columns: repeat(2, minmax(180px, 1fr));
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
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 12px 14px;
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
  font-size: 0.98rem;
  transition: all var(--transition-fast);
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--input-focus-border);
}

.form-group textarea {
  resize: vertical;
  min-height: 110px;
}

.form-hint {
  color: var(--text-muted);
  font-size: 0.84rem;
  margin: 0;
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.char-count {
  font-size: 0.84rem;
  color: var(--text-muted);
}

.password-match {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.match-icon,
.match-text {
  font-size: 0.9rem;
  font-weight: 600;
}

.match-icon.match,
.match-text.match {
  color: #22c55e;
}

.match-icon.mismatch,
.match-text.mismatch {
  color: #ef4444;
}

.password-strength,
.sub-card,
.favorites-analysis,
.danger-zone {
  padding: 18px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
}

.strength-label {
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.strength-meter,
.year-bar {
  height: 8px;
  background: var(--nav-hover-bg);
  border-radius: 999px;
  overflow: hidden;
}

.strength-bar,
.bar-fill {
  height: 100%;
  transition: width 0.3s;
}

.strength-bar.weak {
  background: #ef4444;
}

.strength-bar.medium {
  background: #f59e0b;
}

.strength-bar.strong {
  background: #22c55e;
}

.strength-text {
  margin-top: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.form-actions,
.settings-actions,
.danger-actions,
.favorite-actions,
.favorites-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.form-actions,
.settings-actions {
  margin-top: 24px;
}

.primary-btn,
.secondary-btn,
.danger-btn,
.action-btn,
.browse-btn {
  border: none;
  border-radius: var(--radius-sm);
  padding: 11px 18px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.primary-btn {
  background: var(--primary-gradient);
  color: #fff;
}

.secondary-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.danger-btn {
  background: #ef4444;
  color: #fff;
}

.primary-btn:hover,
.secondary-btn:hover,
.danger-btn:hover,
.action-btn:hover,
.browse-btn:hover {
  transform: translateY(-1px);
}

.primary-btn:disabled,
.secondary-btn:disabled,
.danger-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
}

.chip-group,
.chip-selector {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.info-chip,
.empty-chip,
.selector-chip,
.meta-badge {
  padding: 7px 12px;
  border-radius: var(--radius-full);
  font-size: 0.88rem;
}

.info-chip {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.info-chip.muted {
  color: var(--text-secondary);
}

.empty-chip {
  background: var(--nav-hover-bg);
  color: var(--text-muted);
}

.selector-chip {
  border: 1px solid var(--panel-border);
  background: var(--panel-bg);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.selector-chip.active {
  background: var(--primary-gradient);
  color: #fff;
  border-color: transparent;
}

.profile-summary-text {
  margin: 0 0 14px;
  line-height: 1.8;
  color: var(--text-primary);
}

.meta-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.meta-badge {
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
}

.year-range-display {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.favorites-stats {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  margin-top: 18px;
}

.stat-inline {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 48px 24px;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 14px;
}

.spinner {
  width: 46px;
  height: 46px;
  border: 4px solid rgba(102, 126, 234, 0.12);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 18px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.favorites-controls {
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sort-controls label {
  font-weight: 700;
  color: var(--text-secondary);
}

.sort-controls select {
  padding: 10px 12px;
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
  margin-bottom: 28px;
}

.favorite-card {
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  padding: 18px;
  background: var(--panel-bg);
  transition: all var(--transition-fast);
}

.favorite-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--panel-shadow);
}

.favorite-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
  margin-bottom: 12px;
}

.favorite-header .movie-title {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.movie-rating {
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(245, 158, 11, 0.16);
  padding: 5px 10px;
  border-radius: var(--radius-full);
}

.rating-value {
  font-weight: 700;
  color: #d97706;
}

.movie-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.meta-item {
  padding: 5px 8px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.movie-quote {
  margin: 12px 0 14px;
  padding: 12px;
  border-radius: var(--radius-sm);
  background: var(--primary-bg);
  border-left: 3px solid #667eea;
}

.quote-text {
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 0.92rem;
}

.link-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.small-btn {
  padding: 10px 14px;
  font-size: 0.88rem;
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
  width: 52px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 700;
}

.bar-fill {
  background: var(--primary-gradient);
}

.year-count {
  width: 52px;
  text-align: right;
  font-size: 0.84rem;
  color: var(--text-muted);
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.setting-item {
  padding: 18px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
}

.setting-info h4 {
  margin: 0 0 6px;
  color: var(--text-primary);
}

.setting-info p {
  margin: 0;
  color: var(--text-secondary);
}

.switch {
  position: relative;
  display: inline-block;
  width: 58px;
  height: 32px;
  min-width: 58px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  inset: 0;
  background: #cbd5e1;
  border-radius: 999px;
  transition: 0.3s;
  cursor: pointer;
}

.slider::before {
  content: "";
  position: absolute;
  width: 24px;
  height: 24px;
  left: 4px;
  top: 4px;
  background: #fff;
  border-radius: 50%;
  transition: 0.3s;
}

input:checked + .slider {
  background: #667eea;
}

input:checked + .slider::before {
  transform: translateX(26px);
}

.danger-zone {
  margin-top: 30px;
  background: linear-gradient(
    135deg,
    rgba(254, 226, 226, 0.75),
    rgba(254, 202, 202, 0.9)
  );
  border-color: rgba(239, 68, 68, 0.28);
}

.danger-zone h3 {
  margin: 0 0 10px;
  color: #b91c1c;
}

.danger-warning {
  margin: 0 0 16px;
  color: #7f1d1d;
}

@media (max-width: 1100px) {
  .profile-container {
    grid-template-columns: 1fr;
  }

  .profile-sidebar {
    order: 1;
  }

  .profile-content {
    order: 2;
  }
}

@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    padding: 24px;
  }

  .hero-title {
    font-size: 1.9rem;
  }

  .profile-content {
    padding: 18px;
  }

  .form-grid,
  .two-column-layout,
  .analysis-grid,
  .profile-overview-grid,
  .year-range-grid {
    grid-template-columns: 1fr;
  }

  .favorites-controls,
  .form-actions,
  .settings-actions,
  .danger-actions,
  .favorite-actions {
    flex-direction: column;
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
  }
}
</style>
