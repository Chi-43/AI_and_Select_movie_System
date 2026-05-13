# 基于协同过滤与 AI 的电影推荐系统

融合协同过滤算法与大语言模型的智能电影推荐系统，前后端分离架构，支持个性化推荐、自然语言交互、用户画像分析与社交互动。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Django 5 + Django REST Framework |
| 数据库 | MySQL |
| 推荐算法 | 协同过滤（User-based / Item-based）、冷启动、热门排行 |
| AI 能力 | DeepSeek API（推荐理由生成、自然语言推荐检索、智能对话） |
| 科学计算 | NumPy / scikit-learn |
| 爬虫 | Selenium + BeautifulSoup（豆瓣页面抓取） |
| 前端框架 | Vue 3 + TypeScript |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| HTTP | Axios |
| 样式 | 原生 CSS（深色/浅色主题切换） |

## 功能特性

### 用户系统
- 注册 / 登录 / 注销（Token + Session 双认证）
- 新用户注册后引导完成兴趣偏好选择（4 步向导）
- 个人信息管理（头像上传、简介编辑）
- 密码修改
- 公开个人主页（查看其他用户的评分、评论、偏好、收藏）

### 推荐引擎
- **用户协同过滤** — 基于用户-电影评分矩阵 + 余弦相似度，找到相似用户并预测评分
- **冷启动推荐** — 根据用户偏好标签（类型/国家/年份/关键词）筛选高分电影
- **自然语言推荐** — 输入观影需求，AI 解析意图 → 硬过滤候选池 → 结合 CF 排序 → 返回结果
- **热门排行** — 评分数据不足时自动用豆瓣高分电影兜底
- **相似电影（看了又看）** — 基于物品协同过滤，展示与当前电影相似的影片
- **推荐持久化** — 首次推荐结果存入数据库，刷新页面不丢失；点击"换一批"才重新生成
- **推荐理由生成** — DeepSeek 为每条推荐生成个性化中文理由，未配置 API Key 时降级为规则版

### 电影浏览
- 豆瓣 TOP250 数据浏览，支持名称/导演/主演搜索
- 多维筛选（年份范围、评分范围、国家、类型）
- 多维度排序（评分、年份、名称）
- 电影详情页（海报、导演、演员、剧情简介、扩展信息）
- 视频平台链接查询（爱奇艺、腾讯、优酷、B站、Netflix 等），支持豆瓣实时抓取
- 电影收藏

### 用户互动
- **星级评分**（1-5 星），实时更新平均分
- **点赞 / 点踩**，统计展示
- **二级评论** — 一级评论 + 嵌套回复，评论用户名点击可查看对方主页
- 评论分页加载

### 用户画像
- 冷启动兴趣选择（类型/国家/年份/关键词）
- 根据评分行为自动更新画像偏好
- 画像总结自动生成
- 兴趣偏好可随时修改
- 公开收藏夹开关（可控制是否对外展示喜欢列表）

### AI 智能助手
- AI 对话（支持 SSE 流式输出和非流式输出）
- 自然语言推荐检索
- AI 配置管理

### 管理员后台
- 管理员专属登录
- 仪表盘、用户/电影/评论管理（支持分页、搜索、新增、编辑、删除）

## 项目结构

```
movie_recommendation_system/
├── backend/
│   ├── movie_recommender/          # Django 项目配置
│   │   ├── settings.py
│   │   └── urls.py
│   ├── recommendation/             # 核心业务应用
│   │   ├── models.py               # 数据模型
│   │   ├── serializers.py          # DRF 序列化器
│   │   ├── views.py                # 核心视图
│   │   ├── auth_views.py           # 认证视图
│   │   ├── auth_serializers.py     # 认证序列化器
│   │   ├── ai_views.py             # AI 视图
│   │   ├── admin_views.py          # 管理员视图
│   │   ├── collaborative_filtering.py  # 协同过滤算法
│   │   ├── movie_detail_cache.py   # 电影详情缓存
│   │   ├── management/commands/    # Django 管理命令
│   │   └── migrations/             # 数据库迁移
│   ├── scrapers/                   # 豆瓣爬虫
│   └── manage.py
│
├── frontend/
│   ├── src/
│   │   ├── views/                  # 页面组件
│   │   │   ├── HomeView.vue        # 首页（个性化推荐 + 热门精选）
│   │   │   ├── AboutView.vue       # 智能推荐中心
│   │   │   ├── LoginView.vue       # 登录
│   │   │   ├── RegisterView.vue    # 注册
│   │   │   ├── OnboardingView.vue  # 兴趣偏好引导
│   │   │   ├── ProfileView.vue     # 个人中心
│   │   │   ├── PublicUserView.vue  # 公开用户主页
│   │   │   ├── DoubanView.vue      # 电影库
│   │   │   ├── MovieDetailView.vue # 电影详情
│   │   │   ├── VideoPlatformView.vue # 视频平台
│   │   │   ├── AIChatView.vue      # AI 对话
│   │   │   └── Admin*.vue          # 管理员页面
│   │   ├── components/             # StarRating 等组件
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

修改 `backend/movie_recommender/settings.py` 中的数据库连接信息。

### 2. 后端

```bash
cd backend
pip install django djangorestframework django-cors-headers numpy scikit-learn requests python-dotenv beautifulsoup4 pillow mysqlclient selenium

python manage.py migrate
python manage.py import_movies ../豆瓣电影TOP250.json
python manage.py seed_ratings        # 可选：生成模拟评分
python manage.py runserver           # http://localhost:8000
```

### 3. 前端

```bash
cd frontend
npm install
npm run serve                        # http://localhost:8080
```

### 4. DeepSeek API Key（可选）

```bash
export DEEPSEEK_API_KEY="your-key"
# 或在 backend/.env 中设置 DEEPSEEK_API_KEY=your-key
```

## API 接口一览

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register/` | 注册 |
| POST | `/api/auth/login/` | 登录 |
| POST | `/api/auth/logout/` | 注销 |
| GET/PUT | `/api/auth/profile/` | 个人信息 |
| POST | `/api/auth/change-password/` | 修改密码 |

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
| GET | `/api/similar-movies/{id}/` | 相似电影 |
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

### AI
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai/chat/` | AI 对话（SSE 流式） |
| POST | `/api/ai/nl-recommend/` | 自然语言推荐 |
| GET | `/api/ai/config/` | AI 配置 |

### 管理员
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/login/` | 登录 |
| GET | `/api/admin/users/` | 用户列表 |
| GET/PUT/DELETE | `/api/admin/users/{id}/` | 用户管理 |
| GET/POST | `/api/admin/movies/` | 电影列表/新增 |
| GET/PUT/DELETE | `/api/admin/movies/{id}/` | 电影管理 |
| GET | `/api/admin/comments/` | 评论列表 |
| GET/DELETE | `/api/admin/comments/{id}/` | 评论管理 |

## 算法说明

### 协同过滤（Collaborative Filtering）

基于用户-电影评分矩阵构建：

1. **User-based CF**：计算用户间余弦相似度 → 找到相似用户 → 加权预测未评分电影的偏好
2. **Item-based CF**：计算电影间余弦相似度 → 基于用户高评分电影推荐相似影片

新用户无评分时相似度为 0，自动降级到热门推荐；积累评分后协同过滤逐步生效。

### 冷启动推荐

引导用户选择偏好（类型/国家/年份/关键词）→ 数据库硬过滤 + 豆瓣评分排序 → 返回匹配结果。用户产生评分后画像自动更新，推荐精度逐步提升。

### 自然语言推荐

```
用户输入 → DeepSeek 解析意图（JSON）
         → 硬过滤候选池（类型/国家/年份/评分）
         → 有评分记录 → 结合 CF 排序
         → 无评分记录 → 豆瓣评分排序
         → 生成推荐理由 + 友好回复语
```

## 管理员账号

```bash
cd backend
python manage.py createsuperuser
```

管理员登录入口：`/admin/login`

## 注意事项

1. 先启动后端再启动前端
2. 推荐理由和 NL 推荐需要 DeepSeek API Key，未配置时自动降级为规则版
3. 视频平台链接优先查库，无数据时自动抓取豆瓣
4. 生产环境请关闭 `DEBUG`，更换 `SECRET_KEY`，配置 `ALLOWED_HOSTS`
5. MySQL 需提前创建好数据库，迁移会自动建表
