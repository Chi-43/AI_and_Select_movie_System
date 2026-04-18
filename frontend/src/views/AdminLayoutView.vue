<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">🎬</div>
        <div class="brand-text">
          <h2>后台管理</h2>
          <p>电影推荐系统</p>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          to="/admin/dashboard"
          class="nav-item"
          active-class="active"
        >
          <span>📊</span>
          <span>控制台</span>
        </router-link>
        <router-link to="/admin/users" class="nav-item" active-class="active">
          <span>👤</span>
          <span>用户管理</span>
        </router-link>
        <router-link to="/admin/movies" class="nav-item" active-class="active">
          <span>🎞️</span>
          <span>电影管理</span>
        </router-link>
        <router-link
          to="/admin/comments"
          class="nav-item"
          active-class="active"
        >
          <span>💬</span>
          <span>评论管理</span>
        </router-link>
        <router-link to="/admin/profile" class="nav-item" active-class="active">
          <span>⚙️</span>
          <span>个人信息</span>
        </router-link>
      </nav>
    </aside>

    <div class="main-area">
      <header class="topbar">
        <div>
          <h1 class="page-title">{{ currentTitle }}</h1>
          <p class="page-subtitle">管理员后台功能入口</p>
        </div>

        <div class="topbar-right">
          <div class="admin-info">
            <span class="admin-avatar">👑</span>
            <div>
              <div class="admin-name">
                {{ adminUser?.username || "管理员" }}
              </div>
              <div class="admin-role">系统管理员</div>
            </div>
          </div>

          <button class="logout-btn" @click="handleLogout">退出</button>
        </div>
      </header>

      <main class="content-area">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref, onMounted } from "vue";
import { useRoute } from "vue-router";

export default defineComponent({
  name: "AdminLayoutView",
  setup() {
    const route = useRoute();
    const adminUser = ref<any>(null);

    const titleMap: Record<string, string> = {
      "/admin/dashboard": "后台控制台",
      "/admin/users": "用户管理",
      "/admin/movies": "电影管理",
      "/admin/comments": "评论管理",
      "/admin/profile": "个人信息",
    };

    const currentTitle = computed(() => {
      return titleMap[route.path] || "后台管理";
    });

    const loadAdminUser = () => {
      const userText = localStorage.getItem("admin_user");
      if (userText) {
        try {
          adminUser.value = JSON.parse(userText);
        } catch {
          adminUser.value = null;
        }
      }
    };

    const handleLogout = () => {
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_user");
      window.location.href = "/admin/login";
    };

    onMounted(() => {
      loadAdminUser();

      const token = localStorage.getItem("admin_token");
      if (!token) {
        window.location.href = "/admin/login";
      }
    });

    return {
      adminUser,
      currentTitle,
      handleLogout,
    };
  },
});
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 260px 1fr;
  background: radial-gradient(
      circle at top right,
      rgba(99, 102, 241, 0.08),
      transparent 28%
    ),
    radial-gradient(
      circle at bottom left,
      rgba(139, 92, 246, 0.08),
      transparent 30%
    ),
    var(--bg-main);
}

.sidebar {
  border-right: 1px solid var(--panel-border);
  background: var(--panel-bg);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  padding: 24px 18px;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--panel-border);
}

.brand-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-glow);
  font-size: 24px;
}

.brand-text h2 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-primary);
}

.brand-text p {
  margin: 4px 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  border-radius: var(--radius-lg);
  background: rgba(99, 102, 241, 0.04);
  border: 1px solid rgba(99, 102, 241, 0.08);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 14px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  font-weight: 700;
}

.nav-item:hover {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--primary-gradient);
  color: white;
  box-shadow: var(--shadow-glow);
}

.main-area {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px 28px;
  border-bottom: 1px solid var(--panel-border);
  background: var(--panel-bg);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.page-title {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.8rem;
}

.page-subtitle {
  margin: 6px 0 0;
  color: var(--text-secondary);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--card-bg, rgba(255, 255, 255, 0.08));
  border: 1px solid var(--panel-border);
}

.admin-avatar {
  font-size: 1.4rem;
}

.admin-name {
  color: var(--text-primary);
  font-weight: 800;
}

.admin-role {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.logout-btn {
  border: none;
  border-radius: var(--radius-md);
  padding: 10px 16px;
  background: #ef4444;
  color: white;
  font-weight: 800;
  cursor: pointer;
}

.content-area {
  padding: 24px 28px;
}

@media (max-width: 960px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    display: none;
  }

  .topbar {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .topbar-right {
    justify-content: space-between;
  }
}
</style>
