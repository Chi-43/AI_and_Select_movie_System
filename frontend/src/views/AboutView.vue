<template>
  <div class="about">
    <!-- 英雄区域 -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">🎬 关于电影推荐系统</h1>
        <p class="hero-subtitle">基于协同过滤算法的智能电影推荐平台</p>
        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-number">15+</div>
            <div class="stat-label">电影数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">2</div>
            <div class="stat-label">推荐算法</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">63+</div>
            <div class="stat-label">用户评分</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">100%</div>
            <div class="stat-label">个性化</div>
          </div>
        </div>
      </div>
      <div class="hero-image">
        <div class="movie-reel">
          <div class="reel-item">🎞️</div>
          <div class="reel-item">📽️</div>
          <div class="reel-item">🎥</div>
          <div class="reel-item">🍿</div>
        </div>
      </div>
    </div>

    <!-- 系统介绍 -->
    <div class="intro-section">
      <div class="container">
        <h2 class="section-title">系统介绍</h2>
        <p class="section-description">
          本系统是一个基于协同过滤算法的电影推荐平台，采用前后端分离架构，为用户提供个性化的电影推荐服务。
          系统通过分析用户的评分行为，发现用户之间的相似性和电影之间的关联性，从而为用户推荐他们可能感兴趣的电影。
        </p>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3 class="feature-title">智能推荐</h3>
            <p class="feature-description">
              采用协同过滤算法，基于用户行为和电影特征进行智能推荐，提供个性化的观影建议。
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">🔐</div>
            <h3 class="feature-title">用户认证</h3>
            <p class="feature-description">
              完整的用户注册、登录、注销系统，保护用户隐私，提供安全的个性化服务。
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3 class="feature-title">实时评分</h3>
            <p class="feature-description">
              用户可以实时为电影评分，系统会根据新的评分动态调整推荐结果。
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3 class="feature-title">多算法支持</h3>
            <p class="feature-description">
              支持基于用户的协同过滤和基于物品的协同过滤两种算法，满足不同推荐需求。
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 技术栈 -->
    <div class="tech-section">
      <div class="container">
        <h2 class="section-title">技术栈</h2>

        <div class="tech-stack">
          <div class="tech-category">
            <h3 class="tech-category-title">前端技术</h3>
            <div class="tech-items">
              <div class="tech-item">
                <span class="tech-icon">⚡</span>
                <span class="tech-name">Vue 3</span>
              </div>
              <div class="tech-item">
                <span class="tech-icon">📘</span>
                <span class="tech-name">TypeScript</span>
              </div>
              <div class="tech-item">
                <span class="tech-icon">🎨</span>
                <span class="tech-name">Pinia</span>
              </div>
              <div class="tech-item">
                <span class="tech-icon">🛣️</span>
                <span class="tech-name">Vue Router</span>
              </div>
              <div class="tech-item">
                <span class="tech-icon">📡</span>
                <span class="tech-name">Axios</span>
              </div>
            </div>
          </div>

          <div class="tech-category">
            <h3 class="tech-category-title">后端技术</h3>
            <div class="tech-items">
              <div class="tech-item">
                <span class="tech-icon">🐍</span>
                <span class="tech-name">Django</span>
              </div>
              <div class="tech-item">
                <span class="tech-icon">🔌</span>
                <span class="tech-name">Django REST Framework</span>
              </div>
              <div class="tech-item">
                <span class="tech-icon">🗄️</span>
                <span class="tech-name">SQLite3</span>
              </div>
              <div class="tech-item">
                <span class="tech-icon">🔐</span>
                <span class="tech-name">Token Authentication</span>
              </div>
              <div class="tech-item">
                <span class="tech-icon">📈</span>
                <span class="tech-name">scikit-learn</span>
              </div>
            </div>
          </div>

          <div class="tech-category">
            <h3 class="tech-category-title">算法技术</h3>
            <div class="tech-items">
              <div class="tech-item">
                <span class="tech-icon">👥</span>
                <span class="tech-name">基于用户的协同过滤</span>
              </div>
              <div class="tech-item">
                <span class="tech-icon">🎬</span>
                <span class="tech-name">基于物品的协同过滤</span>
              </div>
              <div class="tech-item">
                <span class="tech-icon">📐</span>
                <span class="tech-name">余弦相似度计算</span>
              </div>
              <div class="tech-item">
                <span class="tech-icon">🔥</span>
                <span class="tech-name">热门电影推荐</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 使用指南 -->
    <div class="guide-section">
      <div class="container">
        <h2 class="section-title">使用指南</h2>

        <div class="steps">
          <div class="step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3 class="step-title">注册账户</h3>
              <p class="step-description">
                点击右上角"注册"按钮，填写用户名、邮箱和密码创建新账户。
              </p>
            </div>
          </div>

          <div class="step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3 class="step-title">登录系统</h3>
              <p class="step-description">
                使用注册的账户登录系统，或使用测试账户（admin/admin123）直接登录。
              </p>
            </div>
          </div>

          <div class="step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3 class="step-title">获取推荐</h3>
              <p class="step-description">
                登录后点击"基于用户的推荐"或"基于电影的推荐"按钮获取个性化电影推荐。
              </p>
            </div>
          </div>

          <div class="step">
            <div class="step-number">4</div>
            <div class="step-content">
              <h3 class="step-title">评分互动</h3>
              <p class="step-description">
                为看过的电影评分，系统会根据您的评分优化后续的推荐结果。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 联系信息 -->
    <div class="contact-section">
      <div class="container">
        <h2 class="section-title">联系我们</h2>
        <p class="contact-description">
          如果您有任何问题、建议或合作意向，欢迎通过以下方式联系我们。
        </p>

        <div class="contact-info">
          <div class="contact-item">
            <div class="contact-icon">📧</div>
            <div class="contact-details">
              <h4 class="contact-title">邮箱</h4>
              <p class="contact-text">contact@movierecommendation.com</p>
            </div>
          </div>

          <div class="contact-item">
            <div class="contact-icon">🌐</div>
            <div class="contact-details">
              <h4 class="contact-title">GitHub</h4>
              <p class="contact-text">
                github.com/Chi-43/AI_and_Select_movie_System
              </p>
            </div>
          </div>

          <div class="contact-item">
            <div class="contact-icon">📱</div>
            <div class="contact-details">
              <h4 class="contact-title">版本</h4>
              <p class="contact-text">v1.0.0 - 电影推荐系统</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="footer">
      <div class="container">
        <p class="footer-text">
          🎬 电影推荐系统 © 2024 - 基于协同过滤算法的智能推荐平台
        </p>
        <p class="footer-subtext">让电影发现变得更简单、更个性化</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "AboutView",
  setup() {
    return {};
  },
});
</script>

<style scoped>
.about {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* 英雄区域样式 */
.hero-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 0 0 20px 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.hero-content {
  flex: 1;
  max-width: 600px;
}

.hero-title {
  font-size: 3rem;
  margin: 0 0 20px 0;
  font-weight: 700;
}

.hero-subtitle {
  font-size: 1.5rem;
  margin: 0 0 40px 0;
  opacity: 0.9;
}

.hero-stats {
  display: flex;
  gap: 30px;
  margin-top: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 1rem;
  opacity: 0.8;
}

.hero-image {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.movie-reel {
  display: flex;
  gap: 20px;
  animation: rotate 20s linear infinite;
}

.reel-item {
  font-size: 4rem;
  animation: bounce 2s ease-in-out infinite;
}

.reel-item:nth-child(2) {
  animation-delay: 0.2s;
}

.reel-item:nth-child(3) {
  animation-delay: 0.4s;
}

.reel-item:nth-child(4) {
  animation-delay: 0.6s;
}

/* 容器样式 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 通用区域样式 */
.intro-section,
.tech-section,
.guide-section,
.contact-section {
  padding: 80px 0;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 20px;
  color: #333;
}

.section-description {
  text-align: center;
  font-size: 1.2rem;
  color: #666;
  max-width: 800px;
  margin: 0 auto 60px;
  line-height: 1.6;
}

/* 特性网格样式 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin-top: 40px;
}

.feature-card {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature-title {
  font-size: 1.5rem;
  margin: 0 0 15px 0;
  color: #333;
}

.feature-description {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* 技术栈样式 */
.tech-stack {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 40px;
  margin-top: 40px;
}

.tech-category {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.tech-category-title {
  font-size: 1.8rem;
  margin: 0 0 25px 0;
  color: #333;
  text-align: center;
}

.tech-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.tech-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 20px;
  background: #f8f9fa;
  border-radius: 10px;
  transition: background 0.3s;
}

.tech-item:hover {
  background: #e9ecef;
}

.tech-icon {
  font-size: 1.5rem;
}

.tech-name {
  font-size: 1.1rem;
  color: #333;
}

/* 使用指南样式 */
.steps {
  display: flex;
  flex-direction: column;
  gap: 30px;
  max-width: 800px;
  margin: 40px auto 0;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 25px;
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.step-number {
  flex-shrink: 0;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 700;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 1.5rem;
  margin: 0 0 10px 0;
  color: #333;
}

.step-description {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* 联系信息样式 */
.contact-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin-top: 40px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 20px;
  background: white;
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.contact-icon {
  font-size: 2.5rem;
}

.contact-details {
  flex: 1;
}

.contact-title {
  font-size: 1.3rem;
  margin: 0 0 8px 0;
  color: #333;
}

.contact-text {
  color: #666;
  margin: 0;
  word-break: break-all;
}

/* 页脚样式 */
.footer {
  background: #333;
  color: white;
  padding: 40px 0;
  text-align: center;
}

.footer-text {
  font-size: 1.2rem;
  margin: 0 0 10px 0;
}

.footer-subtext {
  font-size: 1rem;
  opacity: 0.8;
}

/* 动画定义 */
@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    text-align: center;
    padding: 40px 20px;
  }

  .hero-title {
    font-size: 2.2rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .hero-stats {
    justify-content: center;
    flex-wrap: wrap;
  }

  .stat-number {
    font-size: 2rem;
  }

  .movie-reel {
    margin-top: 30px;
  }

  .section-title {
    font-size: 2rem;
  }

  .features-grid,
  .tech-stack,
  .contact-info {
    grid-template-columns: 1fr;
  }

  .step {
    flex-direction: column;
    text-align: center;
  }

  .step-number {
    margin: 0 auto 20px;
  }
}
</style>
