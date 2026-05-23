import { createRouter, createWebHistory } from "vue-router";

import AppLayout from "@/layouts/AppLayout.vue";
import { useSessionStore } from "@/stores/session";
import DashboardView from "@/views/DashboardView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { title: "登录", public: true },
    },
    {
      path: "/",
      component: AppLayout,
      children: [
        {
          path: "",
          name: "dashboard",
          component: DashboardView,
          meta: { title: "工作台", roles: ["teacher", "student"] },
        },
        {
          path: "questions",
          name: "questions",
          component: () => import("@/views/questions/QuestionsView.vue"),
          meta: { title: "题库管理", module: "questions", roles: ["teacher"] },
        },
        {
          path: "papers",
          name: "papers",
          component: () => import("@/views/papers/PapersView.vue"),
          meta: { title: "试卷管理", module: "papers", roles: ["teacher"] },
        },
        {
          path: "papers/:id/configure",
          name: "paper-configure",
          component: () => import("@/views/papers/PaperConfigureView.vue"),
          meta: { title: "试卷配置", module: "papers", roles: ["teacher"] },
        },
        {
          path: "exams",
          name: "exams",
          component: () => import("@/views/exams/ExamTakingView.vue"),
          meta: { title: "考试管理", module: "exams", roles: ["teacher", "student"] },
        },
        {
          path: "reviews",
          name: "reviews",
          component: () => import("@/views/reviews/ReviewsView.vue"),
          meta: { title: "阅卷中心", module: "reviews", roles: ["teacher"] },
        },
        {
          path: "users",
          name: "users",
          component: () => import("@/views/users/UsersView.vue"),
          meta: { title: "用户管理", module: "users", roles: ["teacher"] },
        },
      ],
    },
  ],
});

router.beforeEach((to) => {
  const session = useSessionStore();
  if (to.meta.public) {
    return session.isLoggedIn ? "/" : true;
  }
  if (!session.isLoggedIn) {
    return "/login";
  }
  const roles = to.meta.roles as string[] | undefined;
  if (roles && session.role && !roles.includes(session.role)) {
    return session.role === "student" ? "/exams" : "/";
  }
  return true;
});

router.afterEach((to) => {
  document.title = `${String(to.meta.title || "工作台")} - 在线考试系统`;
});

export default router;
