<template>
  <div class="history-list">
    <div class="toolbar">
      <div class="toolbar-left">
        <span class="toolbar-title">全部记录</span>
        <span class="toolbar-count" v-if="entries.length"
          >{{ entries.length }} 条</span
        >
      </div>
      <div class="toolbar-right">
        <input
          type="date"
          class="date-filter"
          v-model="filterStart"
          @change="fetchEntries"
        />
        <span class="date-sep">~</span>
        <input
          type="date"
          class="date-filter"
          v-model="filterEnd"
          @change="fetchEntries"
        />
        <button class="refresh-btn" @click="fetchEntries" :disabled="loading">
          <svg
            :class="{ spinning: loading }"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            width="15"
            height="15"
          >
            <polyline points="23 4 23 10 17 10" />
            <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" />
          </svg>
        </button>
      </div>
    </div>

    <div class="entry-table" v-if="entries.length">
      <div class="table-header">
        <span class="col-date">日期</span>
        <span class="col-cat">分类</span>
        <span class="col-content">内容</span>
        <span class="col-hour">耗时</span>
        <span class="col-del"></span>
      </div>
      <div class="table-body">
        <div class="table-row" v-for="e in entries" :key="e.id">
          <span class="col-date">{{ e.date }}</span>
          <span class="col-cat">
            <span
              class="cat-tag"
              :style="{ background: catColors[e.category_name] || '#b8ad93' }"
            >
              {{ e.category_name }}
            </span>
          </span>
          <span class="col-content">{{ e.content }}</span>
          <span class="col-hour"
            >{{ (e.duration_minutes / 60).toFixed(1) }}h</span
          >
          <span class="col-del">
            <button class="del-btn" @click="handleDelete(e.id)" title="删除">
              ×
            </button>
          </span>
        </div>
      </div>
    </div>

    <div class="entry-empty" v-else-if="!loading">暂无记录</div>

    <div class="table-summary" v-if="entries.length">
      共 <strong>{{ entries.length }}</strong> 条记录，合计
      <strong>{{ totalHours }}</strong> 小时
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import dayjs from "dayjs";
import api from "../api";

const entries = ref([]);
const loading = ref(false);
const filterStart = ref("");
const filterEnd = ref("");

const catColors = {
  开发: "#c8963e",
  会议: "#5b8c5a",
  文档: "#c25450",
  沟通: "#8c8068",
  其他: "#b8ad93",
};

const totalHours = computed(() => {
  const total = entries.value.reduce((s, e) => s + e.duration_minutes, 0);
  return (total / 60).toFixed(1);
});

async function fetchEntries() {
  loading.value = true;
  try {
    const params = {};
    if (filterStart.value) params.start = filterStart.value;
    if (filterEnd.value) params.end = filterEnd.value;
    const { data: entryData } = await api.get("/entries", { params });
    const { data: cats } = await api.get("/categories");
    const catMap = Object.fromEntries(cats.map((c) => [c.id, c.name]));
    entries.value = entryData.map((e) => ({
      ...e,
      category_name: catMap[e.category_id] || "",
    }));
  } finally {
    loading.value = false;
  }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm("确定删除该记录？", "提示", { type: "warning" });
    await api.delete(`/entries/${id}`);
    entries.value = entries.value.filter((e) => e.id !== id);
    ElMessage.success("已删除");
  } catch {
    /* cancelled */
  }
}

onMounted(fetchEntries);
defineExpose({ fetchEntries });
</script>

<style scoped>
.history-list {
  max-width: 900px;
}

/* === Toolbar === */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.toolbar-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.toolbar-title {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
}

.toolbar-count {
  font-size: 13px;
  color: var(--color-text-muted);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-filter {
  height: 32px;
  padding: 0 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text);
  background: var(--color-surface);
  outline: none;
}

.date-filter:focus {
  border-color: var(--color-accent);
}

.date-sep {
  color: var(--color-text-muted);
  font-size: 13px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.refresh-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.spinning {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* === Table === */
.entry-table {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border-light);
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table-body {
  display: flex;
  flex-direction: column;
}

.table-row {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border-light);
  font-size: 14px;
  transition: background var(--transition-fast);
}

.table-row:last-child {
  border-bottom: none;
}
.table-row:hover {
  background: var(--color-bg);
}

.col-date {
  width: 100px;
  flex-shrink: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.col-cat {
  width: 70px;
  flex-shrink: 0;
}

.cat-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.03em;
}

.col-content {
  flex: 1;
  color: var(--color-text);
}

.col-hour {
  width: 50px;
  flex-shrink: 0;
  text-align: right;
  color: var(--color-text-secondary);
  font-weight: 500;
  font-size: 13px;
}

.col-del {
  width: 32px;
  flex-shrink: 0;
  text-align: center;
}

.del-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  font-size: 16px;
  cursor: pointer;
  border-radius: 4px;
  opacity: 0;
  transition: all var(--transition-fast);
}

.table-row:hover .del-btn {
  opacity: 1;
}
.del-btn:hover {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

/* === Empty === */
.entry-empty {
  text-align: center;
  padding: 40px;
  color: var(--color-text-muted);
  font-size: 13px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

/* === Summary === */
.table-summary {
  margin-top: 12px;
  text-align: right;
  font-size: 13px;
  color: var(--color-text-muted);
}
.table-summary strong {
  color: var(--color-accent);
  font-weight: 600;
}
</style>
