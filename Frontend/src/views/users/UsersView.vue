<script setup lang="ts">
import { Edit3, Plus, RefreshCw, Search, Trash2 } from "lucide-vue-next";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import { computed, onMounted, reactive, ref, watch } from "vue";

import { createUser, deleteUser, getUsers, updateUser, type AppUser, type UserPayload, type UserRole } from "@/api/users";

interface UserForm {
  id: string;
  username: string;
  password: string;
  real_name: string;
}

const activeRole = ref<UserRole>("student");
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const editingId = ref("");
const formRef = ref<FormInstance>();
const users = ref<AppUser[]>([]);
const total = ref(0);

const query = reactive({
  keyword: "",
  currentPage: 1,
  pageSize: 10,
});

const form = reactive<UserForm>({
  id: "",
  username: "",
  password: "",
  real_name: "",
});

const rules: FormRules<UserForm> = {
  id: [{ required: true, message: "请输入用户 ID", trigger: "blur" }],
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [
    {
      validator: (_rule, value, callback) => {
        if (!editingId.value && !value) {
          callback(new Error("请输入初始密码"));
          return;
        }
        callback();
      },
      trigger: "blur",
    },
  ],
};

const dialogTitle = computed(() => `${editingId.value ? "编辑" : "新增"}${activeRole.value === "teacher" ? "教师" : "学生"}`);

function resetForm() {
  editingId.value = "";
  Object.assign(form, {
    id: "",
    username: "",
    password: "",
    real_name: "",
  });
  formRef.value?.clearValidate();
}

async function loadUsers() {
  loading.value = true;
  try {
    const result = await getUsers(activeRole.value, query);
    users.value = result.data.data;
    total.value = result.data.total;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  query.currentPage = 1;
  void loadUsers();
}

function handleReset() {
  query.keyword = "";
  query.currentPage = 1;
  void loadUsers();
}

function openCreateDialog() {
  resetForm();
  dialogVisible.value = true;
}

function openEditDialog(row: AppUser) {
  editingId.value = row.id;
  Object.assign(form, {
    id: row.id,
    username: row.username,
    password: "",
    real_name: row.real_name,
  });
  dialogVisible.value = true;
}

async function submitForm() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    const payload: UserPayload = {
      id: form.id.trim(),
      username: form.username.trim(),
      real_name: form.real_name.trim(),
    };
    if (form.password) {
      payload.password = form.password;
    }

    if (editingId.value) {
      await updateUser(activeRole.value, editingId.value, payload);
      ElMessage.success("用户已更新");
    } else {
      await createUser(activeRole.value, payload);
      ElMessage.success("用户已创建");
    }

    dialogVisible.value = false;
    await loadUsers();
  } finally {
    saving.value = false;
  }
}

async function removeUser(row: AppUser) {
  try {
    await ElMessageBox.confirm(`确认删除用户「${row.username}」吗？`, "删除确认", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
    await deleteUser(activeRole.value, row.id);
    ElMessage.success("用户已删除");
    await loadUsers();
  } catch {
    // User cancelled the confirmation dialog.
  }
}

watch(activeRole, () => {
  query.keyword = "";
  query.currentPage = 1;
  void loadUsers();
});

onMounted(() => {
  void loadUsers();
});
</script>

<template>
  <section class="page-stack">
    <el-tabs v-model="activeRole" class="workspace-tabs">
      <el-tab-pane label="学生账号" name="student" />
      <el-tab-pane label="教师账号" name="teacher" />
    </el-tabs>

    <div class="toolbar-panel">
      <el-form :model="query" class="query-form" inline>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" clearable placeholder="用户名、姓名或 ID" @keyup.enter="handleSearch">
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

      <el-button type="primary" :icon="Plus" @click="openCreateDialog">
        新增{{ activeRole === "teacher" ? "教师" : "学生" }}
      </el-button>
    </div>

    <div class="table-panel">
      <el-table v-loading="loading" :data="users" border stripe height="calc(100vh - 330px)">
        <el-table-column prop="id" label="用户 ID" min-width="160" />
        <el-table-column prop="username" label="用户名" min-width="160" />
        <el-table-column prop="real_name" label="姓名" min-width="160" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.role === "teacher" ? "教师" : "学生" }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="190" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-tooltip content="编辑">
              <el-button circle :icon="Edit3" @click="openEditDialog(row)" />
            </el-tooltip>
            <el-tooltip content="删除">
              <el-button circle type="danger" :icon="Trash2" @click="removeUser(row)" />
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
          @size-change="loadUsers"
          @current-change="loadUsers"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px" destroy-on-close @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="88px">
        <el-form-item label="用户 ID" prop="id">
          <el-input v-model="form.id" :disabled="Boolean(editingId)" placeholder="例如 student001" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item :label="editingId ? '重置密码' : '初始密码'" prop="password">
          <el-input v-model="form.password" type="password" show-password :placeholder="editingId ? '不填写则不修改密码' : '请输入初始密码'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>
