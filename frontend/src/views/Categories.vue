<template>
  <div class="categories-page">
    <el-card>
      <template #header>
        <span>分类管理</span>
        <el-button
          type="primary"
          size="small"
          style="float: right"
          @click="showAdd"
          >新增分类</el-button
        >
      </template>

      <el-table :data="categories" stripe v-loading="loading">
        <el-table-column label="颜色" width="80">
          <template #default="{ row }">
            <span class="color-dot" :style="{ background: row.color }" />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button text size="small" @click="editRow(row)">编辑</el-button>
            <el-button
              text
              size="small"
              type="danger"
              @click="handleDelete(row.id)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </el-card>

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
const form = reactive({ name: "", color: "#409EFF", sort_order: 0 });

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
  form.color = "#409EFF";
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
.color-dot {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  vertical-align: middle;
}
</style>
