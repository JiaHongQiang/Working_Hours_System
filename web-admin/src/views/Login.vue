<template>
  <div class="login-container">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>
    
    <div class="login-content">
      <div class="brand-section">
        <div class="logo-box">
          <el-icon :size="40" color="#fff"><TrendCharts /></el-icon>
        </div>
        <h1>医院工时统计系统</h1>
        <p class="subtitle">Efficient • Smart • Professional</p>
      </div>

      <el-card class="login-card">
        <div class="card-header">
          <h3>欢迎登录</h3>
          <p>请使用您的工号和密码访问系统</p>
        </div>
        
        <el-form :model="loginForm" :rules="rules" ref="formRef" size="large" class="login-form">
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入工号"
              prefix-icon="User"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="handleLogin" class="submit-btn">
              登录系统
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
    
    <div class="footer-copyright">
      © {{ new Date().getFullYear() }} Hospital Working Hours System. All Rights Reserved.
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { User, Lock, ArrowRight, TrendCharts } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value.validate()
  if (!valid) return

  loading.value = true
  try {
    const response = await axios.post('/api/token/', {
      username: loginForm.username,
      password: loginForm.password
    })
    
    const { access, refresh } = response.data
    localStorage.setItem('token', access)
    localStorage.setItem('refresh_token', refresh)
    userStore.setToken(access)
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.error('工号或密码错误')
    } else {
      ElMessage.error(error.response?.data?.detail || '登录失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  position: relative;
  overflow: hidden;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 动态背景图形 */
.background-shapes .shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: float 20s infinite;
}

.shape-1 {
  width: 400px;
  height: 400px;
  background: #3b82f6;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 300px;
  height: 300px;
  background: #8b5cf6;
  top: 50%;
  right: -50px;
  animation-delay: -5s;
}

.shape-3 {
  width: 250px;
  height: 250px;
  background: #06b6d4;
  bottom: -50px;
  left: 20%;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  33% { transform: translate(30px, -50px); }
  66% { transform: translate(-20px, 20px); }
}

.login-content {
  display: flex;
  align-items: center;
  gap: 80px;
  z-index: 10;
  padding: 20px;
}

.brand-section {
  color: white;
  text-align: left;
}

.logo-box {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.5);
}

.brand-section h1 {
  font-size: 3rem;
  font-weight: 700;
  margin: 0 0 12px 0;
  background: linear-gradient(to right, #fff, #94a3b8);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.02em;
}

.brand-section .subtitle {
  font-size: 1.25rem;
  color: #94a3b8;
  margin: 0;
  font-weight: 300;
}

.login-card {
  width: 420px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 10px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  transition: transform 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.card-header h3 {
  font-size: 1.75rem;
  color: #1e293b;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.card-header p {
  color: #64748b;
  margin: 0;
  font-size: 0.95rem;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 4px 15px;
  box-shadow: 0 0 0 1px #e2e8f0 inset;
  transition: all 0.3s ease;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #3b82f6 inset;
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.submit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.footer-copyright {
  position: absolute;
  bottom: 24px;
  color: #64748b;
  font-size: 0.875rem;
  z-index: 10;
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .login-content {
    flex-direction: column;
    gap: 40px;
    text-align: center;
  }
  
  .brand-section {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .brand-section h1 {
    font-size: 2.5rem;
  }
}
</style>
