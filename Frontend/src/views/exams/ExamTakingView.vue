<script setup lang="ts">
import { ClipboardCheck, Save, SendHorizontal } from "lucide-vue-next";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import { computed, reactive, ref } from "vue";

import { enterExam, getOnlinePaper, type ExamEnterResult, type OnlinePaper } from "@/api/exams";
import { commitAnswers, type AnswerItem } from "@/api/scores";

interface EnterForm {
  exam_id: string;
  student_id: string;
}

const enterFormRef = ref<FormInstance>();
const entering = ref(false);
const saving = ref(false);
const submitting = ref(false);
const enterResult = ref<ExamEnterResult | null>(null);
const onlinePaper = ref<OnlinePaper | null>(null);
const answers = reactive<Record<string, string>>({});

const enterForm = reactive<EnterForm>({
  exam_id: "",
  student_id: "",
});

const enterRules: FormRules<EnterForm> = {
  exam_id: [{ required: true, message: "请输入考试 ID", trigger: "blur" }],
  student_id: [{ required: true, message: "请输入学生 ID", trigger: "blur" }],
};

const allQuestions = computed(() => onlinePaper.value?.modules.flatMap((module) => module.questions) || []);
const answeredCount = computed(() => allQuestions.value.filter((item) => answers[item.question_id]).length);

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

async function handleEnter() {
  await enterFormRef.value?.validate();
  entering.value = true;
  try {
    const enterResponse = await enterExam(enterForm);
    enterResult.value = enterResponse.data;
    const paperResponse = await getOnlinePaper({ exam_id: enterForm.exam_id });
    onlinePaper.value = paperResponse.data;
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
  } finally {
    loadingTarget.value = false;
  }
}
</script>

<template>
  <section class="page-stack">
    <div class="toolbar-panel">
      <el-form ref="enterFormRef" :model="enterForm" :rules="enterRules" class="query-form" inline>
        <el-form-item label="考试 ID" prop="exam_id">
          <el-input v-model="enterForm.exam_id" placeholder="请输入考试 ID" />
        </el-form-item>
        <el-form-item label="学生 ID" prop="student_id">
          <el-input v-model="enterForm.student_id" placeholder="请输入学生 ID" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="ClipboardCheck" :loading="entering" @click="handleEnter">进入考试</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div v-if="!onlinePaper" class="table-panel">
      <el-empty description="请输入考试 ID 和学生 ID 后进入考试" />
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

            <el-radio-group
              v-if="question.type === 'select'"
              v-model="answers[question.question_id]"
              class="answer-options"
            >
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
  </section>
</template>
