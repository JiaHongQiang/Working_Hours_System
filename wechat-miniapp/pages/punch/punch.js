// pages/punch/punch.js
// 打卡页面 - 定位打卡功能
const app = getApp()

Page({
    data: {
        // 当前时间
        currentTime: '--:--:--',
        currentDate: '',

        // 定位信息
        latitude: null,
        longitude: null,
        address: '获取位置中...',
        isInGeofence: false,
        distance: 0,

        // 今日打卡状态
        hasPunchedIn: false,
        hasPunchedOut: false,
        punchInTime: '',
        punchOutTime: '',

        // 今日记录
        todayRecords: [],

        // 今日排班
        todayRoster: null,

        // 状态
        loading: false,
        locationError: false,

        // 医院位置配置（应从后端获取）
        hospitalLocation: {
            latitude: 39.9042,
            longitude: 116.4074,
            radius: 200  // 允许打卡半径(米)
        }
    },

    // 定时器ID
    timeIntervalId: null,

    onLoad() {
        this.startClock()
        this.getLocation()
        this.loadTodayData()
    },

    onShow() {
        this.loadTodayData()
    },

    onUnload() {
        // 清除定时器
        if (this.timeIntervalId) {
            clearInterval(this.timeIntervalId)
        }
    },

    // 启动实时时钟
    startClock() {
        const updateTime = () => {
            const now = new Date()
            const time = now.toLocaleTimeString('zh-CN', { hour12: false })
            const date = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
            this.setData({
                currentTime: time,
                currentDate: date
            })
        }
        updateTime()
        this.timeIntervalId = setInterval(updateTime, 1000)
    },

    // 获取当前位置
    getLocation() {
        this.setData({ locationError: false })

        wx.getLocation({
            type: 'gcj02',
            success: (res) => {
                const distance = this.calculateDistance(
                    res.latitude,
                    res.longitude,
                    this.data.hospitalLocation.latitude,
                    this.data.hospitalLocation.longitude
                )

                this.setData({
                    latitude: res.latitude,
                    longitude: res.longitude,
                    distance: Math.round(distance),
                    isInGeofence: distance <= this.data.hospitalLocation.radius
                })

                // 逆地理编码获取地址（可选）
                this.reverseGeocoding(res.latitude, res.longitude)
            },
            fail: (err) => {
                console.error('获取位置失败:', err)
                this.setData({
                    locationError: true,
                    address: '位置获取失败，请检查权限设置'
                })
                wx.showToast({
                    title: '请开启位置权限',
                    icon: 'none'
                })
            }
        })
    },

    // 计算两点距离（米）
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371000 // 地球半径(米)
        const dLat = this.toRad(lat2 - lat1)
        const dLon = this.toRad(lon2 - lon1)
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2)
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
        return R * c
    },

    toRad(deg) {
        return deg * (Math.PI / 180)
    },

    // 逆地理编码
    reverseGeocoding(lat, lng) {
        // 这里可以调用腾讯地图API获取详细地址
        // 简化处理：直接显示坐标
        this.setData({
            address: this.data.isInGeofence ? '医院范围内' : `距医院${this.data.distance}米`
        })
    },

    // 加载今日数据
    loadTodayData() {
        const today = this.formatDate(new Date())

        // 获取今日打卡记录
        app.request({
            url: `/attendance/my_records/?date=${today}`,
            method: 'GET'
        }).then(records => {
            const punchIn = records.find(r => r.type === 'IN')
            const punchOut = records.find(r => r.type === 'OUT')

            this.setData({
                todayRecords: records,
                hasPunchedIn: !!punchIn,
                hasPunchedOut: !!punchOut,
                punchInTime: punchIn ? this.formatTime(punchIn.punch_time) : '',
                punchOutTime: punchOut ? this.formatTime(punchOut.punch_time) : ''
            })
        }).catch(err => {
            console.error('加载打卡记录失败:', err)
        })

        // 获取今日排班
        app.request({
            url: `/rosters/calendar/?start_date=${today}&end_date=${today}&user_id=${app.globalData.userInfo?.id || ''}`,
            method: 'GET'
        }).then(data => {
            if (data[today] && data[today].length > 0) {
                this.setData({ todayRoster: data[today][0] })
            }
        }).catch(err => {
            console.error('加载排班失败:', err)
        })
    },

    // 执行打卡
    doPunch(type) {
        if (this.data.loading) return

        // 检查位置
        if (!this.data.latitude || !this.data.longitude) {
            wx.showToast({ title: '请先获取位置', icon: 'error' })
            return
        }

        // 检查是否在围栏内
        if (!this.data.isInGeofence) {
            wx.showModal({
                title: '提示',
                content: `您当前距离医院${this.data.distance}米，超出打卡范围(${this.data.hospitalLocation.radius}米)，是否继续？`,
                success: (res) => {
                    if (res.confirm) {
                        this.submitPunch(type)
                    }
                }
            })
            return
        }

        this.submitPunch(type)
    },

    // 提交打卡请求
    submitPunch(type) {
        this.setData({ loading: true })

        app.request({
            url: '/attendance/punch/',
            method: 'POST',
            data: {
                type: type,
                latitude: this.data.latitude,
                longitude: this.data.longitude,
                note: ''
            }
        }).then(res => {
            wx.showToast({
                title: type === 'IN' ? '上班打卡成功' : '下班打卡成功',
                icon: 'success'
            })
            this.loadTodayData()
        }).catch(err => {
            console.error('打卡失败:', err)
            wx.showToast({
                title: err.message || '打卡失败',
                icon: 'error'
            })
        }).finally(() => {
            this.setData({ loading: false })
        })
    },

    // 上班打卡
    punchIn() {
        this.doPunch('IN')
    },

    // 下班打卡
    punchOut() {
        this.doPunch('OUT')
    },

    // 刷新位置
    refreshLocation() {
        this.getLocation()
    },

    // 格式化日期
    formatDate(date) {
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
    },

    // 格式化时间显示
    formatTime(dateTimeStr) {
        if (!dateTimeStr) return ''
        const date = new Date(dateTimeStr)
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
    },

    // 下拉刷新
    onPullDownRefresh() {
        this.getLocation()
        this.loadTodayData()
        wx.stopPullDownRefresh()
    }
})
