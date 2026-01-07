<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon" style="background: #409eff;">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">在职员工</div>
              <div class="stat-value">{{ stats.totalUsers }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon" style="background: #67c23a;">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">今日出勤</div>
              <div class="stat-value">{{ stats.todayAttendance }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon" style="background: #e6a23c;">
              <el-icon><DocumentChecked /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">待审批</div>
              <div class="stat-value">{{ stats.pendingApproval }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon" style="background: #f56c6c;">
              <el-icon><Wallet /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">本月加班费</div>
              <div class="stat-value">¥{{ stats.monthlyOvertime }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>近7日考勤统计</span>
          </template>
          <div ref="chartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>待处理事项</span>
          </template>
          <el-empty v-if="!pendingItems.length" description="暂无待处理事项" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="item in pendingItems"
              :key="item.id"
              :timestamp="item.time"
            >
              {{ item.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const stats = ref({
  totalUsers: 156,
  todayAttendance: 142,
  pendingApproval: 8,
  monthlyOvertime: '12,580'
})

const pendingItems = ref([
  { id: 1, time: '2024-01-15 14:30', content: '张三提交加班申请' },
  { id: 2, time: '2024-01-15 10:20', content: '李四申请调休' }
])

const chartRef = ref()

onMounted(() => {
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: [142, 138, 145, 140, 139, 65, 58],
        type: 'line',
        smooth: true
      }
    ]
  })
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}

.stat-content {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}
</style>
