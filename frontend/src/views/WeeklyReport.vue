<template>
  <div class="weekly-report">
    <h1 class="page-title">工作周报</h1>
    <p class="page-subtitle">
      {{ report?.week_label || "" }} · {{ report?.week_start || "" }} ~
      {{ report?.week_end || "" }}
    </p>

    <el-tabs v-model="activeTab" type="border-card" @tab-click="handleTabClick">
      <el-tab-pane label="工作录入" name="entry">
        <WorkEntryForm @saved="handleEntrySaved" />
        <TodayEntries ref="todayRef" />
      </el-tab-pane>
      <el-tab-pane label="统计看板" name="stats">
        <StatsDashboard :report="report" :loading="loading" />
      </el-tab-pane>
      <el-tab-pane label="周报预览" name="preview">
        <WeeklyPreview :report="report" />
      </el-tab-pane>
      <el-tab-pane label="历史记录" name="history">
        <HistoryList ref="historyRef" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from "vue";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
import api from "../api";
import WorkEntryForm from "../components/WorkEntryForm.vue";
import TodayEntries from "../components/TodayEntries.vue";
import StatsDashboard from "../components/StatsDashboard.vue";
import WeeklyPreview from "../components/WeeklyPreview.vue";
import HistoryList from "../components/HistoryList.vue";

dayjs.extend(isoWeek);

const activeTab = ref("entry");
const report = ref(null);
const loading = ref(false);
const todayRef = ref(null);
const historyRef = ref(null);
const currentDate = ref(dayjs().format("YYYY-MM-DD"));

async function fetchReport(date) {
  loading.value = true;
  try {
    const { data } = await api.get("/reports/weekly", { params: { date } });
    report.value = data;
  } finally {
    loading.value = false;
  }
}

function handleEntrySaved() {
  todayRef.value?.refresh();
  fetchReport(currentDate.value);
}

function handleTabClick(tab) {
  if (tab.paneName === "stats" || tab.paneName === "preview") {
    fetchReport(currentDate.value);
  }
  if (tab.paneName === "entry") {
    todayRef.value?.refresh();
  }
  if (tab.paneName === "history") {
    historyRef.value?.fetchEntries();
  }
}

fetchReport(currentDate.value);
</script>

<style scoped>
.page-title {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 4px;
  letter-spacing: -0.01em;
}

.page-subtitle {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: 0 0 24px;
}
</style>
