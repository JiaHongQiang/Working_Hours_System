<template>
  <div class="department-management">
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>{{ title }}</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 新增{{ title }}
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" style="width: 100%" row-key="id" default-expand-all>
        <el-table-column prop="dept_name" label="名称" min-width="180" />
        <el-table-column prop="dept_code" label="编码" width="120" />
        <el-table-column prop="dept_type_display" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getDeptTypeTag(row.dept_type)">{{ row.dept_type_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="manager_name" label="负责人" width="120">
             <template #default="{ row }">
                {{ row.manager_name || '-' }}
             </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="dept_name">
          <el-input v-model="formData.dept_name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="编码" prop="dept_code">
          <el-input v-model="formData.dept_code" placeholder="唯一编码" />
        </el-form-item>
        <el-form-item label="类型" prop="dept_type">
          <el-select v-model="formData.dept_type" placeholder="请选择类型" :disabled="isWardOnly">
             <el-option label="行政科室" value="ADMIN" />
             <el-option label="临床科室" value="CLINICAL" />
             <el-option label="病区" value="WARD" />
             <el-option label="医技科室" value="TECH" />
          </el-select>
        </el-form-item>
         <el-form-item label="上级" prop="parent">
          <el-tree-select
            v-model="formData.parent"
            :data="deptTree"
            :props="{ label: 'dept_name', value: 'id', children: 'children' }"
            placeholder="请选择上级部门"
            check-strictly
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="formData.is_active" active-text="启用" inactive-text="禁用" />
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const props = defineProps({
  type: {
    type: String,
    default: 'ALL' // 'ALL' or 'WARD'
  }
})

const loading = ref(false)
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const tableData = ref([])
const deptTree = ref([]) // 用于上级选择

const title = computed(() => props.type === 'WARD' ? '病区管理' : '科室管理')
const isWardOnly = computed(() => props.type === 'WARD')

const formData = reactive({
  id: null,
  dept_name: '',
  dept_code: '',
  dept_type: '',
  parent: null,
  is_active: true
})

const rules = {
  dept_name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  dept_code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
  dept_type: [{ required: true, message: '请选择类型', trigger: 'change' }]
}

const dialogTitle = computed(() => (isEdit.value ? '编辑' : '新增') + title.value)

const getDeptTypeTag = (type) => {
    const map = { 'ADMIN': 'info', 'CLINICAL': 'primary', 'WARD': 'success', 'TECH': 'warning' }
    return map[type]
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (props.type === 'WARD') {
        params.dept_type = 'WARD'
    }
    const res = await request.get('/departments/', { params })
    tableData.value = res.data.results || res.data
    
    // 如果是编辑上级，需要完整的树
    if (!deptTree.value.length) {
        const treeRes = await request.get('/departments/tree/')
        deptTree.value = treeRes.data
    }
  } catch (err) {
    console.error(err)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  formData.id = null
  formData.dept_name = ''
  formData.dept_code = ''
  formData.dept_type = isWardOnly.value ? 'WARD' : 'ADMIN'
  formData.parent = null
  formData.is_active = true
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
                await request.patch(`/departments/${formData.id}/`, formData)
                ElMessage.success('更新成功')
            } else {
                await request.post('/departments/', formData)
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
    ElMessageBox.confirm(`确定删除 "${row.dept_name}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
        try {
            await request.delete(`/departments/${row.id}/`)
            ElMessage.success('删除成功')
            loadData()
        } catch (err) {
            ElMessage.error('删除失败')
        }
    })
}

watch(() => props.type, () => {
    loadData()
})

onMounted(() => {
    loadData()
})
</script>

<style scoped>
.department-management {
    height: 100%;
    display: flex;
    flex-direction: column;
}
.table-card {
    flex: 1;
    display: flex;
    flex-direction: column;
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
