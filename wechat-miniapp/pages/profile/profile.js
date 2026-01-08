// pages/profile/profile.js
// 个人中心页面 - 用户信息与统计
const app = getApp()

Page({
    data: {
        // 用户信息
        userInfo: {},

        // 统计数据
        stats: {
            thisMonth: {
                workDays: 0,
                overtimeHours: 0,
                overtimePay: 0
            },
            thisQuarter: {
                workDays: 0,
                overtimeHours: 0,
                overtimePay: 0
            }
        },

        // 当前统计维度
        statsPeriod: 'month', // 'month' 或 'quarter'

        // 功能菜单
        menuItems: [
            { icon: '📋', title: '我的排班', url: '/pages/roster/roster', type: 'tab' },
            { icon: '⏰', title: '打卡记录', url: '/pages/punch/punch', type: 'tab' },
            { icon: '📝', title: '加班记录', url: '/pages/overtime/overtime', type: 'tab' },
            { icon: '🔔', title: '消息通知', url: '', type: 'page', disabled: true },
            { icon: '⚙️', title: '设置', url: '', type: 'page', disabled: true }
        ],

        loading: false
    },

    onLoad() {
        this.loadUserInfo()
        this.loadStats()
    },

    onShow() {
        // 页面显示时刷新数据
        this.loadUserInfo()
        this.loadStats()
    },

    // 加载用户信息
    loadUserInfo() {
        const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo')
        if (userInfo) {
            this.setData({ userInfo })
        }
    },

    // 加载统计数据
    loadStats() {
        // 开发模式使用模拟数据
        if (app.globalData.devMode) {
            this.setData({
                stats: {
                    thisMonth: {
                        workDays: 22,
                        overtimeHours: 16,
                        overtimePay: 480
                    },
                    thisQuarter: {
                        workDays: 65,
                        overtimeHours: 48,
                        overtimePay: 1440
                    }
                }
            })
            return
        }

        this.loadMonthStats()
        this.loadQuarterStats()
    },

    // 加载本月统计
    loadMonthStats() {
        const now = new Date()
        const year = now.getFullYear()
        const month = now.getMonth() + 1
        const startDate = `${year}-${String(month).padStart(2, '0')}-01`
        const endDate = `${year}-${String(month).padStart(2, '0')}-${new Date(year, month, 0).getDate()}`

        this.fetchStats(startDate, endDate, 'thisMonth')
    },

    // 加载本季度统计
    loadQuarterStats() {
        const now = new Date()
        const year = now.getFullYear()
        const quarter = Math.floor(now.getMonth() / 3)
        const startMonth = quarter * 3 + 1
        const endMonth = quarter * 3 + 3

        const startDate = `${year}-${String(startMonth).padStart(2, '0')}-01`
        const endDate = `${year}-${String(endMonth).padStart(2, '0')}-${new Date(year, endMonth, 0).getDate()}`

        this.fetchStats(startDate, endDate, 'thisQuarter')
    },

    // 获取统计数据
    fetchStats(startDate, endDate, period) {
        app.request({
            url: `/overtime/statistics/?start_date=${startDate}&end_date=${endDate}`,
            method: 'GET'
        }).then(data => {
            if (data && data.length > 0) {
                // 找到当前用户的统计数据
                const userId = this.data.userInfo.id
                const myStats = data.find(d => d.user__id === userId) || data[0]

                this.setData({
                    [`stats.${period}`]: {
                        workDays: Math.round((myStats.total_hours || 0) / 8),
                        overtimeHours: myStats.total_hours || 0,
                        overtimePay: myStats.total_pay || 0
                    }
                })
            }
        }).catch(err => {
            console.error('加载统计数据失败:', err)
        })
    },

    // 切换统计周期
    switchStatsPeriod(e) {
        const period = e.currentTarget.dataset.period
        this.setData({ statsPeriod: period })
    },

    // 菜单点击
    onMenuTap(e) {
        const item = e.currentTarget.dataset.item

        if (item.disabled) {
            wx.showToast({ title: '功能开发中', icon: 'none' })
            return
        }

        if (item.type === 'tab') {
            wx.switchTab({ url: item.url })
        } else {
            wx.navigateTo({ url: item.url })
        }
    },

    // 登录
    goLogin() {
        app.login().then(data => {
            if (data.user) {
                this.setData({ userInfo: data.user })
                this.loadStats()
            }
        }).catch(err => {
            console.error('登录失败:', err)
            wx.showToast({ title: err.message || '登录失败', icon: 'none' })
        })
    },

    // 退出登录
    logout() {
        wx.showModal({
            title: '确认退出',
            content: '确定要退出登录吗？',
            success: (res) => {
                if (res.confirm) {
                    // 清除本地存储
                    wx.removeStorageSync('token')
                    wx.removeStorageSync('userInfo')

                    // 清除全局数据
                    app.globalData.token = ''
                    app.globalData.userInfo = null

                    // 开发模式重新设置模拟用户
                    if (app.globalData.devMode) {
                        app.setMockUser()
                        this.loadUserInfo()
                        this.loadStats()
                    } else {
                        // 生产模式：清空页面数据
                        this.setData({
                            userInfo: {},
                            stats: {
                                thisMonth: { workDays: 0, overtimeHours: 0, overtimePay: 0 },
                                thisQuarter: { workDays: 0, overtimeHours: 0, overtimePay: 0 }
                            }
                        })
                    }

                    wx.showToast({ title: '已退出登录', icon: 'success' })
                }
            }
        })
    },

    // 下拉刷新
    onPullDownRefresh() {
        this.loadUserInfo()
        this.loadStats()
        wx.stopPullDownRefresh()
    }
})
