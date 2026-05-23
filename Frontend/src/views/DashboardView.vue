<script setup lang="ts">
import { ClipboardCheck, FileQuestion, NotebookTabs, UsersRound } from "lucide-vue-next";

const modules = [
  {
    title: "题库管理",
    description: "维护选择题、判断题，支持筛选、增删改查和随机抽题。",
    path: "/questions",
    icon: FileQuestion,
    accent: "teal",
  },
  {
    title: "试卷管理",
    description: "创建试卷、配置模块、关联题目并发布到考试流程。",
    path: "/papers",
    icon: NotebookTabs,
    accent: "blue",
  },
  {
    title: "考试管理",
    description: "进入考试、读取在线试卷、保存答案和提交答卷。",
    path: "/exams",
    icon: ClipboardCheck,
    accent: "amber",
  },
  {
    title: "阅卷中心",
    description: "查看提交记录，客观题自动判分，主观题人工评分。",
    path: "/reviews",
    icon: UsersRound,
    accent: "rose",
  },
];
</script>

<template>
  <section class="dashboard">
    <div class="summary-band">
      <div>
        <p>Frontend Phase 1</p>
        <h2>前端基础框架已就绪</h2>
      </div>
      <span>Vue 3 / Vite / Element Plus / Pinia</span>
    </div>

    <div class="module-grid">
      <RouterLink v-for="item in modules" :key="item.path" :to="item.path" class="module-card" :class="item.accent">
        <component :is="item.icon" :size="28" />
        <h3>{{ item.title }}</h3>
        <p>{{ item.description }}</p>
      </RouterLink>
    </div>
  </section>
</template>
