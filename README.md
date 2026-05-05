# 基于协同过滤与AI的电影推荐系统

一个融合协同过滤算法与大语言模型的智能电影推荐系统，采用前后端分离架构。

## 技术栈

### 后端
- **框架**: Django + Django REST Framework
- **数据库**: MySQL
- **推荐算法**: 协同过滤（User-based / Item-based）+ 冷启动 + 热门推荐
- **AI 能力**: DeepSeek API（推荐理由生成、自然语言推荐检索、智能对话）
- **爬虫**: requests + BeautifulSoup（豆瓣页面信息抓取）
- **科学计算**: numpy / pandas / scikit-learn

### 前端
- **框架**: Vue 3 + TypeScript
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios
- **样式**: 原生 CSS（主题切换支持）

## 功能特性

### 用户认证
- 账号注册 / 登录 / 注销（Token-based + Session 双认证）
- 个人信息管理（头像上传、个人简介编辑）
- 密码修改

### 推荐引擎
- **基于用户的协同过滤** — 找到兴趣相似的用户，根据他们的评分做推荐
- **基于物品的协同过滤** — 找到与用户高评分电影相似的电影
- **冷启动推荐** — 新用户通过兴趣标签初选偏好，无需历史评分即可获得推荐
- **自然语言推荐** — 输入自然语言需求（如"我想看一部2000年以后的悬疑片"），AI 自动解析意图并检索匹配电影
- **热门推荐** — 基于全体用户评分数据的综合热度排行
- **相似电影** — 查看任意电影的相似电影列表
- **推荐理由生成** — 每条推荐结果均附带由 DeepSeek 生成的个性化中文推荐理由
- **推荐日志记录** — 所有推荐历史自动记录，支持后续分析

### 电影浏览与发现
- 豆瓣 TOP250 电影数据浏览
- 电影详情页（评分、导演、演员、简介、类型、国家等）
- 视频平台链接查询（爱奇艺、腾讯视频、优酷、B站、Netflix 等），支持豆瓣实时抓取

### 用户互动
- **电影评分**（1-5 星），实时更新用户画像
- **点赞 / 拉踩**电影
- **电影评论**（发表、修改、删除）
- **用户画像** — 根据评分行为自动更新偏好类型、国家、年份范围，支持冷启动兴趣标签选择

### AI 智能助手
- **AI 对话** — 电影推荐助手，支持流式（SSE）和非流式输出
- **自然语言推荐检索** — 输入一段话，AI 解析意图 → 硬过滤候选池 → 结合协同过滤排序 → 返回推荐结果
- **电影分析** — 对指定电影进行 AI 分析
- **AI 配置管理** — 查看可用模型和 API 状态

### 管理员后台
- 管理员专属登录（仅 `is_staff` 用户可登录）
- 用户管理（列表 / 详情）
- 电影管理（列表 / 详情）
- 评论管理（列表 / 详情）

---

## 项目结构

```
movie_recommendation_system/
├── backend/                              # Django 后端
│   ├── movie_recommender/                # Django 项目配置
│   │   ├── settings.py                   # 配置（数据库、CORS、DRF、DeepSeek）
│   │   └── urls.py                       # 全局路由
│   ├── recommendation/                   # 推荐应用（核心业务）
│   │   ├── models.py                     # 数据模型（Movie / User / Rating / Comment / Feedback / Platform）
│   │   ├── serializers.py                # DRF 序列化器
│   │   ├── views.py                      # 核心业务视图（推荐、评分、点赞、评论、画像等）
│   │   ├── auth_views.py                 # 认证视图（注册、登录、注销、个人信息）
│   │   ├── auth_serializers.py           # 认证序列化器
│   │   ├── ai_views.py                   # AI 视图（对话、自然语言推荐、推荐理由生成）
│   │   ├── admin_views.py                # 管理员后台视图
│   │   ├── collaborative_filtering.py    # 协同过滤算法实现
│   │   ├── movie_detail_cache.py         # 电影详情缓存
│   │   ├── management/commands/          # Django 管理命令
│   │   │   ├── import_movies.py          # 导入豆瓣电影数据
│   │   │   └── seed_ratings.py           # 生成模拟评分数据
│   │   └── migrations/                   # 数据库迁移文件
│   ├── scrapers/                         # 爬虫模块
│   │   ├── movie_detail.py               # 豆瓣电影详情抓取
│   │   └── video_url.py                  # 豆瓣视频平台链接抓取
│   ├── manage.py                         # Django 管理脚本
│   └── populate_data.py                  # 示例数据填充脚本
│
├── frontend/                             # Vue 3 前端
│   ├── src/
│   │   ├── views/                        # 页面视图
│   │   │   ├── HomeView.vue              # 首页（推荐、热门电影展示）
│   │   │   ├── LoginView.vue             # 登录页
│   │   │   ├── RegisterView.vue          # 注册页
│   │   │   ├── ProfileView.vue           # 个人中心
│   │   │   ├── DoubanView.vue            # 豆瓣TOP250浏览
│   │   │   ├── MovieDetailView.vue       # 电影详情页
│   │   │   ├── VideoPlatformView.vue     # 视频平台链接页
│   │   │   ├── AIChatView.vue            # AI 对话页
│   │   │   ├── AdminLoginView.vue        # 管理员登录
│   │   │   ├── AdminLayoutView.vue       # 管理员布局
│   │   │   ├── AdminDashboardHome.vue    # 管理员首页
│   │   │   ├── AdminUsersView.vue        # 用户管理
│   │   │   ├── AdminMoviesView.vue       # 电影管理
│   │   │   ├── AdminCommentsView.vue     # 评论管理
│   │   │   └── AdminProfileView.vue      # 管理员个人信息
│   │   ├── components/                   # 通用组件
│   │   │   ├── StarRating.vue            # 星级评分组件
│   │   │   └── HelloWorld.vue            # 示例组件
│   │   ├── stores/                       # Pinia 状态管理
│   │   │   ├── auth.ts                   # 认证状态
│   │   │   └── theme.ts                  # 主题状态
│   │   ├── router/                       # 路由配置
│   │   │   └── index.ts                  # 路由 + 导航守卫
│   │   ├── types/                        # TypeScript 类型定义
│   │   │   └── auth.ts
│   │   ├── assets/                       # 静态资源
│   │   └── main.ts                       # 应用入口
│   └── package.json
│
├── 豆瓣电影TOP250.csv                     # 豆瓣TOP250数据（CSV格式）
├── 豆瓣电影TOP250.json                    # 豆瓣TOP250数据（JSON格式）
└── 获取豆瓣TOP250.py                      # 豆瓣TOP250数据抓取脚本
```

---

## 快速开始

### 环境要求

- **Python** 3.10+
- **Node.js** 16+
- **MySQL** 8.0+
- **DeepSeek API Key**（可选，用于AI功能）

### 1. 数据库准备

创建 MySQL 数据库：

```sql
CREATE DATABASE movieproject DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

数据库连接配置在 `backend/movie_recommender/settings.py` 中，请根据本地环境修改 `USER`、`PASSWORD`、`HOST`、`PORT`。

### 2. 后端设置

```bash
cd backend

# 安装 Python 依赖
pip install django djangorestframework django-cors-headers numpy pandas scikit-learn requests python-dotenv django-filter beautifulsoup4 pillow mysqlclient

# 运行数据库迁移
python manage.py migrate

# 导入豆瓣TOP250数据
python manage.py import_movies ../豆瓣电影TOP250.json

# （可选）生成模拟评分数据
python manage.py seed_ratings

# （可选）填充电影详情缓存
python populate_movie_detail_cache.py

# 启动后端服务
python manage.py runserver
```

后端服务运行在 http://localhost:8000

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run serve
```

前端应用运行在 http://localhost:8080

### 4. 配置 AI 功能（可选）

设置 DeepSeek API Key 以启用 AI 推荐理由生成和智能对话功能：

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="your-api-key"

# Linux / macOS
export DEEPSEEK_API_KEY="your-api-key"
```

或在 `backend/.env` 文件中配置：

```
DEEPSEEK_API_KEY=your-api-key
```

---

## API 接口概览

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register/` | 用户注册 |
| POST | `/api/auth/login/` | 用户登录 |
| POST | `/api/auth/logout/` | 用户注销（需认证） |
| GET | `/api/auth/profile/` | 获取个人信息（需认证） |
| PUT | `/api/auth/profile/` | 更新个人信息（需认证） |
| POST | `/api/auth/change-password/` | 修改密码（需认证） |
| GET | `/api/auth/check/` | 检查认证状态 |
| POST | `/api/auth/token-login/` | Token 登录 |

### 电影
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/movies/` | 电影列表 |
| GET | `/api/movies/{id}/` | 电影详情 |
| GET | `/api/movie-detail/` | 扩展电影详情（含豆瓣缓存） |
| GET | `/api/video-platform-links/` | 查询视频平台链接 |

### 推荐
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/recommendations/` | 获取个性化推荐 |
| GET | `/api/top-movies/` | 热门电影排行 |
| GET | `/api/similar-movies/{movie_id}/` | 相似电影 |
| GET/POST | `/api/onboarding-preferences/` | 冷启动兴趣管理 |
| GET/POST | `/api/user-profile/` | 用户画像 |

### 互动
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST/DELETE | `/api/movie-ratings/` | 电影评分 |
| GET/POST/DELETE | `/api/movie-feedback/` | 点赞/拉踩 |
| GET/POST | `/api/movie-comments/` | 电影评论 |
| PUT/DELETE | `/api/movie-comments/{comment_id}/` | 修改/删除评论 |

### AI
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai/chat/` | AI 对话（支持 SSE 流式） |
| POST | `/api/ai/nl-recommend/` | 自然语言推荐检索 |
| POST | `/api/ai/recommendations/` | AI 电影推荐（预留） |
| POST | `/api/ai/analysis/` | AI 电影分析 |
| GET/POST | `/api/ai/config/` | AI 配置 |

### 管理员
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/login/` | 管理员登录 |
| GET/PUT | `/api/admin/profile/` | 管理员信息 |
| GET | `/api/admin/users/` | 用户列表 |
| GET | `/api/admin/users/{user_id}/` | 用户详情 |
| GET | `/api/admin/movies/` | 电影列表 |
| GET | `/api/admin/movies/{movie_id}/` | 电影详情 |
| GET | `/api/admin/comments/` | 评论列表 |
| DELETE | `/api/admin/comments/{comment_id}/` | 删除评论 |

---

## 算法说明

### 协同过滤

系统基于用户-电影评分矩阵实现两种协同过滤算法：

1. **基于用户的协同过滤（User-based CF）**
   - 构建用户-电影评分矩阵
   - 计算用户间余弦相似度
   - 找到与目标用户最相似的 K 个用户
   - 根据相似用户的加权评分预测目标用户对未评分电影的偏好
   - 返回预测评分最高的 N 部电影

2. **基于物品的协同过滤（Item-based CF）**
   - 构建电影-用户评分矩阵（用户-电影矩阵的转置）
   - 计算电影间余弦相似度
   - 基于用户已评分的高分电影，找到相似电影
   - 加权预测未评分电影的偏好分数

### 冷启动推荐

针对没有评分记录的新用户：
- 引导用户选择偏好的电影类型、国家/地区、年份范围
- 根据偏好标签在数据库中筛选匹配的高分电影
- 用户产生评分后自动降级到协同过滤推荐

### 自然语言推荐（AI-NL）

1. DeepSeek 解析用户自然语言输入为结构化意图（JSON）
2. 根据意图中的类型、国家、年份、评分等条件硬过滤候选池
3. 若用户有评分记录，结合协同过滤结果加权排序
4. 若无记录，按豆瓣评分降序排列
5. 为每条推荐结果生成个性化中文推荐理由
6. 返回推荐列表 + AI 生成的友好回复语

### 相似度计算

使用余弦相似度：

```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```

---

## 管理员账号

通过 Django shell 创建管理员：

```bash
cd backend
python manage.py createsuperuser
```

创建后，该账号即可登录前端管理员后台（`/admin/login`）。

---

## 注意事项

1. 确保后端服务先启动，前端才能正常获取数据
2. 自然语言推荐和推荐理由生成需要配置 DeepSeek API Key，未配置时自动降级到规则版推荐理由
3. 视频平台链接查询优先从数据库读取，数据库无数据时自动通过豆瓣爬虫实时抓取
4. 生产环境建议关闭 `DEBUG` 模式，并配置安全的 `SECRET_KEY` 和 `ALLOWED_HOSTS`
