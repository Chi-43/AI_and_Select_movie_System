# 基于协同过滤的电影推荐系统

这是一个基于协同过滤算法的电影推荐系统，采用前后端分离架构。

## 技术栈

### 后端
- **框架**: Django + Django REST Framework
- **数据库**: SQLite3
- **算法**: 协同过滤（基于用户和基于物品）
- **Python包**: 
  - Django
  - Django REST Framework
  - django-cors-headers
  - numpy
  - pandas
  - scikit-learn

### 前端
- **框架**: Vue 3 + TypeScript
- **UI库**: 原生CSS
- **HTTP客户端**: Axios
- **状态管理**: Pinia
- **路由**: Vue Router

## 功能特性

1. **用户认证管理**
   - 用户注册（用户名、邮箱、密码）
   - 用户登录/注销
   - 用户个人信息管理
   - 密码修改功能
   - Token-based认证

2. **电影推荐**
   - 基于用户的协同过滤推荐
   - 基于物品的协同过滤推荐
   - 热门电影推荐

3. **电影浏览**
   - 查看所有电影
   - 查看电影详情
   - 查找相似电影

4. **交互功能**
   - 真实电影评分
   - 实时推荐更新
   - 个性化推荐

## 项目结构

```
movie_recommendation_system/
├── backend/                    # Django后端
│   ├── movie_recommender/      # Django项目配置
│   ├── recommendation/         # 推荐应用
│   │   ├── models.py          # 数据模型
│   │   ├── serializers.py     # API序列化器
│   │   ├── views.py           # API视图
│   │   ├── collaborative_filtering.py  # 协同过滤算法
│   │   └── migrations/        # 数据库迁移
│   ├── db.sqlite3             # 数据库文件
│   ├── manage.py              # Django管理脚本
│   ├── populate_data.py       # 示例数据脚本
│   └── requirements.txt       # Python依赖
│
└── frontend/                  # Vue前端
    ├── public/                # 静态资源
    ├── src/                   # 源代码
    │   ├── components/        # Vue组件
    │   ├── views/             # 页面视图
    │   │   └── HomeView.vue   # 主页面
    │   ├── router/            # 路由配置
    │   └── main.ts            # 应用入口
    ├── package.json           # Node.js依赖
    └── vue.config.js          # Vue配置
```

## 安装和运行

### 后端设置

1. 进入后端目录：
   ```bash
   cd movie_recommendation_system/backend
   ```

2. 安装Python依赖：
   ```bash
   pip install django djangorestframework django-cors-headers numpy pandas scikit-learn
   ```

3. 运行数据库迁移：
   ```bash
   python manage.py migrate
   ```

4. 创建示例数据：
   ```bash
   python populate_data.py
   ```

5. 启动开发服务器：
   ```bash
   python manage.py runserver
   ```
   服务器将在 http://localhost:8000 运行

### 前端设置

1. 进入前端目录：
   ```bash
   cd movie_recommendation_system/frontend
   ```

2. 安装Node.js依赖：
   ```bash
   npm install
   ```

3. 启动开发服务器：
   ```bash
   npm run serve
   ```
   应用将在 http://localhost:8080 运行

## API接口

### 认证相关
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/logout/` - 用户注销
- `GET /api/auth/profile/` - 获取用户信息
- `PUT /api/auth/profile/` - 更新用户信息
- `POST /api/auth/change-password/` - 修改密码
- `GET /api/auth/check/` - 检查认证状态
- `POST /api/auth/token-login/` - Token登录

### 电影相关
- `GET /api/movies/` - 获取所有电影
- `GET /api/movies/{id}/` - 获取特定电影

### 用户相关
- `GET /api/users/` - 获取所有用户（需要认证）
- `GET /api/users/{id}/` - 获取特定用户（需要认证）

### 推荐相关
- `GET /api/recommendations/` - 获取电影推荐（需要认证）
  - 参数: `user_id`, `algorithm` (user_based/item_based), `top_n`
- `GET /api/top-movies/` - 获取热门电影
  - 参数: `top_n`
- `GET /api/similar-movies/{movie_id}/` - 获取相似电影
  - 参数: `top_n`

### 评分相关
- `GET /api/ratings/` - 获取所有评分（需要认证）
- `POST /api/ratings/` - 创建新评分（需要认证）

## 算法说明

### 协同过滤算法

系统实现了两种协同过滤算法：

1. **基于用户的协同过滤**
   - 计算用户之间的相似度（余弦相似度）
   - 找到与目标用户相似的用户
   - 根据相似用户的评分预测目标用户对未评分电影的评分
   - 推荐预测评分最高的电影

2. **基于物品的协同过滤**
   - 计算电影之间的相似度（余弦相似度）
   - 找到与用户已评分电影相似的电影
   - 根据相似电影的评分预测用户对未评分电影的评分
   - 推荐预测评分最高的电影

### 相似度计算

使用余弦相似度计算用户或电影之间的相似度：
```
similarity(A, B) = (A·B) / (||A|| * ||B||)
```

## 使用示例

1. 访问前端应用：http://localhost:8080
2. 注册新账户或使用测试账户登录（用户名: admin, 密码: admin123）
3. 登录后，点击"基于用户的推荐"获取个性化推荐
4. 点击电影卡片查看相似电影
5. 尝试不同的推荐算法进行比较
6. 为电影评分以改进推荐结果

## 注意事项

1. 确保后端服务器在运行状态，前端才能正常获取数据
2. 示例数据是随机生成的，实际推荐效果可能有限
3. 可以修改`populate_data.py`添加更多电影和评分数据
4. 生产环境建议使用更强大的数据库（如PostgreSQL）和缓存系统

## 扩展建议

1. **算法优化**
   - 实现矩阵分解（SVD）算法
   - 添加时间衰减因子
   - 考虑冷启动问题

2. **功能增强**
   - 用户注册和登录
   - 真实的评分系统
   - 电影搜索功能
   - 个性化推荐列表

3. **性能优化**
   - 添加缓存层（Redis）
   - 异步计算推荐结果
   - 分页加载电影列表

## 许可证

MIT License