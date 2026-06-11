<template>
  <el-card class="entry-form-card">
    <template #header>新增工作记录</template>
    <el-form :model="form" label-width="80px" @submit.prevent="handleSubmit">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item label="日期">
            <el-date-picker
              v-model="form.date"
              type="date"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="分类">
            <el-select v-model="form.category_id" style="width: 100%">
              <el-option
                v-for="cat in categories"
                :key="cat.id"
                :label="cat.name"
                :value="cat.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="耗时(小时)">
            <el-input-number
              v-model="form.hours"
              :min="0.5"
              :max="24"
              :step="0.5"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="内容">
            <el-input v-model="form.content" placeholder="简要描述工作内容" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-button type="primary" :loading="saving" @click="handleSubmit"
        >保存</el-button
      >
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import dayjs from "dayjs";
import api from "../api";

const emit = defineEmits(["saved"]);

const categories = ref([]);
const saving = ref(false);
const form = reactive({
  date: dayjs().format("YYYY-MM-DD"),
  category_id: null,
  content: "",
  hours: 1,
});

onMounted(async () => {
  const { data } = await api.get("/categories");
  categories.value = data;
  if (data.length) form.category_id = data[0].id;
});

async function handleSubmit() {
  if (!form.content.trim()) return;
  saving.value = true;
  try {
    await api.post("/entries", {
      date: form.date,
      category_id: form.category_id,
      content: form.content,
      duration_minutes: Math.round(form.hours * 60),
    });
    form.content = "";
    form.hours = 1;
    form.date = dayjs().format("YYYY-MM-DD");
    emit("saved");
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.entry-form-card {
  margin-bottom: 16px;
}
</style>
