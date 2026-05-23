<script setup lang="ts">
import { Check, Edit3, Plus, RefreshCw, Search, Trash2, X } from "lucide-vue-next";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";

import {
  createQuestion,
  deleteQuestion,
  getQuestions,
  updateQuestion,
  type Question,
  type QuestionQuery,
  type QuestionType,
} from "@/api/questions";

interface QuestionForm {
  id: string;
  topic: string;
  type: QuestionType;
  answer: string;
  options: string[];
}

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const editingId = ref("");
const formRef = ref<FormInstance>();
const questions = ref<Question[]>([]);
const total = ref(0);

const query = reactive<QuestionQuery>({
  topic: "",
  type: "",
  currentPage: 1,
  pageSize: 10,
});

const form = reactive<QuestionForm>({
  id: "",
  topic: "",
  type: "select",
  answer: "",
  options: ["", "", "", ""],
});

const rules: FormRules<QuestionForm> = {
  topic: [{ required: true, message: "请输入题干", trigger: "blur" }],
  type: [{ required: true, message: "请选择题型", trigger: "change" }],
  answer: [{ required: true, message: "请输入答案", trigger: "blur" }],
};

const dialogTitle = computed(() => (editingId.value ? "编辑试题" : "新增试题"));

function typeLabel(type: QuestionType) {
  return type === "select" ? "选择题" : "判断题";
}

function parseOptions(raw: string) {
  try {
    const value = JSON.parse(raw);
    return Array.isArray(value) ? value.map((item) => String(item)) : [];
  } catch {
    return raw ? raw.split(/\r?\n/).filter(Boolean) : [];
  }
}

function optionPreview(question: Question) {
  const options = parseOptions(question.options);
  if (question.type === "judge") {
    return "正确 / 错误";
  }
  return options.length ? options.join("；") : "未配置选项";
}

function normalizeOptions() {
  if (form.type === "judge") {
    return JSON.stringify(["正确", "错误"]);
  }

  return JSON.stringify(form.options.map((item) => item.trim()).filter(Boolean));
}

function resetForm() {
  editingId.value = "";
  Object.assign(form, {
    id: "",
    topic: "",
    type: "select",
    answer: "",
    options: ["", "", "", ""],
  });
  formRef.value?.clearValidate();
}

async function loadQuestions() {
  loading.value = true;
  try {
    const result = await getQuestions(query);
    questions.value = result.data.data;
    total.value = result.data.total;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  query.currentPage = 1;
  void loadQuestions();
}

function handleReset() {
  query.topic = "";
  query.type = "";
  query.currentPage = 1;
  void loadQuestions();
}

function openCreateDialog() {
  resetForm();
  dialogVisible.value = true;
}

function openEditDialog(row: Question) {
  editingId.value = row.id;
  Object.assign(form, {
    id: row.id,
    topic: row.topic,
    type: row.type,
    answer: row.answer,
    options: row.type === "select" ? [...parseOptions(row.options), "", "", "", ""].slice(0, 6) : ["", "", "", ""],
  });
  dialogVisible.value = true;
}

function addOption() {
  if (form.options.length < 8) {
    form.options.push("");
  }
}

function removeOption(index: number) {
  if (form.options.length > 2) {
    form.options.splice(index, 1);
  }
}

async function submitForm() {
  await formRef.value?.validate();

  if (form.type === "select" && form.options.map((item) => item.trim()).filter(Boolean).length < 2) {
    ElMessage.warning("选择题至少需要 2 个选项");
    return;
  }

  saving.value = true;
  try {
    const payload = {
      topic: form.topic.trim(),
      type: form.type,
      answer: form.answer.trim(),
      options: normalizeOptions(),
    };

    if (editingId.value) {
      await updateQuestion(editingId.value, payload);
      ElMessage.success("试题已更新");
    } else {
      await createQuestion(payload);
      ElMessage.success("试题已创建");
    }

    dialogVisible.value = false;
    await loadQuestions();
  } finally {
    saving.value = false;
  }
}

async function handleDelete(row: Question) {
  try {
    await ElMessageBox.confirm(`确认删除这道${typeLabel(row.type)}吗？`, "删除确认", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });

    await deleteQuestion(row.id);
    ElMessage.success("试题已删除");
    await loadQuestions();
  } catch {
    // User cancelled the confirmation dialog.
  }
}

onMounted(() => {
  void loadQuestions();
});
</script>

<template>
  <section class="page-stack">
    <div class="toolbar-panel">
      <el-form :model="query" class="query-form" inline>
        <el-form-item label="题干">
          <el-input v-model="query.topic" clearable placeholder="按题干关键字搜索" @keyup.enter="handleSearch">
            <template #prefix>
              <Search :size="16" />
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="题型">
          <el-select v-model="query.type" clearable placeholder="全部题型" class="type-select">
            <el-option label="选择题" value="select" />
            <el-option label="判断题" value="judge" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="RefreshCw" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增试题</el-button>
    </div>

    <div class="table-panel">
      <el-table v-loading="loading" :data="questions" border stripe height="calc(100vh - 300px)">
        <el-table-column label="题干" min-width="280">
          <template #default="{ row }">
            <div class="topic-cell">{{ row.topic }}</div>
          </template>
        </el-table-column>

        <el-table-column label="题型" width="110">
          <template #default="{ row }">
            <el-tag :type="row.type === 'select' ? 'primary' : 'success'">{{ typeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="选项" min-width="260">
          <template #default="{ row }">
            <span class="muted-text">{{ optionPreview(row) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="answer" label="答案" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="190" />

        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-tooltip content="编辑">
              <el-button circle :icon="Edit3" @click="openEditDialog(row)" />
            </el-tooltip>
            <el-tooltip content="删除">
              <el-button circle type="danger" :icon="Trash2" @click="handleDelete(row)" />
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
          @size-change="loadQuestions"
          @current-change="loadQuestions"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="720px" destroy-on-close @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="82px">
        <el-form-item label="题型" prop="type">
          <el-segmented
            v-model="form.type"
            :options="[
              { label: '选择题', value: 'select' },
              { label: '判断题', value: 'judge' },
            ]"
          />
        </el-form-item>

        <el-form-item label="题干" prop="topic">
          <el-input v-model="form.topic" type="textarea" :rows="4" placeholder="请输入试题题干" />
        </el-form-item>

        <el-form-item v-if="form.type === 'select'" label="选项">
          <div class="option-editor">
            <div v-for="(_, index) in form.options" :key="index" class="option-row">
              <el-input v-model="form.options[index]" :placeholder="`选项 ${index + 1}`" />
              <el-button circle :icon="X" :disabled="form.options.length <= 2" @click="removeOption(index)" />
            </div>
            <el-button :icon="Plus" plain @click="addOption">添加选项</el-button>
          </div>
        </el-form-item>

        <el-form-item v-else label="选项">
          <div class="judge-options">
            <el-tag type="success">
              <Check :size="14" />
              正确
            </el-tag>
            <el-tag type="danger">
              <X :size="14" />
              错误
            </el-tag>
          </div>
        </el-form-item>

        <el-form-item label="答案" prop="answer">
          <el-input v-model="form.answer" placeholder="选择题填写正确选项文本，判断题填写 正确 或 错误" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>
