<template>
  <div class="ai-chat-view">
    <!-- 头部区域 -->
    <div class="chat-header">
      <div class="header-content">
        <div class="header-icon">
          <img :src="chatIcon" alt="AI对话图标" class="chat-icon-img" />
        </div>
        <div class="header-text">
          <h1 class="header-title">🤖 AI电影助手</h1>
          <p class="header-subtitle">基于DeepSeek的智能电影对话系统</p>
        </div>
      </div>
      <div class="header-actions">
        <button
          @click="clearChat"
          class="clear-btn"
          :disabled="messages.length === 0"
        >
          🗑️ 清空对话
        </button>
        <button @click="toggleDarkMode" class="theme-btn">
          {{ isDarkMode ? "☀️ 浅色模式" : "🌙 深色模式" }}
        </button>
      </div>
    </div>

    <!-- 聊天主体区域 -->
    <div class="chat-container" :class="{ 'dark-mode': isDarkMode }">
      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-content">
            <div class="welcome-icon">🎬</div>
            <h2 class="welcome-title">欢迎使用AI电影助手！</h2>
            <p class="welcome-text">
              我是基于DeepSeek的智能电影助手，可以为您：
            </p>
            <div class="welcome-features">
              <div class="feature-item">
                <span class="feature-icon">🎯</span>
                <span class="feature-text">推荐个性化电影</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">📝</span>
                <span class="feature-text">分析电影剧情</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🎭</span>
                <span class="feature-text">介绍演员导演</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🌟</span>
                <span class="feature-text">提供观影建议</span>
              </div>
            </div>
            <p class="welcome-tip">
              试试问我："推荐一部科幻电影" 或 "《肖申克的救赎》讲的是什么？"
            </p>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message-wrapper"
        >
          <!-- 用户消息 -->
          <div v-if="message.role === 'user'" class="message user-message">
            <div class="message-avatar">
              <div class="avatar user-avatar">👤</div>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-sender">您</span>
                <span class="message-time">{{
                  formatTime(message.timestamp)
                }}</span>
              </div>
              <div class="message-text">{{ message.content }}</div>
            </div>
          </div>

          <!-- AI消息 -->
          <div v-else class="message ai-message">
            <div class="message-avatar">
              <div class="avatar ai-avatar">
                <img :src="chatIcon" alt="AI助手" class="ai-avatar-img" />
              </div>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-sender">AI电影助手</span>
                <span class="message-time">{{
                  formatTime(message.timestamp)
                }}</span>
              </div>
              <div class="message-text">
                <div v-if="message.isLoading" class="loading-indicator">
                  <div class="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span class="loading-text">AI正在思考...</span>
                </div>
                <div v-else class="ai-response">
                  <div v-html="formatAIResponse(message.content)"></div>

                  <!-- 电影推荐卡片 -->
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
                        class="movie-card"
                      >
                        <div class="movie-card-header">
                          <h5 class="movie-title">{{ movie.title }}</h5>
                          <div class="movie-rating">
                            <span class="rating-star">⭐</span>
                            <span class="rating-value">{{ movie.rating }}</span>
                          </div>
                        </div>
                        <div class="movie-meta">
                          <span class="meta-item">{{ movie.year }}</span>
                          <span class="meta-item">{{ movie.genre }}</span>
                          <span class="meta-item">{{ movie.country }}</span>
                        </div>
                        <p class="movie-description" v-if="movie.description">
                          {{ movie.description }}
                        </p>
                        <div class="movie-actions">
                          <button
                            @click="askAboutMovie(movie.title)"
                            class="movie-action-btn"
                          >
                            💬 了解更多
                          </button>
                          <a
                            :href="movie.link"
                            target="_blank"
                            class="movie-action-btn"
                            v-if="movie.link"
                          >
                            🔗 查看详情
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 消息操作 -->
              <div v-if="!message.isLoading" class="message-actions">
                <button
                  @click="copyToClipboard(message.content)"
                  class="action-btn"
                >
                  📋 复制
                </button>
                <button
                  @click="regenerateResponse(index)"
                  class="action-btn"
                  v-if="message.role === 'assistant'"
                >
                  🔄 重新生成
                </button>
                <button @click="likeMessage(index)" class="action-btn">
                  {{ message.liked ? "❤️ 已点赞" : "🤍 点赞" }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 正在输入指示器 -->
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

      <!-- 输入区域 -->
      <div class="input-container">
        <div class="input-wrapper">
          <textarea
            ref="inputRef"
            v-model="userInput"
            @input="autoResize"
            @keydown.enter.exact.prevent="sendMessage"
            @keydown.enter.shift.exact.stop
            placeholder="有问题，尽管问"
            rows="1"
            class="message-input"
            :disabled="isLoading"
          ></textarea>
          <div class="input-actions">
            <div class="input-tools">
              <button
                @click="showComposerExtras = !showComposerExtras"
                class="tool-btn"
              >
                {{ showComposerExtras ? "收起" : "更多" }} ⚙️
              </button>

              <!-- 可选：保留 1~2 个最常用的快捷 -->
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
            <div class="send-actions">
              <button
                @click="clearInput"
                class="secondary-btn"
                :disabled="!userInput.trim()"
              >
                清空
              </button>
              <button
                @click="sendMessage"
                class="primary-btn"
                :disabled="!userInput.trim() || isLoading"
              >
                {{ isLoading ? "发送中..." : "发送" }}
                <span class="send-icon">🚀</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 输入提示 -->
        <transition name="fade">
          <div v-if="showComposerExtras" class="input-hints">
            <p class="hint-text">
              💡 提示：您可以询问电影推荐、剧情分析、演员介绍、观影建议等
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
    </div>

    <!-- 侧边栏（电影数据库） -->
    <div class="sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <button @click="toggleSidebar" class="sidebar-toggle">
        {{ isSidebarCollapsed ? "▶️" : "◀️" }}
      </button>

      <div v-if="!isSidebarCollapsed" class="sidebar-content">
        <div class="sidebar-section">
          <h3 class="sidebar-title">🎬 电影数据库</h3>
          <div class="movie-stats">
            <div class="stat-item">
              <div class="stat-value">{{ movieCount }}</div>
              <div class="stat-label">电影总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ genreCount }}</div>
              <div class="stat-label">电影类型</div>
            </div>
          </div>
        </div>

        <div class="sidebar-section">
          <h4 class="sidebar-subtitle">🔍 快速搜索</h4>
          <input
            v-model="searchQuery"
            @input="searchMovies"
            placeholder="搜索电影..."
            class="search-input"
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

        <div class="sidebar-section">
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

        <div class="sidebar-section">
          <h4 class="sidebar-subtitle">⚙️ 对话设置</h4>
          <div class="settings">
            <div class="setting-item">
              <label class="setting-label">AI模型</label>
              <select v-model="selectedModel" class="model-select">
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
            <div class="setting-item">
              <label class="setting-label">
                <input v-model="enableMovieRecommendations" type="checkbox" />
                自动推荐电影
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, nextTick } from "vue";
import axios from "axios";
import doubanData from "../data/豆瓣电影TOP250.json";

// 导入聊天图标
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
    // 状态管理
    const inputRef = ref<HTMLTextAreaElement | null>(null);
    const autoResize = () => {
      nextTick(() => {
        const el = inputRef.value;
        if (!el) return;
        el.style.height = "0px";
        const max = 160; // px，最多高度（约 6 行）
        el.style.height = Math.min(el.scrollHeight, max) + "px";
      });
    };
    const showComposerExtras = ref(false);
    const messages = ref<Message[]>([]);
    const userInput = ref("");
    const isLoading = ref(false);
    const isDarkMode = ref(false);
    const isSidebarCollapsed = ref(false);
    const searchQuery = ref("");
    const searchResults = ref<Movie[]>([]);
    const selectedModel = ref("deepseek-chat");
    const temperature = ref(0.7);
    const enableMovieRecommendations = ref(true);
    const enableStream = ref(true); // 你也可以用现有的开关项替代它
    // 电影数据
    const allMovies = ref<Movie[]>([]);
    const messagesContainer = ref<HTMLElement | null>(null);

    // 计算属性
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

    // 方法
    const formatTime = (date: Date) => {
      return date.toLocaleTimeString("zh-CN", {
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    const formatAIResponse = (text: string) => {
      // 简单的Markdown格式转换
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

    const sendMessage = async () => {
      const content = userInput.value.trim();
      if (!content || isLoading.value) return;

      // 1) 先塞用户消息
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

      // 2) 再塞 AI 占位消息
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

      // 用于统一更新 AI 消息（避免重复写一堆 messages.value[lastIndex] = ...）
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
        // ====== A. 流式输出 ======
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

          // 有些服务端会按行发送（SSE / NDJSON），我们用 buffer 处理“半行”情况
          let buffer = "";

          for (;;) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // 按行切分（兼容 SSE：\n\n 也会产生空行）
            const lines = buffer.split(/\r?\n/);
            buffer = lines.pop() ?? ""; // 最后一段可能是不完整行，留到下次拼

            for (const rawLine of lines) {
              const line = rawLine.trim();
              if (!line) continue;

              // 1) SSE：data: ....
              let payload = line;
              if (payload.startsWith("data:")) {
                payload = payload.replace(/^data:\s*/, "");
              }

              // 2) 常见结束标记
              if (payload === "[DONE]" || payload === "DONE") continue;

              // 3) 尝试按 JSON 解析
              let deltaText = "";
              try {
                const obj = JSON.parse(payload);

                // 你后端可能返回这些字段之一（按你实际返回结构改一改就行）
                deltaText =
                  obj.delta ??
                  obj.content ??
                  obj.text ??
                  obj.response ??
                  obj.message ??
                  "";

                // 有些实现会把 token 放在 choices[0].delta.content
                if (!deltaText && obj.choices?.[0]?.delta?.content) {
                  deltaText = obj.choices[0].delta.content;
                }
              } catch {
                // 4) 不是 JSON，就当纯文本片段
                deltaText = payload;
              }

              if (!deltaText) continue;

              fullResponse += deltaText;

              // 实时更新 UI（流式打字效果）
              messages.value[lastIndex] = {
                ...messages.value[lastIndex],
                content: fullResponse,
                isLoading: false, // 让“AI正在思考...”消失
              };

              scrollToBottom();
            }
          }

          // 处理 buffer 里可能残留的最后一段
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

          // 最终收尾：补齐推荐卡片、保存历史等
          finalizeAIMessage(fullResponse);
          saveChatHistory();
          return;
        }

        // ====== B. 非流式输出（axios 一次性返回） ======
        // 你原第一段逻辑基本不变
        // （如果你不想用 axios，也可以用 fetch 非流式写法）
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

    const extractMovieRecommendations = (
      response: string
    ): MovieRecommendation[] => {
      const recommendations: MovieRecommendation[] = [];

      // 简单的关键词匹配
      const movieKeywords = allMovies.value.map((movie) =>
        movie.title.toLowerCase()
      );

      // 检查响应中是否包含电影名称
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

      return recommendations.slice(0, 3); // 最多返回3个推荐
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
          // 转换时间戳字符串为Date对象
          messages.value = history.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp),
          }));
        }
      } catch (error) {
        console.error("加载聊天历史失败:", error);
      }
    };

    const clearChat = () => {
      if (confirm("确定要清空所有对话记录吗？此操作不可撤销。")) {
        messages.value = [];
        localStorage.removeItem("ai_chat_history");
      }
    };

    const toggleDarkMode = () => {
      isDarkMode.value = !isDarkMode.value;
      if (isDarkMode.value) {
        document.documentElement.classList.add("dark-mode");
      } else {
        document.documentElement.classList.remove("dark-mode");
      }
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

    // 初始化
    const init = () => {
      // 加载电影数据
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

      // 加载聊天历史
      loadChatHistory();

      // 检查深色模式
      if (
        window.matchMedia &&
        window.matchMedia("(prefers-color-scheme: dark)").matches
      ) {
        isDarkMode.value = true;
        document.documentElement.classList.add("dark-mode");
      }
    };

    // 生命周期钩子
    onMounted(() => {
      init();
      scrollToBottom();
    });

    // 返回所有需要暴露给模板的属性和方法
    return {
      // 数据
      inputRef,
      autoResize,
      showComposerExtras,
      chatIcon,
      messages,
      userInput,
      isLoading,
      isDarkMode,
      isSidebarCollapsed,
      searchQuery,
      searchResults,
      selectedModel,
      temperature,
      enableMovieRecommendations,
      movieCount,
      genreCount,
      topMovies,
      enableStream,

      // 方法
      formatTime,
      formatAIResponse,
      sendMessage,
      clearChat,
      toggleDarkMode,
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
/* ====== 主题变量（浅色/深色统一管理）====== */
.ai-chat-view {
  --bg: #f6f7fb;
  --panel: rgba(255, 255, 255, 0.85);
  --panel-solid: #ffffff;
  --text: #0f172a;
  --muted: #64748b;
  --border: rgba(15, 23, 42, 0.08);
  --shadow: 0 18px 50px rgba(2, 8, 23, 0.1);
  --shadow-soft: 0 10px 30px rgba(2, 8, 23, 0.08);
  --primary: #6366f1; /* indigo */
  --primary-2: #8b5cf6; /* purple */
  --green: #10b981;
  --amber: #f59e0b;
  --danger: #ef4444;

  --radius-xl: 18px;
  --radius-lg: 14px;
  --radius-md: 12px;

  height: 100vh;
  display: flex;
  background: radial-gradient(
      1200px 700px at 20% 10%,
      rgba(99, 102, 241, 0.18),
      transparent 60%
    ),
    radial-gradient(
      900px 600px at 80% 20%,
      rgba(139, 92, 246, 0.16),
      transparent 55%
    ),
    radial-gradient(
      900px 600px at 60% 90%,
      rgba(16, 185, 129, 0.1),
      transparent 55%
    ),
    var(--bg);
  color: var(--text);
  overflow: hidden;
}

/* 深色主题：你现在是给 chat-container 加 dark-mode，这里同步覆盖变量 */
.chat-container.dark-mode {
  --bg: #0b1220;
  --panel: rgba(17, 24, 39, 0.78);
  --panel-solid: #111827;
  --text: #e5e7eb;
  --muted: #94a3b8;
  --border: rgba(148, 163, 184, 0.14);
  --shadow: 0 24px 70px rgba(0, 0, 0, 0.45);
  --shadow-soft: 0 14px 40px rgba(0, 0, 0, 0.35);
}

/* ====== 顶部 Header ====== */
.chat-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 74px;
  z-index: 1000;

  background: linear-gradient(
    135deg,
    rgba(99, 102, 241, 0.9),
    rgba(139, 92, 246, 0.86)
  );
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);

  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 10px 30px rgba(2, 8, 23, 0.18);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-icon-img {
  width: 28px;
  height: 28px;
  object-fit: contain;
  filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.18));
}

.header-title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.2px;
}

.header-subtitle {
  margin: 2px 0 0;
  font-size: 12px;
  opacity: 0.9;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 统一按钮 */
.clear-btn,
.theme-btn,
.primary-btn,
.secondary-btn,
.tool-btn,
.quick-btn,
.action-btn,
.movie-action-btn,
.sidebar-toggle {
  border: none;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease,
    color 0.15s ease;
}

.clear-btn,
.theme-btn {
  padding: 10px 14px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.95);
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.22);
}

.theme-btn {
  background: rgba(255, 255, 255, 0.95);
  color: rgba(99, 102, 241, 1);
}

.clear-btn:hover:not(:disabled),
.theme-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(2, 8, 23, 0.2);
}

.clear-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

/* ====== 主体布局（侧边栏 + 聊天区）====== */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-top: 74px;
  margin-left: 320px;
  transition: margin-left 0.25s ease;
  background: transparent;
}

/* ====== 侧边栏 ====== */
.sidebar {
  position: fixed;
  left: 0;
  top: 74px;
  bottom: 0;
  width: 320px;
  z-index: 900;

  background: var(--panel);
  border-right: 1px solid var(--border);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);

  overflow: hidden;
  box-shadow: var(--shadow-soft);
}

.sidebar-collapsed {
  transform: translateX(-320px);
}

.sidebar-toggle {
  position: absolute;
  right: -44px;
  top: 18px;
  width: 44px;
  height: 44px;
  border-radius: 0 14px 14px 0;
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: #fff;
  font-size: 16px;
  box-shadow: 0 14px 30px rgba(99, 102, 241, 0.32);
}

.sidebar-toggle:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 40px rgba(99, 102, 241, 0.4);
}

.sidebar-content {
  height: 100%;
  overflow-y: auto;
  padding: 18px;
}

/* sidebar 滚动条 */
.sidebar-content::-webkit-scrollbar {
  width: 10px;
}
.sidebar-content::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.25);
  border-radius: 999px;
  border: 2px solid transparent;
  background-clip: padding-box;
}

.sidebar-title {
  font-size: 16px;
  margin: 0 0 14px 0;
  font-weight: 900;
}

.sidebar-subtitle {
  font-size: 13px;
  margin: 0 0 12px 0;
  color: var(--muted);
  font-weight: 800;
}

.sidebar-section {
  margin-bottom: 18px;
  padding: 14px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.55);
}

.chat-container.dark-mode .sidebar-section {
  background: rgba(17, 24, 39, 0.55);
}

.movie-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-item {
  padding: 12px;
  border-radius: 14px;
  background: linear-gradient(
    180deg,
    rgba(99, 102, 241, 0.1),
    rgba(99, 102, 241, 0.04)
  );
  border: 1px solid rgba(99, 102, 241, 0.16);
  text-align: left;
}

.stat-value {
  font-size: 22px;
  font-weight: 900;
  color: var(--primary);
  margin-bottom: 2px;
}

.stat-label {
  font-size: 12px;
  color: var(--muted);
  font-weight: 700;
}

.search-input {
  width: 100%;
  padding: 11px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.8);
  outline: none;
  color: var(--text);
}

.chat-container.dark-mode .search-input {
  background: rgba(17, 24, 39, 0.7);
}

.search-input:focus {
  border-color: rgba(99, 102, 241, 0.55);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.14);
}

.search-results {
  margin-top: 10px;
  max-height: 220px;
  overflow-y: auto;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.75);
}

.chat-container.dark-mode .search-results {
  background: rgba(17, 24, 39, 0.65);
}

.search-result-item {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--border);
}

.search-result-item:hover {
  background: rgba(99, 102, 241, 0.08);
}

.result-title {
  font-weight: 900;
  font-size: 13px;
}

.result-meta {
  font-size: 12px;
  color: var(--muted);
  margin-top: 2px;
}

.top-movies {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.top-movie-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  border-radius: 14px;
  cursor: pointer;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.65);
}

.chat-container.dark-mode .top-movie-item {
  background: rgba(17, 24, 39, 0.65);
}

.top-movie-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 30px rgba(2, 8, 23, 0.1);
}

.top-movie-rank {
  width: 30px;
  height: 30px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-weight: 900;
  color: #fff;
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
}

.top-movie-title {
  font-weight: 900;
  font-size: 13px;
}

.top-movie-rating {
  font-size: 12px;
  color: var(--muted);
  margin-top: 2px;
}

.settings {
  display: grid;
  gap: 12px;
}

.setting-label {
  font-weight: 800;
  font-size: 12px;
  color: var(--muted);
}

.model-select {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.8);
  color: var(--text);
  outline: none;
}

.chat-container.dark-mode .model-select {
  background: rgba(17, 24, 39, 0.7);
}

.temperature-slider {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  -webkit-appearance: none;
  background: rgba(100, 116, 139, 0.25);
  outline: none;
}
.temperature-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  box-shadow: 0 10px 18px rgba(99, 102, 241, 0.35);
}

/* ====== 消息区 ====== */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 22px 22px 14px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.messages-container::-webkit-scrollbar {
  width: 10px;
}
.messages-container::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.22);
  border-radius: 999px;
  border: 2px solid transparent;
  background-clip: padding-box;
}

/* 欢迎卡片 */
.welcome-message {
  margin: 10px auto 0;
  max-width: 900px;
  background: var(--panel);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-soft);
  border-radius: 22px;
  padding: 26px 18px;
  backdrop-filter: blur(14px);
}

.welcome-title {
  font-size: 22px;
  font-weight: 900;
  margin: 6px 0 8px;
}

.welcome-text {
  color: var(--muted);
  margin: 0 0 12px 0;
}

.welcome-features {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.feature-item {
  border-radius: 14px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.55);
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-container.dark-mode .feature-item {
  background: rgba(17, 24, 39, 0.55);
}

.feature-icon {
  font-size: 18px;
}

.feature-text {
  font-weight: 800;
  font-size: 13px;
}

.welcome-tip {
  margin-top: 14px;
  color: rgba(99, 102, 241, 1);
  font-weight: 800;
}

/* 消息布局 */
.message {
  display: flex;
  gap: 12px;
  max-width: 920px;
}

.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.ai-message {
  align-self: flex-start;
}

/* 头像 */
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 18px;
}

.user-avatar {
  color: #fff;
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  box-shadow: 0 14px 30px rgba(99, 102, 241, 0.28);
}

.ai-avatar {
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid var(--border);
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.chat-container.dark-mode .ai-avatar {
  background: rgba(17, 24, 39, 0.65);
}

.ai-avatar-img {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

/* 消息头 */
.message-content {
  max-width: 720px;
  flex: 1;
}

.message-header {
  display: flex;
  gap: 10px;
  align-items: center;
  margin: 0 0 6px 0;
}

.message-sender {
  font-weight: 900;
  font-size: 12px;
  color: var(--muted);
  letter-spacing: 0.2px;
}

.message-time {
  font-size: 12px;
  color: rgba(100, 116, 139, 0.75);
}

/* 气泡 */
.message-text {
  border-radius: 18px;
  padding: 14px 14px;
  line-height: 1.7;
  font-size: 14px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 10px 24px rgba(2, 8, 23, 0.06);
}

.chat-container.dark-mode .message-text {
  background: rgba(17, 24, 39, 0.7);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.22);
}

.user-message .message-text {
  color: #fff;
  border: none;
  background: linear-gradient(
    135deg,
    rgba(99, 102, 241, 1),
    rgba(139, 92, 246, 1)
  );
  box-shadow: 0 18px 42px rgba(99, 102, 241, 0.28);
}

/* AI 富文本强调 */
.ai-response strong {
  color: rgba(99, 102, 241, 1);
}
.ai-response em {
  color: var(--muted);
}
.ai-response code {
  background: rgba(2, 8, 23, 0.06);
  padding: 2px 6px;
  border-radius: 8px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    "Liberation Mono", "Courier New", monospace;
}
.chat-container.dark-mode .ai-response code {
  background: rgba(255, 255, 255, 0.1);
}

/* Loading 点 */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
}
.loading-dots {
  display: flex;
  gap: 6px;
}
.loading-dots span {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.9);
  animation: bounce 1.2s infinite ease-in-out both;
}
.loading-dots span:nth-child(1) {
  animation-delay: -0.24s;
}
.loading-dots span:nth-child(2) {
  animation-delay: -0.12s;
}
.loading-text {
  font-size: 13px;
  font-weight: 800;
  color: rgba(99, 102, 241, 1);
}

/* 推荐卡片：现代化 */
.movie-recommendations {
  margin-top: 12px;
  border-radius: 18px;
  border: 1px solid rgba(99, 102, 241, 0.2);
  background: linear-gradient(
    180deg,
    rgba(99, 102, 241, 0.09),
    rgba(99, 102, 241, 0.03)
  );
  padding: 14px;
}

.recommendations-title {
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 900;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.movie-card {
  border-radius: 16px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.82);
  padding: 14px;
  box-shadow: 0 16px 40px rgba(2, 8, 23, 0.08);
}
.chat-container.dark-mode .movie-card {
  background: rgba(17, 24, 39, 0.72);
}

.movie-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 22px 55px rgba(2, 8, 23, 0.12);
}

.movie-card-header {
  display: flex;
  gap: 10px;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.movie-title {
  margin: 0;
  font-size: 14px;
  font-weight: 900;
}

.movie-rating {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.14);
  border: 1px solid rgba(245, 158, 11, 0.22);
  font-weight: 900;
  font-size: 12px;
  color: var(--amber);
}

.movie-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.meta-item {
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  color: rgba(99, 102, 241, 1);
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.16);
}

.movie-description {
  margin: 0 0 12px 0;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.6;
}

.movie-actions {
  display: flex;
  gap: 10px;
}

.movie-action-btn {
  padding: 9px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 900;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.movie-action-btn:first-child {
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: #fff;
  box-shadow: 0 16px 36px rgba(99, 102, 241, 0.26);
}

.movie-action-btn:last-child {
  background: rgba(16, 185, 129, 0.14);
  color: rgba(16, 185, 129, 1);
  border: 1px solid rgba(16, 185, 129, 0.22);
}

.movie-action-btn:hover {
  transform: translateY(-1px);
}

/* 消息操作按钮 */
.message-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.action-btn {
  padding: 8px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.75);
  color: var(--text);
  font-weight: 900;
  font-size: 12px;
}

.chat-container.dark-mode .action-btn {
  background: rgba(17, 24, 39, 0.72);
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 30px rgba(2, 8, 23, 0.1);
}

/* 输入区域：悬浮底部面板 */
.input-container {
  padding: 14px 18px 18px;
  background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.62));
  border-top: 1px solid var(--border);
  backdrop-filter: blur(12px);
}

.chat-container.dark-mode .input-container {
  background: linear-gradient(180deg, transparent, rgba(17, 24, 39, 0.7));
}

.message-input {
  width: 100%;
  padding: 14px 14px;
  border-radius: 18px;
  border: 1px solid var(--border);
  outline: none;
  resize: none;
  font-size: 14px;
  line-height: 1.6;
  background: rgba(255, 255, 255, 0.85);
  color: var(--text);
  box-shadow: 0 16px 40px rgba(2, 8, 23, 0.08);
}

.chat-container.dark-mode .message-input {
  background: rgba(17, 24, 39, 0.75);
}

.message-input:focus {
  border-color: rgba(99, 102, 241, 0.55);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.14),
    0 18px 48px rgba(2, 8, 23, 0.1);
}

.input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  gap: 12px;
  flex-wrap: wrap;
}

.input-tools {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tool-btn {
  padding: 9px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.72);
  font-size: 12px;
  font-weight: 900;
  color: var(--text);
}

.chat-container.dark-mode .tool-btn {
  background: rgba(17, 24, 39, 0.7);
}

.tool-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 30px rgba(2, 8, 23, 0.1);
}

.send-actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.secondary-btn {
  padding: 10px 14px;
  border-radius: 14px;
  border: 1px solid rgba(99, 102, 241, 0.35);
  background: rgba(99, 102, 241, 0.1);
  color: rgba(99, 102, 241, 1);
  font-weight: 900;
  font-size: 13px;
}

.primary-btn {
  padding: 10px 16px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: #fff;
  font-weight: 900;
  font-size: 13px;
  box-shadow: 0 18px 40px rgba(99, 102, 241, 0.28);
}

.primary-btn:hover:not(:disabled),
.secondary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.primary-btn:disabled,
.secondary-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.send-icon {
  font-size: 14px;
}

/* 输入提示 */
.input-hints {
  margin-top: 12px;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.6);
}

.chat-container.dark-mode .input-hints {
  background: rgba(17, 24, 39, 0.55);
}

.hint-text {
  margin: 0 0 10px 0;
  color: var(--muted);
  font-weight: 800;
  font-size: 12px;
}

.quick-questions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 9px 12px;
  border-radius: 999px;
  border: 1px solid rgba(99, 102, 241, 0.3);
  background: rgba(99, 102, 241, 0.1);
  color: rgba(99, 102, 241, 1);
  font-weight: 900;
  font-size: 12px;
}

.quick-btn:hover {
  transform: translateY(-1px);
}

/* typing indicator */
.typing-indicator {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px 14px;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.72);
  max-width: 720px;
}

.chat-container.dark-mode .typing-indicator {
  background: rgba(17, 24, 39, 0.7);
}

.typing-dots {
  display: flex;
  gap: 6px;
}
.typing-dots span {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.9);
  animation: bounce 1.2s infinite ease-in-out both;
}
.typing-dots span:nth-child(1) {
  animation-delay: -0.24s;
}
.typing-dots span:nth-child(2) {
  animation-delay: -0.12s;
}

.typing-text {
  font-size: 12px;
  font-weight: 900;
  color: rgba(99, 102, 241, 1);
}

.typing-avatar-img {
  width: 22px;
  height: 22px;
}

/* 动画 */
@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0.2);
    opacity: 0.45;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* ====== 响应式 ====== */
@media (max-width: 1024px) {
  .chat-container {
    margin-left: 0;
  }
  .sidebar {
    transform: translateX(-320px);
  }
  .sidebar-collapsed {
    transform: translateX(0);
  }
}

@media (max-width: 768px) {
  .chat-header {
    height: 66px;
    padding: 0 14px;
  }
  .chat-container {
    margin-top: 66px;
  }
  .messages-container {
    padding: 14px 14px 10px;
  }
  .welcome-features {
    grid-template-columns: 1fr;
  }
  .message {
    max-width: 100%;
  }
}

/* 输入区整体：固定底部 + 居中窄宽 */
.input-container {
  position: sticky;
  bottom: 0;
  padding: 14px 16px 16px;
  border-top: 1px solid var(--border);
  background: transparent;
  backdrop-filter: none;
}

/* 输入区内容居中 */
.input-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

/* 输入框：更像 ChatGPT 的“圆角卡片” */
.message-input {
  border-radius: 18px;
  padding: 12px 44px 12px 14px; /* 右边给发送按钮留空间 */
  min-height: 48px;
  max-height: 160px;
  box-shadow: 0 18px 50px rgba(2, 8, 23, 0.1);
}

/* 让 textarea 更像单行输入（你可选：配合 JS 自动增高更好） */
.message-input {
  overflow-y: auto;
}

/* actions 行：更紧凑 */
.input-actions {
  margin-top: 10px;
  gap: 10px;
}

/* 工具按钮更轻 */
.tool-btn {
  padding: 8px 10px;
  font-size: 12px;
  border-radius: 999px;
}

/* 发送按钮：ChatGPT 风格右侧“圆形图标按钮” */
.send-actions {
  margin-left: auto;
}

.primary-btn {
  padding: 10px 12px;
  border-radius: 999px;
  width: 44px;
  height: 44px;
  justify-content: center;
}

.primary-btn .send-icon {
  font-size: 16px;
}

/* 折叠提示区域更像附加面板 */
.input-hints {
  max-width: 900px;
  margin: 10px auto 0;
  padding: 12px;
  border-radius: 16px;
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.18s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

/* 输入区整体更紧凑 */
.input-container {
  padding: 12px 16px 14px;
}

/* 输入框更像 ChatGPT：高度小、左右留白舒服 */
.message-input {
  min-height: 44px;
  padding: 10px 14px;
  border-radius: 18px;
}

/* 把 actions 行压扁一点 */
.input-actions {
  margin-top: 8px;
}

/* 发送按钮改成圆形（你现在 primary-btn 已经圆了，但把文字隐藏更像） */
.primary-btn {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  padding: 0;
}

/* 隐藏“发送中/发送”文字，只留图标 */
.primary-btn {
  font-size: 0;
}
.primary-btn .send-icon {
  font-size: 16px;
}

/* 清空按钮更轻（可选） */
.secondary-btn {
  padding: 10px 12px;
  border-radius: 999px;
}

/* 默认让更多区域更“薄”一点 */
.input-hints {
  padding: 10px 12px;
}
</style>
