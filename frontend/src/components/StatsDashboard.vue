<template>
  <div v-loading="loading" class="stats-dashboard">
    <el-empty
      v-if="!report || report.entry_count === 0"
      description="本周暂无数据"
    />
    <template v-else>
      <div class="stat-grid">
        <div class="stat-card stat-card--amber">
          <span class="stat-label">本周总工时</span>
          <span class="stat-value"
            >{{ report.total_hours }}<small>h</small></span
          >
        </div>
        <div class="stat-card stat-card--sage">
          <span class="stat-label">记录条数</span>
          <span class="stat-value"
            >{{ report.entry_count }}<small>条</small></span
          >
        </div>
        <div class="stat-card stat-card--rose">
          <span class="stat-label">工作天数</span>
          <span class="stat-value"
            >{{ report.work_days }}<small>天</small></span
          >
        </div>
        <div class="stat-card stat-card--slate">
          <span class="stat-label">主力分类</span>
          <span class="stat-value">{{ report.top_category || "—" }}</span>
        </div>
      </div>

      <div class="chart-row">
        <div class="chart-box">
          <div class="chart-title">分类占比</div>
          <v-chart :option="pieOption" style="height: 320px" autoresize />
        </div>
        <div class="chart-box">
          <div class="chart-title">每日耗时分布</div>
          <v-chart :option="barOption" style="height: 320px" autoresize />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { PieChart, BarChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

use([
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  CanvasRenderer,
]);

const props = defineProps({
  report: Object,
  loading: Boolean,
});

const CHART_COLORS = ["#c8963e", "#5b8c5a", "#c25450", "#8c8068", "#b8ad93"];

const pieOption = computed(() => ({
  color: CHART_COLORS,
  tooltip: { trigger: "item", formatter: "{b}: {c}h ({d}%)" },
  legend: { bottom: 0, textStyle: { color: "#8c8068", fontSize: 13 } },
  series: [
    {
      type: "pie",
      radius: ["50%", "78%"],
      center: ["50%", "47%"],
      data: (props.report?.category_breakdown || []).map((c) => ({
        name: c.category,
        value: c.hours,
      })),
      label: { formatter: "{b}\n{d}%", fontSize: 12, color: "#8c8068" },
      emphasis: {
        label: { fontSize: 18, fontWeight: "bold" },
        scaleSize: 8,
      },
      itemStyle: {
        borderColor: "#fff",
        borderWidth: 2,
        borderRadius: 4,
      },
    },
  ],
}));

const barOption = computed(() => ({
  color: ["#c8963e"],
  tooltip: { trigger: "axis", formatter: "{b}: {c}h" },
  xAxis: {
    type: "category",
    data: (props.report?.daily_distribution || []).map((d) => d.weekday),
    axisLine: { lineStyle: { color: "#e8e0d0" } },
    axisTick: { show: false },
    axisLabel: { color: "#8c8068", fontSize: 13 },
  },
  yAxis: {
    type: "value",
    name: "小时",
    nameTextStyle: { color: "#b8ad93", fontSize: 12 },
    splitLine: { lineStyle: { color: "#f2ece0", type: "dashed" } },
    axisLabel: { color: "#b8ad93", fontSize: 12 },
  },
  series: [
    {
      type: "bar",
      data: (props.report?.daily_distribution || []).map((d) => d.hours),
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: {
          type: "linear",
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: "#d4a84a" },
            { offset: 1, color: "#c8963e" },
          ],
        },
      },
      barWidth: "40%",
      emphasis: {
        itemStyle: { color: "#b8862d" },
      },
    },
  ],
  grid: { left: 55, right: 25, top: 25, bottom: 35 },
}));
</script>

<style scoped>
.stats-dashboard {
  max-width: 960px;
}

/* === Stat Cards === */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition:
    box-shadow var(--transition-normal),
    transform var(--transition-normal);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stat-card--amber {
  border-left: 3px solid #c8963e;
}
.stat-card--sage {
  border-left: 3px solid #5b8c5a;
}
.stat-card--rose {
  border-left: 3px solid #c25450;
}
.stat-card--slate {
  border-left: 3px solid #8c8068;
}

.stat-label {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 30px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1;
}

.stat-value small {
  font-size: 16px;
  font-weight: 400;
  color: var(--color-text-muted);
  margin-left: 2px;
}

/* === Charts === */
.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-box {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 20px 24px;
}

.chart-title {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 8px;
}
</style>
