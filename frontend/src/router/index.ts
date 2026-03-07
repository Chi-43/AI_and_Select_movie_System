import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import DoubanView from "../views/DoubanView.vue";
import ProfileView from "../views/ProfileView.vue";
import AIChatView from "../views/AIChatView.vue";
import VideoPlatformView from "../views/VideoPlatformView.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/douban",
    name: "douban",
    component: DoubanView,
  },
  {
    path: "/video-platform",
    name: "video-platform",
    component: VideoPlatformView,
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  {
    path: "/register",
    name: "register",
    component: RegisterView,
  },
  {
    path: "/profile",
    name: "profile",
    component: ProfileView,
    meta: { requiresAuth: true },
  },
  {
    path: "/ai-chat",
    name: "ai-chat",
    component: AIChatView,
  },
  {
    path: "/about",
    name: "about",
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/AboutView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// 路由守卫
router.beforeEach((to: any, from: any, next: any) => {
  const authStore = useAuthStore();

  // 检查路由是否需要认证
  if (to.matched.some((record: any) => record.meta.requiresAuth)) {
    if (!authStore.isAuthenticated) {
      // 未登录，重定向到登录页面
      next({
        path: "/login",
        query: { redirect: to.fullPath },
      });
    } else {
      next();
    }
  } else if (to.path === "/login" || to.path === "/register") {
    // 如果用户已经登录，访问登录/注册页面时重定向到首页
    if (authStore.isAuthenticated) {
      next({ path: "/" });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
