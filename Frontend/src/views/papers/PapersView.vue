<script setup lang="ts">
import { Edit3, EyeOff, Megaphone, Plus, RefreshCw, Search, Trash2 } from "lucide-vue-next";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import { computed, onMounted, reactive, ref } from "vue";

import {
  createPaper,
  deletePaper,
  getPapers,
  publishPaper,
  unpublishPaper,
  updatePaper,
  type Paper,
  type PaperQuery,
} from "@/api/papers";

interface PaperForm {
  title: string;
  description: string;
  duration_minutes: number;
  total_marks: number;
  is_published: boolean;
}

const loading = ref(false);
const saving = ref(false);
const statusChanging = ref("");
const dialogVisible = ref(false);
const editingId = ref("");
const formRef = ref<FormInstance>();
const papers = ref<Paper[]>([]);
const total = ref(0);

const query = reactive<PaperQuery>({
  title: "",
  is_published: "",
  currentPage: 1,
  pageSize: 10,
});

const form = reactive<PaperForm>({
  title: "",
  description: "",
  duration_minutes: 60,
  total_marks: 100,
  is_published: false,
});

const rules: FormRules<PaperForm> = {
  title: [{ required: true, message: "请输入试卷名称", trigger: "blur" }],
  duration_minutes: [{ required: true, message: "请输入考试时长", trigger: "blur" }],
  total_marks: [{ required: true, message: "请输入试卷总分", trigger: "blur" }],
};

const dialogTitle = computed(() => (editingId.value ? "编辑试卷" : "新增试卷"));

function resetForm() {
  editingId.value = "";
  Object.assign(form, {
    title: "",
    description: "",
    duration_minutes: 60,
    total_marks: 100,
    is_published: false,
  });
  formRef.value?.clearValidate();
}

async function loadPapers() {
  loading.value = true;
  try {
    const result = await getPapers(query);
    papers.value = result.data.data;
    total.value = result.data.total;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  query.currentPage = 1;
  void loadPapers();
}

function handleReset() {
  query.title = "";
  query.is_published = "";
  query.currentPage = 1;
  void loadPapers();
}

function openCreateDialog() {
  resetForm();
  dialogVisible.value = true;
}

function openEditDialog(row: Paper) {
  editingId.value = row.id;
  Object.assign(form, {
    title: row.title,
    description: row.description,
    duration_minutes: row.duration_minutes,
    total_marks: row.total_marks,
    is_published: row.is_published,
  });
  dialogVisible.value = true;
}

async function submitForm() {
  await formRef.value?.validate();
  saving.value = true;

  try {
    const payload = {
      title: form.title.trim(),
      description: form.description.trim(),
      duration_minutes: Number(form.duration_minutes),
      total_marks: Number(form.total_marks),
      is_published: form.is_published,
    };

    if (editingId.value) {
      await updatePaper(editingId.value, payload);
      ElMessage.success("试卷已更新");
    } else {
      await createPaper(payload);
      ElMessage.success("试卷已创建");
    }

    dialogVisible.value = false;
    await loadPapers();
  } finally {
    saving.value = false;
  }
}

async function handleDelete(row: Paper) {
  try {
    await ElMessageBox.confirm(`确认删除试卷「${row.title}」吗？`, "删除确认", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });

    await deletePaper(row.id);
    ElMessage.success("试卷已删除");
    await loadPapers();
  } catch {
    // User cancelled the confirmation dialog.
  }
}

async function togglePublish(row: Paper) {
  statusChanging.value = row.id;
  try {
    if (row.is_published) {
      await unpublishPaper(row.id);
      ElMessage.success("已取消发布");
    } else {
      await publishPaper(row.id);
      ElMessage.success("试卷已发布");
    }
    await loadPapers();
  } finally {
    statusChanging.value = "";
  }
}

onMounted(() => {
  void loadPapers();
});
</script>

<template>
  <section class="page-stack">
    <div class="toolbar-panel">
      <el-form :model="query" class="query-form" inline>
        <el-form-item label="试卷名称">
          <el-input v-model="query.title" clearable placeholder="按名称搜索" @keyup.enter="handleSearch">
            <template #prefix>
              <Search :size="16" />
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="发布状态">
          <el-select v-model="query.is_published" clearable placeholder="全部状态" class="type-select">
            <el-option label="已发布" value="true" />
            <el-option label="未发布" value="false" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="RefreshCw" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增试卷</el-button>
    </div>

    <div class="table-panel">
      <el-table v-loading="loading" :data="papers" border stripe height="calc(100vh - 300px)">
        <el-table-column label="试卷名称" min-width="220">
          <template #default="{ row }">
            <div class="topic-cell">{{ row.title }}</div>
          </template>
        </el-table-column>

        <el-table-column label="说明" min-width="260">
          <template #default="{ row }">
            <span class="muted-text">{{ row.description || "未填写" }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="duration_minutes" label="时长(分钟)" width="120" />
        <el-table-column prop="total_marks" label="设定总分" width="110" />
        <el-table-column prop="actual_total" label="已配分值" width="110" />

        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'info'">
              {{ row.is_published ? "已发布" : "未发布" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="updated_at" label="更新时间" width="190" />

        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <el-tooltip content="编辑">
              <el-button circle :icon="Edit3" @click="openEditDialog(row)" />
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
          @size-change="loadPapers"
          @current-change="loadPapers"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="680px" destroy-on-close @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="92px">
        <el-form-item label="试卷名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入试卷名称" />
        </el-form-item>

        <el-form-item label="试卷说明">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入试卷说明" />
        </el-form-item>

        <el-form-item label="考试时长" prop="duration_minutes">
          <el-input-number v-model="form.duration_minutes" :min="1" :max="600" controls-position="right" />
        </el-form-item>

        <el-form-item label="试卷总分" prop="total_marks">
          <el-input-number v-model="form.total_marks" :min="1" :max="1000" :precision="1" controls-position="right" />
        </el-form-item>

        <el-form-item label="发布状态">
          <el-switch v-model="form.is_published" active-text="已发布" inactive-text="未发布" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>
