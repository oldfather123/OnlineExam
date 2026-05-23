<script setup lang="ts">
import { BookOpenCheck, LogIn } from "lucide-vue-next";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { useSessionStore } from "@/stores/session";
import type { UserRole } from "@/api/users";

interface LoginForm {
  role: UserRole;
  username: string;
  password: string;
}

const router = useRouter();
const session = useSessionStore();
const formRef = ref<FormInstance>();
const loading = ref(false);

const form = reactive<LoginForm>({
  role: "teacher",
  username: "",
  password: "",
});

const rules: FormRules<LoginForm> = {
  role: [{ required: true, message: "请选择身份", trigger: "change" }],
  username: [{ required: true, message: "请输入用户名或 ID", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

async function handleLogin() {
  await formRef.value?.validate();
  loading.value = true;
  try {
    await session.login(form.role, form.username.trim(), form.password);
    ElMessage.success("登录成功");
    await router.push(form.role === "teacher" ? "/" : "/exams");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-panel">
      <div class="login-brand">
        <BookOpenCheck :size="36" />
        <div>
          <h1>在线考试系统</h1>
          <p>请选择身份并登录</p>
        </div>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="身份" prop="role">
          <el-segmented
            v-model="form.role"
            :options="[
              { label: '教师', value: 'teacher' },
              { label: '学生', value: 'student' },
            ]"
          />
        </el-form-item>
        <el-form-item label="用户名或 ID" prop="username">
          <el-input v-model="form.username" size="large" placeholder="请输入用户名或 ID" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" size="large" type="password" show-password placeholder="请输入密码" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-button type="primary" size="large" class="login-submit" :icon="LogIn" :loading="loading" @click="handleLogin">登录</el-button>
      </el-form>
    </section>
  </main>
</template>
