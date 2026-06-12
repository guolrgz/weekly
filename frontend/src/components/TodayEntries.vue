<template>
  <div class="today-entries">
    <div class="section-header">今日记录</div>
    <div class="entry-list" v-if="entries.length">
      <div class="entry-item" v-for="entry in entries" :key="entry.id">
        <span
          class="entry-cat"
          :style="{ color: catColor(entry.category_name) }"
          >{{ entry.category_name }}</span
        >
        <span class="entry-content">{{ entry.content }}</span>
        <span class="entry-time"
          >{{ (entry.duration_minutes / 60).toFixed(1) }}h</span
        >
        <button
          class="entry-delete"
          @click="handleDelete(entry.id)"
          title="删除"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            width="14"
            height="14"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    </div>
    <div class="entry-empty" v-else>暂无记录</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import dayjs from "dayjs";
import api from "../api";

const entries = ref([]);
const today = dayjs().format("YYYY-MM-DD");

const CAT_COLORS = {
  开发: "#c8963e",
  会议: "#5b8c5a",
  文档: "#c25450",
  沟通: "#8c8068",
  其他: "#b8ad93",
};

function catColor(name) {
  return CAT_COLORS[name] || "#b8ad93";
}

async function refresh() {
  const { data } = await api.get("/entries", {
    params: { start: today, end: today },
  });
  const { data: cats } = await api.get("/categories");
  const catMap = Object.fromEntries(cats.map((c) => [c.id, c.name]));
  entries.value = data.map((e) => ({
    ...e,
    category_name: catMap[e.category_id] || "",
  }));
}

async function handleDelete(id) {
  await api.delete(`/entries/${id}`);
  refresh();
}

onMounted(refresh);
defineExpose({ refresh });
</script>

<style scoped>
.today-entries {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 20px 24px;
}

.section-header {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 14px;
}

.entry-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.entry-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.entry-item:hover {
  background: var(--color-bg);
}

.entry-cat {
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-display);
  letter-spacing: 0.04em;
  width: 48px;
  flex-shrink: 0;
}

.entry-content {
  flex: 1;
  font-size: 14px;
  color: var(--color-text);
}

.entry-time {
  font-size: 13px;
  color: var(--color-text-muted);
  font-weight: 500;
  width: 40px;
  text-align: right;
  flex-shrink: 0;
}

.entry-delete {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  border-radius: 4px;
  transition: all var(--transition-fast);
  flex-shrink: 0;
  opacity: 0;
}

.entry-item:hover .entry-delete {
  opacity: 1;
}

.entry-delete:hover {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

.entry-empty {
  text-align: center;
  padding: 24px;
  color: var(--color-text-muted);
  font-size: 13px;
}
</style>
