<script setup lang="ts">
import { ClipboardCheck, FileQuestion, NotebookTabs, PenLine, TrendingUp, UsersRound } from "lucide-vue-next";
import { computed, onMounted, ref } from "vue";

import { getDashboardSummary, type DashboardSummary } from "@/api/dashboard";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const loading = ref(false);
const summary = ref<DashboardSummary | null>(null);

const teacherStats = computed(() => {
  if (!summary.value || summary.value.role !== "teacher") {
    return [];
  }
  return [
    { label: "题目总数", value: summary.value.question_count, icon: FileQuestion, tone: "teal" },
    { label: "试卷总数", value: summary.value.paper_count, icon: NotebookTabs, tone: "blue" },
    { label: "考试总数", value: summary.value.exam_count, icon: ClipboardCheck, tone: "amber" },
    { label: "待阅答卷", value: summary.value.waiting_review_count, icon: PenLine, tone: "rose" },
    { label: "学生账号", value: summary.value.student_count, icon: UsersRound, tone: "blue" },
    { label: "已提交答卷", value: summary.value.submitted_count, icon: TrendingUp, tone: "teal" },
  ];
});

const studentStats = computed(() => {
  if (!summary.value || summary.value.role !== "student") {
    return [];
  }
  return [
    { label: "可参加考试", value: summary.value.upcoming_exam_count, icon: ClipboardCheck, tone: "amber" },
    { label: "参加次数", value: summary.value.exam_count, icon: NotebookTabs, tone: "blue" },
    { label: "已提交", value: summary.value.submitted_count, icon: TrendingUp, tone: "teal" },
    { label: "平均分", value: summary.value.average_score, icon: PenLine, tone: "rose" },
    { label: "错题收藏", value: summary.value.error_archive_count, icon: FileQuestion, tone: "teal" },
  ];
});

const quickLinks = computed(() => {
  if (session.role === "student") {
    return [
      { title: "参加考试", description: "查看可参加考试，进入答题并提交答卷。", path: "/exams", icon: ClipboardCheck, accent: "amber" },
    ];
  }

  return [
    { title: "题库管理", description: "维护选择题、判断题，支持筛选、增删改查和随机抽题。", path: "/questions", icon: FileQuestion, accent: "teal" },
    { title: "试卷管理", description: "创建试卷、配置模块、关联题目并发布到考试流程。", path: "/papers", icon: NotebookTabs, accent: "blue" },
    { title: "考试管理", description: "创建考试、选择试卷、设置时间并发布考试。", path: "/exams", icon: ClipboardCheck, accent: "amber" },
    { title: "阅卷中心", description: "查看提交记录，客观题自动判分，主观题人工评分。", path: "/reviews", icon: PenLine, accent: "rose" },
  ];
});

async function loadSummary() {
  if (!session.role) {
    return;
  }
  loading.value = true;
  try {
    const result = await getDashboardSummary({
      role: session.role,
      user_id: session.user?.id,
    });
    summary.value = result.data;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void loadSummary();
});
</script>

<template>
  <section class="dashboard" v-loading="loading">
    <div class="summary-band">
      <div>
        <p>{{ session.role === "teacher" ? "Teacher Workspace" : "Student Workspace" }}</p>
        <h2>{{ session.user?.real_name || session.user?.username }}，欢迎回来</h2>
      </div>
      <span>{{ session.role === "teacher" ? "管理题库、试卷、考试与阅卷" : "查看考试安排并完成答题" }}</span>
    </div>

    <div class="stat-grid">
      <div v-for="item in session.role === 'teacher' ? teacherStats : studentStats" :key="item.label" class="stat-card" :class="item.tone">
        <component :is="item.icon" :size="24" />
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </div>

    <div class="module-grid">
      <RouterLink v-for="item in quickLinks" :key="item.path" :to="item.path" class="module-card" :class="item.accent">
        <component :is="item.icon" :size="28" />
        <h3>{{ item.title }}</h3>
        <p>{{ item.description }}</p>
      </RouterLink>
    </div>
  </section>
</template>
