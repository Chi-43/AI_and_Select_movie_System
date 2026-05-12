<template>
  <div class="onboarding-container">
    <div class="onboarding-card">
      <div class="onboarding-header">
        <h1>🎯 选择你的兴趣偏好</h1>
        <p>告诉我们你喜欢什么类型的电影，帮你找到更合口味的影片</p>
      </div>

      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: progressPercent + '%' }"
        ></div>
      </div>

      <div v-if="step === 1" class="step-content">
        <h2>你喜欢的电影类型</h2>
        <p class="step-hint">选择你感兴趣的类型（可多选）</p>
        <div class="tag-grid">
          <button
            v-for="genre in genreOptions"
            :key="genre"
            class="tag-btn"
            :class="{ active: preferences.favorite_genres.includes(genre) }"
            @click="toggleItem(preferences.favorite_genres, genre)"
          >
            {{ genre }}
          </button>
        </div>
        <div class="step-actions">
          <button class="skip-btn" @click="nextStep">跳过</button>
          <button class="primary-btn" @click="nextStep">下一步</button>
        </div>
      </div>

      <div v-if="step === 2" class="step-content">
        <h2>你关注的国家/地区</h2>
        <p class="step-hint">选择你感兴趣的电影出产国家（可多选）</p>
        <div class="tag-grid">
          <button
            v-for="country in countryOptions"
            :key="country"
            class="tag-btn"
            :class="{
              active: preferences.favorite_countries.includes(country),
            }"
            @click="toggleItem(preferences.favorite_countries, country)"
          >
            {{ country }}
          </button>
        </div>
        <div class="step-actions">
          <button class="skip-btn" @click="nextStep">跳过</button>
          <button class="secondary-btn" @click="prevStep">上一步</button>
          <button class="primary-btn" @click="nextStep">下一步</button>
        </div>
      </div>

      <div v-if="step === 3" class="step-content">
        <h2>偏好年份范围</h2>
        <p class="step-hint">你更喜欢哪个年代的影片？</p>
        <div class="year-range">
          <div class="year-item">
            <label>起始年份</label>
            <input
              v-model.number="preferences.favorite_years.min"
              type="number"
              min="1900"
              max="2026"
              placeholder="如 2000"
            />
          </div>
          <span class="year-sep">—</span>
          <div class="year-item">
            <label>结束年份</label>
            <input
              v-model.number="preferences.favorite_years.max"
              type="number"
              min="1900"
              max="2026"
              placeholder="如 2026"
            />
          </div>
        </div>
        <div class="step-actions">
          <button class="skip-btn" @click="nextStep">跳过</button>
          <button class="secondary-btn" @click="prevStep">上一步</button>
          <button class="primary-btn" @click="nextStep">下一步</button>
        </div>
      </div>

      <div v-if="step === 4" class="step-content">
        <h2>兴趣关键词</h2>
        <p class="step-hint">输入你感兴趣的电影关键词，如：科幻、悬疑、治愈</p>
        <div class="keyword-input-row">
          <input
            v-model="keywordInput"
            type="text"
            placeholder="输入关键词后按回车添加"
            class="keyword-input"
            @keyup.enter="addKeyword"
          />
          <button class="primary-btn" @click="addKeyword">添加</button>
        </div>
        <div class="tag-grid" v-if="preferences.favorite_keywords.length > 0">
          <span
            v-for="kw in preferences.favorite_keywords"
            :key="kw"
            class="keyword-tag"
          >
            {{ kw }}
            <button class="remove-tag" @click="removeKeyword(kw)">×</button>
          </span>
        </div>
        <div v-else class="empty-hint">还没有添加关键词</div>
        <div class="step-actions">
          <button class="skip-btn" @click="submitPreferences">跳过</button>
          <button class="secondary-btn" @click="prevStep">上一步</button>
          <button
            class="primary-btn"
            @click="submitPreferences"
            :disabled="submitting"
          >
            {{ submitting ? "保存中..." : "完成" }}
          </button>
        </div>
      </div>

      <div v-if="errorMessage" class="error-box">{{ errorMessage }}</div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

const API_BASE_URL = "http://localhost:8000/api";

const genreOptions = [
  "剧情",
  "喜剧",
  "动作",
  "爱情",
  "科幻",
  "悬疑",
  "犯罪",
  "动画",
  "奇幻",
  "冒险",
  "战争",
  "恐怖",
  "惊悚",
  "历史",
  "纪录片",
  "家庭",
  "音乐",
  "传记",
  "武侠",
  "灾难",
];

const countryOptions = [
  "中国大陆",
  "美国",
  "香港",
  "日本",
  "韩国",
  "英国",
  "法国",
  "德国",
  "意大利",
  "印度",
  "台湾",
  "泰国",
  "西班牙",
  "加拿大",
  "澳大利亚",
  "俄罗斯",
  "瑞典",
  "丹麦",
  "荷兰",
  "巴西",
];

export default defineComponent({
  name: "OnboardingView",
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();

    const step = ref(1);
    const submitting = ref(false);
    const errorMessage = ref("");
    const keywordInput = ref("");

    const preferences = reactive({
      favorite_genres: [] as string[],
      favorite_countries: [] as string[],
      favorite_years: {
        min: null as number | null,
        max: null as number | null,
      },
      favorite_keywords: [] as string[],
    });

    const progressPercent = computed(() => (step.value / 4) * 100);

    const toggleItem = (arr: string[], item: string) => {
      const idx = arr.indexOf(item);
      if (idx >= 0) {
        arr.splice(idx, 1);
      } else {
        arr.push(item);
      }
    };

    const addKeyword = () => {
      const kw = keywordInput.value.trim();
      if (!kw) return;
      if (!preferences.favorite_keywords.includes(kw)) {
        preferences.favorite_keywords.push(kw);
      }
      keywordInput.value = "";
    };

    const removeKeyword = (kw: string) => {
      const idx = preferences.favorite_keywords.indexOf(kw);
      if (idx >= 0) preferences.favorite_keywords.splice(idx, 1);
    };

    const nextStep = () => {
      if (step.value < 4) step.value++;
    };

    const prevStep = () => {
      if (step.value > 1) step.value--;
    };

    const submitPreferences = async () => {
      submitting.value = true;
      errorMessage.value = "";

      try {
        const headers: Record<string, string> = {
          "Content-Type": "application/json",
        };
        if (authStore.token) {
          headers.Authorization = `Token ${authStore.token}`;
        }

        const years: Record<string, number | null> = {};
        if (preferences.favorite_years.min != null) {
          years.min = preferences.favorite_years.min;
        }
        if (preferences.favorite_years.max != null) {
          years.max = preferences.favorite_years.max;
        }

        const response = await fetch(
          `${API_BASE_URL}/onboarding-preferences/`,
          {
            method: "POST",
            headers,
            body: JSON.stringify({
              favorite_genres: preferences.favorite_genres,
              favorite_countries: preferences.favorite_countries,
              favorite_keywords: preferences.favorite_keywords,
              favorite_years: Object.keys(years).length > 0 ? years : {},
            }),
          }
        );

        if (!response.ok) {
          const data = await response.json().catch(() => ({}));
          throw new Error(data.error || data.detail || "保存失败");
        }

        // 偏好保存成功，触发一次冷启动推荐存入数据库
        try {
          await fetch(
            `${API_BASE_URL}/recommendations/?user_id=${authStore.user?.id}&algorithm=cold_start&top_n=8`
          );
        } catch {
          // 推荐生成失败不阻塞流程
        }

        router.push("/");
      } catch (error: any) {
        errorMessage.value = error.message || "保存偏好失败，请稍后重试";
      } finally {
        submitting.value = false;
      }
    };

    return {
      step,
      submitting,
      errorMessage,
      keywordInput,
      preferences,
      progressPercent,
      genreOptions,
      countryOptions,
      toggleItem,
      addKeyword,
      removeKeyword,
      nextStep,
      prevStep,
      submitPreferences,
    };
  },
});
</script>

<style scoped>
.onboarding-container {
  min-height: calc(100vh - 80px);
  display: grid;
  place-items: center;
  padding: 32px 16px;
}

.onboarding-card {
  width: 100%;
  max-width: 640px;
  padding: 34px 28px;
  border-radius: var(--radius-lg);
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  box-shadow: var(--panel-shadow);
}

.onboarding-header {
  text-align: center;
  margin-bottom: 20px;
}

.onboarding-header h1 {
  margin: 0;
  font-size: 1.6rem;
  color: var(--text-primary);
}

.onboarding-header p {
  margin: 10px 0 0;
  color: var(--text-secondary);
}

.progress-bar {
  height: 4px;
  border-radius: 2px;
  background: var(--nav-hover-bg);
  margin-bottom: 28px;
}

.progress-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--primary-gradient);
  transition: width 0.4s ease;
}

.step-content h2 {
  margin: 0 0 6px;
  color: var(--text-primary);
}

.step-hint {
  margin: 0 0 18px;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.tag-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
}

.tag-btn {
  border: 1px solid var(--panel-border);
  background: var(--primary-bg);
  color: var(--text-secondary);
  border-radius: var(--radius-full);
  padding: 9px 16px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
}

.tag-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.tag-btn.active {
  background: var(--primary-gradient);
  color: #fff;
  border-color: transparent;
}

.year-range {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.year-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.year-item label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.year-item input {
  padding: 11px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
}

.year-item input:focus {
  border-color: var(--input-focus-border);
}

.year-sep {
  color: var(--text-muted);
  font-size: 1.2rem;
  margin-top: 20px;
}

.keyword-input-row {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.keyword-input {
  flex: 1;
  padding: 11px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
}

.keyword-input:focus {
  border-color: var(--input-focus-border);
}

.keyword-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: var(--radius-full);
  background: var(--primary-gradient);
  color: #fff;
  font-weight: 600;
  font-size: 0.9rem;
}

.remove-tag {
  border: none;
  background: rgba(255, 255, 255, 0.3);
  color: #fff;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  cursor: pointer;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-hint {
  color: var(--text-muted);
  margin-bottom: 24px;
}

.step-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.primary-btn,
.secondary-btn,
.skip-btn {
  border: none;
  border-radius: var(--radius-sm);
  padding: 11px 20px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.primary-btn {
  background: var(--primary-gradient);
  color: #fff;
}

.secondary-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.skip-btn {
  background: transparent;
  color: var(--text-muted);
  margin-right: auto;
}

.skip-btn:hover {
  color: var(--text-secondary);
}

.primary-btn:hover,
.secondary-btn:hover {
  transform: translateY(-1px);
}

.primary-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.error-box {
  margin-top: 16px;
  padding: 12px;
  border-radius: var(--radius-md);
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
  font-weight: 600;
}

@media (max-width: 600px) {
  .onboarding-card {
    padding: 24px 16px;
  }

  .year-range {
    flex-direction: column;
    gap: 10px;
  }

  .step-actions {
    flex-wrap: wrap;
  }
}
</style>
