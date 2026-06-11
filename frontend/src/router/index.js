import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("../views/Register.vue"),
  },
  {
    path: "/",
    component: () => import("../views/Layout.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        redirect: "/weekly-report",
      },
      {
        path: "weekly-report",
        name: "WeeklyReport",
        component: () => import("../views/WeeklyReport.vue"),
      },
      {
        path: "categories",
        name: "Categories",
        component: () => import("../views/Categories.vue"),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  if (to.meta.requiresAuth && !token) {
    next("/login");
  } else if ((to.path === "/login" || to.path === "/register") && token) {
    next("/");
  } else {
    next();
  }
});

export default router;
