import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import DoubanView from "../views/DoubanView.vue";
import ProfileView from "../views/ProfileView.vue";
import AIChatView from "../views/AIChatView.vue";
import VideoPlatformView from "../views/VideoPlatformView.vue";
import MovieDetailView from "../views/MovieDetailView.vue";

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
    path: "/movie-detail",
    name: "movie-detail",
    component: MovieDetailView,
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
    component: () => import("../views/AboutView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach((to: any, from: any, next: any) => {
  const authStore = useAuthStore();

  if (to.matched.some((record: any) => record.meta.requiresAuth)) {
    if (!authStore.isAuthenticated) {
      next({
        path: "/login",
        query: { redirect: to.fullPath },
      });
    } else {
      next();
    }
  } else if (to.path === "/login" || to.path === "/register") {
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
