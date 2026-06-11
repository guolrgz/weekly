<template>
  <div v-loading="loading">
    <el-empty
      v-if="!report || report.entry_count === 0"
      description="本周暂无数据"
    />
    <template v-else>
      <el-row :gutter="16" class="stat-cards">
        <el-col :span="6">
          <el-statistic
            title="本周总工时"
            :value="report.total_hours"
            suffix="h"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic title="记录条数" :value="report.entry_count" />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="工作天数"
            :value="report.work_days"
            suffix="天"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic title="主力分类" :value="report.top_category || '-'" />
        </el-col>
      </el-row>
      <el-row :gutter="16" style="margin-top: 20px">
        <el-col :span="12">
          <el-card>
            <template #header>分类占比</template>
            <v-chart :option="pieOption" style="height: 300px" autoresize />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>每日耗时分布</template>
            <v-chart :option="barOption" style="height: 300px" autoresize />
          </el-card>
        </el-col>
      </el-row>
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

const pieOption = computed(() => ({
  tooltip: { trigger: "item", formatter: "{b}: {c}h ({d}%)" },
  legend: { bottom: 0 },
  series: [
    {
      type: "pie",
      radius: ["45%", "75%"],
      center: ["50%", "45%"],
      data: (props.report?.category_breakdown || []).map((c) => ({
        name: c.category,
        value: c.hours,
        itemStyle: { color: c.color },
      })),
      label: { formatter: "{b}\n{d}%" },
    },
  ],
}));

const barOption = computed(() => ({
  tooltip: { trigger: "axis" },
  xAxis: {
    type: "category",
    data: (props.report?.daily_distribution || []).map((d) => d.weekday),
  },
  yAxis: { type: "value", name: "小时" },
  series: [
    {
      type: "bar",
      data: (props.report?.daily_distribution || []).map((d) => d.hours),
      itemStyle: { color: "#409EFF", borderRadius: [4, 4, 0, 0] },
      barWidth: "50%",
    },
  ],
  grid: { left: 50, right: 20, top: 20, bottom: 30 },
}));
</script>

<style scoped>
.stat-cards .el-col {
  text-align: center;
}
</style>
