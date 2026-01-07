<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="部门管理" name="department">
          <el-empty description="部门管理功能开发中..." />
        </el-tab-pane>
        <el-tab-pane label="员工管理" name="user">
          <el-empty description="员工管理功能开发中..." />
        </el-tab-pane>
        <el-tab-pane label="班次设置" name="shift">
          <el-empty description="班次设置功能开发中..." />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('department')
</script>
