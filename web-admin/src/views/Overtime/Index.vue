<template>
  <div class="overtime-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>加班审批</span>
          <el-badge :value="8" class="item">
            <el-button>待审批</el-button>
          </el-badge>
        </div>
      </template>
      <el-empty description="加班审批功能开发中..." />
    </el-card>
  </div>
</template>

<script setup>
// 加班审批页面 - 待完善
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
