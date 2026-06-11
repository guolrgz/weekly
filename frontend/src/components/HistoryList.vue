<template>
  <el-card>
    <template #header>
      <span>历史周报</span>
      <el-button
        text
        size="small"
        style="float: right"
        @click="fetchWeeks"
        :loading="loading"
        >刷新</el-button
      >
    </template>
    <el-table :data="weeks" stripe v-loading="loading" v-if="weeks.length">
      <el-table-column prop="label" label="周期" width="120" />
      <el-table-column prop="range" label="日期范围" width="220" />
      <el-table-column prop="total_hours" label="总工时" width="100">
        <template #default="{ row }">{{ row.total_hours }}h</template>
      </el-table-column>
      <el-table-column prop="entry_count" label="记录数" width="80" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button
            type="primary"
            text
            size="small"
            @click="$emit('view', row.start)"
            >查看</el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-else description="暂无历史记录" :image-size="60" />
  </el-card>
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
