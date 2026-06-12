# 工作周报系统 — 设计文档

## 概述

为 AI 原生门户（情报平台）增加按周统计分析功能，用户通过手动录入每日工作记录，系统自动汇总生成周报，支持图表可视化和 Markdown 导出。

## 技术栈

| 层级    | 技术                  | 说明                  |
| ------- | --------------------- | --------------------- |
| 后端    | Python 3 / FastAPI    | RESTful API，JWT 认证 |
| 数据库  | SQLite                | 轻量，单文件部署      |
| 前端    | Vue 3 + Vite          | SPA 应用              |
| UI 组件 | Element Plus          | 后台组件库            |
| 图表    | ECharts               | 饼图、柱状图          |
| 认证    | python-jose + passlib | JWT + bcrypt          |

## 数据模型

### users

| 字段            | 类型        | 说明        |
| --------------- | ----------- | ----------- |
| id              | INTEGER PK  | 自增主键    |
| username        | TEXT UNIQUE | 用户名      |
| hashed_password | TEXT        | bcrypt 哈希 |
| created_at      | TIMESTAMP   | 创建时间    |

### categories

| 字段       | 类型                | 说明            |
| ---------- | ------------------- | --------------- |
| id         | INTEGER PK          | 自增主键        |
| name       | TEXT UNIQUE         | 分类名称        |
| color      | TEXT                | 图表颜色（hex） |
| sort_order | INTEGER             | 排序            |
| user_id    | INTEGER FK→users.id | 所属用户        |

预设分类：开发(#1a73e8)、会议(#16a34a)、文档(#ea580c)、沟通(#8b5cf6)、其他(#6b7280)

### work_entries

| 字段             | 类型                     | 说明         |
| ---------------- | ------------------------ | ------------ |
| id               | INTEGER PK               | 自增主键     |
| user_id          | INTEGER FK→users.id      | 所属用户     |
| date             | DATE                     | 工作日期     |
| category_id      | INTEGER FK→categories.id | 分类         |
| content          | TEXT                     | 工作内容描述 |
| duration_minutes | INTEGER                  | 耗时（分钟） |
| created_at       | TIMESTAMP                | 创建时间     |

## API 设计

### 认证

```
POST /api/auth/register  → 注册
POST /api/auth/login     → 登录，返回 JWT
GET  /api/auth/me        → 当前用户
```

### 工作记录

```
GET    /api/entries?start=&end=  → 查询（支持日期范围）
POST   /api/entries              → 新建
PUT    /api/entries/{id}         → 修改
DELETE /api/entries/{id}         → 删除
```

### 分类管理

```
GET    /api/categories     → 列表
POST   /api/categories     → 新增
PUT    /api/categories/{id}  → 修改
DELETE /api/categories/{id}  → 删除（无记录引用时）
```

### 周报

```
GET  /api/reports/weekly?date=2026-06-11  → 包含该日期的周统计
GET  /api/reports/weekly/export?date=...   → 导出 Markdown 文本
```

周报响应结构：

```json
{
  "week_start": "2026-06-08",
  "week_end": "2026-06-14",
  "week_label": "第24周",
  "total_hours": 28.5,
  "entry_count": 12,
  "work_days": 3,
  "top_category": "开发",
  "daily_distribution": [
    { "date": "2026-06-08", "weekday": "周一", "hours": 8, "entry_count": 5 }
  ],
  "category_breakdown": [
    { "category": "开发", "color": "#1a73e8", "hours": 13.5, "percentage": 47 }
  ],
  "entries": [
    { "date": "2026-06-08", "category": "开发", "content": "...", "hours": 3.5 }
  ]
}
```

## 前端结构

### 路由

```
/           → 重定向到 /weekly-report
/weekly-report → 工作周报（默认 Tab）
/login      → 登录
/register   → 注册
```

### 页面结构

```
App
├── 侧边栏
│   ├── 工作周报 → /weekly-report
│   └── 分类管理 → /categories
│
└── 工作周报页（4 Tab）
    ├── Tab 1: 工作录入
    │   └── 表单（日期/分类/内容/耗时）+ 今日记录列表
    ├── Tab 2: 统计看板
    │   └── 统计卡片 + 分类饼图(ECharts) + 每日柱状图(ECharts)
    ├── Tab 3: 周报预览
    │   └── Markdown 渲染（marked.js）+ 复制/导出按钮
    └── Tab 4: 历史记录
        └── 周列表 → 点击查看历史周报
```

## 周统计逻辑

1. 接收任意日期，计算所在周的周一（week_start）和周日（week_end）
2. 查询该周范围内该用户的所有 work_entries
3. 聚合：分类维度（按 category 分组求和）、日维度（按 date 分组求和）
4. 计算百分比、工作天数、主力分类
5. 导出时转换为 Markdown 模板文本

## 目录结构

```
cproject/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── database.py          # SQLite 连接 + 建表
│   ├── models.py            # Pydantic 模型
│   ├── auth.py              # JWT 认证逻辑
│   ├── routers/
│   │   ├── auth.py          # 认证路由
│   │   ├── entries.py       # 工作记录路由
│   │   ├── categories.py   # 分类路由
│   │   └── reports.py       # 周报路由
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router/
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── WeeklyReport.vue   # 4 Tab 主页面
│   │   │   └── Categories.vue
│   │   ├── components/
│   │   │   ├── Sidebar.vue
│   │   │   ├── WorkEntryForm.vue
│   │   │   ├── TodayEntries.vue
│   │   │   ├── StatsDashboard.vue
│   │   │   ├── WeeklyPreview.vue
│   │   │   └── HistoryList.vue
│   │   └── api/                   # axios 封装
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```
