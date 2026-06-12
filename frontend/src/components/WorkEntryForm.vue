<template>
  <div class="entry-form">
    <div class="form-header">新增工作记录</div>
    <form class="form-row" @submit.prevent="handleSubmit">
      <div class="form-field">
        <label class="form-label">日期</label>
        <el-date-picker
          v-model="form.date"
          type="date"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </div>
      <div class="form-field">
        <label class="form-label">分类</label>
        <el-select v-model="form.category_id" style="width: 100%">
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>
      </div>
      <div class="form-field form-field--narrow">
        <label class="form-label">耗时</label>
        <el-input-number
          v-model="form.hours"
          :min="0.5"
          :max="24"
          :step="0.5"
          style="width: 100%"
        />
      </div>
      <div class="form-field form-field--wide">
        <label class="form-label">内容</label>
        <el-input v-model="form.content" placeholder="简要描述工作内容" />
      </div>
      <button class="save-btn" type="submit" :disabled="saving">
        <span v-if="!saving">保存</span>
        <span v-else class="spinner" />
      </button>
    </form>
  </div>
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
.entry-form {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  margin-bottom: 20px;
}

.form-header {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 16px;
}

.form-row {
  display: flex;
  align-items: flex-end;
  gap: 14px;
}

.form-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-field--narrow {
  flex: 0 0 120px;
}
.form-field--wide {
  flex: 2;
}

.form-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.save-btn {
  height: 32px;
  padding: 0 24px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: #fff;
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
  margin-bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 64px;
}

.save-btn:hover {
  background: var(--color-accent-hover);
}

.save-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
