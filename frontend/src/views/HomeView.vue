<template>
  <div class="about-view">
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">系统介绍</div>
        <h1 class="hero-title">🎬 智能电影推荐系统</h1>
        <p class="hero-subtitle">
          基于大模型与协同过滤技术构建，融合冷启动兴趣选择、用户画像分析、
          自然语言推荐检索与推荐理由生成，为用户提供更智能、更可解释的电影推荐体验。
        </p>

        <div class="hero-tags">
          <span class="hero-tag">协同过滤</span>
          <span class="hero-tag">大模型增强</span>
          <span class="hero-tag">用户画像</span>
          <span class="hero-tag">自然语言推荐</span>
        </div>

        <div class="hero-actions">
          <router-link to="/ai-chat" class="primary-btn">
            立即体验 AI 推荐
          </router-link>
          <router-link to="/douban" class="secondary-btn">
            浏览电影库
          </router-link>
        </div>
      </div>

      <div class="hero-side">
        <div class="hero-stat-card">
          <div class="stat-number">6+</div>
          <div class="stat-label">核心功能模块</div>
        </div>
        <div class="hero-stat-card">
          <div class="stat-number">AI</div>
          <div class="stat-label">大模型推荐解释</div>
        </div>
        <div class="hero-stat-card">
          <div class="stat-number">CF</div>
          <div class="stat-label">协同过滤推荐引擎</div>
        </div>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>📌 项目简介</h2>
        <p>这是一个面向个性化电影推荐场景的智能系统。</p>
      </div>

      <div class="intro-grid">
        <div class="intro-card">
          <h3>项目目标</h3>
          <p>
            通过结合传统推荐算法与大模型能力，解决电影推荐中“冷启动、解释性不足、
            自然语言交互弱”等问题，提升推荐体验与系统智能化程度。
          </p>
        </div>

        <div class="intro-card">
          <h3>核心思路</h3>
          <p>
            使用协同过滤生成推荐候选结果，利用用户画像补充用户兴趣，再通过大模型完成
            推荐理由生成与自然语言推荐检索，实现“可推荐、可解释、可交互”的推荐系统。
          </p>
        </div>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>🚀 核心功能</h2>
        <p>系统当前已经实现的主要模块。</p>
      </div>

      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">🎯</div>
          <h3>协同过滤推荐</h3>
          <p>
            基于用户评分行为进行个性化推荐，支持基于用户的协同过滤推荐结果生成。
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🧠</div>
          <h3>用户画像分析</h3>
          <p>
            根据用户冷启动兴趣与评分行为构建画像，用于个性化推荐和推荐解释增强。
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🌱</div>
          <h3>冷启动兴趣选择</h3>
          <p>用户首次进入系统时可以主动设置类型、国家、年份和关键词偏好。</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">💬</div>
          <h3>AI 对话问答</h3>
          <p>
            用户可以通过 AI 对话页面进行电影问答、剧情分析、导演风格了解等交互。
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">📝</div>
          <h3>推荐理由生成</h3>
          <p>
            利用大模型对推荐结果生成自然语言解释，让推荐结果更具可读性和可信度。
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🔍</div>
          <h3>自然语言推荐检索</h3>
          <p>
            支持用户直接输入观影需求，如“推荐几部高分科幻电影”，系统自动解析并推荐。
          </p>
        </div>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>🔄 系统流程</h2>
        <p>从用户输入到推荐结果展示的主要流程。</p>
      </div>

      <div class="flow-steps">
        <div class="flow-step">
          <div class="step-index">01</div>
          <div class="step-content">
            <h3>用户输入兴趣或行为数据</h3>
            <p>
              用户注册后可选择兴趣偏好，并在后续通过评分、收藏和 AI
              交互留下行为数据。
            </p>
          </div>
        </div>

        <div class="flow-step">
          <div class="step-index">02</div>
          <div class="step-content">
            <h3>构建用户画像</h3>
            <p>
              系统融合冷启动偏好与评分行为，提取用户偏好的类型、国家、年份和关键词信息。
            </p>
          </div>
        </div>

        <div class="flow-step">
          <div class="step-index">03</div>
          <div class="step-content">
            <h3>推荐引擎生成候选结果</h3>
            <p>
              协同过滤算法根据用户评分记录和相似用户行为生成个性化候选电影。
            </p>
          </div>
        </div>

        <div class="flow-step">
          <div class="step-index">04</div>
          <div class="step-content">
            <h3>大模型增强推荐解释</h3>
            <p>
              系统将候选结果、用户画像和推荐上下文交给大模型，生成自然语言推荐理由。
            </p>
          </div>
        </div>

        <div class="flow-step">
          <div class="step-index">05</div>
          <div class="step-content">
            <h3>前端展示推荐结果</h3>
            <p>
              最终将电影信息、推荐分数、推荐算法和推荐理由展示给用户，完成推荐闭环。
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>🧰 技术栈</h2>
        <p>本项目使用的前后端与算法相关技术。</p>
      </div>

      <div class="stack-grid">
        <div class="stack-card">
          <h3>前端技术</h3>
          <div class="chip-group">
            <span class="tech-chip">Vue 3</span>
            <span class="tech-chip">TypeScript</span>
            <span class="tech-chip">Vue Router</span>
            <span class="tech-chip">Pinia</span>
            <span class="tech-chip">Axios</span>
          </div>
        </div>

        <div class="stack-card">
          <h3>后端技术</h3>
          <div class="chip-group">
            <span class="tech-chip">Django</span>
            <span class="tech-chip">Django REST Framework</span>
            <span class="tech-chip">SQLite</span>
            <span class="tech-chip">Token Authentication</span>
          </div>
        </div>

        <div class="stack-card">
          <h3>智能推荐技术</h3>
          <div class="chip-group">
            <span class="tech-chip">Collaborative Filtering</span>
            <span class="tech-chip">User Profile</span>
            <span class="tech-chip">Cold Start</span>
            <span class="tech-chip">Explainable Recommendation</span>
          </div>
        </div>

        <div class="stack-card">
          <h3>大模型能力</h3>
          <div class="chip-group">
            <span class="tech-chip">DeepSeek API</span>
            <span class="tech-chip">AI Chat</span>
            <span class="tech-chip">NL Recommendation</span>
            <span class="tech-chip">Reason Generation</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>📚 数据与算法说明</h2>
        <p>系统展示数据与算法实验数据采用双数据源设计。</p>
      </div>

      <div class="data-grid">
        <div class="data-card">
          <h3>展示数据</h3>
          <p>
            前端电影展示主要基于豆瓣电影数据，用于电影信息展示、详情查看与推荐结果呈现。
          </p>
        </div>

        <div class="data-card">
          <h3>实验数据</h3>
          <p>
            推荐算法训练与实验评估使用 MovieLens
            数据集，用于验证协同过滤推荐算法的实现效果。
          </p>
        </div>

        <div class="data-card">
          <h3>推荐逻辑</h3>
          <p>
            系统在线推荐以用户评分记录、冷启动偏好和用户画像为基础，结合协同过滤与规则筛选生成结果。
          </p>
        </div>

        <div class="data-card">
          <h3>大模型融合方式</h3>
          <p>
            大模型主要用于推荐理由生成、AI
            电影问答、自然语言推荐检索和推荐回复增强。
          </p>
        </div>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>✨ 项目亮点</h2>
        <p>本系统相较于传统电影推荐页面的增强点。</p>
      </div>

      <div class="highlight-list">
        <div class="highlight-item">
          <span class="highlight-dot"></span>
          <span>融合协同过滤与大模型能力，实现推荐与解释一体化。</span>
        </div>
        <div class="highlight-item">
          <span class="highlight-dot"></span>
          <span>支持冷启动兴趣选择，提升新用户初始推荐质量。</span>
        </div>
        <div class="highlight-item">
          <span class="highlight-dot"></span>
          <span>构建用户画像，用于增强推荐结果的个性化与可解释性。</span>
        </div>
        <div class="highlight-item">
          <span class="highlight-dot"></span>
          <span>支持自然语言推荐检索，让用户可以直接用口语描述需求。</span>
        </div>
        <div class="highlight-item">
          <span class="highlight-dot"></span>
          <span>AI 对话页面支持电影问答与智能推荐双模式交互。</span>
        </div>
      </div>
    </section>

    <section class="cta-section panel-card">
      <div class="cta-content">
        <h2>开始体验系统</h2>
        <p>
          你可以直接进入 AI 对话页体验自然语言推荐，或进入电影库浏览高分电影。
        </p>
      </div>
      <div class="cta-actions">
        <router-link to="/ai-chat" class="primary-btn">
          前往 AI 对话
        </router-link>
        <router-link to="/douban" class="secondary-btn">
          前往电影库
        </router-link>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "AboutView",
});
</script>

<style scoped>
.about-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-section {
  background: var(--bg-hero);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  padding: 40px;
  color: #fff;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 260px;
  gap: 28px;
  align-items: start;
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
  margin: 0 0 14px;
  font-size: 2.5rem;
  font-weight: 800;
  color: #fff;
}

.hero-subtitle {
  margin: 0 0 20px;
  max-width: 820px;
  line-height: 1.8;
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.92);
}

.hero-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.hero-tag {
  padding: 7px 12px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  font-size: 0.88rem;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.hero-stat-card {
  border-radius: var(--radius-md);
  padding: 18px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 800;
  color: #fff;
}

.stat-label {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.92rem;
}

.section-card,
.cta-section {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
  padding: 28px;
}

.section-header {
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0 0 8px;
  color: var(--text-primary);
  font-size: 1.6rem;
}

.section-header p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.intro-grid,
.feature-grid,
.stack-grid,
.data-grid {
  display: grid;
  gap: 18px;
}

.intro-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.feature-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.stack-grid,
.data-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.intro-card,
.feature-card,
.stack-card,
.data-card {
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  padding: 20px;
}

.intro-card h3,
.feature-card h3,
.stack-card h3,
.data-card h3 {
  margin: 0 0 10px;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.intro-card p,
.feature-card p,
.stack-card p,
.data-card p {
  margin: 0;
  line-height: 1.75;
  color: var(--text-secondary);
}

.feature-icon {
  font-size: 1.8rem;
  margin-bottom: 12px;
}

.flow-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.flow-step {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  padding: 18px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
}

.step-index {
  min-width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.step-content h3 {
  margin: 0 0 8px;
  color: var(--text-primary);
  font-size: 1.08rem;
}

.step-content p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.chip-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tech-chip {
  padding: 7px 12px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-primary);
  font-size: 0.88rem;
}

.highlight-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.highlight-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px 16px;
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  line-height: 1.7;
}

.highlight-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 8px;
  background: linear-gradient(135deg, #667eea, #8b5cf6);
  flex-shrink: 0;
}

.cta-section {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
}

.cta-content h2 {
  margin: 0 0 8px;
  color: var(--text-primary);
}

.cta-content p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.cta-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-btn,
.secondary-btn {
  border: none;
  border-radius: var(--radius-sm);
  padding: 12px 18px;
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

.primary-btn:hover,
.secondary-btn:hover {
  transform: translateY(-1px);
}

@media (max-width: 1100px) {
  .hero-section {
    grid-template-columns: 1fr;
  }

  .feature-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .hero-section,
  .section-card,
  .cta-section {
    padding: 20px;
  }

  .hero-title {
    font-size: 2rem;
  }

  .intro-grid,
  .feature-grid,
  .stack-grid,
  .data-grid {
    grid-template-columns: 1fr;
  }

  .cta-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-actions,
  .cta-actions {
    width: 100%;
  }
}
</style>
