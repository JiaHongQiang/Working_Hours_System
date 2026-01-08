// pages/punch/punch.js
// 打卡页面 - 定位打卡功能
const app = getApp()

Page({
    data: {
        // 当前时间
        currentTime: '',
        currentDate: '',
        weekDay: '',

        // 定位相关
        latitude: 0,
        longitude: 0,
        locationName: '',
        inGeofence: false,      // 是否在地理围栏内
        distance: 0,            // 距离医院的距离
        locationLoading: false,
        locationFailed: false,

        // 今日排班
        todayRoster: null,

        // 打卡记录
        punchRecords: [],

        // 地理围栏配置（从后端获取）
        hospitalName: '医院',
        hospitalLat: 39.9042,  // 医院纬度（默认值，会被后端配置覆盖）
        hospitalLng: 116.4074, // 医院经度
        geofenceRadius: 200,   // 围栏半径（米）
        configLoaded: false
    },

    onLoad() {
        this.updateTime()
        // 每秒更新时间
        this.timeInterval = setInterval(() => {
            this.updateTime()
        }, 1000)

        // 先获取打卡配置，再获取位置
        this.loadPunchConfig().then(() => {
            this.getLocation()
        })
        this.loadTodayData()
    },

    onUnload() {
        if (this.timeInterval) {
            clearInterval(this.timeInterval)
        }
    },

    onShow() {
        this.loadTodayData()
    },

    // 加载打卡配置（从后端获取）
    loadPunchConfig() {
        return new Promise((resolve) => {
            app.request({
                url: '/config/punch_config/',
                method: 'GET',
                skipAuth: true  // 公开接口，无需认证
            }).then(config => {
                console.log('打卡配置:', config)
                this.setData({
                    hospitalName: config.hospital_name || '医院',
                    hospitalLat: config.hospital_latitude || 39.9042,
                    hospitalLng: config.hospital_longitude || 116.4074,
                    geofenceRadius: config.geofence_radius || 200,
                    configLoaded: true
                })
                resolve()
            }).catch(err => {
                console.error('加载打卡配置失败:', err)
                // 使用默认配置
                this.setData({ configLoaded: true })
                resolve()
            })
        })
    },

    // 更新当前时间显示
    updateTime() {
        const now = new Date()
        const hours = String(now.getHours()).padStart(2, '0')
        const minutes = String(now.getMinutes()).padStart(2, '0')
        const seconds = String(now.getSeconds()).padStart(2, '0')

        const weekDays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']

        this.setData({
            currentTime: `${hours}:${minutes}:${seconds}`,
            currentDate: `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`,
            weekDay: weekDays[now.getDay()]
        })
    },

    // 获取当前位置
    getLocation() {
        this.setData({ locationLoading: true, locationFailed: false })

        wx.getLocation({
            type: 'gcj02',
            success: (res) => {
                const { latitude, longitude } = res
                const distance = this.calculateDistance(latitude, longitude)
                const inGeofence = distance <= this.data.geofenceRadius

                this.setData({
                    latitude,
                    longitude,
                    distance: Math.round(distance),
                    inGeofence,
                    locationName: inGeofence ? '医院范围内' : `距离医院 ${Math.round(distance)}米`,
                    locationLoading: false,
                    locationFailed: false
                })
            },
            fail: (err) => {
                console.error('获取位置失败:', err)
                this.setData({
                    locationLoading: false,
                    locationFailed: true,
                    locationName: '获取位置失败，请点击刷新',
                    inGeofence: false
                })

                // 提示用户授权
                wx.showModal({
                    title: '定位失败',
                    content: '无法获取您的位置，请确保已授权位置权限。是否前往设置？',
                    success: (res) => {
                        if (res.confirm) {
                            wx.openSetting()
                        }
                    }
                })
            }
        })
    },

    // 计算两点间距离（单位：米）
    calculateDistance(lat1, lng1) {
        const lat2 = this.data.hospitalLat
        const lng2 = this.data.hospitalLng

        const rad = Math.PI / 180
        const dLat = (lat2 - lat1) * rad
        const dLng = (lng2 - lng1) * rad

        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * rad) * Math.cos(lat2 * rad) *
            Math.sin(dLng / 2) * Math.sin(dLng / 2)

        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
        return 6371000 * c  // 地球半径 * 弧度 = 米
    },

    // 加载今日数据
    loadTodayData() {
        // 开发模式使用模拟数据
        if (app.globalData.devMode) {
            this.loadMockData()
            return
        }

        // 加载今日排班
        const today = this.data.currentDate
        app.request({
            url: `/attendance/my_records/?date=${today}`,
            method: 'GET'
        }).then(data => {
            this.setData({ punchRecords: data || [] })
        }).catch(err => {
            console.error('加载打卡记录失败:', err)
        })
    },

    // 加载模拟数据（开发模式）
    loadMockData() {
        this.setData({
            todayRoster: {
                shift_name: '早班',
                start_time: '08:00',
                end_time: '16:00'
            },
            punchRecords: [
                { id: 1, type: 'IN', time: '07:58:23', status: 'NORMAL' }
            ]
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

    // 执行打卡
    doPunch(type) {
        // 检查是否已获取位置
        if (this.data.locationFailed || (this.data.latitude === 0 && this.data.longitude === 0)) {
            wx.showModal({
                title: '无法打卡',
                content: '未能获取您的位置，请先点击"刷新位置"按钮获取定位',
                showCancel: false
            })
            return
        }

        if (!this.data.inGeofence) {
            wx.showModal({
                title: '位置异常',
                content: `您当前距离医院${this.data.distance}米，超出打卡范围（${this.data.geofenceRadius}米）。确定要打卡吗？`,
                success: (res) => {
                    if (res.confirm) {
                        this.submitPunch(type)
                    }
                }
            })
        } else {
            this.submitPunch(type)
        }
    },

    // 提交打卡
    submitPunch(type) {
        // 开发模式模拟打卡
        if (app.globalData.devMode) {
            wx.showToast({ title: type === 'IN' ? '上班打卡成功' : '下班打卡成功', icon: 'success' })
            const now = new Date()
            const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
            const newRecord = {
                id: Date.now(),
                type: type,
                time: timeStr,
                status: 'NORMAL'
            }
            this.setData({
                punchRecords: [...this.data.punchRecords, newRecord]
            })
            return
        }

        app.request({
            url: '/attendance/punch/',
            method: 'POST',
            data: {
                type: type,
                latitude: this.data.latitude,
                longitude: this.data.longitude
            }
        }).then(res => {
            wx.showToast({
                title: type === 'IN' ? '上班打卡成功' : '下班打卡成功',
                icon: 'success'
            })
            this.loadTodayData()
        }).catch(err => {
            console.error('打卡失败:', err)
            wx.showToast({ title: err.message || '打卡失败', icon: 'error' })
        })
    },

    // 刷新位置
    refreshLocation() {
        this.getLocation()
    },

    // 下拉刷新
    onPullDownRefresh() {
        this.getLocation()
        this.loadTodayData()
        wx.stopPullDownRefresh()
    }
})
