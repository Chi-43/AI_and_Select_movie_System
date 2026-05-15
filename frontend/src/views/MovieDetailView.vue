<template>
  <div class="movie-detail-view">
    <div v-if="!movie" class="error-section panel-card">
      <div class="error-icon">⚠️</div>
      <h2>未找到电影信息</h2>
      <p>请从首页或电影库重新进入电影详情页。</p>
      <router-link to="/" class="primary-btn">返回首页</router-link>
    </div>

    <template v-else>
      <section class="hero-section">
        <div class="poster-wrap">
          <img
            v-if="extraDetail?.poster && !posterLoadFailed"
            :src="`http://localhost:8000/api/image-proxy/?url=${encodeURIComponent(
              extraDetail.poster
            )}`"
            :alt="movie['电影名字']"
            class="poster"
            @error="handlePosterError"
          />
          <div v-else class="poster-placeholder">
            <span class="poster-icon">🎬</span>
            <span class="poster-text">电影海报</span>
          </div>
        </div>

        <div class="hero-content">
          <div class="hero-badge">电影详情</div>

          <div class="title-row">
            <h1 class="movie-title">{{ movie["电影名字"] }}</h1>
            <span class="year-badge">{{ movie["年份"] || "未知年份" }}</span>
          </div>

          <p class="sub-title">
            {{ movie["国家"] || "未知国家" }} ·
            {{ movie["类型"] || "未知类型" }}
          </p>

          <div class="rating-row">
            <div class="rating-card">
              <span class="rating-star">⭐</span>
              <span class="rating-value">{{
                movie["评分"] || "暂无评分"
              }}</span>
              <span class="rating-count" v-if="movie['评分人数']">
                {{ movie["评分人数"] }} 人评分
              </span>
            </div>
          </div>
          <div v-if="isLoggedIn" class="user-rating-row">
            <div class="user-rating-label">我的评分</div>
            <StarRating
              v-model="userRating"
              :disabled="ratingLoading"
              @update:modelValue="submitRating"
            />
            <span v-if="avgRating !== null" class="avg-rating-info">
              均分 {{ avgRating }}（{{ ratingCount }}人）
            </span>
          </div>
          <div v-else class="user-rating-row">
            <span class="rating-login-tip">登录后即可评分</span>
          </div>
          <div class="tag-row">
            <span v-for="tag in movieTypes" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>

          <div class="meta-grid">
            <div class="meta-item">
              <span class="meta-label">导演</span>
              <span class="meta-value">{{ movie["导演"] || "未知" }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">主演</span>
              <span class="meta-value">{{ movie["主演"] || "未知" }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">年份</span>
              <span class="meta-value">{{ movie["年份"] || "未知" }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">国家/地区</span>
              <span class="meta-value">{{ movie["国家"] || "未知" }}</span>
            </div>
          </div>

          <div class="action-row">
            <router-link
              :to="{
                name: 'video-platform',
                query: {
                  movie_title: movie['电影名字'],
                  douban_url: movie['电影链接'],
                },
              }"
              class="action-btn primary"
            >
              📺 查看观看链接
            </router-link>

            <button class="action-btn secondary" @click="handleFavorite">
              {{ isFavorite ? "❤️ 已收藏" : "🤍 收藏" }}
            </button>
            <button
              class="action-btn secondary"
              @click="
                fetchMyCollections();
                showCollectionModal = true;
              "
            >
              📚 加入片单
            </button>
          </div>

          <!-- 加入片单弹窗 -->
          <div
            v-if="showCollectionModal"
            class="modal-mask"
            @click.self="showCollectionModal = false"
          >
            <div class="modal-card collection-modal">
              <h3>选择片单</h3>
              <div v-if="myCollections.length === 0" class="no-coll">
                你还没有片单，先去创建一个吧
              </div>
              <div v-else class="coll-list">
                <div
                  v-for="c in myCollections"
                  :key="c.id"
                  class="coll-opt"
                  @click="addToCollection(c.id)"
                >
                  {{ c.title }}（{{ c.movie_count }}部）
                </div>
              </div>
              <button class="cancel-btn" @click="showCollectionModal = false">
                关闭
              </button>
            </div>
          </div>

          <div class="feedback-bar">
            <button
              class="feedback-btn"
              :class="{ active: currentFeedback === 'like' }"
              @click="handleLike"
              :disabled="feedbackLoading"
            >
              👍 点赞
              <span class="feedback-count">{{
                feedbackSummary.like_count
              }}</span>
            </button>

            <button
              class="feedback-btn"
              :class="{ active: currentFeedback === 'dislike' }"
              @click="handleDislike"
              :disabled="feedbackLoading"
            >
              👎 点踩
              <span class="feedback-count">{{
                feedbackSummary.dislike_count
              }}</span>
            </button>

            <button
              v-if="currentFeedback"
              class="feedback-btn neutral"
              @click="clearFeedback"
              :disabled="feedbackLoading"
            >
              取消反馈
            </button>
          </div>
        </div>
      </section>

      <section class="content-grid">
        <div class="main-column">
          <!-- <div class="panel-card">
            <h2>一句话评价</h2>
            <p class="summary">
              {{ movie["一句话评价"] || "暂无一句话评价" }}
            </p>
          </div> -->

          <div class="panel-card">
            <div class="panel-header">
              <h2>剧情简介</h2>
              <span v-if="extraLoading" class="loading-badge">加载中...</span>
            </div>

            <p v-if="extraLoading" class="summary placeholder-text">
              正在加载剧情简介...
            </p>

            <p v-else-if="extraDetail?.summary" class="summary">
              {{ extraDetail.summary }}
            </p>

            <p v-else class="summary placeholder-text">暂无剧情简介</p>
          </div>

          <div class="panel-card comment-panel">
            <div class="panel-header">
              <h2>用户评论</h2>
              <span class="comment-count">共 {{ comments.length }} 条评论</span>
            </div>

            <div class="comment-box" v-if="isLoggedIn">
              <textarea
                v-model="commentText"
                placeholder="写下你对这部电影的看法..."
                class="comment-input"
                maxlength="500"
              ></textarea>

              <div class="comment-actions">
                <span class="comment-length">{{ commentText.length }}/500</span>
                <button
                  class="primary-btn"
                  @click="submitComment"
                  :disabled="commentLoading || !commentText.trim()"
                >
                  {{ commentLoading ? "发布中..." : "发表评论" }}
                </button>
              </div>
            </div>

            <div v-else class="comment-login-tip">登录后即可发表评论。</div>

            <div v-if="commentsLoading" class="comment-loading">
              加载评论中...
            </div>

            <div v-else-if="comments.length === 0" class="comment-empty">
              暂无评论，快来发表第一条评论吧。
            </div>

            <div v-else class="comment-list">
              <div v-for="item in comments" :key="item.id" class="comment-item">
                <div class="comment-user-row">
                  <div class="comment-user">
                    <div class="user-avatar">
                      {{ getUserInitial(item.user?.username) }}
                    </div>
                    <div class="user-meta">
                      <router-link
                        :to="'/user/' + item.user?.id"
                        class="username-link"
                      >
                        {{ item.user?.username || "匿名用户" }}
                      </router-link>
                      <div class="time">
                        {{ formatDateTime(item.created_at) }}
                      </div>
                    </div>
                  </div>

                  <button
                    v-if="
                      currentUser &&
                      item.user &&
                      currentUser.id === item.user.id
                    "
                    class="delete-comment-btn"
                    @click="deleteComment(item.id)"
                  >
                    删除
                  </button>
                </div>

                <div class="comment-content">{{ item.content }}</div>

                <div class="comment-footer">
                  <button
                    v-if="isLoggedIn"
                    class="reply-toggle-btn"
                    @click="toggleReplyInput(item.id)"
                  >
                    💬 回复
                  </button>
                </div>

                <!-- 回复列表 -->
                <div
                  v-if="item.replies && item.replies.length > 0"
                  class="replies-section"
                >
                  <div
                    v-for="reply in item.replies"
                    :key="reply.id"
                    class="reply-item"
                  >
                    <div class="reply-user">
                      <router-link
                        :to="'/user/' + reply.user?.id"
                        class="reply-username-link"
                      >
                        {{ reply.user?.username || "匿名" }}
                      </router-link>
                      <span class="reply-time">{{
                        formatDateTime(reply.created_at)
                      }}</span>
                    </div>
                    <div class="reply-content">{{ reply.content }}</div>
                  </div>
                </div>

                <!-- 回复输入框 -->
                <div v-if="replyingTo === item.id" class="reply-input-row">
                  <input
                    v-model="replyText"
                    type="text"
                    placeholder="写下你的回复..."
                    class="reply-input"
                    maxlength="200"
                    @keyup.enter="submitReply(item.id)"
                  />
                  <button
                    class="reply-submit-btn"
                    @click="submitReply(item.id)"
                    :disabled="replyLoading || !replyText.trim()"
                  >
                    {{ replyLoading ? "..." : "发送" }}
                  </button>
                  <button class="reply-cancel-btn" @click="cancelReply">
                    取消
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="side-column">
          <div class="panel-card">
            <h3>基础信息</h3>
            <ul class="side-list">
              <li>
                <strong>电影名:</strong> {{ movie["电影名字"] || "未知" }}
              </li>
              <li><strong>评分:</strong> {{ movie["评分"] || "暂无" }}</li>
              <li><strong>年份:</strong> {{ movie["年份"] || "未知" }}</li>
              <li><strong>国家:</strong> {{ movie["国家"] || "未知" }}</li>
              <li><strong>类型:</strong> {{ movie["类型"] || "未知" }}</li>
            </ul>
          </div>

          <div class="panel-card">
            <div class="panel-header">
              <h3>扩展信息</h3>
              <span v-if="extraLoading" class="loading-badge">加载中...</span>
            </div>

            <div v-if="extraError" class="placeholder-text">
              {{ extraError }}
            </div>

            <ul v-else-if="extraDetail" class="side-list">
              <!-- <li>
                <strong>英文名:</strong>
                {{ extraDetail.english_title || "暂无" }}
              </li> -->
              <!-- <li>
                <strong>IMDb:</strong>
                {{ extraDetail.imdb || "暂无" }}
              </li> -->
              <li>
                <strong>上映日期:</strong>
                {{ joinList(extraDetail.release_dates) }}
              </li>
              <li>
                <strong>片长:</strong>
                {{ joinList(extraDetail.runtime) }}
              </li>
              <li>
                <strong>语言:</strong>
                {{ joinList(extraDetail.languages) }}
              </li>
              <li>
                <strong>又名:</strong>
                {{ joinList(extraDetail.aka) }}
              </li>
              <!-- <li>
                <strong>编剧:</strong>
                {{ joinList(extraDetail.writer) }}
              </li> -->
              <li>
                <strong>主演:</strong>
                {{ joinList(extraDetail.actors) }}
              </li>
            </ul>

            <div v-else class="placeholder-text">暂无扩展信息</div>
          </div>

          <div class="panel-card">
            <h3>互动统计</h3>
            <div class="stats-box">
              <div class="mini-stat">
                <div class="mini-stat-value">
                  {{ feedbackSummary.like_count }}
                </div>
                <div class="mini-stat-label">点赞数</div>
              </div>
              <div class="mini-stat">
                <div class="mini-stat-value">
                  {{ feedbackSummary.dislike_count }}
                </div>
                <div class="mini-stat-label">点踩数</div>
              </div>
              <div class="mini-stat">
                <div class="mini-stat-value">{{ comments.length }}</div>
                <div class="mini-stat-label">评论数</div>
              </div>
            </div>
          </div>

          <div
            class="panel-card"
            v-if="similarMovies.length > 0 || similarLoading"
          >
            <h3>看了又看</h3>
            <div v-if="similarLoading" class="placeholder-text">加载中...</div>
            <ul v-else class="similar-list">
              <li
                v-for="item in similarMovies"
                :key="item.movie.id"
                class="similar-item"
                @click="goToSimilarMovie(item.movie)"
              >
                <div class="similar-title">{{ item.movie.title }}</div>
                <div class="similar-meta">
                  <span>⭐ {{ item.movie.rating }}</span>
                  <span>{{ item.movie.year }}</span>
                </div>
              </li>
            </ul>
          </div>

          <div class="panel-card">
            <h3>外部入口</h3>
            <a
              :href="movie['电影链接']"
              target="_blank"
              rel="noopener noreferrer"
              class="external-link"
            >
              打开原始豆瓣页
            </a>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import StarRating from "@/components/StarRating.vue";

interface DoubanMovie {
  id?: number;
  movie_id?: number;
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

interface MovieExtraDetail {
  movie_id?: number;
  movie_title?: string;
  english_title?: string;
  douban_url?: string;
  poster?: string;
  rating?: string;
  rating_count?: string;
  director?: string[];
  writer?: string[];
  actors?: string[];
  genres?: string[];
  countries?: string[];
  languages?: string[];
  release_dates?: string[];
  runtime?: string[];
  aka?: string[];
  imdb?: string;
  summary?: string;
  year?: string;
  source?: string;
}

interface CommentUser {
  id: number;
  username: string;
}

interface ReplyItem {
  id: number;
  user?: CommentUser;
  content: string;
  created_at: string;
}

interface CommentItem {
  id: number;
  user?: CommentUser;
  content: string;
  created_at: string;
  updated_at: string;
  replies?: ReplyItem[];
  reply_count?: number;
}

const API_BASE_URL = "http://localhost:8000";

export default defineComponent({
  name: "MovieDetailView",
  components: { StarRating },
  setup() {
    const authStore = useAuthStore();

    const movie = ref<DoubanMovie | null>(null);
    const commentText = ref("");
    const favoriteLinks = ref<Set<string>>(new Set());

    const extraDetail = ref<MovieExtraDetail | null>(null);
    const extraLoading = ref(false);
    const extraError = ref("");
    const posterLoadFailed = ref(false);

    const feedbackLoading = ref(false);
    const commentLoading = ref(false);
    const commentsLoading = ref(false);

    const comments = ref<CommentItem[]>([]);
    const similarMovies = ref<any[]>([]);
    const similarLoading = ref(false);
    const replyingTo = ref<number | null>(null);
    const replyText = ref("");
    const replyLoading = ref(false);
    const showCollectionModal = ref(false);
    const myCollections = ref<any[]>([]);

    const feedbackSummary = ref({
      like_count: 0,
      dislike_count: 0,
      current_user_feedback: null as string | null,
    });

    const userRating = ref(0);
    const ratingLoading = ref(false);
    const avgRating = ref<number | null>(null);
    const ratingCount = ref(0);
    const currentUser = computed(() => authStore.user);
    const isLoggedIn = computed(() => Boolean(authStore.token));

    const movieTypes = computed(() => {
      if (!movie.value?.["类型"]) return [];
      return movie.value["类型"]
        .split(/[ /、,，]+/)
        .map((item) => item.trim())
        .filter(Boolean);
    });

    const loadFavorites = () => {
      const saved = localStorage.getItem("movie_favorites");
      const favorites: string[] = saved ? JSON.parse(saved) : [];
      favoriteLinks.value = new Set(favorites);
    };

    const handlePosterError = () => {
      posterLoadFailed.value = true;
    };
    const currentFeedback = computed(
      () => feedbackSummary.value.current_user_feedback
    );

    const isFavorite = computed(() => {
      if (!movie.value) return false;
      // const saved = localStorage.getItem("movie_favorites");
      // const favorites: string[] = saved ? JSON.parse(saved) : [];
      // return favorites.includes(movie.value["电影链接"]);
      return favoriteLinks.value.has(movie.value["电影链接"]);
    });

    const joinList = (arr?: string[]) => {
      if (!arr || arr.length === 0) return "暂无";
      return arr.join(" / ");
    };

    const getUserInitial = (username?: string) => {
      if (!username) return "?";
      return username.charAt(0).toUpperCase();
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

    const getErrorMessage = (error: unknown) => {
      if (error instanceof Error) return error.message;
      return "请求失败";
    };

    const getMovieIdFromSession = (): number | null => {
      const saved = sessionStorage.getItem("current_movie_detail");
      if (!saved) return null;

      try {
        const parsed = JSON.parse(saved) as DoubanMovie;

        if (parsed.movie_id) return parsed.movie_id;
        if (parsed.id) return parsed.id;

        return null;
      } catch {
        return null;
      }
    };

    const getAuthHeaders = (): Record<string, string> => {
      const headers: Record<string, string> = {};
      if (authStore.token) {
        headers.Authorization = `Token ${authStore.token}`;
      }
      headers["Content-Type"] = "application/json";
      return headers;
    };

    const getTokenHeaders = (): Record<string, string> => {
      const headers: Record<string, string> = {};
      if (authStore.token) {
        headers.Authorization = `Token ${authStore.token}`;
      }
      return headers;
    };

    const loadMovieFromSession = () => {
      const saved = sessionStorage.getItem("current_movie_detail");
      if (!saved) return;

      try {
        movie.value = JSON.parse(saved) as DoubanMovie;
      } catch (error) {
        console.error("解析 sessionStorage 电影详情失败:", error);
      }
    };

    const fetchExtraDetail = async () => {
      if (!movie.value?.["电影链接"]) return;

      extraLoading.value = true;
      extraError.value = "";

      try {
        const params = new URLSearchParams();
        params.append("douban_url", movie.value["电影链接"]);
        params.append("movie_title", movie.value["电影名字"]);

        const response = await fetch(
          `${API_BASE_URL}/api/movie-detail/?${params.toString()}`
        );

        if (!response.ok) {
          throw new Error(`请求失败: ${response.status}`);
        }

        const data = (await response.json()) as MovieExtraDetail;
        extraDetail.value = data;

        // 关键修复：把后端返回的 movie_id 写回当前电影对象
        if (movie.value && data.movie_id) {
          movie.value.movie_id = data.movie_id;
          sessionStorage.setItem(
            "current_movie_detail",
            JSON.stringify(movie.value)
          );
          console.log("后端返回详情数据：", data);
        }
      } catch (error: unknown) {
        console.error("获取扩展详情失败:", error);
        extraError.value = "扩展详情加载失败，当前已显示基础信息";
      } finally {
        extraLoading.value = false;
      }
    };

    const loadFeedbackSummary = async () => {
      const movieId = getMovieIdFromSession();
      if (!movieId || !authStore.token) return;

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/movie-feedback/?movie_id=${movieId}`,
          {
            headers: getTokenHeaders(),
          }
        );

        if (!response.ok) {
          throw new Error(`获取反馈失败: ${response.status}`);
        }

        const data = (await response.json()) as {
          like_count?: number;
          dislike_count?: number;
          current_user_feedback?: string | null;
        };

        feedbackSummary.value = {
          like_count: data.like_count || 0,
          dislike_count: data.dislike_count || 0,
          current_user_feedback: data.current_user_feedback || null,
        };
      } catch (error) {
        console.error("加载点赞/点踩统计失败:", error);
      }
    };

    const submitFeedback = async (feedbackType: "like" | "dislike") => {
      const movieId = getMovieIdFromSession();

      if (!movieId) {
        alert("未获取到电影ID,无法提交反馈");
        return;
      }

      if (!authStore.token) {
        alert("请先登录后再进行点赞或点踩");
        return;
      }

      feedbackLoading.value = true;
      try {
        const response = await fetch(`${API_BASE_URL}/api/movie-feedback/`, {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            movie_id: movieId,
            feedback_type: feedbackType,
          }),
        });

        const data = (await response.json()) as { error?: string };

        if (!response.ok) {
          throw new Error(data.error || "提交反馈失败");
        }

        await loadFeedbackSummary();
      } catch (error: unknown) {
        console.error("提交反馈失败:", error);
        alert(getErrorMessage(error));
      } finally {
        feedbackLoading.value = false;
      }
    };

    const clearFeedback = async () => {
      const movieId = getMovieIdFromSession();

      if (!movieId || !authStore.token) return;

      feedbackLoading.value = true;
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/movie-feedback/?movie_id=${movieId}`,
          {
            method: "DELETE",
            headers: getTokenHeaders(),
          }
        );

        const data = (await response.json()) as { error?: string };

        if (!response.ok) {
          throw new Error(data.error || "取消反馈失败");
        }

        await loadFeedbackSummary();
      } catch (error: unknown) {
        console.error("取消反馈失败:", error);
        alert(getErrorMessage(error));
      } finally {
        feedbackLoading.value = false;
      }
    };
    const loadRating = async () => {
      const movieId = getMovieIdFromSession();
      if (!movieId || !authStore.token) return;

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/movie-ratings/?movie_id=${movieId}`,
          { headers: getTokenHeaders() }
        );

        if (!response.ok) throw new Error("获取评分失败");

        const data = (await response.json()) as {
          user_rating?: number | null;
          avg_rating?: number | null;
          rating_count?: number;
        };

        userRating.value = data.user_rating || 0;
        avgRating.value = data.avg_rating ?? null;
        ratingCount.value = data.rating_count || 0;
      } catch (error) {
        console.error("加载评分失败:", error);
      }
    };

    const loadSimilarMovies = async () => {
      const movieId = getMovieIdFromSession();
      if (!movieId) return;

      similarLoading.value = true;
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/similar-movies/${movieId}/`
        );
        if (response.ok) {
          const data = await response.json();
          similarMovies.value = data.similar_movies || [];
        }
      } catch (error) {
        console.error("加载相似电影失败:", error);
      } finally {
        similarLoading.value = false;
      }
    };

    const goToSimilarMovie = (item: any) => {
      const detailMovie = {
        id: item.id,
        movie_id: item.id,
        电影名字: item.title,
        电影链接: item.douban_url || "",
        评分: String(item.rating || ""),
        评分人数: "",
        导演: item.director || "",
        主演: item.actors || "",
        年份: String(item.year || ""),
        国家: item.country || "",
        类型: item.genre || "",
        一句话评价: item.quote || "",
      };
      sessionStorage.setItem(
        "current_movie_detail",
        JSON.stringify(detailMovie)
      );
      window.scrollTo(0, 0);
      movie.value = detailMovie;
      extraDetail.value = null;
      extraError.value = "";
      comments.value = [];
      similarMovies.value = [];
      feedbackSummary.value = {
        like_count: 0,
        dislike_count: 0,
        current_user_feedback: null,
      };
      userRating.value = 0;
      avgRating.value = null;
      ratingCount.value = 0;
      fetchExtraDetail();
      if (isLoggedIn.value) {
        loadRating();
        loadFeedbackSummary();
        loadComments();
        loadSimilarMovies();
      }
    };

    const submitRating = async (value: number) => {
      const movieId = getMovieIdFromSession();

      if (!movieId) {
        alert("未获取到电影ID，无法提交评分");
        return;
      }

      if (!authStore.token) {
        alert("请先登录后再进行评分");
        return;
      }

      ratingLoading.value = true;
      try {
        const response = await fetch(`${API_BASE_URL}/api/movie-ratings/`, {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({ movie_id: movieId, rating: value }),
        });

        const data = (await response.json()) as { error?: string };

        if (!response.ok) {
          throw new Error(data.error || "提交评分失败");
        }

        userRating.value = value;
        await loadRating();
      } catch (error: unknown) {
        console.error("提交评分失败:", error);
        alert(getErrorMessage(error));
      } finally {
        ratingLoading.value = false;
      }
    };
    const clearRating = async () => {
      const movieId = getMovieIdFromSession();

      if (!movieId || !authStore.token) return;

      ratingLoading.value = true;
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/movie-ratings/?movie_id=${movieId}`,
          { method: "DELETE", headers: getTokenHeaders() }
        );

        if (!response.ok) {
          const data = (await response.json()) as { error?: string };
          throw new Error(data.error || "删除评分失败");
        }

        userRating.value = 0;
        await loadRating();
      } catch (error: unknown) {
        console.error("删除评分失败:", error);
        alert(getErrorMessage(error));
      } finally {
        ratingLoading.value = false;
      }
    };
    const loadComments = async () => {
      const movieId = getMovieIdFromSession();

      if (!movieId || !authStore.token) return;

      commentsLoading.value = true;
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/movie-comments/?movie_id=${movieId}`,
          {
            headers: getTokenHeaders(),
          }
        );

        const data = (await response.json()) as {
          results?: CommentItem[];
          comments?: CommentItem[];
          count?: number;
          error?: string;
        };

        if (!response.ok) {
          throw new Error(data.error || "获取评论失败");
        }

        comments.value = data.results || data.comments || [];
      } catch (error) {
        console.error("加载评论失败:", error);
        comments.value = [];
      } finally {
        commentsLoading.value = false;
      }
    };

    const submitComment = async () => {
      const movieId = getMovieIdFromSession();

      if (!movieId) {
        alert("未获取到电影ID,无法发表评论");
        return;
      }

      if (!authStore.token) {
        alert("请先登录后再发表评论");
        return;
      }

      if (!commentText.value.trim()) {
        alert("请输入评论内容");
        return;
      }

      commentLoading.value = true;
      try {
        const response = await fetch(`${API_BASE_URL}/api/movie-comments/`, {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            movie_id: movieId,
            content: commentText.value.trim(),
          }),
        });

        const data = (await response.json()) as { error?: string };

        if (!response.ok) {
          throw new Error(data.error || "发表评论失败");
        }

        commentText.value = "";
        await loadComments();
      } catch (error: unknown) {
        console.error("发表评论失败:", error);
        alert(getErrorMessage(error));
      } finally {
        commentLoading.value = false;
      }
    };

    const toggleReplyInput = (commentId: number) => {
      if (replyingTo.value === commentId) {
        replyingTo.value = null;
        replyText.value = "";
      } else {
        replyingTo.value = commentId;
        replyText.value = "";
      }
    };

    const cancelReply = () => {
      replyingTo.value = null;
      replyText.value = "";
    };

    const submitReply = async (commentId: number) => {
      const movieId = getMovieIdFromSession();
      if (!movieId || !authStore.token || !replyText.value.trim()) return;

      replyLoading.value = true;
      try {
        const response = await fetch(`${API_BASE_URL}/api/movie-comments/`, {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            movie_id: movieId,
            parent_id: commentId,
            content: replyText.value.trim(),
          }),
        });

        const data = (await response.json()) as { error?: string };
        if (!response.ok) throw new Error(data.error || "回复失败");

        replyText.value = "";
        replyingTo.value = null;
        await loadComments();
      } catch (error: unknown) {
        console.error("回复失败:", error);
        alert(getErrorMessage(error));
      } finally {
        replyLoading.value = false;
      }
    };

    const deleteComment = async (commentId: number) => {
      if (!authStore.token) return;
      if (!confirm("确定要删除这条评论吗？")) return;

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/movie-comments/${commentId}/`,
          {
            method: "DELETE",
            headers: getTokenHeaders(),
          }
        );

        const data = (await response.json()) as { error?: string };

        if (!response.ok) {
          throw new Error(data.error || "删除评论失败");
        }

        await loadComments();
      } catch (error: unknown) {
        console.error("删除评论失败:", error);
        alert(getErrorMessage(error));
      }
    };

    const fetchMyCollections = async () => {
      if (!authStore.token || !authStore.user) return;
      try {
        const r = await fetch(
          `${API_BASE_URL}/collections/?user_id=${authStore.user.id}`
        );
        if (r.ok) {
          const d = await r.json();
          myCollections.value = d.results || [];
        }
      } catch {
        /* 加载失败 */
      }
    };

    const addToCollection = async (collectionId: number) => {
      const movieId = getMovieIdFromSession();
      if (!movieId) {
        alert("未获取到电影ID，请先从电影库进入详情页");
        return;
      }
      if (!authStore.token) {
        alert("请先登录");
        return;
      }
      try {
        const r = await fetch(`${API_BASE_URL}/collections/movies/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${authStore.token}`,
          },
          body: JSON.stringify({
            collection_id: collectionId,
            movie_id: movieId,
          }),
        });
        if (r.ok) {
          alert("已加入片单");
          showCollectionModal.value = false;
        } else {
          const d = await r.json().catch(() => ({}));
          alert((d as any).error || "加入失败");
        }
      } catch {
        alert("操作失败");
      }
    };

    const handleFavorite = () => {
      if (!movie.value) return;

      const movieLink = movie.value["电影链接"];
      const exists = favoriteLinks.value.has(movieLink);

      if (exists) {
        favoriteLinks.value.delete(movieLink);
      } else {
        favoriteLinks.value.add(movieLink);
      }

      localStorage.setItem(
        "movie_favorites",
        JSON.stringify(Array.from(favoriteLinks.value))
      );

      alert(exists ? "已取消收藏" : "收藏成功");
    };

    const handleLike = async () => {
      await submitFeedback("like");
    };

    const handleDislike = async () => {
      await submitFeedback("dislike");
    };

    onMounted(async () => {
      loadMovieFromSession();
      loadFavorites();
      await fetchExtraDetail();
      loadSimilarMovies();

      if (isLoggedIn.value) {
        await loadRating();
        await loadFeedbackSummary();
        await loadComments();
        fetchMyCollections();
      }
    });

    return {
      movie,
      commentText,
      extraDetail,
      extraLoading,
      extraError,
      movieTypes,
      joinList,
      currentUser,
      isLoggedIn,
      isFavorite,
      comments,
      similarMovies,
      similarLoading,
      commentsLoading,
      commentLoading,
      feedbackLoading,
      feedbackSummary,
      currentFeedback,
      userRating,
      ratingLoading,
      avgRating,
      ratingCount,
      submitRating,
      clearRating,
      formatDateTime,
      getUserInitial,
      replyingTo,
      replyText,
      replyLoading,
      toggleReplyInput,
      cancelReply,
      submitReply,
      submitComment,
      deleteComment,
      showCollectionModal,
      myCollections,
      addToCollection,
      handleFavorite,
      handleLike,
      handleDislike,
      clearFeedback,
      posterLoadFailed,
      handlePosterError,
    };
  },
});
</script>

<style scoped>
.movie-detail-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: 100vh;
  padding: 24px;
  max-width: var(--max-width);
  margin: 0 auto;
  color: var(--text-primary);
}

.panel-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  backdrop-filter: var(--panel-blur);
  -webkit-backdrop-filter: var(--panel-blur);
  padding: 22px;
}

.error-section {
  text-align: center;
  padding: 80px 20px;
}

.error-icon {
  font-size: 42px;
  margin-bottom: 12px;
}

.hero-section {
  background: var(--bg-hero);
  border-radius: var(--radius-lg);
  box-shadow: var(--panel-shadow);
  padding: 28px;
  color: #fff;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 28px;
  align-items: start;
}

.poster-wrap {
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.poster {
  width: 100%;
  max-width: 280px;
  border-radius: 20px;
  object-fit: cover;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
}

.poster-placeholder {
  width: 280px;
  height: 400px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.12);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
}

.poster-icon {
  font-size: 48px;
}

.poster-text {
  color: rgba(255, 255, 255, 0.9);
}

.hero-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.16);
  font-size: 0.9rem;
  margin-bottom: 14px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.movie-title {
  margin: 0;
  font-size: 2.2rem;
  font-weight: 900;
  color: #fff;
}

.sub-title {
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.7;
}

.year-badge,
.tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.year-badge {
  background: rgba(245, 158, 11, 0.18);
  color: #fff;
}

.rating-row {
  margin-top: 18px;
}

.rating-card {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  font-weight: 900;
}

.rating-value {
  font-size: 1.2rem;
}

.rating-count {
  color: rgba(255, 255, 255, 0.88);
  font-weight: 600;
}

.tag-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 18px;
}

.tag {
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 20px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.1);
}

.meta-label {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.78);
  font-weight: 700;
}

.meta-value {
  font-size: 14px;
  line-height: 1.6;
  color: #fff;
}

.action-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 20px;
}

.feedback-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 18px;
}

.feedback-btn {
  border: none;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  transition: all var(--transition-fast);
}

.feedback-btn.active {
  background: #fff;
  color: #111827;
}

.feedback-btn.neutral {
  background: rgba(239, 68, 68, 0.18);
  color: #fff;
}

.feedback-count {
  margin-left: 8px;
  font-weight: 800;
}

.action-btn,
.primary-btn,
.external-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  border: none;
  cursor: pointer;
  border-radius: var(--radius-md);
  padding: 10px 16px;
  font-weight: 900;
  transition: all var(--transition-fast);
}

.action-btn.primary,
.primary-btn {
  background: var(--primary-gradient);
  color: #fff;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.action-btn:hover,
.primary-btn:hover,
.external-link:hover,
.feedback-btn:hover {
  transform: translateY(-1px);
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.main-column,
.side-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.panel-card h2,
.panel-card h3 {
  margin: 0;
  color: var(--text-primary);
}

.loading-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 800;
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.summary {
  line-height: 1.9;
  color: var(--text-secondary);
  margin: 0;
}

.placeholder-text {
  color: var(--text-muted);
}

.comment-count {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.comment-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-input {
  min-height: 120px;
  border: 1px solid var(--input-border);
  border-radius: var(--radius-md);
  padding: 14px;
  resize: vertical;
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
  font-size: 0.96rem;
  line-height: 1.7;
}

.comment-input:focus {
  border-color: var(--input-focus-border);
  box-shadow: var(--input-focus-shadow);
}

.comment-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.comment-length {
  color: var(--text-muted);
  font-size: 0.84rem;
}

.comment-login-tip,
.comment-empty,
.comment-loading {
  margin-top: 14px;
  color: var(--text-muted);
}

.comment-list {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.comment-item {
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  padding: 16px;
}

.comment-user-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username-link,
.reply-username-link {
  font-weight: 700;
  color: var(--text-primary);
  text-decoration: none;
}

.username-link:hover,
.reply-username-link:hover {
  color: var(--primary);
  text-decoration: underline;
}

.username {
  font-weight: 700;
  color: var(--text-primary);
}

.time {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.comment-content {
  color: var(--text-secondary);
  line-height: 1.8;
  white-space: pre-wrap;
}

.comment-footer {
  margin-top: 10px;
}

.reply-toggle-btn {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.85rem;
  cursor: pointer;
  padding: 4px 0;
  transition: color var(--transition-fast);
}

.reply-toggle-btn:hover {
  color: var(--primary);
}

.replies-section {
  margin-top: 12px;
  padding-left: 12px;
  border-left: 2px solid var(--panel-border);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reply-item {
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: var(--panel-bg);
}

.reply-user {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.reply-username {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.reply-time {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.reply-content {
  color: var(--text-secondary);
  font-size: 0.92rem;
  line-height: 1.7;
}

.reply-input-row {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  align-items: center;
}

.reply-input {
  flex: 1;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  font-size: 0.9rem;
  outline: none;
}

.reply-input:focus {
  border-color: var(--input-focus-border);
}

.reply-submit-btn {
  border: none;
  border-radius: var(--radius-sm);
  padding: 8px 14px;
  background: var(--primary-gradient);
  color: #fff;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
}

.reply-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reply-cancel-btn {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.85rem;
  cursor: pointer;
  padding: 8px 4px;
}

.reply-cancel-btn:hover {
  color: var(--text-secondary);
}

.delete-comment-btn {
  border: none;
  background: #ef4444;
  color: #fff;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 700;
}

.side-list {
  margin: 0;
  padding-left: 18px;
  line-height: 1.9;
  color: var(--text-secondary);
}

.stats-box {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.mini-stat {
  padding: 14px 10px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  text-align: center;
}

.mini-stat-value {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--primary);
  margin-bottom: 4px;
}

.mini-stat-label {
  font-size: 0.84rem;
  color: var(--text-secondary);
}

.similar-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.similar-item {
  padding: 10px 12px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.similar-item:hover {
  transform: translateY(-1px);
  box-shadow: var(--panel-shadow);
}

.similar-title {
  color: var(--text-primary);
  font-weight: 700;
  margin-bottom: 4px;
}

.similar-meta {
  display: flex;
  gap: 10px;
  font-size: 0.84rem;
  color: var(--text-secondary);
}

.collection-modal {
  max-width: 400px;
}
.collection-modal h3 {
  margin: 0 0 14px;
  color: var(--text-primary);
}
.no-coll {
  color: var(--text-muted);
  margin-bottom: 14px;
}
.coll-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 14px;
  max-height: 240px;
  overflow-y: auto;
}
.coll-opt {
  padding: 12px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  border: 1px solid var(--panel-border);
  cursor: pointer;
  color: var(--text-primary);
  font-weight: 600;
  transition: all var(--transition-fast);
}
.coll-opt:hover {
  border-color: var(--primary);
  background: var(--nav-hover-bg);
}

.external-link {
  width: 100%;
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

@media (max-width: 1000px) {
  .hero-section {
    grid-template-columns: 1fr;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .meta-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .movie-detail-view {
    padding: 16px;
  }

  .hero-section,
  .panel-card {
    padding: 18px;
  }

  .movie-title {
    font-size: 1.7rem;
  }

  .action-row,
  .feedback-bar,
  .comment-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .stats-box {
    grid-template-columns: 1fr;
  }
  .user-rating-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 14px;
    flex-wrap: wrap;
  }

  .user-rating-label {
    font-size: 0.9rem;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.88);
  }

  .avg-rating-info {
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.65);
  }

  .rating-login-tip {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.55);
  }
}
</style>
