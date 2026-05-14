# 基于协同过滤与 AI 的电影推荐系统

融合协同过滤算法与大语言模型的智能电影推荐系统，前后端分离架构，支持个性化推荐、自然语言交互、社区讨论、电影片单与用户画像分析。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Django 5 + Django REST Framework |
| 数据库 | MySQL |
| 推荐算法 | 协同过滤（User-based / Item-based）、冷启动、热门排行 |
| AI 能力 | DeepSeek API（推荐理由生成、自然语言推荐、智能对话，支持 SSE 流式输出） |
| 科学计算 | NumPy / scikit-learn |
| 爬虫 | Selenium + BeautifulSoup |
| 前端框架 | Vue 3 + TypeScript |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| HTTP | Axios |
| 样式 | 原生 CSS（深色/浅色主题切换） |

## 功能特性

### 用户系统
- 注册 / 登录 / 注销（Token + Session 双认证）
- 新用户注册后引导完成 4 步兴趣偏好选择
- 个人信息管理（头像上传、简介编辑、密码修改）
- 公开个人主页：查看任意用户的评分记录、评论、偏好标签、收藏（支持公开/私密控制）

### 推荐引擎
- **用户协同过滤**：基于用户-电影评分矩阵 + 余弦相似度，找相似用户预测评分
- **冷启动推荐**：根据偏好标签（类型/国家/年份/关键词）筛选高分电影
- **自然语言推荐**：输入观影需求 → AI 解析意图 → 硬过滤候选池 → 结合 CF 排序
- **热门排行**：评分数据不足时自动用豆瓣高分电影兜底
- **相似电影（看了又看）**：基于物品协同过滤，电影详情页右侧展示
- **推荐持久化**：首次推荐结果存入数据库，刷新页面不丢失；点击"换一批"才重新生成
- **推荐理由生成**：DeepSeek 为每条推荐生成个性化中文理由

### 电影浏览
- 豆瓣 TOP250 电影数据，支持名称/导演/主演搜索与多维筛选（年份/评分/国家/类型）
- 多维度排序（评分、年份、名称）
- 电影详情页（海报、导演、演员、剧情简介、扩展信息）
- 视频平台链接查询（支持爱奇艺、腾讯、优酷、B站、Netflix 等，豆瓣实时抓取）
- 电影收藏（localStorage）

### 用户互动
- **星级评分**（1-5 星），实时更新平均分
- **点赞 / 点踩**，统计展示
- **二级评论**：一级评论 + 嵌套回复，用户名点击可查看对方主页，支持分页

### 用户画像
- 冷启动兴趣选择（类型/国家/年份/关键词）
- 根据评分行为自动更新偏好
- 画像总结自动生成，兴趣偏好可随时修改
- 公开收藏夹开关

### AI 智能助手
- 多会话管理（新建/切换/删除对话），对话历史按用户隔离持久化
- AI 问答模式 + 智能推荐模式
- 支持 SSE 流式输出和非流式输出
- 快速提问提示、Markdown 渲染

### 社区讨论区
- 5 个预设话题（电影推荐、观影讨论、导演与演员、影视杂谈、经典老片）
- 发帖支持 Markdown 渲染 + 配图上传
- 二级回复（嵌套评论）+ 点赞/拉踩，按热度排序
- 帖子列表分页、浏览量统计

### 电影片单（豆列）
- 创建片单（标题/描述/封面图/公开私密切换），创建时可搜索并添加电影
- 片单广场：公开片单全员可见，私密片单仅创建者自己可见
- 片单详情：搜索添加电影、拖拽移除、公开/私密切换
- 片单互动：点赞/拉踩、二级评论（按赞排序）、回复
- 电影详情页"加入片单"按钮

### 全局搜索
- 导航栏搜索框：输入关键词同时搜电影名、导演、演员、类型
- 防抖下拉提示，点击跳转电影详情

### 管理员后台
- **控制台**：6 个统计卡片（用户/电影/评分/评论/片单/帖子）+ 近 7 天新增 + 热门类型 + 评分分布
- **数据分析**：用户增长趋势折线图、每日活跃折线图、类型分布柱状图、评分分布柱状图、社区活跃面板（SVG 绘制）
- **用户管理**：列表（分页/搜索）、编辑、删除
- **电影管理**：列表（分页/搜索）、新增、编辑、删除
- **评论管理**：列表（分页/搜索）、删除
- **社区管理**：话题增删改、帖子/回复列表与删除
- **片单管理**：全部片单列表（含可见性标识）、删除
- 管理员后台与普通用户前台的导航栏完全隔离

## 项目结构

```
movie_recommendation_system/
├── backend/
│   ├── movie_recommender/          # Django 项目配置
│   │   ├── settings.py
│   │   └── urls.py
│   ├── recommendation/             # 核心业务应用
│   │   ├── models.py               # 数据模型（14 个模型）
│   │   ├── serializers.py          # DRF 序列化器
│   │   ├── views.py                # 核心视图（推荐/电影/用户/互动/搜索/仪表盘）
│   │   ├── auth_views.py           # 认证视图
│   │   ├── auth_serializers.py     # 认证序列化器
│   │   ├── ai_views.py             # AI 视图（对话/推荐/分析）
│   │   ├── admin_views.py          # 管理员视图
│   │   ├── community_views.py      # 社区讨论区视图
│   │   ├── collection_views.py     # 电影片单视图
│   │   ├── collaborative_filtering.py  # 协同过滤算法
│   │   ├── movie_detail_cache.py   # 电影详情缓存
│   │   ├── management/commands/    # Django 管理命令
│   │   └── migrations/             # 数据库迁移
│   ├── scrapers/                   # 豆瓣爬虫
│   └── manage.py
│
├── frontend/
│   ├── src/
│   │   ├── views/                  # 页面组件（25 个页面）
│   │   │   ├── HomeView.vue        # 首页（个性化推荐 + 热门精选）
│   │   │   ├── AboutView.vue       # 智能推荐中心
│   │   │   ├── CollectionsView.vue # 片单广场
│   │   │   ├── CollectionDetailView.vue  # 片单详情
│   │   │   ├── CommunityView.vue   # 社区首页
│   │   │   ├── CommunityTopicView.vue    # 话题页
│   │   │   ├── CommunityPostView.vue     # 帖子详情
│   │   │   ├── AIChatView.vue      # AI 对话
│   │   │   ├── DoubanView.vue      # 电影库
│   │   │   ├── MovieDetailView.vue # 电影详情
│   │   │   ├── ProfileView.vue     # 个人中心
│   │   │   ├── PublicUserView.vue  # 公开用户主页
│   │   │   ├── OnboardingView.vue  # 新用户兴趣引导
│   │   │   ├── AdminLayoutView.vue       # 管理员布局
│   │   │   ├── AdminDashboardHome.vue    # 控制台
│   │   │   ├── AdminAnalyticsView.vue    # 数据分析
│   │   │   ├── AdminUsersView.vue        # 用户管理
│   │   │   ├── AdminMoviesView.vue       # 电影管理
│   │   │   ├── AdminCommentsView.vue     # 评论管理
│   │   │   ├── AdminCommunityView.vue    # 社区管理
│   │   │   └── AdminCollectionsView.vue  # 片单管理
│   │   ├── stores/                 # Pinia（auth / theme）
│   │   ├── router/                 # 路由 + 导航守卫
│   │   └── types/                  # TypeScript 类型
│   └── package.json
│
└── 豆瓣电影TOP250.json
```

## 快速开始

### 环境
- Python 3.10+ / Node.js 16+ / MySQL 8.0+
- DeepSeek API Key（可选，未配置时 AI 功能降级为规则版）

### 1. 数据库

```sql
CREATE DATABASE movieproject DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `backend/movie_recommender/settings.py` 中的 `DATABASES` 配置。

### 2. 后端

```bash
cd backend
pip install django djangorestframework django-cors-headers numpy scikit-learn requests python-dotenv beautifulsoup4 pillow mysqlclient selenium

python manage.py migrate
python manage.py import_movies ../豆瓣电影TOP250.json
python manage.py seed_ratings        # 可选：生成模拟评分数据
python manage.py seed_topics         # 可选：初始化社区话题
python manage.py createsuperuser     # 创建管理员
python manage.py runserver           # http://localhost:8000
```

### 3. 前端

```bash
cd frontend
npm install
npm run serve                        # http://localhost:8080
```

### 4. DeepSeek API（可选）

```bash
export DEEPSEEK_API_KEY="your-key"
# 或在 backend/.env 中设置 DEEPSEEK_API_KEY=your-key
```

## 管理员账号

```bash
cd backend
python manage.py createsuperuser
```

管理员后台入口：`/admin/login`，管理员后台与普通用户导航栏完全隔离。

## API 接口一览

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register/` | 注册 |
| POST | `/api/auth/login/` | 登录 |
| POST | `/api/auth/logout/` | 注销 |
| GET/PUT | `/api/auth/profile/` | 个人信息 |
| POST | `/api/auth/change-password/` | 修改密码 |
| GET | `/api/auth/check/` | 检查认证状态 |

### 电影
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/movies/` | 电影列表（分页） |
| GET | `/api/movies/{id}/` | 电影详情 |
| GET | `/api/movie-detail/` | 扩展详情（含豆瓣缓存） |
| GET | `/api/video-platform-links/` | 视频平台链接 |

### 推荐
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/recommendations/` | 个性化推荐（实时生成，存入日志） |
| GET | `/api/my-recommendations/` | 已保存的推荐结果 |
| GET | `/api/top-movies/` | 热门排行 |
| GET | `/api/similar-movies/{id}/` | 相似电影（看了又看） |
| GET/POST | `/api/onboarding-preferences/` | 冷启动兴趣管理 |
| GET/POST/PUT | `/api/user-profile/` | 用户画像及设置 |
| GET | `/api/users/{id}/profile/` | 公开用户主页 |

### 互动
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST/DELETE | `/api/movie-ratings/` | 评分 |
| GET/POST/DELETE | `/api/movie-feedback/` | 点赞/点踩 |
| GET/POST | `/api/movie-comments/` | 评论（支持 parent_id 回复） |
| PUT/DELETE | `/api/movie-comments/{id}/` | 修改/删除评论 |

### 社区
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/community/topics/` | 话题列表/创建 |
| GET/POST | `/api/community/posts/` | 帖子列表（分页）/发帖 |
| GET/DELETE | `/api/community/posts/{id}/` | 帖子详情/删除 |
| POST/DELETE | `/api/community/replies/` | 回复/删除 |
| POST/DELETE | `/api/community/likes/` | 帖子点赞/取消 |

### 片单
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/collections/` | 片单列表/创建 |
| GET/PUT/DELETE | `/api/collections/{id}/` | 片单详情/编辑/删除 |
| POST/DELETE | `/api/collections/movies/` | 添加/移除电影 |
| GET/POST | `/api/collections/comments/` | 片单评论（含二级回复+按赞排序） |
| POST/DELETE | `/api/collections/comments/likes/` | 评论点赞/取消 |
| POST/DELETE | `/api/collections/likes/` | 片单点赞/取消 |

### AI
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai/chat/` | AI 对话（SSE 流式） |
| POST | `/api/ai/nl-recommend/` | 自然语言推荐 |
| GET | `/api/ai/config/` | AI 配置 |

### 全局搜索
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/search/` | 搜索电影（名/导演/演员/类型） |

### 管理员
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/login/` | 管理员登录 |
| GET | `/api/admin/dashboard/` | 仪表盘数据 |
| GET | `/api/admin/analytics/` | 数据分析 |
| GET/POST/PUT/DELETE | `/api/admin/users/` | 用户管理 |
| GET/POST/PUT/DELETE | `/api/admin/movies/` | 电影管理 |
| GET/DELETE | `/api/admin/comments/` | 评论管理 |
| GET/POST/PUT/DELETE | `/api/admin/topics/` | 话题管理 |
| GET/DELETE | `/api/admin/posts/` | 帖子管理 |
| GET/DELETE | `/api/admin/replies/` | 回复管理 |
| GET/DELETE | `/api/admin/collections/` | 片单管理 |

## 算法说明

### 协同过滤
基于用户-电影评分矩阵，计算余弦相似度。新用户无评分时自动降级到热门推荐或冷启动。

### 冷启动推荐
引导用户选择偏好（类型/国家/年份/关键词）→ 数据库硬过滤 + 豆瓣评分排序。

### 自然语言推荐
用户输入 → DeepSeek 解析意图（JSON）→ 硬过滤候选池 → 有评分则结合 CF 排序 → 生成推荐理由 + 友好回复语。

## 注意事项

1. 先启动后端再启动前端
2. AI 功能需要 DeepSeek API Key，未配置时自动降级为规则版
3. 视频平台链接优先查库，无数据时自动抓取豆瓣
4. 生产环境请关闭 `DEBUG`，更换 `SECRET_KEY`，配置 `ALLOWED_HOSTS`
5. MySQL 需提前创建好数据库，迁移会自动建表
