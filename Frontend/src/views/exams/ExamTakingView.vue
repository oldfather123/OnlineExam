<script setup lang="ts">
import { ClipboardCheck, Edit3, EyeOff, Megaphone, Plus, RefreshCw, Save, SendHorizontal, Trash2 } from "lucide-vue-next";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import {
  createExam,
  deleteExam,
  enterExam,
  getAttendableExams,
  getExams,
  getOnlinePaper,
  publishExam,
  unpublishExam,
  updateExam,
  type Exam,
  type ExamPayload,
  type ExamQuery,
  type ExamEnterResult,
  type OnlinePaper,
} from "@/api/exams";
import { getPaperSelector, type Paper } from "@/api/papers";
import { commitAnswers, type AnswerItem } from "@/api/scores";
import { useSessionStore } from "@/stores/session";

interface EnterForm {
  exam_id: string;
  student_id: string;
}

const activeTab = ref("manage");
const session = useSessionStore();
const router = useRouter();
const loading = ref(false);
const savingExam = ref(false);
const statusChanging = ref("");
const examDialogVisible = ref(false);
const editingExamId = ref("");
const examFormRef = ref<FormInstance>();
const enterFormRef = ref<FormInstance>();
const exams = ref<Exam[]>([]);
const attendableExams = ref<Exam[]>([]);
const papers = ref<Paper[]>([]);
const total = ref(0);
const entering = ref(false);
const saving = ref(false);
const submitting = ref(false);
const enterResult = ref<ExamEnterResult | null>(null);
const onlinePaper = ref<OnlinePaper | null>(null);
const answers = reactive<Record<string, string>>({});

const query = reactive<ExamQuery>({
  title: "",
  is_published: "",
  currentPage: 1,
  pageSize: 10,
});

const examForm = reactive<ExamPayload>({
  paper_id: "",
  title: "",
  start_time: "",
  end_time: "",
  is_published: false,
});

const enterForm = reactive<EnterForm>({
  exam_id: "",
  student_id: session.role === "student" ? session.user?.id || "" : "",
});

const examRules: FormRules<ExamPayload> = {
  paper_id: [{ required: true, message: "请选择试卷", trigger: "change" }],
  title: [{ required: true, message: "请输入考试名称", trigger: "blur" }],
  start_time: [{ required: true, message: "请选择开始时间", trigger: "change" }],
  end_time: [{ required: true, message: "请选择结束时间", trigger: "change" }],
};

const enterRules: FormRules<EnterForm> = {
  exam_id: [{ required: true, message: "请选择或输入考试 ID", trigger: "blur" }],
  student_id: [{ required: true, message: "请输入学生 ID", trigger: "blur" }],
};

const allQuestions = computed(() => onlinePaper.value?.modules.flatMap((module) => module.questions) || []);
const answeredCount = computed(() => allQuestions.value.filter((item) => answers[item.question_id]).length);
const examDialogTitle = computed(() => (editingExamId.value ? "编辑考试" : "新增考试"));

function optionList(options: string[] | string | undefined) {
  if (Array.isArray(options)) {
    return options;
  }
  if (!options) {
    return [];
  }
  try {
    const parsed = JSON.parse(options);
    return Array.isArray(parsed) ? parsed.map((item) => String(item)) : [];
  } catch {
    return String(options).split(/\r?\n/).filter(Boolean);
  }
}

function buildAnswerItems(): AnswerItem[] {
  return allQuestions.value.map((item) => ({
    question_id: item.question_id,
    type: item.type,
    payload: {
      value: answers[item.question_id] || "",
    },
  }));
}

function resetExamForm() {
  editingExamId.value = "";
  Object.assign(examForm, {
    paper_id: "",
    title: "",
    start_time: "",
    end_time: "",
    is_published: false,
  });
  examFormRef.value?.clearValidate();
}

async function loadExams() {
  loading.value = true;
  try {
    const result = await getExams(query);
    exams.value = result.data.data;
    total.value = result.data.total;
  } finally {
    loading.value = false;
  }
}

async function loadPapers() {
  const result = await getPaperSelector();
  papers.value = result.data.data;
}

async function loadAttendableExams() {
  const result = await getAttendableExams();
  attendableExams.value = result.data.data;
}

function handleSearch() {
  query.currentPage = 1;
  void loadExams();
}

function handleReset() {
  query.title = "";
  query.is_published = "";
  query.currentPage = 1;
  void loadExams();
}

function openCreateExamDialog() {
  resetExamForm();
  examDialogVisible.value = true;
}

function openEditExamDialog(row: Exam) {
  editingExamId.value = row.id;
  Object.assign(examForm, {
    paper_id: row.paper_id,
    title: row.title,
    start_time: row.start_time,
    end_time: row.end_time,
    is_published: row.is_published,
  });
  examDialogVisible.value = true;
}

async function submitExamForm() {
  await examFormRef.value?.validate();
  if (new Date(examForm.start_time).getTime() >= new Date(examForm.end_time).getTime()) {
    ElMessage.warning("考试开始时间必须早于结束时间");
    return;
  }

  savingExam.value = true;
  try {
    const payload = { ...examForm };
    if (editingExamId.value) {
      await updateExam(editingExamId.value, payload);
      ElMessage.success("考试已更新");
    } else {
      await createExam(payload);
      ElMessage.success("考试已创建");
    }
    examDialogVisible.value = false;
    await Promise.all([loadExams(), loadAttendableExams()]);
  } finally {
    savingExam.value = false;
  }
}

async function removeExam(row: Exam) {
  try {
    await ElMessageBox.confirm(`确认删除考试「${row.title}」吗？`, "删除确认", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
    await deleteExam(row.id);
    ElMessage.success("考试已删除");
    await Promise.all([loadExams(), loadAttendableExams()]);
  } catch {
    // User cancelled the confirmation dialog.
  }
}

async function togglePublish(row: Exam) {
  statusChanging.value = row.id;
  try {
    if (row.is_published) {
      await unpublishExam(row.id);
      ElMessage.success("已取消发布");
    } else {
      await publishExam(row.id);
      ElMessage.success("考试已发布");
    }
    await Promise.all([loadExams(), loadAttendableExams()]);
  } finally {
    statusChanging.value = "";
  }
}

function selectAttendExam(row: Exam) {
  enterForm.exam_id = row.id;
}

async function handleEnter() {
  await enterFormRef.value?.validate();
  entering.value = true;
  try {
    const enterResponse = await enterExam(enterForm);
    enterResult.value = enterResponse.data;
    const paperResponse = await getOnlinePaper({ exam_id: enterForm.exam_id });
    onlinePaper.value = paperResponse.data;
    Object.keys(answers).forEach((key) => delete answers[key]);
    ElMessage.success("进入考试成功");
  } finally {
    entering.value = false;
  }
}

async function saveAnswers(action: "save" | "submit") {
  if (!enterResult.value) {
    ElMessage.warning("请先进入考试");
    return;
  }

  if (action === "submit") {
    await ElMessageBox.confirm("提交后不能重复提交或修改，确认提交吗？", "提交确认", {
      type: "warning",
      confirmButtonText: "提交",
      cancelButtonText: "取消",
    });
  }

  const loadingTarget = action === "save" ? saving : submitting;
  loadingTarget.value = true;
  try {
    await commitAnswers({
      exam_result_id: enterResult.value.exam_result_id,
      action,
      client_ts: Date.now(),
      answers: buildAnswerItems(),
    });
    ElMessage.success(action === "save" ? "答案已保存" : "答卷已提交");
    if (action === "submit") {
      onlinePaper.value = null;
      enterResult.value = null;
      Object.keys(answers).forEach((key) => delete answers[key]);
      await loadAttendableExams();
      if (session.role === "student") {
        await router.push("/analysis");
      }
    }
  } finally {
    loadingTarget.value = false;
  }
}

onMounted(() => {
  if (session.role === "student") {
    activeTab.value = "taking";
    enterForm.student_id = session.user?.id || "";
  }
  void Promise.all([loadExams(), loadPapers(), loadAttendableExams()]);
});
</script>

<template>
  <section class="page-stack">
    <el-tabs v-model="activeTab" class="workspace-tabs">
      <el-tab-pane v-if="session.role === 'teacher'" label="考试管理" name="manage">
        <div class="toolbar-panel">
          <el-form :model="query" class="query-form" inline>
            <el-form-item label="考试名称">
              <el-input v-model="query.title" clearable placeholder="按考试名称搜索" @keyup.enter="handleSearch" />
            </el-form-item>
            <el-form-item label="发布状态">
              <el-select v-model="query.is_published" clearable placeholder="全部状态" class="type-select">
                <el-option label="已发布" value="true" />
                <el-option label="未发布" value="false" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :icon="RefreshCw" @click="handleSearch">查询</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
          <el-button type="primary" :icon="Plus" @click="openCreateExamDialog">新增考试</el-button>
        </div>

        <div class="table-panel">
          <el-table v-loading="loading" :data="exams" border stripe height="calc(100vh - 360px)">
            <el-table-column prop="title" label="考试名称" min-width="190" />
            <el-table-column prop="paper_title" label="关联试卷" min-width="180" />
            <el-table-column prop="start_time" label="开始时间" width="190" />
            <el-table-column prop="end_time" label="结束时间" width="190" />
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <el-tag :type="row.is_published ? 'success' : 'info'">{{ row.is_published ? "已发布" : "未发布" }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="210" fixed="right">
              <template #default="{ row }">
                <el-tooltip content="编辑">
                  <el-button circle :icon="Edit3" @click="openEditExamDialog(row)" />
                </el-tooltip>
                <el-tooltip :content="row.is_published ? '取消发布' : '发布'">
                  <el-button
                    circle
                    :type="row.is_published ? 'warning' : 'success'"
                    :icon="row.is_published ? EyeOff : Megaphone"
                    :loading="statusChanging === row.id"
                    @click="togglePublish(row)"
                  />
                </el-tooltip>
                <el-tooltip content="删除">
                  <el-button circle type="danger" :icon="Trash2" @click="removeExam(row)" />
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-row">
            <el-pagination
              v-model:current-page="query.currentPage"
              v-model:page-size="query.pageSize"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
              @size-change="loadExams"
              @current-change="loadExams"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="参加考试" name="taking">
        <div class="toolbar-panel">
          <el-form ref="enterFormRef" :model="enterForm" :rules="enterRules" class="query-form" inline>
            <el-form-item label="考试 ID" prop="exam_id">
              <el-input v-model="enterForm.exam_id" placeholder="从列表选择或手动输入" />
            </el-form-item>
            <el-form-item label="学生 ID" prop="student_id">
              <el-input v-model="enterForm.student_id" :disabled="session.role === 'student'" placeholder="请输入学生 ID" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :icon="ClipboardCheck" :loading="entering" @click="handleEnter">进入考试</el-button>
            </el-form-item>
          </el-form>
          <el-button :icon="RefreshCw" @click="loadAttendableExams">刷新可参加考试</el-button>
        </div>

        <div v-if="!onlinePaper" class="table-panel">
          <el-table :data="attendableExams" border stripe empty-text="暂无可参加考试" @row-click="selectAttendExam">
            <el-table-column prop="title" label="考试名称" min-width="190" />
            <el-table-column prop="paper_title" label="试卷" min-width="180" />
            <el-table-column prop="start_time" label="开始时间" width="190" />
            <el-table-column prop="end_time" label="结束时间" width="190" />
          </el-table>
        </div>

        <template v-else>
          <div class="detail-header">
            <div class="detail-title">
              <h2>{{ onlinePaper.paper.title }}</h2>
              <p>{{ onlinePaper.paper.description || "请在规定时间内完成答题" }}</p>
            </div>
            <div class="score-summary">
              <span>时长：{{ onlinePaper.paper.duration_minutes }} 分钟</span>
              <strong>{{ answeredCount }} / {{ allQuestions.length }} 已答</strong>
            </div>
          </div>

          <el-collapse :model-value="onlinePaper.modules.map((module) => module.module_id)" class="module-collapse">
            <el-collapse-item v-for="module in onlinePaper.modules" :key="module.module_id" :name="module.module_id">
              <template #title>
                <div class="module-title">
                  <strong>{{ module.title }}</strong>
                  <span>{{ module.questions.length }} 题</span>
                </div>
              </template>

              <div v-for="question in module.questions" :key="question.question_id" class="question-block">
                <div class="question-heading">
                  <strong>{{ question.sequence_number }}. {{ question.topic }}</strong>
                  <el-tag>{{ question.marks }} 分</el-tag>
                </div>

                <el-radio-group v-if="question.type === 'select'" v-model="answers[question.question_id]" class="answer-options">
                  <el-radio v-for="option in optionList(question.options)" :key="option" :label="option">
                    {{ option }}
                  </el-radio>
                </el-radio-group>

                <el-radio-group v-else v-model="answers[question.question_id]" class="answer-options">
                  <el-radio label="正确">正确</el-radio>
                  <el-radio label="错误">错误</el-radio>
                </el-radio-group>
              </div>
            </el-collapse-item>
          </el-collapse>

          <div class="sticky-actions">
            <el-button :icon="Save" :loading="saving" @click="saveAnswers('save')">保存答案</el-button>
            <el-button type="primary" :icon="SendHorizontal" :loading="submitting" @click="saveAnswers('submit')">提交答卷</el-button>
          </div>
        </template>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="examDialogVisible" :title="examDialogTitle" width="680px" destroy-on-close @closed="resetExamForm">
      <el-form ref="examFormRef" :model="examForm" :rules="examRules" label-width="92px">
        <el-form-item label="考试名称" prop="title">
          <el-input v-model="examForm.title" placeholder="请输入考试名称" />
        </el-form-item>
        <el-form-item label="关联试卷" prop="paper_id">
          <el-select v-model="examForm.paper_id" filterable placeholder="请选择已发布试卷" class="full-control">
            <el-option v-for="paper in papers" :key="paper.id" :label="paper.title" :value="paper.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker v-model="examForm.start_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ssZ" class="full-control" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker v-model="examForm.end_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ssZ" class="full-control" />
        </el-form-item>
        <el-form-item label="发布状态">
          <el-switch v-model="examForm.is_published" active-text="已发布" inactive-text="未发布" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="examDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingExam" @click="submitExamForm">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>
