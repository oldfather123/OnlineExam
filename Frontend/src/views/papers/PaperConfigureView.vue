<script setup lang="ts">
import { ArrowLeft, Edit3, Plus, RefreshCw, Search, Trash2 } from "lucide-vue-next";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getPaperAvailableQuestions, type Question, type QuestionType } from "@/api/questions";
import {
  createPaperModule,
  createPaperQuestionLinks,
  deletePaperModule,
  deletePaperQuestionLink,
  getPaper,
  getPaperDetail,
  updatePaperModule,
  updatePaperQuestionLink,
  type Paper,
  type PaperDetailModule,
  type PaperQuestionLink,
} from "@/api/papers";

interface ModuleForm {
  title: string;
  description: string;
}

const route = useRoute();
const router = useRouter();
const paperId = computed(() => String(route.params.id || ""));

const loading = ref(false);
const moduleSaving = ref(false);
const questionLoading = ref(false);
const linking = ref(false);
const moduleDialogVisible = ref(false);
const questionDrawerVisible = ref(false);
const editingModuleId = ref("");
const currentModuleId = ref("");
const paper = ref<Paper | null>(null);
const modules = ref<PaperDetailModule[]>([]);
const activeNames = ref<string[]>([]);
const availableQuestions = ref<Question[]>([]);
const selectedQuestions = ref<Question[]>([]);
const defaultMarks = ref(5);
const moduleFormRef = ref<FormInstance>();

const moduleForm = reactive<ModuleForm>({
  title: "",
  description: "",
});

const questionQuery = reactive({
  topic: "",
  type: "" as QuestionType | "",
});

const moduleRules: FormRules<ModuleForm> = {
  title: [{ required: true, message: "请输入模块名称", trigger: "blur" }],
};

const moduleDialogTitle = computed(() => (editingModuleId.value ? "编辑模块" : "新增模块"));
const actualTotal = computed(() =>
  modules.value.reduce((sum, item) => sum + item.questions.reduce((inner, question) => inner + Number(question.marks || 0), 0), 0),
);

function typeLabel(type?: QuestionType) {
  return type === "judge" ? "判断题" : "选择题";
}

function resetModuleForm() {
  editingModuleId.value = "";
  Object.assign(moduleForm, { title: "", description: "" });
  moduleFormRef.value?.clearValidate();
}

async function loadPaperConfig() {
  loading.value = true;
  try {
    const [paperResult, detailResult] = await Promise.all([getPaper(paperId.value), getPaperDetail(paperId.value)]);
    paper.value = paperResult.data;
    modules.value = detailResult.data;
    activeNames.value = detailResult.data.map((item) => item.id);
  } finally {
    loading.value = false;
  }
}

function openCreateModuleDialog() {
  resetModuleForm();
  moduleDialogVisible.value = true;
}

function openEditModuleDialog(module: PaperDetailModule) {
  editingModuleId.value = module.id;
  Object.assign(moduleForm, {
    title: module.title,
    description: module.description,
  });
  moduleDialogVisible.value = true;
}

async function submitModuleForm() {
  await moduleFormRef.value?.validate();
  moduleSaving.value = true;
  try {
    const payload = {
      paper_id: paperId.value,
      title: moduleForm.title.trim(),
      description: moduleForm.description.trim(),
    };

    if (editingModuleId.value) {
      await updatePaperModule(editingModuleId.value, payload);
      ElMessage.success("模块已更新");
    } else {
      await createPaperModule(payload);
      ElMessage.success("模块已创建");
    }

    moduleDialogVisible.value = false;
    await loadPaperConfig();
  } finally {
    moduleSaving.value = false;
  }
}

async function removeModule(module: PaperDetailModule) {
  try {
    await ElMessageBox.confirm(`确认删除模块「${module.title}」吗？已关联题目的模块不能删除。`, "删除确认", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
    await deletePaperModule(module.id, paperId.value);
    ElMessage.success("模块已删除");
    await loadPaperConfig();
  } catch {
    // User cancelled the confirmation dialog.
  }
}

async function loadAvailableQuestions() {
  questionLoading.value = true;
  try {
    const result = await getPaperAvailableQuestions(questionQuery);
    const linkedIds = new Set(modules.value.flatMap((item) => item.questions.map((question) => question.question_id)));
    availableQuestions.value = result.data.filter((question) => !linkedIds.has(question.id));
  } finally {
    questionLoading.value = false;
  }
}

async function openQuestionDrawer(moduleId: string) {
  currentModuleId.value = moduleId;
  selectedQuestions.value = [];
  questionDrawerVisible.value = true;
  await loadAvailableQuestions();
}

async function submitQuestionLinks() {
  if (selectedQuestions.value.length === 0) {
    ElMessage.warning("请选择要加入试卷的题目");
    return;
  }

  linking.value = true;
  try {
    await createPaperQuestionLinks(
      selectedQuestions.value.map((question) => ({
        paper_id: paperId.value,
        question_id: question.id,
        module: currentModuleId.value,
        marks: defaultMarks.value,
      })),
    );
    ElMessage.success("题目已加入试卷");
    questionDrawerVisible.value = false;
    await loadPaperConfig();
  } finally {
    linking.value = false;
  }
}

async function changeQuestionMarks(link: PaperQuestionLink) {
  await updatePaperQuestionLink(link.id, { marks: Number(link.marks || 0) });
  ElMessage.success("分值已更新");
  await loadPaperConfig();
}

async function removeQuestion(link: PaperQuestionLink) {
  try {
    await ElMessageBox.confirm("确认从试卷中移除这道题吗？", "移除确认", {
      type: "warning",
      confirmButtonText: "移除",
      cancelButtonText: "取消",
    });
    await deletePaperQuestionLink(link.id);
    ElMessage.success("题目已移除");
    await loadPaperConfig();
  } catch {
    // User cancelled the confirmation dialog.
  }
}

onMounted(() => {
  void loadPaperConfig();
});
</script>

<template>
  <section class="page-stack" v-loading="loading">
    <div class="detail-header">
      <el-button :icon="ArrowLeft" @click="router.push('/papers')">返回</el-button>
      <div class="detail-title">
        <h2>{{ paper?.title || "试卷配置" }}</h2>
        <p>{{ paper?.description || "配置试卷模块、题目和分值" }}</p>
      </div>
      <div class="score-summary">
        <span>设定总分：{{ paper?.total_marks ?? 0 }}</span>
        <strong>已配分值：{{ actualTotal }}</strong>
      </div>
    </div>

    <div class="toolbar-panel">
      <div class="muted-text">每份试卷可拆分为多个模块，再从题库中关联题目。</div>
      <el-button type="primary" :icon="Plus" @click="openCreateModuleDialog">新增模块</el-button>
    </div>

    <div v-if="modules.length === 0" class="table-panel">
      <el-empty description="暂无模块">
        <el-button type="primary" :icon="Plus" @click="openCreateModuleDialog">创建第一个模块</el-button>
      </el-empty>
    </div>

    <el-collapse v-else v-model="activeNames" class="module-collapse">
      <el-collapse-item v-for="module in modules" :key="module.id" :name="module.id">
        <template #title>
          <div class="module-title">
            <strong>{{ module.sequence_number }}. {{ module.title }}</strong>
            <span>{{ module.questions.length }} 题</span>
          </div>
        </template>

        <div class="module-actions">
          <span class="muted-text">{{ module.description || "未填写模块说明" }}</span>
          <div>
            <el-button :icon="Plus" type="primary" plain @click="openQuestionDrawer(module.id)">添加题目</el-button>
            <el-button :icon="Edit3" @click="openEditModuleDialog(module)">编辑模块</el-button>
            <el-button :icon="Trash2" type="danger" @click="removeModule(module)">删除模块</el-button>
          </div>
        </div>

        <el-table :data="module.questions" border stripe>
          <el-table-column label="序号" prop="sequence_number" width="80" />
          <el-table-column label="题干" min-width="260">
            <template #default="{ row }">
              <div class="topic-cell">{{ row.question_detail?.topic || row.question_id }}</div>
            </template>
          </el-table-column>
          <el-table-column label="题型" width="100">
            <template #default="{ row }">
              <el-tag>{{ typeLabel(row.question_detail?.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="答案" width="120">
            <template #default="{ row }">
              {{ row.question_detail?.answer || "-" }}
            </template>
          </el-table-column>
          <el-table-column label="分值" width="160">
            <template #default="{ row }">
              <el-input-number v-model="row.marks" :min="0" :max="1000" :precision="1" controls-position="right" @change="changeQuestionMarks(row)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90" fixed="right">
            <template #default="{ row }">
              <el-tooltip content="移除">
                <el-button circle type="danger" :icon="Trash2" @click="removeQuestion(row)" />
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table>
      </el-collapse-item>
    </el-collapse>

    <el-dialog v-model="moduleDialogVisible" :title="moduleDialogTitle" width="560px" destroy-on-close @closed="resetModuleForm">
      <el-form ref="moduleFormRef" :model="moduleForm" :rules="moduleRules" label-width="82px">
        <el-form-item label="模块名称" prop="title">
          <el-input v-model="moduleForm.title" placeholder="例如：单项选择题" />
        </el-form-item>
        <el-form-item label="模块说明">
          <el-input v-model="moduleForm.description" type="textarea" :rows="3" placeholder="请输入模块说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="moduleSaving" @click="submitModuleForm">保存</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="questionDrawerVisible" title="从题库添加题目" size="720px">
      <div class="drawer-stack">
        <el-form :model="questionQuery" class="query-form" inline>
          <el-form-item label="题干">
            <el-input v-model="questionQuery.topic" clearable placeholder="按题干搜索">
              <template #prefix>
                <Search :size="16" />
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="题型">
            <el-select v-model="questionQuery.type" clearable placeholder="全部题型" class="type-select">
              <el-option label="选择题" value="select" />
              <el-option label="判断题" value="judge" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button :icon="RefreshCw" @click="loadAvailableQuestions">刷新</el-button>
          </el-form-item>
        </el-form>

        <div class="drawer-tools">
          <span class="muted-text">已选 {{ selectedQuestions.length }} 题</span>
          <el-input-number v-model="defaultMarks" :min="0" :max="1000" :precision="1" controls-position="right" />
        </div>

        <el-table
          v-loading="questionLoading"
          :data="availableQuestions"
          border
          stripe
          height="calc(100vh - 270px)"
          @selection-change="selectedQuestions = $event"
        >
          <el-table-column type="selection" width="48" />
          <el-table-column label="题干" min-width="300">
            <template #default="{ row }">
              <div class="topic-cell">{{ row.topic }}</div>
            </template>
          </el-table-column>
          <el-table-column label="题型" width="100">
            <template #default="{ row }">
              <el-tag>{{ typeLabel(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="answer" label="答案" width="100" />
        </el-table>

        <div class="drawer-footer">
          <el-button @click="questionDrawerVisible = false">取消</el-button>
          <el-button type="primary" :loading="linking" @click="submitQuestionLinks">加入试卷</el-button>
        </div>
      </div>
    </el-drawer>
  </section>
</template>
