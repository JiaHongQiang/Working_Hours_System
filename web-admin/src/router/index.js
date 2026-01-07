import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layouts/Layout.vue'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Login.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/',
        component: Layout,
        redirect: '/dashboard',
        children: [
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('@/views/Dashboard.vue'),
                meta: { title: '首页' }
            },
            {
                path: 'user',
                name: 'User',
                component: () => import('@/views/User/Index.vue'),
                meta: { title: '人员管理' }
            },
            {
                path: 'roster',
                name: 'Roster',
                component: () => import('@/views/Roster/Index.vue'),
                meta: { title: '排班管理' }
            },
            {
                path: 'attendance',
                name: 'Attendance',
                component: () => import('@/views/Attendance/Index.vue'),
                meta: { title: '考勤管理' }
            },
            {
                path: 'overtime',
                name: 'Overtime',
                component: () => import('@/views/Overtime/Index.vue'),
                meta: { title: '加班审批' }
            },
            {
                path: 'report',
                name: 'Report',
                component: () => import('@/views/Report/Index.vue'),
                meta: { title: '统计报表' }
            },
            {
                path: 'settings',
                name: 'Settings',
                component: () => import('@/views/Settings/Index.vue'),
                meta: { title: '系统settings' }
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')

    if (to.matched.some(record => record.meta.requiresAuth !== false)) {
        if (!token && to.path !== '/login') {
            next('/login')
        } else {
            next()
        }
    } else {
        next()
    }
})

export default router
