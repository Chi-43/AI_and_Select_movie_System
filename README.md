# 基于协同过滤与 AI 的电影推荐系统

## 系统概述

本系统是一个融合**协同过滤算法**与**大语言模型**的智能电影推荐平台，采用前后端分离架构，集成了推荐引擎、用户画像分析、AI 智能助手、社区讨论、电影片单和后台数据管理等功能模块。

### 核心指标

| 指标 | 数值 |
|------|------|
| 数据模型 | 17 个 |
| 后端视图模块 | 7 个（views、auth_views、ai_views、admin_views、community_views、collection_views） |
| 前端页面 | 26 个 |
| 爬虫脚本 | 3 个 |
| 管理命令 | 5 个 |
| API 接口 | 40+ 个 |

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | Django 5 + Django REST Framework | RESTful API 设计，Token + Session 双重认证 |
| 数据库 | MySQL 8.0 | 关系型存储，支持全文检索 |
| AI 能力 | DeepSeek API | 推荐理由生成、自然语言检索、智能对话（SSE 流式输出） |
| 推荐算法 | 协同过滤 + 冷启动 + 热门排行 | NumPy / scikit-learn 实现余弦相似度矩阵 |
| 爬虫 | Selenium + BeautifulSoup | 动态/静态豆瓣页面抓取，类型排行榜批量爬取 |
| 前端框架 | Vue 3 + TypeScript | Composition API，组件化开发 |
| 状态管理 | Pinia | 用户认证、主题切换 |
| 路由 | Vue Router 4 | 导航守卫，权限控制 |
| 网络请求 | Axios + Fetch | API 通信，流式数据读取 |

---

## 系统架构

```
┌─────────────────────────────────────┐
│              前端 (Vue 3)            │
│  25 个页面 · Pinia · Router · Axios  │
└─────────────┬───────────────────────┘
              │ HTTP / SSE
┌─────────────▼───────────────────────┐
│          后端 (Django + DRF)         │
│  认证 · 推荐 · 社区 · 片单 · AI · 管理 │
└──────┬──────────────────┬───────────┘
       │                  │
  ┌────▼────┐      ┌──────▼──────┐
  │  MySQL  │      │  DeepSeek   │
  │ 数据库   │      │  API (AI)   │
  └─────────┘      └─────────────┘
       │
  ┌────▼────┐
  │  豆瓣爬虫 │
  │ Selenium │
  │ requests │
  └─────────┘
```

---

## 功能模块详述

### 一、用户系统

| 功能 | 说明 |
|------|------|
| 注册与登录 | Token + Session 双认证机制，支持管理员专用登录入口 |
| 新用户引导 | 注册后进入 4 步兴趣选择向导（类型→国家→年份→关键词），完成后自动触发生成首次推荐 |
| 个人信息管理 | 头像上传/移除、用户名、邮箱、姓名、个人简介编辑 |
| 密码管理 | 当前密码验证、强度检测、实时密码匹配提示 |
| 公开个人主页 | 任何用户可查看他人主页：基本信息、偏好标签、画像总结、最近评分、最近评论 |
| 收藏夹公开控制 | 用户可选择是否公开收藏夹，公开后他人主页可查看喜欢的电影列表 |

### 二、推荐引擎

**五种推荐策略：**

| 策略 | 核心算法 | 适用场景 |
|------|---------|---------|
| 用户协同过滤 | 构建用户-电影评分矩阵 → 余弦相似度 → 加权预测评分 | 有评分记录的用户 |
| 物品协同过滤 | 构建电影相似度矩阵 → 推荐与高评分电影相似的影片 | 有评分记录的用户 |
| 冷启动推荐 | 用户偏好标签（类型/国家/年份/关键词）→ 数据库硬过滤 + 评分排序 | 新用户 |
| 自然语言推荐 | DeepSeek 解析自然语言输入 → 意图提取（JSON）→ 硬过滤 → CF 排序 | 所有用户 |
| 热门排行 | 基于全体评分 + 豆瓣评分兜底 | 所有用户 |

**推荐增强功能：**

| 功能 | 说明 |
|------|------|
| 推荐理由生成 | 每条推荐附带 DeepSeek 生成的个性化中文理由（含用户偏好匹配、高分标签、相似用户关联等维度） |
| 推荐持久化 | 首次推荐结果存入 RecommendationLog 表，刷新页面不丢失，点击"换一批"才重新生成 |
| 降级兜底 | 协同过滤无结果时自动降级，用户协同→热门排行，冷启动→偏好筛选，保证始终有推荐输出 |
| 看了又看 | 电影详情页右侧展示相似电影，CF + 同类型高分电影兜底，每部电影都能出结果 |

### 三、电影浏览与发现

**数据来源：**
- 豆瓣 TOP250（JSON 文件导入）
- 豆瓣类型排行榜批量爬取（20 种类型 × 3 评分段，详见 `scrapers/typerank.py`）
- 电影详情页实时爬取（Selenium + BeautifulSoup，获取海报、演员、剧情简介等扩展信息）

**功能：**

| 功能 | 说明 |
|------|------|
| 多维筛选 | 电影名称/导演/主演搜索，年份范围、评分范围、国家、类型下拉筛选 |
| 多维排序 | 评分高低、年份新旧、名称 A-Z |
| 电影详情 | 海报、导演、演员、类型、国家、上映日期、片长、语言、IMDb、又名、剧情简介 |
| 海报显示 | 通过后端图片代理绕开豆瓣防盗链（`/api/image-proxy/`），支持缓存图片正常显示 |
| 视频平台链接 | 查询爱奇艺、腾讯、优酷、B站、Netflix 等平台链接，数据库优先，豆瓣实时抓取兜底 |
| 电影收藏 | 前端 localStorage 存储收藏列表，支持收藏分析（类型分布、年份分布、平均评分） |

### 四、用户互动体系

**五层互动：**

| 层级 | 功能 | 技术实现 |
|------|------|---------|
| 评分 | 1-5 星评分，实时更新平均分，提交后自动刷新用户画像 | StarRating 组件 |
| 点赞/点踩 | 电影点赞/拉踩，统计展示，可取消反馈 | MovieFeedback 模型 |
| 评论 | 二级评论体系（一级评论 + 嵌套回复），分页加载 | MovieComment 模型（自引用 parent） |
| 用户画像 | 评分行为自动更新偏好（类型/国家/年份/关键词），画像总结自动生成 | UserProfile 模型 |
| 用户关联 | 评论中用户名可点击跳转对方主页，查看评分、偏好、收藏 | PublicUserView |

### 五、AI 智能助手

**对话系统特性：**

| 功能 | 说明 |
|------|------|
| 多会话管理 | 支持新建/切换/删除对话，每个用户独立存储（localStorage 隔离） |
| 双模式 | AI 问答模式 + 智能推荐模式，一键切换 |
| SSE 流式输出 | 支持 Server-Sent Events，文字逐字出现，打字动画效果 |
| 快速提问 | 预设 4 个常见问题，一键发送 |
| 电影卡片 | AI 回复中嵌入可点击的推荐电影卡片 |
| 用户隔离 | 对话历史按用户 ID 隔离存储，切换账号自动切换历史 |

### 六、社区讨论区

**讨论架构：** 话题 → 帖子 → 回复（二级）

| 功能 | 说明 |
|------|------|
| 话题管理 | 5 个预设话题（电影推荐、观影讨论、导演与演员、影视杂谈、经典老片），管理员可增删改 |
| 发帖 | 支持 Markdown 渲染 + 配图上传，帖内支持标题、加粗、代码块、引用、列表 |
| 回复 | 二级回复（嵌套评论），支持回复指定楼层 |
| 互动 | 帖子和回复均支持点赞/拉踩，按热度排序 |
| 浏览统计 | 每次打开帖子浏览量 +1，展示浏览数/回复数/点赞数 |
| 分页 | 帖子列表支持分页 |

### 七、电影片单系统

**类似豆瓣"豆列"功能：**

| 功能 | 说明 |
|------|------|
| 创建片单 | 标题 + 描述 + 封面图上传 + 公开/私密切换，创建时可搜索并批量添加电影 |
| 片单广场 | 卡片网格展示所有公开片单，登录后可看到自己的私密片单（🔒标识） |
| 片单详情 | 电影海报缩略图 + 名称 + 评分 + 年份 + 推荐语，片主可移除电影 |
| 添加电影 | 两种方式：1) 片单内搜索框搜电影添加 2) 电影详情页"加入片单"弹窗 |
| 互动 | 片单点赞/拉踩，二级评论（含回复、按赞排序），评论点赞/拉踩 |
| 权限 | 公开片单所有人可见可互动，私密片单仅片主自己可见和管理 |
| 管理端 | 管理后台可查看所有片单列表（含可见性标识），可删除 |

### 八、全局搜索

导航栏搜索框，支持同时搜索电影名、导演、演员、类型，200ms 防抖，下拉提示，点击跳转详情，回车跳转电影库。

### 九、管理员后台

管理员后台与普通用户前台**导航栏完全隔离**，拥有独立的侧边栏布局。

| 模块 | 功能 |
|------|------|
| 控制台 | 6 个统计卡片（用户/电影/评分/评论/片单/帖子）+ 近 7 天新增数据 + 热门电影类型柱状图 + 评分分布柱状图 |
| 数据分析 | SVG 折线图（用户增长趋势、每日活跃趋势）+ 柱状图（类型分布、评分分布）+ 社区活跃面板 |
| 用户管理 | 列表分页/搜索、编辑用户信息、删除用户、查看用户画像弹窗（偏好标签+评分统计+评论记录） |
| 电影管理 | 列表分页/搜索、新增/编辑/删除电影 |
| 评论管理 | 列表分页/搜索、删除评论 |
| 社区管理 | 话题增删改、帖子列表与删除、回复列表与删除 |
| 片单管理 | 全部片单列表（含可见性标识）、删除片单 |

---

## 数据模型

| 序号 | 模型 | 说明 |
|------|------|------|
| 1 | Movie | 电影信息（标题/豆瓣链接/评分/导演/演员/类型/国家/年份/简介） |
| 2 | User | 用户（扩展自 Django AbstractUser，含头像/简介） |
| 3 | UserProfile | 用户画像（偏好类型/国家/年份/关键词/画像总结/冷启动状态/公开收藏夹开关） |
| 4 | Rating | 电影评分（用户+电影+分数，唯一约束） |
| 5 | MovieComment | 电影评论（支持自引用 parent 二级回复） |
| 6 | MovieFeedback | 电影点赞/拉踩 |
| 7 | VideoPlatform | 视频平台链接 |
| 8 | RecommendationLog | 推荐日志（用户+电影+算法+分数+理由） |
| 9 | DiscussionTopic | 社区话题 |
| 10 | DiscussionPost | 社区帖子（支持 Markdown + 配图） |
| 11 | DiscussionReply | 帖子回复（支持嵌套） |
| 12 | PostLike | 帖子点赞 |
| 13 | MovieCollection | 电影片单（支持封面图/公开私密） |
| 14 | CollectionMovie | 片单电影关联（支持推荐语/排序） |
| 15 | CollectionComment | 片单评论（支持二级回复/点赞数/拉踩数） |
| 16 | CollectionCommentLike | 片单评论反馈 |
| 17 | CollectionLike | 片单点赞/拉踩 |

---

## 项目结构

```
movie_recommendation_system/
├── backend/
│   ├── movie_recommender/
│   │   ├── settings.py               # 项目配置
│   │   └── urls.py                   # 全局路由（172 行，40+ 接口）
│   ├── recommendation/
│   │   ├── models.py                 # 17 个数据模型
│   │   ├── serializers.py            # DRF 序列化器
│   │   ├── views.py                  # 核心视图（推荐/电影/用户/互动/搜索/仪表盘/图片代理）
│   │   ├── auth_views.py             # 认证视图（注册/登录/注销/个人信息/密码修改）
│   │   ├── auth_serializers.py       # 认证序列化器
│   │   ├── ai_views.py               # AI 视图（SSE 流式对话/自然语言推荐/推荐理由生成）
│   │   ├── admin_views.py            # 管理员视图（用户/电影/评论/话题/帖子/回复/片单管理）
│   │   ├── community_views.py        # 社区视图（话题/帖子/回复/点赞）
│   │   ├── collection_views.py       # 片单视图（CRUD/电影管理/评论树/点赞）
│   │   ├── collaborative_filtering.py # 协同过滤算法（User-based/Item-based/矩阵构建/相似度计算）
│   │   ├── movie_detail_cache.py     # 电影详情缓存 JSON 读写
│   │   ├── management/commands/      # 5 个管理命令
│   │   └── migrations/               # 数据库迁移文件
│   └── scrapers/
│       ├── movie_detail.py           # 豆瓣电影详情爬虫（Selenium）
│       ├── video_url.py              # 豆瓣视频平台链接爬虫（Selenium）
│       └── typerank.py               # 豆瓣类型排行榜批量爬虫（20种×3评分段，输出 cache 格式）
│
├── frontend/
│   ├── src/
│   │   ├── views/                    # 26 个页面组件
│   │   ├── components/               # 通用组件（StarRating 等）
│   │   ├── stores/                   # Pinia 状态（auth.ts, theme.ts）
│   │   ├── router/                   # Vue Router 路由 + 全局导航守卫
│   │   ├── types/                    # TypeScript 类型定义
│   │   └── assets/                   # 静态资源（logo, 主题样式）
│   └── package.json
│
├── 豆瓣电影TOP250.json               # 豆瓣 TOP250 原始数据
└── README.md
```

---

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 16+
- MySQL 8.0+
- DeepSeek API Key（可选）

### 1. 数据库

```sql
CREATE DATABASE movieproject DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `backend/movie_recommender/settings.py` 中 `DATABASES` 配置。

### 2. 后端

```bash
cd backend
pip install django djangorestframework django-cors-headers numpy scikit-learn requests python-dotenv beautifulsoup4 pillow mysqlclient selenium

python manage.py migrate
python manage.py import_movies ../豆瓣电影TOP250.json    # 导入 TOP250
python manage.py seed_ratings                            # 可选：生成模拟评分
python manage.py seed_topics                             # 可选：初始化社区话题
python manage.py createsuperuser                          # 创建管理员
python manage.py runserver                               # http://localhost:8000
```

### 3. 前端

```bash
cd frontend
npm install
npm run serve                                            # http://localhost:8080
```

### 4. 扩展数据（可选）

```bash
cd backend/scrapers
python typerank.py                                       # 爬取类型排行榜
python typerank.py --genres 剧情,科幻                     # 只爬指定类型

cd ..
python manage.py import_typerank scrapers/douban_typerank.json
```

### 5. AI 配置（可选）

```bash
export DEEPSEEK_API_KEY="your-key"
# 或在 backend/.env 中设置 DEEPSEEK_API_KEY=your-key
```

---

## API 接口总览

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register/` | 用户注册 |
| POST | `/api/auth/login/` | 用户登录 |
| POST | `/api/auth/logout/` | 注销 |
| GET/PUT | `/api/auth/profile/` | 个人信息 |
| POST | `/api/auth/change-password/` | 修改密码 |
| GET | `/api/auth/check/` | 检查认证状态 |

### 电影

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/movies/` | 电影列表（分页） |
| GET | `/api/movies/{id}/` | 电影详情 |
| GET | `/api/movie-detail/` | 扩展详情（含豆瓣缓存+海报） |
| GET | `/api/video-platform-links/` | 视频平台链接 |
| GET | `/api/image-proxy/` | 图片代理（绕过豆瓣防盗链） |

### 推荐

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/recommendations/` | 生成个性化推荐（存入日志） |
| GET | `/api/my-recommendations/` | 已保存的推荐结果 |
| GET | `/api/top-movies/` | 热门排行（评分不足兜底） |
| GET | `/api/similar-movies/{id}/` | 相似电影（CF+类型兜底） |
| GET/POST | `/api/onboarding-preferences/` | 冷启动兴趣管理 |
| GET/POST/PUT | `/api/user-profile/` | 用户画像及设置 |
| GET | `/api/users/{id}/profile/` | 公开用户主页 |

### 互动

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST/DELETE | `/api/movie-ratings/` | 评分（1-5星） |
| GET/POST/DELETE | `/api/movie-feedback/` | 点赞/点踩 |
| GET/POST | `/api/movie-comments/` | 评论（支持 parent_id 回复） |
| PUT/DELETE | `/api/movie-comments/{id}/` | 修改/删除评论 |

### 社区

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/community/topics/` | 话题列表/创建 |
| GET/POST | `/api/community/posts/` | 帖子列表（分页）/发帖 |
| GET/DELETE | `/api/community/posts/{id}/` | 帖子详情（浏览量+1）/删除 |
| POST/DELETE | `/api/community/replies/` | 回复/删除 |
| POST/DELETE | `/api/community/likes/` | 帖子点赞/取消 |

### 片单

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/collections/` | 片单列表/创建（含批量添加电影） |
| GET/PUT/DELETE | `/api/collections/{id}/` | 片单详情/编辑/删除 |
| POST/DELETE | `/api/collections/movies/` | 添加/移除电影 |
| GET/POST | `/api/collections/comments/` | 片单评论（树形结构+按赞排序） |
| POST/DELETE | `/api/collections/comments/likes/` | 评论点赞/取消 |
| POST/DELETE | `/api/collections/likes/` | 片单点赞/取消 |

### AI

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai/chat/` | AI 对话（SSE 流式） |
| POST | `/api/ai/nl-recommend/` | 自然语言推荐 |
| GET | `/api/ai/config/` | AI 配置状态 |

### 搜索
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/search/` | 全局搜索（名/导演/演员/类型） |

### 管理后台

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/login/` | 管理员登录 |
| GET | `/api/admin/dashboard/` | 仪表盘统计 |
| GET | `/api/admin/analytics/` | 数据分析 |
| GET/POST/PUT/DELETE | `/api/admin/users/` 等 | 用户/电影/评论/话题/帖子/回复/片单管理 |

---

## 推荐算法详解

### 协同过滤流程

```
用户评分数据 → 构建评分矩阵(M×N)
    ├── User-CF: 行=用户, 列=电影 → 计算用户余弦相似度
    │   → KNN找相似用户 → 加权预测评分 → 返回 Top-N
    └── Item-CF: 行=电影, 列=用户 → 计算电影余弦相似度
        → 基于高评分电影找相似条目 → 预测评分 → 返回 Top-N

新用户无评分 → 相似度为0 → 自动降级
    用户协同 → 热门排行
    冷启动  → 偏好筛选
```

### 冷启动流程

```
用户选择偏好（类型/国家/年份/关键词）
    → 数据库硬过滤
    → 评分排序
    → 返回匹配结果
用户产生评分后 → 自动更新画像 → 协同过滤逐步接管
```

### 自然语言推荐流程

```
自然语言输入
    → DeepSeek 解析意图（JSON）
    → 硬过滤候选池（类型/国家/年份/评分）
    → 有评分 → 结合 CF 排序
    → 无评分 → 豆瓣评分排序
    → 生成推荐理由 + 友好回复语
```

### 相似电影（看了又看）

```
CF 矩阵中计算电影相似度
    → 不足 top_n 部 → 同类型 + 高分电影兜底
    → 保证每部电影都有推荐结果
```

---

## 系统亮点

1. **多层次推荐体系**：协同过滤 + 冷启动 + 自然语言 + 热门排行，覆盖所有用户状态
2. **推荐可解释性**：每条推荐附带 AI 生成的个性化理由，类型匹配度、相似用户偏好等多维度说明
3. **完整的社交生态**：电影评论 + 社区讨论 + 电影片单，三级内容体系
4. **AI 深度集成**：SSE 流式对话、自然语言转化为推荐、多会话管理
5. **画像驱动的个性化**：冷启动引导 → 评分行为追踪 → 画像自动更新 → 推荐精准度持续提升
6. **完善的权限体系**：用户-管理员双层架构，导航栏隔离，内容公开/私密控制
7. **数据可视化**：管理员后台含 SVG 趋势图、柱状图、统计面板
8. **可扩展的数据源**：TOP250 快速导入 + 类型排行榜批量爬取，支持增量更新
