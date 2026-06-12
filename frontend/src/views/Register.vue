<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-mark">周</div>
        <h1>创建账号</h1>
        <p>开始记录你的工作周报</p>
      </div>

      <form class="auth-form" @submit.prevent="handleRegister">
        <div class="field">
          <label class="field-label">用户名</label>
          <input
            v-model="form.username"
            class="field-input"
            type="text"
            placeholder="设置用户名"
            autocomplete="username"
          />
        </div>
        <div class="field">
          <label class="field-label">密码</label>
          <input
            v-model="form.password"
            class="field-input"
            type="password"
            placeholder="设置密码"
            autocomplete="new-password"
          />
        </div>
        <button class="submit-btn" type="submit" :disabled="loading">
          <span v-if="!loading">注册</span>
          <span v-else class="spinner" />
        </button>
      </form>

      <p class="auth-switch">
        已有账号？<router-link to="/login">去登录</router-link>
      </p>
    </div>
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

async function handleRegister() {
  if (!form.username || !form.password) return;
  loading.value = true;
  try {
    await auth.register(form.username, form.password);
    router.push("/");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background:
    radial-gradient(
      ellipse at 30% 20%,
      rgba(200, 150, 62, 0.06) 0%,
      transparent 60%
    ),
    radial-gradient(
      ellipse at 70% 80%,
      rgba(200, 150, 62, 0.04) 0%,
      transparent 60%
    ),
    var(--color-bg);
  padding: 24px;
}

.auth-card {
  width: 380px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 44px 40px 32px;
  border: 1px solid var(--color-border);
}

.auth-header {
  text-align: center;
  margin-bottom: 36px;
}

.auth-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--color-accent);
  color: #fff;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  border-radius: var(--radius-md);
  margin-bottom: 16px;
}

.auth-header h1 {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 6px;
}

.auth-header p {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.field-input {
  height: 44px;
  padding: 0 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--color-text);
  background: var(--color-bg);
  outline: none;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
}

.field-input::placeholder {
  color: var(--color-text-muted);
}

.field-input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-light);
}

.submit-btn {
  height: 44px;
  margin-top: 4px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: #fff;
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn:hover {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(200, 150, 62, 0.3);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.spinner {
  width: 20px;
  height: 20px;
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

.auth-switch {
  text-align: center;
  margin-top: 24px;
  font-size: 13px;
  color: var(--color-text-muted);
}

.auth-switch a {
  color: var(--color-accent);
  font-weight: 600;
  text-decoration: none;
}

.auth-switch a:hover {
  text-decoration: underline;
}
</style>
