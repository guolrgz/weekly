<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-mark">周</span>
        <span class="brand-text">工作周报</span>
      </div>

      <nav class="sidebar-nav">
        <router-link
          to="/weekly-report"
          class="nav-item"
          active-class="nav-item--active"
        >
          <svg
            class="nav-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
          </svg>
          <span>工作周报</span>
        </router-link>
        <router-link
          to="/categories"
          class="nav-item"
          active-class="nav-item--active"
        >
          <svg
            class="nav-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M4 4h16v4H4zM4 10h16v4H4zM4 16h16v4H4z" />
          </svg>
          <span>分类管理</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            {{ auth.user?.username?.[0]?.toUpperCase() }}
          </div>
          <span class="user-name">{{ auth.user?.username }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout" title="退出登录">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            width="18"
            height="18"
          >
            <path
              d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"
            />
          </svg>
        </button>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

function handleLogout() {
  auth.logout();
  router.push("/login");
}
</script>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
}

/* === Sidebar === */
.sidebar {
  width: 220px;
  background: var(--color-sidebar);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
}

.sidebar-brand {
  padding: 28px 24px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--color-accent);
  color: #fff;
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.brand-text {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 0.02em;
}

/* === Nav === */
.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  color: var(--color-sidebar-text);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.nav-item:hover {
  background: var(--color-sidebar-hover);
  color: #e0d5c0;
}

.nav-item--active {
  background: rgba(200, 150, 62, 0.15);
  color: var(--color-sidebar-active);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  opacity: 0.7;
}

.nav-item--active .nav-icon {
  opacity: 1;
}

/* === Footer === */
.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  background: rgba(200, 150, 62, 0.2);
  color: var(--color-sidebar-active);
  font-size: 12px;
  font-weight: 700;
  font-family: var(--font-display);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-name {
  color: var(--color-sidebar-text);
  font-size: 13px;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--color-sidebar-text);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.logout-btn:hover {
  background: rgba(194, 84, 80, 0.2);
  color: var(--color-danger);
}

/* === Main === */
.main-content {
  flex: 1;
  padding: 32px 40px;
  min-width: 0;
  background: var(--color-bg);
}
</style>
