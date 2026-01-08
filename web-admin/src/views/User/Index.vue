<template>
  <div class="user-management">
    <!-- 搜索筛选区 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="关键词">
          <el-input 
            v-model="filterForm.keyword" 
            placeholder="工号/姓名/手机号" 
            clearable 
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="科室">
          <el-select v-model="filterForm.admin_dept" placeholder="请选择科室" clearable>
            <el-option
              v-for="dept in departmentList"
              :key="dept.id"
              :label="dept.dept_name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="人员类别">
          <el-select v-model="filterForm.staff_category" placeholder="请选择" clearable>
            <el-option label="医生" value="DOCTOR" />
            <el-option label="护士" value="NURSE" />
            <el-option label="医技" value="TECH" />
            <el-option label="行政" value="ADMIN" />
          </el-select>
        </el-form-item>
        <el-form-item label="用工性质">
          <el-select v-model="filterForm.emp_status" placeholder="请选择" clearable>
            <el-option label="正式在编" value="REGULAR" />
            <el-option label="合同制" value="CONTRACT" />
            <el-option label="实习生" value="INTERN" />
            <el-option label="规培生" value="RESIDENT" />
            <el-option label="规培生" value="RESIDENT" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.search_work_status" placeholder="请选择" style="width: 120px">
             <el-option label="全部" value="" />
             <el-option label="在职" :value="1" />
             <el-option label="离职" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>人员列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增员工
            </el-button>
            <el-button type="success" @click="handleExport">
              <el-icon><Download /></el-icon> 导出
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table 
        v-loading="loading" 
        :data="tableData" 
        stripe 
        border
        style="width: 100%"
      >
        <el-table-column prop="emp_code" label="工号" width="100" fixed />
        <el-table-column prop="full_name" label="姓名" min-width="120" />
        <el-table-column prop="admin_dept_name" label="行政科室" min-width="140" />
        <el-table-column prop="scheduling_ward_name" label="排班病区" min-width="140">
          <template #default="{ row }">
            {{ row.scheduling_ward_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="staff_category_display" label="人员类别" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.staff_category)">
              {{ row.staff_category_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="emp_status_display" label="用工性质" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.emp_status)" effect="plain">
              {{ row.emp_status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="job_title" label="职称" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.job_title || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_scheduling_required" label="参与排班" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_scheduling_required ? 'success' : 'info'" size="small">
              {{ row.is_scheduling_required ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="work_status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.work_status === 1 ? 'success' : 'danger'" size="small">
              {{ row.work_status === 1 ? '在职' : '离职' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" link size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button type="warning" link size="small" @click="handleResetPassword(row)">
                <el-icon><Key /></el-icon> 重置密码
              </el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="700px"
      destroy-on-close
    >
      <el-form 
        ref="formRef" 
        :model="formData" 
        :rules="formRules" 
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工号" prop="emp_code">
              <el-input v-model="formData.emp_code" placeholder="请输入工号" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="full_name">
              <el-input v-model="formData.full_name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="行政科室" prop="admin_dept">
              <el-select v-model="formData.admin_dept" placeholder="请选择行政科室" style="width: 100%">
                <el-option
                  v-for="dept in departmentList"
                  :key="dept.id"
                  :label="dept.dept_name"
                  :value="dept.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排班病区" prop="scheduling_ward">
              <el-select v-model="formData.scheduling_ward" placeholder="请选择排班病区" clearable style="width: 100%">
                <el-option
                  v-for="ward in wardList"
                  :key="ward.id"
                  :label="ward.dept_name"
                  :value="ward.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="人员类别" prop="staff_category">
              <el-select v-model="formData.staff_category" placeholder="请选择" style="width: 100%">
                <el-option label="医生" value="DOCTOR" />
                <el-option label="护士" value="NURSE" />
                <el-option label="医技" value="TECH" />
                <el-option label="行政" value="ADMIN" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用工性质" prop="emp_status">
              <el-select v-model="formData.emp_status" placeholder="请选择" style="width: 100%">
                <el-option label="正式在编" value="REGULAR" />
                <el-option label="合同制" value="CONTRACT" />
                <el-option label="实习生" value="INTERN" />
                <el-option label="规培生" value="RESIDENT" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="人员状态" prop="work_status">
               <el-select v-model="formData.work_status" placeholder="请选择" style="width: 100%">
                <el-option label="在职" :value="1" />
                <el-option label="离职" :value="2" />
                <!-- 0是未知，一般不用 -->
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="job_title">
              <el-input v-model="formData.job_title" placeholder="如：主任医师、护士长" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="基础时薪" prop="base_hourly_rate">
              <el-input-number 
                v-model="formData.base_hourly_rate" 
                :min="0" 
                :precision="2" 
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="formData.phone" placeholder="请输入手机号" maxlength="11" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号" prop="id_card">
              <el-input v-model="formData.id_card" placeholder="请输入身份证号" maxlength="18" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入职日期" prop="hire_date">
              <el-date-picker
                v-model="formData.hire_date"
                type="date"
                placeholder="选择入职日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="参与排班">
              <el-switch v-model="formData.is_scheduling_required" />
            </el-form-item>
          </el-col>
        </el-row>

        <template v-if="!isEdit">
          <el-divider content-position="left">登录信息</el-divider>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="登录账号" prop="username">
                <el-input v-model="formData.username" placeholder="请输入登录账号" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="登录密码" prop="password">
                <el-input v-model="formData.password" type="password" placeholder="请输入密码" show-password />
              </el-form-item>
            </el-col>
          </el-row>
        </template>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Refresh, Plus, Download, Edit, Delete, Key 
} from '@element-plus/icons-vue'
import request from '@/utils/request'

// ========== 数据定义 ==========
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const tableData = ref([])
const departmentList = ref([])
const wardList = ref([])

// 筛选表单
const filterForm = reactive({
  keyword: '',
  admin_dept: '',
  staff_category: '',
  emp_status: '',
  search_work_status: 1 // 默认查在职
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 表单数据
const defaultFormData = {
  emp_code: '',
  username: '',
  password: '',
  full_name: '',
  admin_dept: '',
  scheduling_ward: null,
  staff_category: 'NURSE',
  emp_status: 'CONTRACT',
  work_status: 1,
  job_title: '',
  base_hourly_rate: 0,
  phone: '',
  id_card: '',
  hire_date: '',
  is_scheduling_required: true
}

const formData = reactive({ ...defaultFormData })

// 表单校验规则
const formRules = {
  emp_code: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  full_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  admin_dept: [{ required: true, message: '请选择行政科室', trigger: 'change' }],
  staff_category: [{ required: true, message: '请选择人员类别', trigger: 'change' }],
  emp_status: [{ required: true, message: '请选择用工性质', trigger: 'change' }],
  username: [{ required: true, message: '请输入登录账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入登录密码', trigger: 'blur' }]
}

// 弹窗标题
const dialogTitle = computed(() => isEdit.value ? '编辑员工' : '新增员工')

// ========== 方法 ==========

// 获取人员类别标签颜色
const getCategoryTagType = (category) => {
  const map = {
    'DOCTOR': 'primary',
    'NURSE': 'success',
    'TECH': 'warning',
    'ADMIN': 'info'
  }
  return map[category] || 'info'
}

// 获取用工性质标签颜色
const getStatusTagType = (status) => {
  const map = {
    'REGULAR': 'success',
    'CONTRACT': 'primary',
    'INTERN': 'warning',
    'RESIDENT': 'info'
  }
  return map[status] || 'info'
}

// 加载科室列表
const loadDepartments = async () => {
  try {
    const res = await request.get('/departments/', {
      params: { is_active: true }
    })
    departmentList.value = res.data.results || res.data
    // 筛选病区
    wardList.value = departmentList.value.filter(d => d.dept_type === 'WARD')
  } catch (error) {
    console.error('加载科室失败', error)
  }
}

// 加载员工列表
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      search: filterForm.keyword || undefined,
      admin_dept: filterForm.admin_dept || undefined,
      staff_category: filterForm.staff_category || undefined,
      admin_dept: filterForm.admin_dept || undefined,
      staff_category: filterForm.staff_category || undefined,
      emp_status: filterForm.emp_status || undefined,
      work_status: filterForm.search_work_status === '' ? '' : filterForm.search_work_status // 空串代表全部
    }
    // 特殊处理：如果需要查全部（即发空串），request params会自动忽略undefined，但我们需要发一个空串key
    // 不过由于axios behavior，params里的空串可能会被忽略。
    // 为了配合后端 "if 'work_status' in params"，我们需要确保key存在。
    // 如果是 ''，axios可能会保留 key=''。我们来验证一下。
    // 另外一种方式：如果选全部，传 undefined？不行，后端说没key就默认1。
    // 所以：选全部 -> 传 work_status: ''。
    
    // 修正逻辑：
    if (filterForm.search_work_status === '') {
        params.work_status = '' 
    } else {
        params.work_status = filterForm.search_work_status
    }
    const res = await request.get('/users/', { params })
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || tableData.value.length
  } catch (error) {
    console.error('加载员工列表失败', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置筛选
const handleReset = () => {
  filterForm.keyword = ''
  filterForm.admin_dept = ''
  filterForm.staff_category = ''
  filterForm.emp_status = ''
  filterForm.search_work_status = 1 // 重置回在职
  handleSearch()
}

// 分页变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadData()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadData()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  Object.assign(formData, defaultFormData)
  dialogVisible.value = true
}

// 编辑
const handleEdit = async (row) => {
  isEdit.value = true
  dialogVisible.value = true
  // 先重置表单防止残留
  // Object.assign(formData, defaultFormData) // 不能直接重置，否则ID没了
  // 先填入已知的基础信息，避免弹窗空白
  Object.assign(formData, {
      ...defaultFormData,
      id: row.id,
      emp_code: row.emp_code,
      full_name: row.full_name
  })
  
  // 获取完整详情
  try {
      const res = await request.get(`/users/${row.id}/`)
      const data = res.data
      Object.assign(formData, {
        id: data.id,
        emp_code: data.emp_code,
        full_name: data.full_name,
        admin_dept: data.admin_dept,
        scheduling_ward: data.scheduling_ward,
        staff_category: data.staff_category,
        emp_status: data.emp_status,
        work_status: data.work_status,
        job_title: data.job_title || '',
        base_hourly_rate: data.base_hourly_rate || 0,
        // 处理可能为null的字段
        phone: data.phone || '',
        id_card: data.id_card || '',
        hire_date: data.hire_date || '',
        is_scheduling_required: data.is_scheduling_required
      })
  } catch (err) {
      ElMessage.error('获取员工详情失败')
      dialogVisible.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    // 构造提交数据，处理空值
    const submitData = { ...formData }
    if (!submitData.scheduling_ward) submitData.scheduling_ward = null
    if (!submitData.phone) submitData.phone = ''
    if (!submitData.id_card) submitData.id_card = ''
    if (!submitData.hire_date) submitData.hire_date = null
    
    // 如果是编辑，不需要传password
    if (isEdit.value) {
      delete submitData.password
      delete submitData.username
    }

    submitLoading.value = true
    try {
      if (isEdit.value) {
        await request.patch(`/users/${formData.id}/`, submitData)
        ElMessage.success('更新成功')
      } else {
        await request.post('/users/', submitData)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadData()
    } catch (error) {
      console.error('提交失败', error)
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除员工 "${row.full_name}" 吗？此操作不可恢复。`,
    '删除确认',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    try {
      await request.delete(`/users/${row.id}/`)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 重置密码
const handleResetPassword = (row) => {
  ElMessageBox.prompt(
    `请输入员工 "${row.full_name}" 的新密码：`,
    '重置密码',
    { confirmButtonText: '确定', cancelButtonText: '取消', inputType: 'password' }
  ).then(async ({ value }) => {
    if (!value || value.length < 6) {
      ElMessage.warning('密码长度至少6位')
      return
    }
    try {
      await request.post(`/users/${row.id}/reset_password/`, { password: value })
      ElMessage.success('密码重置成功')
    } catch (error) {
      ElMessage.error('重置失败')
    }
  }).catch(() => {})
}

// 导出
const handleExport = () => {
  ElMessage.info('导出功能开发中...')
}

// ========== 生命周期 ==========
onMounted(() => {
  loadDepartments()
  loadData()
})
</script>

<style scoped>
.user-management {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card {
  flex-shrink: 0;
}

.table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.table-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: hidden;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 让表格自动填充剩余空间 */
.table-card :deep(.el-table) {
  flex: 1;
  height: 0;
}

.table-card :deep(.action-buttons) {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

.el-form-item {
  margin-bottom: 0; /* 移除默认下边距，由gap控制 */
}

/* 筛选下拉框宽度 */
.filter-form .el-select {
  width: 160px;
}

.filter-form .el-input {
  width: 180px;
}
</style>
