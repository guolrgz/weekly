<template>
  <div class="history-list">
    <div class="section-header">
      <span>历史周报</span>
      <button class="refresh-btn" @click="fetchWeeks" :disabled="loading">
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

    <div class="week-grid" v-if="weeks.length">
      <div
        class="week-card"
        v-for="w in weeks"
        :key="w.start"
        @click="$emit('view', w.start)"
      >
        <div class="week-label">{{ w.label }}</div>
        <div class="week-range">{{ w.range }}</div>
        <div class="week-stats">
          <span>{{ w.total_hours }}h</span>
          <span class="dot">·</span>
          <span>{{ w.entry_count }}条</span>
        </div>
      </div>
    </div>
    <div class="entry-empty" v-else>暂无历史记录</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
import api from "../api";

dayjs.extend(isoWeek);
defineEmits(["view"]);

const weeks = ref([]);
const loading = ref(false);

async function fetchWeeks() {
  loading.value = true;
  try {
    const { data } = await api.get("/entries", {
      params: { start: "2000-01-01", end: dayjs().format("YYYY-MM-DD") },
    });
    const weekMap = new Map();
    for (const e of data) {
      const d = dayjs(e.date);
      const monday = d.startOf("isoWeek").format("YYYY-MM-DD");
      if (!weekMap.has(monday)) {
        const sunday = d.endOf("isoWeek").format("YYYY-MM-DD");
        weekMap.set(monday, {
          start: monday,
          end: sunday,
          range: `${monday} ~ ${sunday}`,
          label: `第${d.isoWeek()}周`,
          total_hours: 0,
          entry_count: 0,
        });
      }
      const w = weekMap.get(monday);
      w.total_hours += e.duration_minutes;
      w.entry_count += 1;
    }
    weeks.value = Array.from(weekMap.values())
      .map((w) => ({ ...w, total_hours: +(w.total_hours / 60).toFixed(1) }))
      .reverse();
  } finally {
    loading.value = false;
  }
}

onMounted(fetchWeeks);
</script>

<style scoped>
.history-list {
  max-width: 780px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 16px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
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

.week-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.week-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 18px 20px;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.week-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.week-label {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.week-range {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-bottom: 10px;
}

.week-stats {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-accent);
  font-weight: 600;
}

.dot {
  color: var(--color-border);
}

.entry-empty {
  text-align: center;
  padding: 32px;
  color: var(--color-text-muted);
  font-size: 13px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}
</style>
