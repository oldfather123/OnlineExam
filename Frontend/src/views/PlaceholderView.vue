<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const title = computed(() => String(route.meta.title || "模块"));
const moduleName = computed(() => String(route.meta.module || ""));
</script>

<template>
  <section class="placeholder">
    <el-empty :description="`${title}页面将在后续步骤实现`">
      <el-tag type="info" size="large">module: {{ moduleName }}</el-tag>
    </el-empty>
  </section>
</template>
