<template>
  <div class="ai-chat-page">
    <!-- 页面头部（不是导航栏，导航栏继续用 App.vue 的全局 nav） -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">AI 对话</div>
        <h1 class="hero-title">🤖 AI电影助手</h1>
        <p class="hero-subtitle">
          基于 DeepSeek
          的智能电影对话系统，支持电影推荐、剧情分析、观影建议与影片问答
        </p>

        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-number">{{ movieCount }}</div>
            <div class="stat-label">电影总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ genreCount }}</div>
            <div class="stat-label">类型数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ messages.length }}</div>
            <div class="stat-label">对话消息</div>
          </div>
        </div>
      </div>

      <div class="hero-actions">
        <button
          @click="clearChat"
          class="header-btn danger-btn"
          :disabled="messages.length === 0"
        >
          🗑️ 清空对话
        </button>
        <button @click="toggleTheme" class="header-btn">
          {{ themeStore.isDark ? "☀️ 浅色模式" : "🌙 深色模式" }}
        </button>
      </div>
    </section>

    <!-- 主体 -->
    <div class="content-layout">
      <!-- 左侧聊天主体 -->
      <section class="chat-panel">
        <div class="panel-title-row">
          <h2 class="panel-title">智能对话</h2>
          <span class="panel-subtitle">输入你想了解的电影问题</span>
        </div>

        <!-- 消息区 -->
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="welcome-card">
            <div class="welcome-icon">🎬</div>
            <h3 class="welcome-title">欢迎使用 AI 电影助手</h3>
            <p class="welcome-text">
              你可以向我提问电影推荐、剧情解析、演员导演信息、类型片推荐等问题。
            </p>

            <div class="welcome-features">
              <div class="feature-item">🎯 个性化推荐</div>
              <div class="feature-item">📝 剧情分析</div>
              <div class="feature-item">🎭 演员导演介绍</div>
              <div class="feature-item">🌟 观影建议</div>
            </div>

            <div class="quick-questions">
              <button
                @click="quickQuestion('推荐一部适合周末看的喜剧电影')"
                class="quick-btn"
              >
                周末喜剧
              </button>
              <button
                @click="quickQuestion('分析一下《盗梦空间》的剧情')"
                class="quick-btn"
              >
                剧情分析
              </button>
              <button
                @click="quickQuestion('最近有什么热门电影推荐？')"
                class="quick-btn"
              >
                热门推荐
              </button>
              <button
                @click="quickQuestion('适合家庭观看的电影有哪些？')"
                class="quick-btn"
              >
                家庭观影
              </button>
            </div>
          </div>

          <div
            v-for="(message, index) in messages"
            :key="index"
            class="message-wrapper"
          >
            <!-- 用户消息 -->
            <div v-if="message.role === 'user'" class="message user-message">
              <div class="message-avatar user-avatar">👤</div>
              <div class="message-body">
                <div class="message-meta">
                  <span class="message-sender">您</span>
                  <span class="message-time">{{
                    formatTime(message.timestamp)
                  }}</span>
                </div>
                <div class="message-text user-bubble">
                  {{ message.content }}
                </div>
              </div>
            </div>

            <!-- AI消息 -->
            <div v-else class="message ai-message">
              <div class="message-avatar ai-avatar">
                <img :src="chatIcon" alt="AI助手" class="ai-avatar-img" />
              </div>
              <div class="message-body">
                <div class="message-meta">
                  <span class="message-sender">AI电影助手</span>
                  <span class="message-time">{{
                    formatTime(message.timestamp)
                  }}</span>
                </div>

                <div class="message-text ai-bubble">
                  <div v-if="message.isLoading" class="loading-indicator">
                    <div class="loading-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span class="loading-text">AI 正在思考...</span>
                  </div>
                  <div
                    v-else
                    class="ai-response"
                    v-html="formatAIResponse(message.content)"
                  ></div>

                  <div
                    v-if="
                      message.movieRecommendations &&
                      message.movieRecommendations.length > 0
                    "
                    class="movie-recommendations"
                  >
                    <h4 class="recommendations-title">🎬 相关电影推荐</h4>
                    <div class="recommendations-grid">
                      <div
                        v-for="movie in message.movieRecommendations"
                        :key="movie.id"
                        class="recommendation-card"
                      >
                        <div class="recommendation-header">
                          <h5 class="movie-title">{{ movie.title }}</h5>
                          <div class="movie-rating">⭐ {{ movie.rating }}</div>
                        </div>

                        <div class="recommendation-meta">
                          <span>{{ movie.year }}</span>
                          <span>{{ movie.genre }}</span>
                          <span>{{ movie.country }}</span>
                        </div>

                        <p class="movie-description" v-if="movie.description">
                          {{ movie.description }}
                        </p>

                        <div class="movie-actions">
                          <button
                            @click="askAboutMovie(movie.title)"
                            class="action-btn primary-btn"
                          >
                            了解更多
                          </button>
                          <a
                            v-if="movie.link"
                            :href="movie.link"
                            target="_blank"
                            class="action-btn link-btn"
                          >
                            查看详情
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="!message.isLoading" class="message-actions">
                  <button
                    @click="copyToClipboard(message.content)"
                    class="mini-btn"
                  >
                    📋 复制
                  </button>
                  <button
                    v-if="message.role === 'assistant'"
                    @click="regenerateResponse(index)"
                    class="mini-btn"
                  >
                    🔄 重新生成
                  </button>
                  <button @click="likeMessage(index)" class="mini-btn">
                    {{ message.liked ? "❤️ 已点赞" : "🤍 点赞" }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="isLoading" class="typing-indicator">
            <div class="typing-avatar">
              <img :src="chatIcon" alt="AI助手" class="typing-avatar-img" />
            </div>
            <div class="typing-content">
              <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span class="typing-text">AI正在输入...</span>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="input-panel">
          <div class="input-wrapper">
            <textarea
              ref="inputRef"
              v-model="userInput"
              @input="autoResize"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.enter.shift.exact.stop
              placeholder="请输入你想问的电影问题..."
              rows="1"
              class="message-input"
              :disabled="isLoading"
            ></textarea>

            <div class="input-toolbar">
              <div class="tool-group">
                <button
                  @click="showComposerExtras = !showComposerExtras"
                  class="tool-btn"
                >
                  {{ showComposerExtras ? "收起" : "更多" }} ⚙️
                </button>
                <button
                  @click="insertExample('推荐一部适合周末看的喜剧电影')"
                  class="tool-btn"
                >
                  🎭 喜剧
                </button>
                <button
                  @click="insertExample('分析一下《盗梦空间》的剧情')"
                  class="tool-btn"
                >
                  📖 分析
                </button>
              </div>

              <div class="tool-group">
                <button
                  @click="clearInput"
                  class="secondary-btn"
                  :disabled="!userInput.trim()"
                >
                  清空
                </button>
                <button
                  @click="sendMessage"
                  class="primary-btn send-btn"
                  :disabled="!userInput.trim() || isLoading"
                >
                  {{ isLoading ? "发送中..." : "发送" }} 🚀
                </button>
              </div>
            </div>
          </div>

          <transition name="fade">
            <div v-if="showComposerExtras" class="input-hints">
              <p class="hint-text">
                💡 你可以问我电影推荐、剧情解析、演员导演信息、类型片推荐等问题
              </p>
              <div class="quick-questions">
                <button
                  @click="quickQuestion('最近有什么热门电影推荐？')"
                  class="quick-btn"
                >
                  热门推荐
                </button>
                <button
                  @click="quickQuestion('经典电影有哪些？')"
                  class="quick-btn"
                >
                  经典电影
                </button>
                <button
                  @click="quickQuestion('适合家庭观看的电影？')"
                  class="quick-btn"
                >
                  家庭观影
                </button>
                <button
                  @click="quickQuestion('悬疑推理电影推荐')"
                  class="quick-btn"
                >
                  悬疑推理
                </button>
              </div>
            </div>
          </transition>
        </div>
      </section>

      <!-- 右侧边栏 -->
      <aside class="sidebar-panel" :class="{ collapsed: isSidebarCollapsed }">
        <div class="sidebar-header">
          <h3 class="sidebar-title">🎬 电影数据库</h3>
          <button @click="toggleSidebar" class="collapse-btn">
            {{ isSidebarCollapsed ? "展开" : "收起" }}
          </button>
        </div>

        <div v-if="!isSidebarCollapsed" class="sidebar-content">
          <div class="sidebar-card">
            <div class="movie-stats">
              <div class="sidebar-stat">
                <div class="sidebar-stat-value">{{ movieCount }}</div>
                <div class="sidebar-stat-label">电影总数</div>
              </div>
              <div class="sidebar-stat">
                <div class="sidebar-stat-value">{{ genreCount }}</div>
                <div class="sidebar-stat-label">电影类型</div>
              </div>
            </div>
          </div>

          <div class="sidebar-card">
            <h4 class="sidebar-subtitle">🔍 快速搜索</h4>
            <input
              v-model="searchQuery"
              @input="searchMovies"
              placeholder="搜索电影..."
              class="sidebar-input"
            />
            <div v-if="searchResults.length > 0" class="search-results">
              <div
                v-for="movie in searchResults"
                :key="movie.id"
                class="search-result-item"
                @click="askAboutMovie(movie.title)"
              >
                <div class="result-title">{{ movie.title }}</div>
                <div class="result-meta">
                  {{ movie.year }} · {{ movie.genre }}
                </div>
              </div>
            </div>
          </div>

          <div class="sidebar-card">
            <h4 class="sidebar-subtitle">🏆 热门电影</h4>
            <div class="top-movies">
              <div
                v-for="movie in topMovies"
                :key="movie.id"
                class="top-movie-item"
                @click="askAboutMovie(movie.title)"
              >
                <div class="top-movie-rank">{{ movie.rank }}</div>
                <div class="top-movie-info">
                  <div class="top-movie-title">{{ movie.title }}</div>
                  <div class="top-movie-rating">⭐ {{ movie.rating }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="sidebar-card">
            <h4 class="sidebar-subtitle">⚙️ 对话设置</h4>

            <div class="setting-item">
              <label class="setting-label">AI模型</label>
              <select v-model="selectedModel" class="sidebar-select">
                <option value="deepseek-chat">DeepSeek Chat</option>
                <option value="deepseek-coder">DeepSeek Coder</option>
              </select>
            </div>

            <div class="setting-item">
              <label class="setting-label">温度：{{ temperature }}</label>
              <input
                v-model="temperature"
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                class="temperature-slider"
              />
              <div class="temperature-hint">
                <span>保守</span>
                <span>创意</span>
              </div>
            </div>

            <div class="setting-item checkbox-item">
              <label class="setting-label">
                <input v-model="enableMovieRecommendations" type="checkbox" />
                自动推荐电影
              </label>
            </div>

            <div class="setting-item checkbox-item">
              <label class="setting-label">
                <input v-model="enableStream" type="checkbox" />
                流式输出
              </label>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, nextTick } from "vue";
import axios from "axios";
import doubanData from "../data/豆瓣电影TOP250.json";
import { useThemeStore } from "@/stores/theme";

const chatIcon = "/media/chat_ico.png";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  liked?: boolean;
  movieRecommendations?: MovieRecommendation[];
}

interface MovieRecommendation {
  id: number;
  title: string;
  rating: string;
  year: string;
  genre: string;
  country: string;
  description?: string;
  link?: string;
}

interface Movie {
  id: number;
  title: string;
  rating: string;
  year: string;
  genre: string;
  country: string;
  description?: string;
  link?: string;
}

export default defineComponent({
  name: "AIChatView",
  setup() {
    const themeStore = useThemeStore();

    const inputRef = ref<HTMLTextAreaElement | null>(null);
    const showComposerExtras = ref(false);
    const messages = ref<Message[]>([]);
    const userInput = ref("");
    const isLoading = ref(false);
    const isSidebarCollapsed = ref(false);
    const searchQuery = ref("");
    const searchResults = ref<Movie[]>([]);
    const selectedModel = ref("deepseek-chat");
    const temperature = ref(0.7);
    const enableMovieRecommendations = ref(true);
    const enableStream = ref(true);

    const allMovies = ref<Movie[]>([]);
    const messagesContainer = ref<HTMLElement | null>(null);

    const movieCount = computed(() => allMovies.value.length);

    const genreCount = computed(() => {
      const genres = new Set<string>();
      allMovies.value.forEach((movie) => {
        if (movie.genre) {
          movie.genre.split(" ").forEach((g) => genres.add(g.trim()));
        }
      });
      return genres.size;
    });

    const topMovies = computed(() => {
      return allMovies.value.slice(0, 5).map((movie, index) => ({
        ...movie,
        rank: index + 1,
      }));
    });

    const autoResize = () => {
      nextTick(() => {
        const el = inputRef.value;
        if (!el) return;
        el.style.height = "0px";
        const max = 160;
        el.style.height = Math.min(el.scrollHeight, max) + "px";
      });
    };

    const formatTime = (date: Date) => {
      return date.toLocaleTimeString("zh-CN", {
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    const formatAIResponse = (text: string) => {
      return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/`(.*?)`/g, "<code>$1</code>")
        .replace(/\n/g, "<br>");
    };

    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop =
            messagesContainer.value.scrollHeight;
        }
      });
    };

    const extractMovieRecommendations = (
      response: string
    ): MovieRecommendation[] => {
      const recommendations: MovieRecommendation[] = [];

      const movieKeywords = allMovies.value.map((movie) =>
        movie.title.toLowerCase()
      );

      movieKeywords.forEach((keyword, index) => {
        if (response.toLowerCase().includes(keyword)) {
          const movie = allMovies.value[index];
          recommendations.push({
            id: index,
            title: movie.title,
            rating: movie.rating,
            year: movie.year,
            genre: movie.genre,
            country: movie.country,
            description: movie.description,
            link: movie.link,
          });
        }
      });

      return recommendations.slice(0, 3);
    };

    const saveChatHistory = () => {
      try {
        const history = messages.value.filter((msg) => !msg.isLoading);
        localStorage.setItem("ai_chat_history", JSON.stringify(history));
      } catch (error) {
        console.error("保存聊天历史失败:", error);
      }
    };

    const loadChatHistory = () => {
      try {
        const saved = localStorage.getItem("ai_chat_history");
        if (saved) {
          const history = JSON.parse(saved);
          messages.value = history.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp),
          }));
        }
      } catch (error) {
        console.error("加载聊天历史失败:", error);
      }
    };

    const sendMessage = async () => {
      const content = userInput.value.trim();
      if (!content || isLoading.value) return;

      const userMessage: Message = {
        role: "user",
        content,
        timestamp: new Date(),
      };
      messages.value.push(userMessage);
      userInput.value = "";

      nextTick(() => {
        if (inputRef.value) inputRef.value.style.height = "0px";
      });

      const aiMessage: Message = {
        role: "assistant",
        content: "",
        timestamp: new Date(),
        isLoading: true,
        liked: false,
        movieRecommendations: [],
      };
      messages.value.push(aiMessage);

      isLoading.value = true;
      scrollToBottom();

      const lastIndex = messages.value.length - 1;

      const finalizeAIMessage = (finalText: string) => {
        messages.value[lastIndex] = {
          ...messages.value[lastIndex],
          role: "assistant",
          content: finalText,
          timestamp: new Date(),
          isLoading: false,
          liked: messages.value[lastIndex].liked ?? false,
          movieRecommendations: enableMovieRecommendations.value
            ? extractMovieRecommendations(finalText)
            : [],
        };
      };

      try {
        if (enableStream.value) {
          const response = await fetch("http://localhost:8000/api/ai/chat/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              message: content,
              model: selectedModel.value,
              temperature: temperature.value,
              stream: true,
            }),
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const reader = response.body?.getReader();
          if (!reader) throw new Error("无法读取响应流");

          const decoder = new TextDecoder("utf-8");
          let fullResponse = "";
          let buffer = "";

          for (;;) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split(/\r?\n/);
            buffer = lines.pop() ?? "";

            for (const rawLine of lines) {
              const line = rawLine.trim();
              if (!line) continue;

              let payload = line;
              if (payload.startsWith("data:")) {
                payload = payload.replace(/^data:\s*/, "");
              }

              if (payload === "[DONE]" || payload === "DONE") continue;

              let deltaText = "";
              try {
                const obj = JSON.parse(payload);
                deltaText =
                  obj.delta ??
                  obj.content ??
                  obj.text ??
                  obj.response ??
                  obj.message ??
                  "";

                if (!deltaText && obj.choices?.[0]?.delta?.content) {
                  deltaText = obj.choices[0].delta.content;
                }
              } catch {
                deltaText = payload;
              }

              if (!deltaText) continue;

              fullResponse += deltaText;

              messages.value[lastIndex] = {
                ...messages.value[lastIndex],
                content: fullResponse,
                isLoading: false,
              };

              scrollToBottom();
            }
          }

          const tail = buffer.trim();
          if (tail) {
            let tailText = "";
            try {
              const obj = JSON.parse(tail);
              tailText =
                obj.delta ?? obj.content ?? obj.text ?? obj.response ?? "";
              if (!tailText && obj.choices?.[0]?.delta?.content) {
                tailText = obj.choices[0].delta.content;
              }
            } catch {
              tailText = tail.startsWith("data:")
                ? tail.replace(/^data:\s*/, "")
                : tail;
            }

            if (tailText && tailText !== "[DONE]" && tailText !== "DONE") {
              fullResponse += tailText;
            }
          }

          finalizeAIMessage(fullResponse);
          saveChatHistory();
          return;
        }

        const res = await axios.post("http://localhost:8000/api/ai/chat/", {
          message: content,
          model: selectedModel.value,
          temperature: temperature.value,
          stream: false,
        });

        const finalText = res.data?.response ?? "";
        finalizeAIMessage(finalText);
        saveChatHistory();
      } catch (error) {
        console.error("AI对话失败:", error);

        messages.value[lastIndex] = {
          role: "assistant",
          content: "抱歉，AI助手暂时无法响应。请检查网络连接或稍后重试。",
          timestamp: new Date(),
          liked: false,
          isLoading: false,
          movieRecommendations: [],
        };
      } finally {
        isLoading.value = false;
        scrollToBottom();
      }
    };

    const clearChat = () => {
      if (confirm("确定要清空所有对话记录吗？此操作不可撤销。")) {
        messages.value = [];
        localStorage.removeItem("ai_chat_history");
      }
    };

    const toggleTheme = () => {
      themeStore.toggleTheme();
    };

    const toggleSidebar = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value;
    };

    const searchMovies = () => {
      const query = searchQuery.value.toLowerCase().trim();
      if (!query) {
        searchResults.value = [];
        return;
      }

      searchResults.value = allMovies.value
        .filter(
          (movie) =>
            movie.title.toLowerCase().includes(query) ||
            movie.genre.toLowerCase().includes(query) ||
            movie.country.toLowerCase().includes(query)
        )
        .slice(0, 5);
    };

    const askAboutMovie = (movieTitle: string) => {
      userInput.value = `请介绍一下《${movieTitle}》这部电影`;
      sendMessage();
    };

    const copyToClipboard = async (text: string) => {
      try {
        await navigator.clipboard.writeText(text);
        alert("已复制到剪贴板！");
      } catch (error) {
        console.error("复制失败:", error);
        alert("复制失败，请手动复制");
      }
    };

    const regenerateResponse = async (index: number) => {
      if (index > 0 && messages.value[index - 1].role === "user") {
        const userMessage = messages.value[index - 1].content;
        messages.value = messages.value.slice(0, index - 1);
        userInput.value = userMessage;
        await sendMessage();
      }
    };

    const likeMessage = (index: number) => {
      messages.value[index].liked = !messages.value[index].liked;
      saveChatHistory();
    };

    const insertExample = (example: string) => {
      userInput.value = example;
    };

    const clearInput = () => {
      userInput.value = "";
    };

    const quickQuestion = (question: string) => {
      userInput.value = question;
      sendMessage();
    };

    const init = () => {
      allMovies.value = (doubanData as any[]).map((movie, index) => ({
        id: index,
        title: movie["电影名字"],
        rating: movie["评分"],
        year: movie["年份"],
        genre: movie["类型"],
        country: movie["国家"],
        description: movie["一句话评价"],
        link: movie["电影链接"],
      }));

      loadChatHistory();
    };

    onMounted(() => {
      init();
      scrollToBottom();
    });

    return {
      themeStore,
      inputRef,
      showComposerExtras,
      chatIcon,
      messages,
      userInput,
      isLoading,
      isSidebarCollapsed,
      searchQuery,
      searchResults,
      selectedModel,
      temperature,
      enableMovieRecommendations,
      enableStream,
      movieCount,
      genreCount,
      topMovies,
      messagesContainer,
      autoResize,
      formatTime,
      formatAIResponse,
      sendMessage,
      clearChat,
      toggleTheme,
      toggleSidebar,
      searchMovies,
      askAboutMovie,
      copyToClipboard,
      regenerateResponse,
      likeMessage,
      insertExample,
      clearInput,
      quickQuestion,
    };
  },
});
</script>

<style scoped>
.ai-chat-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 顶部介绍区，跟 About / Douban 统一 */
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
  font-size: 2.4rem;
  font-weight: 800;
  color: #fff;
}

.hero-subtitle {
  margin: 0 0 24px;
  font-size: 1.08rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.92);
  max-width: 760px;
}

.hero-stats {
  display: flex;
  gap: 20px;
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

.stat-label {
  margin-top: 6px;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.88);
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
  opacity: 0.45;
  cursor: not-allowed;
}

.danger-btn {
  background: rgba(239, 68, 68, 0.2);
}

.content-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  align-items: start;
}

.chat-panel,
.sidebar-panel {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
}

.chat-panel {
  padding: 24px;
  min-height: 760px;
  display: flex;
  flex-direction: column;
}

.panel-title-row {
  margin-bottom: 18px;
}

.panel-title {
  margin: 0 0 6px;
  font-size: 1.6rem;
  color: var(--text-primary);
}

.panel-subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.messages-container {
  flex: 1;
  min-height: 420px;
  max-height: 700px;
  overflow-y: auto;
  padding-right: 6px;
}

.welcome-card {
  padding: 36px 24px;
  text-align: center;
  background: var(--primary-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--panel-border);
}

.welcome-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.welcome-title {
  margin: 0 0 12px;
  color: var(--text-primary);
}

.welcome-text {
  margin: 0 auto 20px;
  max-width: 720px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.welcome-features {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 22px;
}

.feature-item {
  padding: 10px 14px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  font-size: 0.92rem;
  font-weight: 500;
}

.message-wrapper {
  margin-bottom: 20px;
}

.message {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.message-avatar {
  width: 42px;
  height: 42px;
  min-width: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
}

.user-avatar {
  font-size: 1.1rem;
}

.ai-avatar {
  overflow: hidden;
}

.ai-avatar-img,
.typing-avatar-img {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.message-body {
  flex: 1;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.message-sender {
  font-weight: 700;
  color: var(--text-primary);
}

.message-time {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.message-text {
  border-radius: var(--radius-md);
  padding: 16px;
  line-height: 1.75;
  word-break: break-word;
}

.user-bubble {
  background: var(--bg-hero);
  color: #fff;
}

.ai-bubble {
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  color: var(--text-secondary);
}

.ai-response :deep(code) {
  padding: 2px 6px;
  border-radius: 6px;
  background: var(--nav-hover-bg);
  color: var(--primary);
}

.movie-recommendations {
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px solid var(--panel-border);
}

.recommendations-title {
  margin: 0 0 14px;
  color: var(--text-primary);
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.recommendation-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  padding: 16px;
  transition: all var(--transition-fast);
}

.recommendation-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--panel-shadow);
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
  margin-bottom: 12px;
}

.movie-title {
  margin: 0;
  font-size: 1rem;
  color: var(--text-primary);
}

.movie-rating {
  white-space: nowrap;
  color: var(--rating-text, var(--primary));
  font-weight: 700;
}

.recommendation-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.recommendation-meta span {
  padding: 4px 8px;
  border-radius: var(--radius-full);
  background: var(--nav-hover-bg);
  color: var(--text-muted);
  font-size: 0.82rem;
}

.movie-description {
  color: var(--text-secondary);
  font-size: 0.92rem;
  line-height: 1.6;
  margin-bottom: 14px;
}

.movie-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  text-align: center;
  text-decoration: none;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
}

.primary-btn {
  background: var(--primary-gradient);
  color: #fff;
}

.link-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.message-actions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mini-btn {
  padding: 8px 12px;
  border: 1px solid var(--panel-border);
  background: var(--panel-bg);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.88rem;
  transition: all var(--transition-fast);
}

.mini-btn:hover {
  background: var(--nav-hover-bg);
}

.typing-indicator {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-top: 12px;
}

.typing-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  display: flex;
  align-items: center;
  justify-content: center;
}

.typing-content {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  padding: 12px 16px;
  border-radius: var(--radius-md);
}

.loading-indicator,
.typing-dots {
  display: flex;
  align-items: center;
  gap: 6px;
}

.loading-dots span,
.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  animation: blink 1.2s infinite ease-in-out;
}

.loading-dots span:nth-child(2),
.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3),
.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

.loading-text,
.typing-text {
  color: var(--text-secondary);
  font-size: 0.92rem;
}

.input-panel {
  margin-top: 20px;
  border-top: 1px solid var(--panel-border);
  padding-top: 20px;
}

.input-wrapper {
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  padding: 16px;
}

.message-input,
.sidebar-input,
.sidebar-select {
  width: 100%;
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
  outline: none;
  transition: all var(--transition-fast);
}

.message-input {
  resize: none;
  min-height: 52px;
  max-height: 160px;
  padding: 14px 16px;
  font-size: 1rem;
  line-height: 1.6;
}

.message-input:focus,
.sidebar-input:focus,
.sidebar-select:focus {
  border-color: var(--input-focus-border);
}

.input-toolbar {
  margin-top: 14px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.tool-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tool-btn,
.secondary-btn,
.send-btn,
.collapse-btn {
  border: none;
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  cursor: pointer;
  font-size: 0.92rem;
  font-weight: 600;
  transition: all var(--transition-fast);
}

.tool-btn,
.secondary-btn,
.collapse-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.send-btn {
  color: #fff;
}

.tool-btn:hover,
.secondary-btn:hover,
.collapse-btn:hover,
.send-btn:hover {
  transform: translateY(-1px);
}

.input-hints {
  margin-top: 14px;
  padding: 14px 16px;
  background: var(--primary-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--panel-border);
}

.hint-text {
  margin: 0 0 12px;
  color: var(--text-secondary);
}

.quick-questions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.quick-btn {
  border: none;
  border-radius: var(--radius-full);
  padding: 9px 14px;
  background: var(--nav-hover-bg);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 0.88rem;
  transition: all var(--transition-fast);
}

.quick-btn:hover {
  background: var(--nav-active-bg);
  color: var(--nav-active-text);
}

.sidebar-panel {
  padding: 20px;
  position: sticky;
  top: 84px;
}

.sidebar-panel.collapsed {
  padding-bottom: 20px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.sidebar-title {
  margin: 0;
  color: var(--text-primary);
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar-card {
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  padding: 16px;
}

.sidebar-subtitle {
  margin: 0 0 12px;
  color: var(--text-primary);
}

.movie-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.sidebar-stat {
  text-align: center;
  padding: 14px;
  border-radius: var(--radius-sm);
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
}

.sidebar-stat-value {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--primary);
}

.sidebar-stat-label {
  margin-top: 6px;
  font-size: 0.88rem;
  color: var(--text-muted);
}

.sidebar-input {
  padding: 10px 12px;
  margin-bottom: 10px;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.search-result-item,
.top-movie-item {
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.search-result-item:hover,
.top-movie-item:hover {
  background: var(--nav-hover-bg);
}

.result-title,
.top-movie-title {
  color: var(--text-primary);
  font-weight: 600;
}

.result-meta,
.top-movie-rating {
  margin-top: 4px;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.top-movies {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.top-movie-item {
  display: flex;
  gap: 10px;
  align-items: center;
}

.top-movie-rank {
  width: 28px;
  height: 28px;
  min-width: 28px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.86rem;
  font-weight: 700;
}

.top-movie-info {
  flex: 1;
}

.setting-item {
  margin-bottom: 14px;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 0.92rem;
  font-weight: 600;
}

.sidebar-select {
  padding: 10px 12px;
}

.temperature-slider {
  width: 100%;
}

.temperature-hint {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.checkbox-item .setting-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes blink {
  0%,
  80%,
  100% {
    opacity: 0.35;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

@media (max-width: 1100px) {
  .content-layout {
    grid-template-columns: 1fr;
  }

  .sidebar-panel {
    position: static;
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

  .chat-panel {
    padding: 16px;
  }

  .input-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .tool-group {
    width: 100%;
  }

  .movie-actions {
    flex-direction: column;
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
  }
}
</style>
