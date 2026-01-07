// pages/index/index.js
const app = getApp()

Page({
    data: {
        userInfo: {},
        stats: {
            attendanceDays: 0,
            overtimeHours: 0,
            overtimePay: 0
        }
    },

    onLoad() {
        this.loadUserInfo()
        this.loadStats()
    },

    onShow() {
        // 页面显示时刷新数据
        this.loadStats()
    },

    loadUserInfo() {
        const userInfo = app.globalData.userInfo || wx.getStorageSync('userInfo')
        if (userInfo) {
            this.setData({ userInfo })
        } else {
            // 未登录，跳转到登录页面
            app.login()
        }
    },

    loadStats() {
        // 加载统计数据
        const now = new Date()
        const year = now.getFullYear()
        const month = String(now.getMonth() + 1).padStart(2, '0')
        const startDate = `${year}-${month}-01`
        const endDate = `${year}-${month}-${new Date(year, month, 0).getDate()}`

        app.request({
            url: `/overtime/statistics/?start_date=${startDate}&end_date=${endDate}`,
            method: 'GET'
        }).then(data => {
            if (data && data.length > 0) {
                const myStats = data[0]  // 假设只返回当前用户的数据
                this.setData({
                    stats: {
                        attendanceDays: myStats.total_hours / 8 || 0,
                        overtimeHours: myStats.total_hours || 0,
                        overtimePay: myStats.total_pay || 0
                    }
                })
            }
        }).catch(err => {
            console.error('加载统计数据失败:', err)
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
