<script setup lang="ts">
import { ClipboardCheck, FileQuestion, Percent, RefreshCw, TrendingUp } from "lucide-vue-next";
import { computed, onMounted, ref } from "vue";

import { getScoreAnalyze, type ScoreAnalyzeResult } from "@/api/scores";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const loading = ref(false);
const analysis = ref<ScoreAnalyzeResult | null>(null);

const stats = computed(() => {
  if (!analysis.value) {
    return [];
  }
  return [
    { label: "参加次数", value: analysis.value.exam_count, icon: ClipboardCheck, tone: "blue" },
    { label: "已提交", value: analysis.value.submitted_count, icon: TrendingUp, tone: "teal" },
    { label: "平均分", value: analysis.value.average_score, icon: Percent, tone: "amber" },
    { label: "题型数量", value: Object.keys(analysis.value.question_type_stats).length, icon: FileQuestion, tone: "rose" },
  ];
});

const typeRows = computed(() => {
  if (!analysis.value) {
    return [];
  }
  return Object.entries(analysis.value.question_type_stats).map(([type, row]) => ({
    type,
    ...row,
    rate_percent: Math.round(row.score_rate * 100),
  }));
});

function typeLabel(type: string) {
  if (type === "select") return "选择题";
  if (type === "judge") return "判断题";
  return type || "未知";
}

async function loadAnalysis() {
  if (!session.user?.id) {
    return;
  }
  loading.value = true;
  try {
    const result = await getScoreAnalyze(session.user.id);
    analysis.value = result.data;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void loadAnalysis();
});
</script>

<template>
  <section class="page-stack" v-loading="loading">
    <div class="toolbar-panel">
      <div>
        <strong>学习表现</strong>
        <p class="muted-text">根据已提交考试统计成绩趋势和题型得分率。</p>
      </div>
      <el-button :icon="RefreshCw" @click="loadAnalysis">刷新</el-button>
    </div>

    <div class="stat-grid">
      <div v-for="item in stats" :key="item.label" class="stat-card" :class="item.tone">
        <component :is="item.icon" :size="24" />
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </div>

    <div class="analysis-grid">
      <div class="table-panel">
        <div class="panel-heading">
          <strong>成绩趋势</strong>
        </div>
        <el-table :data="analysis?.trend || []" border stripe>
          <el-table-column prop="exam_title" label="考试" min-width="180" />
          <el-table-column prop="score" label="得分" width="100" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.submit_status ? 'success' : 'info'">{{ row.submit_status ? "已提交" : "未提交" }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="submitted_at" label="提交时间" width="190" />
        </el-table>
      </div>

      <div class="table-panel">
        <div class="panel-heading">
          <strong>题型得分率</strong>
        </div>
        <div v-if="typeRows.length === 0" class="empty-soft">暂无题型统计</div>
        <div v-else class="type-score-list">
          <div v-for="row in typeRows" :key="row.type" class="type-score-row">
            <div>
              <strong>{{ typeLabel(row.type) }}</strong>
              <span>{{ row.actual_mark }} / {{ row.full_mark }} 分</span>
            </div>
            <el-progress :percentage="row.rate_percent" />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
