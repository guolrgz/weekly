<template>
  <el-card>
    <template #header>今日记录</template>
    <el-table :data="entries" stripe size="small" v-if="entries.length">
      <el-table-column prop="category_name" label="分类" width="100" />
      <el-table-column prop="content" label="内容" />
      <el-table-column label="耗时" width="100">
        <template #default="{ row }">
          {{ (row.duration_minutes / 60).toFixed(1) }}h
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row }">
          <el-button
            type="danger"
            text
            size="small"
            @click="handleDelete(row.id)"
            >删除</el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-else description="暂无记录" :image-size="60" />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from "vue";
import dayjs from "dayjs";
import api from "../api";

const entries = ref([]);
const today = dayjs().format("YYYY-MM-DD");

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
