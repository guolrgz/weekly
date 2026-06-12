<template>
  <div class="categories-page">
    <h1 class="page-title">分类管理</h1>

    <div class="cat-toolbar">
      <button class="add-btn" @click="showAdd">+ 新增分类</button>
    </div>

    <div class="cat-grid" v-loading="loading">
      <div class="cat-card" v-for="cat in categories" :key="cat.id">
        <span class="cat-dot" :style="{ background: cat.color }" />
        <span class="cat-name">{{ cat.name }}</span>
        <div class="cat-actions">
          <button class="cat-btn" @click="editRow(cat)">编辑</button>
          <button class="cat-btn cat-btn--danger" @click="handleDelete(cat.id)">
            删除
          </button>
        </div>
      </div>
      <div class="cat-card cat-card--empty" v-if="!categories.length">
        暂无分类
      </div>
    </div>

    <el-dialog
      :title="editing.id ? '编辑分类' : '新增分类'"
      v-model="dialogVisible"
      width="400px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="form.color" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave"
          >保存</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import api from "../api";

const categories = ref([]);
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const editing = ref({});
const form = reactive({ name: "", color: "#c8963e", sort_order: 0 });

async function fetchCategories() {
  loading.value = true;
  try {
    const { data } = await api.get("/categories");
    categories.value = data;
  } finally {
    loading.value = false;
  }
}

function showAdd() {
  editing.value = {};
  form.name = "";
  form.color = "#c8963e";
  form.sort_order = 0;
  dialogVisible.value = true;
}

function editRow(row) {
  editing.value = row;
  form.name = row.name;
  form.color = row.color;
  form.sort_order = row.sort_order;
  dialogVisible.value = true;
}

async function handleSave() {
  saving.value = true;
  try {
    if (editing.value.id) {
      await api.put(`/categories/${editing.value.id}`, { ...form });
    } else {
      await api.post("/categories", { ...form });
    }
    dialogVisible.value = false;
    editing.value = {};
    await fetchCategories();
  } finally {
    saving.value = false;
  }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm("确定删除该分类？", "提示", { type: "warning" });
    await api.delete(`/categories/${id}`);
    await fetchCategories();
    ElMessage.success("已删除");
  } catch {
    /* cancelled */
  }
}

onMounted(fetchCategories);
</script>

<style scoped>
.page-title {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 20px;
  letter-spacing: -0.01em;
}

.cat-toolbar {
  margin-bottom: 16px;
}

.add-btn {
  height: 36px;
  padding: 0 18px;
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: #fff;
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.add-btn:hover {
  background: var(--color-accent-hover);
}

.cat-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 500px;
}

.cat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  transition: box-shadow var(--transition-fast);
}

.cat-card:hover {
  box-shadow: var(--shadow-xs);
}

.cat-card--empty {
  justify-content: center;
  color: var(--color-text-muted);
  font-size: 13px;
  padding: 24px;
}

.cat-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.15);
}

.cat-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.cat-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.cat-card:hover .cat-actions {
  opacity: 1;
}

.cat-btn {
  padding: 4px 10px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: all var(--transition-fast);
}

.cat-btn:hover {
  background: var(--color-bg);
  color: var(--color-accent);
}

.cat-btn--danger:hover {
  background: var(--color-danger-light);
  color: var(--color-danger);
}
</style>
