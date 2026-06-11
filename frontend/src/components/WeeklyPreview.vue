<template>
  <div>
    <el-empty
      v-if="!report || report.entry_count === 0"
      description="本周暂无数据"
    />
    <template v-else>
      <div class="preview-actions">
        <el-button type="primary" @click="handleCopy">复制全文</el-button>
        <el-button @click="handleExport">导出 Markdown</el-button>
      </div>
      <div class="markdown-body" v-html="rendered" />
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
.preview-actions {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
}
.markdown-body {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 24px;
  line-height: 1.8;
}
.markdown-body :deep(h1) {
  font-size: 22px;
  margin-top: 0;
}
.markdown-body :deep(h2) {
  font-size: 17px;
  margin-top: 20px;
}
.markdown-body :deep(ul) {
  padding-left: 20px;
}
</style>
