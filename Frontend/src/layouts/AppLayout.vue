<script setup lang="ts">
import { BookOpenCheck, ClipboardList, FileQuestion, LayoutDashboard, PenLine, ScrollText } from "lucide-vue-next";
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const menuItems = [
  { path: "/", label: "工作台", icon: LayoutDashboard },
  { path: "/questions", label: "题库管理", icon: FileQuestion },
  { path: "/papers", label: "试卷管理", icon: ScrollText },
  { path: "/exams", label: "考试管理", icon: ClipboardList },
  { path: "/reviews", label: "阅卷中心", icon: PenLine },
];

const activePath = computed(() => route.path);
</script>

<template>
  <el-container class="app-shell">
    <el-aside class="app-sidebar" width="236px">
      <div class="brand">
        <BookOpenCheck :size="28" />
        <div>
          <strong>在线考试系统</strong>
          <span>Online Exam</span>
        </div>
      </div>

      <el-menu router :default-active="activePath" class="side-menu">
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div>
          <p>综合实践</p>
          <h1>{{ route.meta.title }}</h1>
        </div>
      </el-header>

      <el-main class="app-main">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>
