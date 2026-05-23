<script setup lang="ts">
import { Edit3, RefreshCw, Search, Trash2 } from "lucide-vue-next";
import { ElMessage, ElMessageBox } from "element-plus";
import { onMounted, reactive, ref } from "vue";

import { deleteErrorArchive, getErrorArchives, updateErrorArchive, type ErrorArchive } from "@/api/questions";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const editingArchive = ref<ErrorArchive | null>(null);
const archives = ref<ErrorArchive[]>([]);
const total = ref(0);

const query = reactive({
  topic: "",
  currentPage: 1,
  pageSize: 10,
});

const form = reactive({
  explanation: "",
});

function typeLabel(type?: string) {
  if (type === "select") return "选择题";
  if (type === "judge") return "判断题";
  return "未知";
}

function optionText(options?: string[] | string) {
  if (Array.isArray(options)) {
    return options.join("；");
  }
  if (!options) {
    return "未配置选项";
  }
  try {
    const parsed = JSON.parse(options);
    return Array.isArray(parsed) ? parsed.join("；") : String(options);
  } catch {
    return String(options);
  }
}

async function loadArchives() {
  if (!session.user?.id) {
    return;
  }
  loading.value = true;
  try {
    const result = await getErrorArchives({
      collector: session.user.id,
      topic: query.topic,
      currentPage: query.currentPage,
      pageSize: query.pageSize,
    });
    archives.value = result.data.data;
    total.value = result.data.total;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  query.currentPage = 1;
  void loadArchives();
}

function handleReset() {
  query.topic = "";
  query.currentPage = 1;
  void loadArchives();
}

function openEditDialog(row: ErrorArchive) {
  editingArchive.value = row;
  form.explanation = row.explanation || "";
  dialogVisible.value = true;
}

async function submitExplanation() {
  if (!editingArchive.value) {
    return;
  }
  saving.value = true;
  try {
    await updateErrorArchive(editingArchive.value.id, { explanation: form.explanation.trim() });
    ElMessage.success("错题备注已更新");
    dialogVisible.value = false;
    await loadArchives();
  } finally {
    saving.value = false;
  }
}

async function removeArchive(row: ErrorArchive) {
  if (!session.user?.id) {
    return;
  }
  try {
    await ElMessageBox.confirm("确认从错题集中移除这道题吗？", "移除确认", {
      type: "warning",
      confirmButtonText: "移除",
      cancelButtonText: "取消",
    });
    await deleteErrorArchive(session.user.id, row.question_id);
    ElMessage.success("已移除错题");
    await loadArchives();
  } catch {
    // User cancelled the confirmation dialog.
  }
}

onMounted(() => {
  void loadArchives();
});
</script>

<template>
  <section class="page-stack">
    <div class="toolbar-panel">
      <el-form :model="query" class="query-form" inline>
        <el-form-item label="题干">
          <el-input v-model="query.topic" clearable placeholder="按题干搜索" @keyup.enter="handleSearch">
            <template #prefix>
              <Search :size="16" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="RefreshCw" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-panel">
      <el-table v-loading="loading" :data="archives" border stripe height="calc(100vh - 300px)">
        <el-table-column label="题干" min-width="280">
          <template #default="{ row }">
            <div class="topic-cell">{{ row.question_detail?.topic || row.question_id }}</div>
          </template>
        </el-table-column>
        <el-table-column label="题型" width="100">
          <template #default="{ row }">
            <el-tag>{{ typeLabel(row.question_detail?.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="选项" min-width="240">
          <template #default="{ row }">
            <span class="muted-text">{{ optionText(row.question_detail?.options) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="答案" width="120">
          <template #default="{ row }">
            {{ row.question_detail?.answer || "-" }}
          </template>
        </el-table-column>
        <el-table-column prop="explanation" label="备注" min-width="180" />
        <el-table-column prop="created_at" label="收藏时间" width="190" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-tooltip content="编辑备注">
              <el-button circle :icon="Edit3" @click="openEditDialog(row)" />
            </el-tooltip>
            <el-tooltip content="移除">
              <el-button circle type="danger" :icon="Trash2" @click="removeArchive(row)" />
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
          @size-change="loadArchives"
          @current-change="loadArchives"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="错题备注" width="560px">
      <el-input v-model="form.explanation" type="textarea" :rows="5" placeholder="记录错误原因或复习提示" />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitExplanation">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>
