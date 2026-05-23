<script setup lang="ts">
import { BookOpenCheck, ClipboardList, FileQuestion, LayoutDashboard, LogOut, PenLine, ScrollText } from "lucide-vue-next";
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useSessionStore } from "@/stores/session";

const route = useRoute();
const router = useRouter();
const session = useSessionStore();

const menuItems = [
  { path: "/", label: "工作台", icon: LayoutDashboard, roles: ["teacher", "student"] },
  { path: "/questions", label: "题库管理", icon: FileQuestion, roles: ["teacher"] },
  { path: "/papers", label: "试卷管理", icon: ScrollText, roles: ["teacher"] },
  { path: "/exams", label: "考试管理", icon: ClipboardList, roles: ["teacher", "student"] },
  { path: "/reviews", label: "阅卷中心", icon: PenLine, roles: ["teacher"] },
];

const activePath = computed(() => route.path);
const visibleMenuItems = computed(() => menuItems.filter((item) => session.role && item.roles.includes(session.role)));

async function logout() {
  session.logout();
  await router.push("/login");
}
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
        <el-menu-item v-for="item in visibleMenuItems" :key="item.path" :index="item.path">
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
        <div class="user-chip">
          <span>{{ session.user?.real_name || session.user?.username }}</span>
          <el-tag size="small">{{ session.role === "teacher" ? "教师" : "学生" }}</el-tag>
          <el-tooltip content="退出登录">
            <el-button circle :icon="LogOut" @click="logout" />
          </el-tooltip>
        </div>
      </el-header>

      <el-main class="app-main">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>
