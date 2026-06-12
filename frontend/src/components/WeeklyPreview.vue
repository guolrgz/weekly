<template>
  <div class="weekly-preview">
    <el-empty
      v-if="!report || report.entry_count === 0"
      description="本周暂无数据"
    />
    <template v-else>
      <div class="preview-toolbar">
        <span class="preview-label"
          >{{ report.week_label }} · {{ report.week_start }} ~
          {{ report.week_end }}</span
        >
        <div class="preview-actions">
          <button class="action-btn action-btn--primary" @click="handleCopy">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              width="16"
              height="16"
            >
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
              <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
            </svg>
            复制全文
          </button>
          <button class="action-btn" @click="handleExport">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              width="16"
              height="16"
            >
              <path
                d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"
              />
            </svg>
            导出 Markdown
          </button>
        </div>
      </div>

      <article class="preview-doc" v-html="rendered" />
    </template>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { ElMessage } from "element-plus";
import { marked } from "marked";
import api from "../api";

const props = defineProps({ report: Object });

const rendered = computed(() => {
  if (!props.report) return "";
  return marked(buildMarkdown(props.report));
});

function buildMarkdown(r) {
  let md = `# 工作周报 (${r.week_start} ~ ${r.week_end})\n\n`;
  md += `**总工时**：${r.total_hours} 小时 | **记录**：${r.entry_count} 条 | **工作天数**：${r.work_days} 天\n\n`;
  md += `## 分类统计\n\n`;
  for (const c of r.category_breakdown) {
    md += `- ${c.category}：${c.hours}h (${c.percentage}%)\n`;
  }
  md += `\n## 每日详情\n\n`;
  for (const d of r.daily_distribution) {
    const dayEntries = r.entries.filter((e) => e.date === d.date);
    const items = dayEntries
      .map((e) => `${e.category}: ${e.content}(${e.hours}h)`)
      .join(" · ");
    md += `**${d.weekday}**：${items}\n\n`;
  }
  return md;
}

async function handleCopy() {
  const md = buildMarkdown(props.report);
  await navigator.clipboard.writeText(md);
  ElMessage.success("已复制到剪贴板");
}

async function handleExport() {
  const { data } = await api.get("/reports/weekly/export", {
    params: { date: props.report.week_start },
  });
  const blob = new Blob([data.markdown], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `周报_${props.report.week_start}_${props.report.week_end}.md`;
  a.click();
  URL.revokeObjectURL(url);
  ElMessage.success("导出成功");
}
</script>

<style scoped>
.weekly-preview {
  max-width: 780px;
}

.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.preview-label {
  font-family: var(--font-display);
  font-size: 14px;
  color: var(--color-text-muted);
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: var(--color-accent-light);
}

.action-btn--primary {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #fff;
}

.action-btn--primary:hover {
  background: var(--color-accent-hover);
  border-color: var(--color-accent-hover);
  color: #fff;
}

.preview-doc {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 36px 40px;
  line-height: 1.9;
  box-shadow: var(--shadow-sm);
}

.preview-doc :deep(h1) {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--color-accent);
}

.preview-doc :deep(h2) {
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text);
  margin: 28px 0 12px;
}

.preview-doc :deep(p) {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin: 8px 0;
}

.preview-doc :deep(strong) {
  color: var(--color-text);
  font-weight: 600;
}

.preview-doc :deep(ul) {
  padding-left: 20px;
}

.preview-doc :deep(li) {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin: 4px 0;
}
</style>
