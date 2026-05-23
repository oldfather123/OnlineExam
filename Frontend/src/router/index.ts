import { createRouter, createWebHistory } from "vue-router";

import AppLayout from "@/layouts/AppLayout.vue";
import DashboardView from "@/views/DashboardView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: AppLayout,
      children: [
        {
          path: "",
          name: "dashboard",
          component: DashboardView,
          meta: { title: "工作台" },
        },
        {
          path: "questions",
          name: "questions",
          component: () => import("@/views/questions/QuestionsView.vue"),
          meta: { title: "题库管理", module: "questions" },
        },
        {
          path: "papers",
          name: "papers",
          component: () => import("@/views/papers/PapersView.vue"),
          meta: { title: "试卷管理", module: "papers" },
        },
        {
          path: "papers/:id/configure",
          name: "paper-configure",
          component: () => import("@/views/papers/PaperConfigureView.vue"),
          meta: { title: "试卷配置", module: "papers" },
        },
        {
          path: "exams",
          name: "exams",
          component: () => import("@/views/PlaceholderView.vue"),
          meta: { title: "考试管理", module: "exams" },
        },
        {
          path: "reviews",
          name: "reviews",
          component: () => import("@/views/PlaceholderView.vue"),
          meta: { title: "阅卷中心", module: "reviews" },
        },
      ],
    },
  ],
});

router.afterEach((to) => {
  document.title = `${String(to.meta.title || "工作台")} - 在线考试系统`;
});

export default router;
