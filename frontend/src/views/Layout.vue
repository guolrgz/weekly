<template>
  <el-container class="layout">
    <el-aside width="200px">
      <div class="logo">工作周报</div>
      <el-menu
        :default-active="route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/weekly-report">
          <el-icon><Edit /></el-icon>
          <span>工作周报</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Collection /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <span>{{ auth.user?.username }}</span>
        <el-button text size="small" @click="handleLogout">退出</el-button>
      </div>
    </el-aside>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

function handleLogout() {
  auth.logout();
  router.push("/login");
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
}
.el-aside {
  background: #304156;
  display: flex;
  flex-direction: column;
}
.logo {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.sidebar-footer {
  margin-top: auto;
  padding: 12px 16px;
  color: #bfcbd9;
  font-size: 13px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
