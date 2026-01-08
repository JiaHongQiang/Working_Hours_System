<template>
  <div class="shift-management">
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>班次定义</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 新增班次
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" style="width: 100%" stripe border>
        <el-table-column prop="name" label="班次名称" min-width="120" />
        <el-table-column label="时间段" min-width="150" align="center">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }} - {{ formatTime(row.end_time) }}
            <el-tag v-if="row.is_cross_day" type="warning" size="small" effect="plain">跨天</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration_hours" label="时长(小时)" width="100" align="center" />
        <el-table-column label="标识颜色" width="100" align="center">
            <template #default="{ row }">
                <div class="color-preview" :style="{ backgroundColor: row.color }"></div>
            </template>
        </el-table-column>
        <el-table-column prop="description" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑班次' : '新增班次'" 
      width="500px" 
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="80px">
        <el-form-item label="班次名称" prop="name">
          <el-input v-model="formData.name" placeholder="如：早班、大夜班" />
        </el-form-item>
        <el-form-item label="时间范围" required>
            <el-col :span="11">
                <el-form-item prop="start_time">
                    <el-time-picker v-model="formData.start_time" format="HH:mm" value-format="HH:mm:ss" placeholder="上班时间" style="width: 100%" />
                </el-form-item>
            </el-col>
            <el-col :span="2" class="text-center">-</el-col>
            <el-col :span="11">
                <el-form-item prop="end_time">
                    <el-time-picker v-model="formData.end_time" format="HH:mm" value-format="HH:mm:ss" placeholder="下班时间" style="width: 100%" />
                </el-form-item>
            </el-col>
        </el-form-item>
        <el-form-item label="属性">
            <el-checkbox v-model="formData.is_cross_day">跨天 (结束于次日)</el-checkbox>
        </el-form-item>
        <el-form-item label="标识颜色" prop="color">
            <el-color-picker v-model="formData.color" :predefine="predefineColors" />
        </el-form-item>
        <el-form-item label="备注" prop="description">
          <el-input v-model="formData.description" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const formData = reactive({
    id: null,
    name: '',
    start_time: '',
    end_time: '',
    is_cross_day: false,
    color: '#409EFF',
    description: '',
    is_active: true
})

const rules = {
    name: [{ required: true, message: '请输入班次名称', trigger: 'blur' }],
    start_time: [{ required: true, message: '请选择上班时间', trigger: 'change' }],
    end_time: [{ required: true, message: '请选择下班时间', trigger: 'change' }],
    color: [{ required: true, message: '请选择颜色', trigger: 'change' }]
}

const predefineColors = [
    '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', 
    '#909399', '#303133', '#b3d8ff', '#d9ecff'
]

const formatTime = (timeStr) => {
    if (!timeStr) return ''
    return timeStr.substring(0, 5)
}

const loadData = async () => {
    loading.value = true
    try {
        const res = await request.get('/shifts/')
        tableData.value = res.data.results || res.data
    } catch (err) {
        ElMessage.error('加载失败')
    } finally {
        loading.value = false
    }
}

const handleAdd = () => {
    isEdit.value = false
    Object.assign(formData, {
        id: null,
        name: '',
        start_time: '08:00:00',
        end_time: '16:00:00',
        is_cross_day: false,
        color: '#409EFF',
        description: '',
        is_active: true
    })
    dialogVisible.value = true
}

const handleEdit = (row) => {
    isEdit.value = true
    Object.assign(formData, row)
    dialogVisible.value = true
}

const handleSubmit = async () => {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (!valid) return
        submitLoading.value = true
        try {
            if (isEdit.value) {
                await request.patch(`/shifts/${formData.id}/`, formData)
                ElMessage.success('更新成功')
            } else {
                await request.post('/shifts/', formData)
                ElMessage.success('创建成功')
            }
            dialogVisible.value = false
            loadData()
        } catch (err) {
            ElMessage.error(err.response?.data?.detail || '操作失败')
        } finally {
            submitLoading.value = false
        }
    })
}

const handleDelete = (row) => {
    ElMessageBox.confirm(`确定要删除班次 "${row.name}" 吗？`, '警告', {
        type: 'warning'
    }).then(async () => {
        try {
            await request.delete(`/shifts/${row.id}/`)
            ElMessage.success('删除成功')
            loadData()
        } catch (err) {
            ElMessage.error('删除失败')
        }
    })
}

onMounted(() => {
    loadData()
})
</script>

<style scoped>
.shift-management {
    height: 100%;
    display: flex;
    flex-direction: column;
}
.table-card {
    flex: 1;
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.color-preview {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    margin: 0 auto;
    border: 1px solid #ddd;
}
.text-center {
    text-align: center;
}
</style>
