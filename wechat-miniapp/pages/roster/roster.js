// pages/roster/roster.js
// 排班页面 - 日历视图展示个人排班
const app = getApp()

Page({
    data: {
        // 日历相关
        showCalendar: true,
        currentDate: new Date().getTime(),
        minDate: new Date(new Date().getFullYear(), new Date().getMonth() - 1, 1).getTime(),
        maxDate: new Date(new Date().getFullYear(), new Date().getMonth() + 2, 0).getTime(),
        
        // 排班数据
        rosters: {},         // 按日期索引的排班数据
        selectedDate: '',    // 当前选中的日期
        selectedRoster: null, // 选中日期的排班详情
        
        // 班次颜色映射
        shiftColors: {
            '早班': '#67C23A',
            '中班': '#E6A23C',
            '大夜班': '#F56C6C',
            'default': '#409EFF'
        },
        
        // 加载状态
        loading: false
    },

    onLoad() {
        this.loadRosters()
    },

    onShow() {
        // 页面显示时刷新数据
        this.loadRosters()
    },

    // 加载排班数据
    loadRosters() {
        const now = new Date()
        const startDate = this.formatDate(new Date(now.getFullYear(), now.getMonth() - 1, 1))
        const endDate = this.formatDate(new Date(now.getFullYear(), now.getMonth() + 2, 0))
        
        this.setData({ loading: true })
        
        app.request({
            url: `/rosters/calendar/?start_date=${startDate}&end_date=${endDate}&user_id=${app.globalData.userInfo?.id || ''}`,
            method: 'GET'
        }).then(data => {
            // 处理返回的排班数据
            const rosters = {}
            for (const [date, rosterList] of Object.entries(data)) {
                if (rosterList.length > 0) {
                    rosters[date] = rosterList[0]  // 每天只有一个排班
                }
            }
            this.setData({ 
                rosters,
                loading: false 
            })
            
            // 如果有今天的排班，显示详情
            const today = this.formatDate(new Date())
            if (rosters[today]) {
                this.setData({
                    selectedDate: today,
                    selectedRoster: rosters[today]
                })
            }
        }).catch(err => {
            console.error('加载排班数据失败:', err)
            this.setData({ loading: false })
            wx.showToast({
                title: '加载失败',
                icon: 'error'
            })
        })
    },

    // 日期点击事件
    onSelectDate(e) {
        const date = this.formatDate(new Date(e.detail))
        const roster = this.data.rosters[date] || null
        
        this.setData({
            selectedDate: date,
            selectedRoster: roster
        })
    },

    // 格式化日期为 YYYY-MM-DD
    formatDate(date) {
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
    },

    // 自定义日历日期格式化器 - 用于显示班次标识
    formatter(day) {
        const dateStr = this.formatDate(new Date(day.date))
        const roster = this.data.rosters[dateStr]
        
        if (roster) {
            day.bottomInfo = roster.shift_name || '有班'
            day.className = 'has-roster'
        }
        
        return day
    },

    // 跳转到打卡页面
    goToPunch() {
        wx.switchTab({ url: '/pages/punch/punch' })
    },

    // 刷新数据
    onPullDownRefresh() {
        this.loadRosters()
        wx.stopPullDownRefresh()
    }
})
