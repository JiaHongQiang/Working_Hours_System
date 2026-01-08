<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      <el-tabs v-model="activeTab">
        <!-- 打卡配置 -->
        <el-tab-pane label="打卡配置" name="punch">
          <el-form 
            ref="punchFormRef"
            :model="punchConfig"
            :rules="punchRules"
            label-width="120px"
            style="max-width: 600px;"
          >
            <el-form-item label="医院名称" prop="hospital_name">
              <el-input v-model="punchConfig.hospital_name" placeholder="请输入医院名称" />
            </el-form-item>
            
            <el-form-item label="医院经度" prop="hospital_longitude">
              <el-input-number 
                v-model="punchConfig.hospital_longitude" 
                :precision="6" 
                :step="0.0001"
                :min="-180"
                :max="180"
                placeholder="经度"
                style="width: 100%;"
              />
              <div class="form-tip">范围: -180 到 180</div>
            </el-form-item>
            
            <el-form-item label="医院纬度" prop="hospital_latitude">
              <el-input-number 
                v-model="punchConfig.hospital_latitude" 
                :precision="6" 
                :step="0.0001"
                :min="-90"
                :max="90"
                placeholder="纬度"
                style="width: 100%;"
              />
              <div class="form-tip">范围: -90 到 90</div>
            </el-form-item>
            
            <el-form-item label="打卡范围(米)" prop="geofence_radius">
              <el-input-number 
                v-model="punchConfig.geofence_radius" 
                :min="10" 
                :max="10000"
                :step="10"
                placeholder="打卡范围"
                style="width: 100%;"
              />
              <div class="form-tip">员工必须在此范围内才能正常打卡，范围: 10-10000米</div>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="savePunchConfig" :loading="saving">
                保存配置
              </el-button>
              <el-button @click="loadPunchConfig">重置</el-button>
            </el-form-item>
          </el-form>
          
          <el-divider />
          
          <div class="config-preview">
            <h4>配置预览</h4>
            <p>医院名称: <strong>{{ punchConfig.hospital_name }}</strong></p>
            <p>坐标位置: <strong>{{ punchConfig.hospital_longitude }}, {{ punchConfig.hospital_latitude }}</strong></p>
            <p>打卡范围: <strong>{{ punchConfig.geofence_radius }}米</strong></p>
            <el-link type="primary" :href="`https://uri.amap.com/marker?position=${punchConfig.hospital_longitude},${punchConfig.hospital_latitude}&name=${punchConfig.hospital_name}`" target="_blank">
              在高德地图中查看 →
            </el-link>
          </div>
        </el-tab-pane>
        
        <!-- 其他设置标签页 -->
        <el-tab-pane label="部门管理" name="department">
          <el-empty description="请在左侧菜单中访问【用户管理 > 科室管理】" />
        </el-tab-pane>
        <el-tab-pane label="员工管理" name="user">
          <el-empty description="请在左侧菜单中访问【用户管理 > 人员管理】" />
        </el-tab-pane>
        <el-tab-pane label="班次设置" name="shift">
          <el-empty description="请在左侧菜单中访问【排班管理 > 班次定义】" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const activeTab = ref('punch')
const punchFormRef = ref(null)
const saving = ref(false)

// 打卡配置
const punchConfig = ref({
  hospital_name: '医院',
  hospital_latitude: 39.9042,
  hospital_longitude: 116.4074,
  geofence_radius: 200
})

// 表单验证规则
const punchRules = {
  hospital_name: [
    { required: true, message: '请输入医院名称', trigger: 'blur' }
  ],
  hospital_latitude: [
    { required: true, message: '请输入纬度', trigger: 'blur' }
  ],
  hospital_longitude: [
    { required: true, message: '请输入经度', trigger: 'blur' }
  ],
  geofence_radius: [
    { required: true, message: '请输入打卡范围', trigger: 'blur' }
  ]
}

// 加载打卡配置
const loadPunchConfig = async () => {
  try {
    const res = await request.get('/config/punch_config/')
    punchConfig.value = {
      hospital_name: res.data.hospital_name || '医院',
      hospital_latitude: res.data.hospital_latitude || 39.9042,
      hospital_longitude: res.data.hospital_longitude || 116.4074,
      geofence_radius: res.data.geofence_radius || 200
    }
  } catch (error) {
    console.error('加载打卡配置失败:', error)
  }
}

// 保存打卡配置
const savePunchConfig = async () => {
  try {
    await punchFormRef.value.validate()
    saving.value = true
    
    await request.post('/config/save_punch_config/', punchConfig.value)
    ElMessage.success('配置保存成功')
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.response?.data?.error || '保存失败')
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadPunchConfig()
})
</script>

<style scoped>
.settings-page {
  padding: 0;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.config-preview {
  background: #f5f7fa;
  padding: 16px 20px;
  border-radius: 8px;
}

.config-preview h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.config-preview p {
  margin: 8px 0;
  color: #606266;
}
</style>
