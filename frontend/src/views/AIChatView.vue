<template>
  <div class="chat-app" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <aside class="chat-sidebar">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="newChat">
          <span>+</span> 新对话
        </button>
      </div>

      <div class="conversation-list">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          class="conv-item"
          :class="{ active: conv.id === activeConvId }"
          @click="switchConv(conv.id)"
        >
          <div class="conv-title">{{ conv.title || "新对话" }}</div>
          <div class="conv-meta">
            <span>{{ formatConvTime(conv.updatedAt) }}</span>
            <span>{{ conv.messages.length }} 条</span>
          </div>

          <button
            class="conv-del"
            title="删除"
            @click.stop="deleteConv(conv.id)"
          >
            ×
          </button>
        </div>

        <div v-if="conversations.length === 0" class="no-convs">
          暂无对话记录
        </div>
      </div>

      <div class="sidebar-footer" v-if="authStore.isAuthenticated">
        <router-link to="/profile" class="sidebar-user">
          👤 {{ authStore.user?.username || "用户" }}
        </router-link>
      </div>
    </aside>

    <button
      class="toggle-sidebar-btn"
      :title="sidebarCollapsed ? '展开对话记录' : '收起对话记录'"
      @click="toggleSidebar"
    >
      {{ sidebarCollapsed ? "▶" : "◀" }}
    </button>

    <main class="chat-main">
      <div class="chat-messages" ref="msgContainer">
        <div v-if="activeMessages.length === 0" class="welcome-area">
          <div class="welcome-logo">🎬</div>
          <h2>AI 电影助手</h2>
          <p>我可以帮你推荐电影、分析剧情、介绍导演演员，随时向我提问。</p>

          <div class="welcome-prompts">
            <button
              v-for="p in quickPrompts"
              :key="p"
              class="prompt-chip"
              :disabled="sending"
              @click="sendMessage(p)"
            >
              {{ p }}
            </button>
          </div>
        </div>

        <div
          v-for="(msg, index) in activeMessages"
          :key="`${index}-${msg.role}`"
          class="msg-row"
          :class="msg.role"
        >
          <div class="msg-avatar">
            {{ msg.role === "user" ? "👤" : "🤖" }}
          </div>

          <div class="msg-body">
            <div
              v-if="msg.role === 'assistant'"
              class="msg-content"
              v-html="formatContent(msg.content)"
            ></div>

            <div v-else class="msg-content">
              {{ msg.content }}
            </div>

            <div v-if="msg.isLoading" class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>

            <div v-if="msg.movies && msg.movies.length" class="msg-movies">
              <div
                v-for="m in msg.movies"
                :key="m.id"
                class="mini-movie-card"
                @click="goToMovie(m)"
              >
                <div class="mm-title">{{ m.title }}</div>
                <div class="mm-meta">
                  ⭐ {{ m.rating || "暂无评分" }} · {{ m.year || "未知年份" }} ·
                  {{ m.genre || "未知类型" }}
                </div>
                <div v-if="m.reason" class="mm-reason">
                  {{ m.reason }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input-bar">
        <textarea
          ref="textareaRef"
          v-model="inputText"
          class="chat-textarea"
          placeholder="输入你的问题..."
          rows="1"
          @keydown.enter.exact.prevent="sendMessage()"
          @keydown.enter.shift.exact.stop
          @input="autoResize"
        ></textarea>

        <button v-if="sending" class="stop-btn" @click="stopGenerate">
          停止
        </button>

        <button
          class="send-btn"
          :disabled="!inputText.trim() || sending"
          @click="sendMessage()"
        >
          发送
        </button>
      </div>
    </main>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  ref,
  computed,
  nextTick,
  watch,
  onMounted,
  onBeforeUnmount,
} from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const API_BASE_URL = "http://localhost:8000/api";

interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
  updatedAt: number;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  isLoading?: boolean;
  movies?: MovieCard[];
}

interface MovieCard {
  id: number;
  title: string;
  rating?: string | number;
  year?: string | number;
  genre?: string;
  reason?: string;
}

interface StreamParseResult {
  text: string;
  done: boolean;
  movies?: MovieCard[];
  error?: string;
}

export default defineComponent({
  name: "AIChatView",

  setup() {
    const authStore = useAuthStore();
    const router = useRouter();

    const sidebarCollapsed = ref(
      localStorage.getItem("ai_sidebar_collapsed") === "1"
    );
    const inputText = ref("");
    const sending = ref(false);
    const activeConvId = ref<string | null>(null);
    const conversations = ref<Conversation[]>([]);

    const msgContainer = ref<HTMLElement | null>(null);
    const textareaRef = ref<HTMLTextAreaElement | null>(null);

    const abortController = ref<AbortController | null>(null);

    const quickPrompts = [
      "最近有什么好看的科幻电影？",
      "分析一下《肖申克的救赎》",
      "推荐几部适合周末看的喜剧",
      "诺兰的电影风格有什么特点？",
    ];

    const storageKey = computed(() => {
      return `ai_conv_${authStore.user?.id || "guest"}`;
    });

    const activeConversation = computed(() => {
      return (
        conversations.value.find((c) => c.id === activeConvId.value) || null
      );
    });

    const activeMessages = computed(() => {
      return activeConversation.value?.messages || [];
    });

    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value;
      localStorage.setItem(
        "ai_sidebar_collapsed",
        sidebarCollapsed.value ? "1" : "0"
      );
    };

    const loadConversations = () => {
      const raw = localStorage.getItem(storageKey.value);

      if (!raw) {
        conversations.value = [];
        activeConvId.value = null;
        return;
      }

      try {
        const parsed = JSON.parse(raw) as Conversation[];

        conversations.value = Array.isArray(parsed)
          ? parsed.filter(
              (item) => item && item.id && Array.isArray(item.messages)
            )
          : [];
      } catch {
        conversations.value = [];
      }

      activeConvId.value =
        conversations.value.length > 0
          ? conversations.value[conversations.value.length - 1].id
          : null;
    };

    const saveConversations = () => {
      localStorage.setItem(
        storageKey.value,
        JSON.stringify(conversations.value)
      );
    };

    const createConversation = () => {
      const now = Date.now();

      const conv: Conversation = {
        id: `${now}_${Math.random().toString(36).slice(2, 8)}`,
        title: "",
        messages: [],
        createdAt: now,
        updatedAt: now,
      };

      conversations.value.push(conv);
      activeConvId.value = conv.id;
      saveConversations();

      return conv;
    };

    const newChat = async () => {
      createConversation();
      await nextTick();
      textareaRef.value?.focus();
    };

    const switchConv = async (id: string) => {
      if (sending.value) return;

      activeConvId.value = id;
      await scrollBottom();
    };

    const deleteConv = (id: string) => {
      if (sending.value) return;

      conversations.value = conversations.value.filter((c) => c.id !== id);

      if (activeConvId.value === id) {
        activeConvId.value =
          conversations.value.length > 0
            ? conversations.value[conversations.value.length - 1].id
            : null;
      }

      saveConversations();
    };

    const getAuthHeaders = (): Record<string, string> => {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      const token =
        localStorage.getItem("access") ||
        localStorage.getItem("access_token") ||
        localStorage.getItem("token");

      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      return headers;
    };

    const sendMessage = async (presetText?: string) => {
      const content = (presetText || inputText.value).trim();
      if (!content || sending.value) return;

      let conv = activeConversation.value;
      if (!conv) {
        conv = createConversation();
      }

      if (!conv.title) {
        conv.title =
          content.length > 18 ? `${content.slice(0, 18)}...` : content;
      }

      const userMsg: ChatMessage = {
        role: "user",
        content,
      };

      const aiMsg: ChatMessage = {
        role: "assistant",
        content: "",
        isLoading: true,
      };

      conv.messages.push(userMsg, aiMsg);
      conv.updatedAt = Date.now();

      inputText.value = "";
      resetTextareaHeight();
      saveConversations();
      await scrollBottom();

      sending.value = true;
      abortController.value = new AbortController();

      try {
        const response = await fetch(`${API_BASE_URL}/ai/chat/`, {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            message: content,
            model: "deepseek-chat",
            temperature: 0.7,
            stream: true,
          }),
          signal: abortController.value.signal,
        });

        if (!response.ok) {
          aiMsg.content = `请求失败：HTTP ${response.status}`;
          aiMsg.isLoading = false;
          return;
        }

        const contentType = response.headers.get("content-type") || "";

        if (contentType.includes("application/json")) {
          const data = await response.json();
          applyNormalResponse(aiMsg, data);
          aiMsg.isLoading = false;
          conv.updatedAt = Date.now();
          return;
        }

        if (!response.body) {
          aiMsg.content = "当前浏览器或后端响应不支持流式读取。";
          aiMsg.isLoading = false;
          return;
        }

        await readStreamResponse(response, aiMsg, conv, contentType);
      } catch (error: unknown) {
        if ((error as Error).name === "AbortError") {
          if (!aiMsg.content) {
            aiMsg.content = "已停止生成。";
          }
        } else {
          if (!aiMsg.content) {
            aiMsg.content = "网络连接失败，请检查后端服务是否正常运行。";
          }
        }

        aiMsg.isLoading = false;
      } finally {
        sending.value = false;
        abortController.value = null;
        aiMsg.isLoading = false;
        conv.updatedAt = Date.now();
        saveConversations();
        await scrollBottom();
      }
    };

    const readStreamResponse = async (
      response: Response,
      aiMsg: ChatMessage,
      conv: Conversation,
      contentType: string
    ) => {
      const reader = response.body!.getReader();
      const decoder = new TextDecoder("utf-8");

      let buffer = "";
      let structuredMode =
        contentType.includes("text/event-stream") ||
        contentType.includes("application/x-ndjson") ||
        contentType.includes("application/jsonl");
      let reading = true;
      while (reading) {
        const { done, value } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        if (
          !structuredMode &&
          (chunk.includes("data:") || chunk.trimStart().startsWith("{"))
        ) {
          structuredMode = true;
        }

        if (!structuredMode) {
          appendAssistantText(aiMsg, chunk);
          conv.updatedAt = Date.now();
          await scrollBottom();
          continue;
        }

        buffer += chunk;
        const lines = buffer.split(/\r?\n/);
        buffer = lines.pop() || "";

        for (const rawLine of lines) {
          const line = rawLine.trim();

          if (!line || line.startsWith(":") || line.startsWith("event:")) {
            continue;
          }

          const payload = line.startsWith("data:")
            ? line.slice(5).trim()
            : line;

          const parsed = parseStreamPayload(payload);

          if (parsed.error) {
            aiMsg.content = parsed.error;
            aiMsg.isLoading = false;
            continue;
          }

          if (parsed.movies?.length) {
            aiMsg.movies = parsed.movies;
          }

          if (parsed.text) {
            appendAssistantText(aiMsg, parsed.text);
            conv.updatedAt = Date.now();
            await scrollBottom();
          }

          if (parsed.done) {
            aiMsg.isLoading = false;
          }
        }
      }

      const tail = buffer.trim();

      if (tail) {
        const payload = tail.startsWith("data:") ? tail.slice(5).trim() : tail;

        const parsed = parseStreamPayload(payload);

        if (parsed.error) {
          aiMsg.content = parsed.error;
        }

        if (parsed.movies?.length) {
          aiMsg.movies = parsed.movies;
        }

        if (parsed.text) {
          appendAssistantText(aiMsg, parsed.text);
        }
      }

      aiMsg.isLoading = false;
    };

    const parseStreamPayload = (payload: string): StreamParseResult => {
      if (!payload || payload === "[DONE]") {
        return {
          text: "",
          done: true,
        };
      }

      try {
        const obj = JSON.parse(payload);

        if (obj.error) {
          return {
            text: "",
            done: true,
            error:
              typeof obj.error === "string" ? obj.error : "AI 服务返回错误。",
          };
        }

        const text =
          obj.content ??
          obj.delta ??
          obj.text ??
          obj.response ??
          obj.message ??
          obj.result ??
          obj.choices?.[0]?.delta?.content ??
          obj.choices?.[0]?.message?.content ??
          "";

        return {
          text: typeof text === "string" ? text : "",
          done: Boolean(obj.done || obj.finished),
          movies: Array.isArray(obj.movies) ? obj.movies : undefined,
        };
      } catch {
        return {
          text: payload,
          done: false,
        };
      }
    };

    const applyNormalResponse = (aiMsg: ChatMessage, data: any) => {
      const text =
        data.content ??
        data.response ??
        data.message ??
        data.text ??
        data.result ??
        data.choices?.[0]?.message?.content ??
        "";

      aiMsg.content = typeof text === "string" ? text : JSON.stringify(text);

      if (Array.isArray(data.movies)) {
        aiMsg.movies = data.movies;
      }
    };

    const appendAssistantText = (aiMsg: ChatMessage, text: string) => {
      if (!text) return;

      aiMsg.content += text;
      aiMsg.isLoading = false;
    };

    const stopGenerate = () => {
      abortController.value?.abort();
      sending.value = false;
    };

    const scrollBottom = async () => {
      await nextTick();

      const el = msgContainer.value;
      if (!el) return;

      el.scrollTop = el.scrollHeight;
    };

    const autoResize = () => {
      const el = textareaRef.value;
      if (!el) return;

      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    };

    const resetTextareaHeight = () => {
      const el = textareaRef.value;
      if (!el) return;

      el.style.height = "auto";
    };

    const escapeHtml = (text: string) => {
      return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    };

    const formatContent = (text: string) => {
      const safe = escapeHtml(text || "");

      return safe
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\n/g, "<br />");
    };

    const formatConvTime = (ts: number) => {
      const d = new Date(ts);
      const now = new Date();

      if (d.toDateString() === now.toDateString()) {
        return d.toLocaleTimeString("zh-CN", {
          hour: "2-digit",
          minute: "2-digit",
        });
      }

      return d.toLocaleDateString("zh-CN", {
        month: "short",
        day: "numeric",
      });
    };

    const goToMovie = (m: MovieCard) => {
      const detail = {
        id: m.id,
        movie_id: m.id,
        电影名字: m.title,
        电影链接: "",
        评分: m.rating || "",
        评分人数: "",
        导演: "",
        主演: "",
        年份: m.year || "",
        国家: "",
        类型: m.genre || "",
        一句话评价: "",
      };

      sessionStorage.setItem("current_movie_detail", JSON.stringify(detail));

      router.push({
        path: "/movie-detail",
        query: {
          movie_id: String(m.id),
          movie_title: m.title,
        },
      });
    };

    watch(
      () => authStore.user?.id,
      () => {
        loadConversations();
      },
      {
        immediate: true,
      }
    );

    onMounted(() => {
      textareaRef.value?.focus();
    });

    onBeforeUnmount(() => {
      abortController.value?.abort();
    });

    return {
      authStore,
      sidebarCollapsed,
      inputText,
      sending,
      activeConvId,
      conversations,
      activeMessages,
      msgContainer,
      textareaRef,
      quickPrompts,
      toggleSidebar,
      newChat,
      switchConv,
      deleteConv,
      sendMessage,
      stopGenerate,
      autoResize,
      formatContent,
      formatConvTime,
      goToMovie,
    };
  },
});
</script>

<style scoped>
.chat-app {
  --sidebar-width: 300px;

  position: relative;
  display: flex;
  height: calc(100vh - 60px);
  margin: -20px;
  background: radial-gradient(
      circle at top right,
      rgba(99, 102, 241, 0.18),
      transparent 32%
    ),
    radial-gradient(
      circle at bottom center,
      rgba(20, 184, 166, 0.14),
      transparent 34%
    ),
    var(--bg-main, #0f172a);
  overflow: hidden;
}

.chat-sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  height: 100%;
  background: var(--panel-bg, rgba(30, 41, 59, 0.92));
  border-right: 1px solid var(--panel-border, rgba(148, 163, 184, 0.18));
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.25s ease, min-width 0.25s ease, opacity 0.2s ease,
    border-color 0.2s ease;
  z-index: 40;
}

.chat-app.sidebar-collapsed .chat-sidebar {
  width: 0;
  min-width: 0;
  opacity: 0;
  pointer-events: none;
  border-right-color: transparent;
}

.toggle-sidebar-btn {
  position: absolute;
  top: 50%;
  left: calc(var(--sidebar-width) - 1px);
  transform: translateY(-50%);
  z-index: 80;
  width: 34px;
  height: 58px;
  border: 1px solid var(--panel-border, rgba(148, 163, 184, 0.22));
  border-left: none;
  border-radius: 0 14px 14px 0;
  background: var(--panel-bg, rgba(30, 41, 59, 0.96));
  color: var(--text-secondary, #cbd5e1);
  cursor: pointer;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: left 0.25s ease, background 0.2s ease, color 0.2s ease;
}

.toggle-sidebar-btn:hover {
  background: var(--nav-hover-bg, rgba(99, 102, 241, 0.18));
  color: var(--text-primary, #f8fafc);
}

.chat-app.sidebar-collapsed .toggle-sidebar-btn {
  left: 0;
}

.sidebar-header {
  padding: 14px 12px;
  border-bottom: 1px solid var(--panel-border, rgba(148, 163, 184, 0.18));
}

.new-chat-btn {
  width: 100%;
  height: 44px;
  border: 1px solid var(--panel-border, rgba(148, 163, 184, 0.22));
  border-radius: var(--radius-md, 14px);
  background: var(--primary-bg, rgba(99, 102, 241, 0.2));
  color: var(--text-primary, #f8fafc);
  font-weight: 700;
  font-size: 0.92rem;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease;
}

.new-chat-btn:hover {
  background: var(--nav-hover-bg, rgba(99, 102, 241, 0.28));
  transform: translateY(-1px);
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 8px;
}

.conv-item {
  position: relative;
  padding: 12px 36px 12px 14px;
  border-radius: var(--radius-md, 14px);
  cursor: pointer;
  margin-bottom: 6px;
  transition: background 0.2s ease, transform 0.2s ease;
}

.conv-item:hover {
  background: var(--nav-hover-bg, rgba(99, 102, 241, 0.18));
}

.conv-item.active {
  background: var(--nav-active-bg, rgba(99, 102, 241, 0.28));
}

.conv-title {
  font-weight: 700;
  color: var(--text-primary, #f8fafc);
  font-size: 0.92rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv-meta {
  display: flex;
  gap: 8px;
  margin-top: 5px;
  font-size: 0.78rem;
  color: var(--text-muted, #94a3b8);
}

.conv-del {
  position: absolute;
  right: 9px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--text-muted, #94a3b8);
  cursor: pointer;
  font-size: 1.15rem;
  line-height: 1;
  opacity: 0;
  transition: opacity 0.2s ease, background 0.2s ease, color 0.2s ease;
}

.conv-item:hover .conv-del {
  opacity: 1;
}

.conv-del:hover {
  background: rgba(239, 68, 68, 0.16);
  color: #ef4444;
}

.no-convs {
  text-align: center;
  color: var(--text-muted, #94a3b8);
  padding: 24px 12px;
  font-size: 0.9rem;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--panel-border, rgba(148, 163, 184, 0.18));
}

.sidebar-user {
  color: var(--text-secondary, #cbd5e1);
  text-decoration: none;
  font-weight: 700;
  font-size: 0.9rem;
}

.chat-main {
  flex: 1;
  min-width: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: transparent;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 28px 48px;
  display: flex;
  flex-direction: column;
  gap: 22px;
  scroll-behavior: smooth;
}

.welcome-area {
  text-align: center;
  margin: auto;
  padding: 40px 20px;
  max-width: 560px;
}

.welcome-logo {
  font-size: 3.1rem;
  margin-bottom: 12px;
}

.welcome-area h2 {
  margin: 0 0 10px;
  color: var(--text-primary, #f8fafc);
  font-size: 1.6rem;
}

.welcome-area p {
  color: var(--text-secondary, #cbd5e1);
  line-height: 1.8;
  margin-bottom: 22px;
}

.welcome-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.prompt-chip {
  padding: 9px 16px;
  border-radius: var(--radius-full, 999px);
  border: 1px solid var(--panel-border, rgba(148, 163, 184, 0.22));
  background: var(--panel-bg, rgba(30, 41, 59, 0.86));
  color: var(--text-secondary, #cbd5e1);
  cursor: pointer;
  font-size: 0.88rem;
  transition: border-color 0.2s ease, color 0.2s ease, background 0.2s ease,
    transform 0.2s ease;
}

.prompt-chip:hover:not(:disabled) {
  border-color: var(--primary, #8b5cf6);
  color: var(--text-primary, #f8fafc);
  background: var(--nav-hover-bg, rgba(99, 102, 241, 0.18));
  transform: translateY(-1px);
}

.prompt-chip:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.msg-row {
  display: flex;
  gap: 12px;
  max-width: 880px;
  width: fit-content;
}

.msg-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.msg-row.assistant {
  align-self: flex-start;
}

.msg-avatar {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--nav-hover-bg, rgba(99, 102, 241, 0.18));
  font-size: 1rem;
}

.msg-row.user .msg-avatar {
  background: var(
    --primary-gradient,
    linear-gradient(135deg, #7c3aed, #6366f1)
  );
}

.msg-body {
  max-width: min(780px, calc(100vw - 180px));
}

.msg-row.user .msg-body {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.msg-content {
  padding: 13px 17px;
  border-radius: 18px;
  line-height: 1.75;
  font-size: 0.96rem;
  color: var(--text-primary, #f8fafc);
  background: var(--panel-bg, rgba(30, 41, 59, 0.88));
  border: 1px solid var(--panel-border, rgba(148, 163, 184, 0.18));
  overflow-wrap: break-word;
  word-break: break-word;
}

.msg-row.assistant .msg-content {
  border-top-left-radius: 8px;
}

.msg-row.user .msg-content {
  background: var(
    --primary-gradient,
    linear-gradient(135deg, #7c3aed, #6366f1)
  );
  color: #fff;
  border: none;
  border-top-right-radius: 8px;
}

.typing-dots {
  display: flex;
  gap: 5px;
  padding: 8px 4px 0;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted, #94a3b8);
  animation: bounce 1.2s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
  }

  30% {
    transform: translateY(-6px);
  }
}

.msg-movies {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.mini-movie-card {
  padding: 11px 14px;
  border-radius: var(--radius-md, 14px);
  background: var(--primary-bg, rgba(99, 102, 241, 0.18));
  border: 1px solid var(--panel-border, rgba(148, 163, 184, 0.18));
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  max-width: 260px;
}

.mini-movie-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--panel-shadow, 0 14px 30px rgba(0, 0, 0, 0.22));
}

.mm-title {
  font-weight: 800;
  color: var(--text-primary, #f8fafc);
  margin-bottom: 5px;
  font-size: 0.92rem;
}

.mm-meta {
  font-size: 0.82rem;
  color: var(--text-secondary, #cbd5e1);
  margin-bottom: 5px;
}

.mm-reason {
  font-size: 0.82rem;
  color: var(--text-muted, #94a3b8);
  line-height: 1.5;
}

.chat-input-bar {
  padding: 14px 28px 18px;
  border-top: 1px solid var(--panel-border, rgba(148, 163, 184, 0.18));
  display: flex;
  gap: 10px;
  align-items: flex-end;
  background: rgba(15, 23, 42, 0.28);
  backdrop-filter: blur(12px);
}

.chat-textarea {
  flex: 1;
  min-height: 44px;
  max-height: 160px;
  padding: 12px 16px;
  border-radius: 22px;
  border: 1px solid var(--input-border, rgba(148, 163, 184, 0.22));
  background: var(--panel-bg, rgba(30, 41, 59, 0.88));
  color: var(--text-primary, #f8fafc);
  font-size: 0.95rem;
  resize: none;
  outline: none;
  line-height: 1.5;
  font-family: inherit;
}

.chat-textarea:focus {
  border-color: var(--input-focus-border, #8b5cf6);
  box-shadow: var(--input-focus-shadow, 0 0 0 3px rgba(139, 92, 246, 0.18));
}

.send-btn,
.stop-btn {
  height: 44px;
  padding: 0 20px;
  border-radius: 22px;
  border: none;
  color: #fff;
  font-weight: 800;
  cursor: pointer;
  font-size: 0.9rem;
  transition: transform 0.2s ease, opacity 0.2s ease;
  flex-shrink: 0;
}

.send-btn {
  background: var(
    --primary-gradient,
    linear-gradient(135deg, #7c3aed, #6366f1)
  );
}

.stop-btn {
  background: linear-gradient(135deg, #ef4444, #f97316);
}

.send-btn:hover:not(:disabled),
.stop-btn:hover {
  transform: translateY(-1px);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

:deep(code) {
  background: var(--nav-hover-bg, rgba(99, 102, 241, 0.18));
  padding: 2px 6px;
  border-radius: 5px;
  font-size: 0.9em;
}

:deep(strong) {
  color: var(--text-primary, #f8fafc);
  font-weight: 800;
}

@media (max-width: 768px) {
  .chat-app {
    --sidebar-width: 82vw;
  }

  .chat-sidebar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    box-shadow: 10px 0 28px rgba(0, 0, 0, 0.28);
  }

  .chat-app.sidebar-collapsed .chat-sidebar {
    transform: translateX(-100%);
    width: var(--sidebar-width);
    min-width: var(--sidebar-width);
    opacity: 1;
  }

  .toggle-sidebar-btn {
    left: calc(var(--sidebar-width) - 1px);
  }

  .chat-app.sidebar-collapsed .toggle-sidebar-btn {
    left: 0;
  }

  .chat-messages {
    padding: 18px 16px;
  }

  .msg-body {
    max-width: calc(100vw - 90px);
  }

  .chat-input-bar {
    padding: 12px 14px 14px;
  }

  .send-btn,
  .stop-btn {
    padding: 0 16px;
  }
}
</style>
