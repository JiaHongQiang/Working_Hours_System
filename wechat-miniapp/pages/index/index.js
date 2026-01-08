// pages/index/index.js
// 首页 - 工时统计概览
const app = getApp()

Page({
    data: {
        userInfo: {},
        stats: {
            attendanceDays: 0,
            overtimeHours: 0,
            overtimePay: 0
        },
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

    loadUserInfo() {
        const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo')
        if (userInfo) {
            this.setData({ userInfo })
        } else if (!app.globalData.devMode) {
            // 非开发模式且未登录，尝试登录
            app.login().catch(err => {
                console.error('登录失败:', err)
            })
        }
    },

    loadStats() {
        // 开发模式使用模拟数据
        if (app.globalData.devMode) {
            this.setData({
                stats: {
                    attendanceDays: 22,
                    overtimeHours: 16,
                    overtimePay: 480
                }
            })
            return
        }

        // 生产模式：从API加载统计数据
        const now = new Date()
        const year = now.getFullYear()
        const month = String(now.getMonth() + 1).padStart(2, '0')
        const startDate = `${year}-${month}-01`
        const endDate = `${year}-${month}-${new Date(year, month, 0).getDate()}`

        this.setData({ loading: true })

        app.request({
            url: `/overtime/statistics/?start_date=${startDate}&end_date=${endDate}`,
            method: 'GET'
        }).then(data => {
            if (data && data.length > 0) {
                const myStats = data[0]
                this.setData({
                    stats: {
                        attendanceDays: Math.round((myStats.total_hours || 0) / 8),
                        overtimeHours: myStats.total_hours || 0,
                        overtimePay: myStats.total_pay || 0
                    }
                })
            }
        }).catch(err => {
            console.error('加载统计数据失败:', err)
        }).finally(() => {
            this.setData({ loading: false })
        })
    },

    goToRoster() {
        wx.switchTab({ url: '/pages/roster/roster' })
    },

    goToPunch() {
        wx.switchTab({ url: '/pages/punch/punch' })
    },

    goToOvertime() {
        wx.switchTab({ url: '/pages/overtime/overtime' })
    },

    goToProfile() {
        wx.switchTab({ url: '/pages/profile/profile' })
    }
})
