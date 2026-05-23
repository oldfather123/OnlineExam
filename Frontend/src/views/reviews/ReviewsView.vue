<script setup lang="ts">
import { Bot, ClipboardList, RefreshCw, Save } from "lucide-vue-next";
import { ElMessage } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";

import {
  autoGrade,
  getReviewPapers,
  getReviewResultDetail,
  getReviewStatistics,
  getReviewStudents,
  submitReviewScores,
  type ReviewPaperItem,
  type ReviewQuestionItem,
  type ReviewResultDetail,
  type ReviewStatistics,
  type ReviewStudentItem,
} from "@/api/scores";

const loadingPapers = ref(false);
const loadingStudents = ref(false);
const loadingDetail = ref(false);
const saving = ref(false);
const papers = ref<ReviewPaperItem[]>([]);
const students = ref<ReviewStudentItem[]>([]);
const statistics = ref<ReviewStatistics | null>(null);
const detail = ref<ReviewResultDetail | null>(null);
const selectedExamId = ref("");
const selectedResultId = ref("");
const totalPapers = ref(0);
const totalStudents = ref(0);

const paperPager = reactive({ page: 1, page_size: 20 });
const studentPager = reactive({ page: 1, page_size: 20 });

const reviewItems = computed(() =>
  (detail.value?.questions || []).map((item) => ({
    question_id: item.question_id,
    mark: Number(item.score || 0),
    comment: item.comment || "",
  })),
);

function answerText(item: ReviewQuestionItem) {
  const value = item.student_answer?.value;
  if (Array.isArray(value)) {
    return value.join("，");
  }
  return value || "未作答";
}

async function loadPapers() {
  loadingPapers.value = true;
  try {
    const result = await getReviewPapers(paperPager);
    papers.value = result.data.items;
    totalPapers.value = result.data.total;
  } finally {
    loadingPapers.value = false;
  }
}

async function selectExam(row: ReviewPaperItem) {
  selectedExamId.value = row.exam_id;
  selectedResultId.value = "";
  detail.value = null;
  await Promise.all([loadStudents(), loadStatistics()]);
}

async function loadStudents() {
  if (!selectedExamId.value) {
    return;
  }
  loadingStudents.value = true;
  try {
    const result = await getReviewStudents(selectedExamId.value, studentPager);
    students.value = result.data.items;
    totalStudents.value = result.data.total;
  } finally {
    loadingStudents.value = false;
  }
}

async function loadStatistics() {
  if (!selectedExamId.value) {
    return;
  }
  const result = await getReviewStatistics(selectedExamId.value);
  statistics.value = result.data;
}

async function selectResult(row: ReviewStudentItem) {
  selectedResultId.value = row.exam_result_id;
  loadingDetail.value = true;
  try {
    const result = await getReviewResultDetail(row.exam_result_id);
    detail.value = result.data;
  } finally {
    loadingDetail.value = false;
  }
}

async function handleAutoGrade() {
  if (!selectedResultId.value) {
    ElMessage.warning("请先选择答卷");
    return;
  }
  const result = await autoGrade(selectedResultId.value);
  ElMessage.success(`自动判分完成：${result.data.auto_graded_count} 题`);
  await selectResult({ exam_result_id: selectedResultId.value } as ReviewStudentItem);
  await loadStudents();
  await loadStatistics();
}

async function saveScores(finalize = false) {
  if (!selectedResultId.value) {
    ElMessage.warning("请先选择答卷");
    return;
  }
  saving.value = true;
  try {
    await submitReviewScores(selectedResultId.value, {
      grader_id: "teacher",
      finalize,
      items: reviewItems.value,
    });
    ElMessage.success(finalize ? "评分已完成" : "评分已保存");
    await selectResult({ exam_result_id: selectedResultId.value } as ReviewStudentItem);
    await loadStudents();
    await loadStatistics();
  } finally {
    saving.value = false;
  }
}

onMounted(() => {
  void loadPapers();
});
</script>

<template>
  <section class="review-layout">
    <div class="table-panel">
      <div class="panel-heading">
        <strong>待阅考试</strong>
        <el-button :icon="RefreshCw" @click="loadPapers">刷新</el-button>
      </div>
      <el-table v-loading="loadingPapers" :data="papers" border stripe height="280" highlight-current-row @row-click="selectExam">
        <el-table-column prop="exam_title" label="考试" min-width="180" />
        <el-table-column label="试卷" min-width="160">
          <template #default="{ row }">{{ row.paper.title }}</template>
        </el-table-column>
        <el-table-column label="提交" width="110">
          <template #default="{ row }">{{ row.review_stats.submitted_students }} / {{ row.review_stats.total_students }}</template>
        </el-table-column>
      </el-table>
      <div class="pagination-row">
        <el-pagination
          v-model:current-page="paperPager.page"
          :page-size="paperPager.page_size"
          layout="total, prev, pager, next"
          :total="totalPapers"
          @current-change="loadPapers"
        />
      </div>
    </div>

    <div class="table-panel">
      <div class="panel-heading">
        <strong>考生答卷</strong>
        <el-tag v-if="statistics">平均分 {{ statistics.average_score }}</el-tag>
      </div>
      <el-table v-loading="loadingStudents" :data="students" border stripe height="280" highlight-current-row @row-click="selectResult">
        <el-table-column prop="student_id" label="学生 ID" min-width="150" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.submit_status ? 'success' : 'info'">{{ row.submit_status ? "已提交" : "未提交" }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="result_mark" label="得分" width="100" />
      </el-table>
      <div class="pagination-row">
        <el-pagination
          v-model:current-page="studentPager.page"
          :page-size="studentPager.page_size"
          layout="total, prev, pager, next"
          :total="totalStudents"
          @current-change="loadStudents"
        />
      </div>
    </div>

    <div class="review-detail table-panel">
      <div class="panel-heading">
        <strong>答卷详情</strong>
        <div>
          <el-button :icon="Bot" :disabled="!detail" @click="handleAutoGrade">客观题判分</el-button>
          <el-button :icon="Save" :disabled="!detail" :loading="saving" @click="saveScores(false)">保存评分</el-button>
          <el-button type="primary" :icon="ClipboardList" :disabled="!detail" :loading="saving" @click="saveScores(true)">完成评分</el-button>
        </div>
      </div>

      <el-empty v-if="!detail" description="请选择一份答卷" />

      <div v-else v-loading="loadingDetail" class="review-question-list">
        <div v-for="(item, index) in detail.questions" :key="item.question_id" class="review-question">
          <div class="question-heading">
            <strong>{{ index + 1 }}. {{ item.topic }}</strong>
            <el-tag>{{ item.marks }} 分</el-tag>
          </div>
          <div class="answer-compare">
            <span>学生答案：{{ answerText(item) }}</span>
            <span>标准答案：{{ item.standard_answer }}</span>
          </div>
          <div class="grade-row">
            <el-input-number v-model="item.score" :min="0" :max="Number(item.marks)" :precision="1" controls-position="right" />
            <el-input v-model="item.comment" placeholder="评分备注" />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
