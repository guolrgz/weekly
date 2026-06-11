<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <h2>工作周报系统</h2>
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleLogin"
          style="width: 100%"
        >
          登录
        </el-button>
      </el-form>
      <p class="auth-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);
const form = reactive({ username: "", password: "" });

async function handleLogin() {
  if (!form.username || !form.password) return;
  loading.value = true;
  try {
    await auth.login(form.username, form.password);
    router.push("/");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}
.auth-card {
  width: 400px;
}
.auth-card h2 {
  text-align: center;
  margin-bottom: 24px;
}
.auth-link {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: #999;
}
</style>
