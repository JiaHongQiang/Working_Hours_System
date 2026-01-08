// app.js
App({
    globalData: {
        userInfo: null,
        token: '',
        apiBase: 'http://192.168.2.213:8000/api',  // 远程服务器地址
        // 开发模式：设置为true使用模拟数据，设置为false使用真实API
        devMode: false
    },

    onLaunch() {
        // 开发模式：使用模拟用户数据
        if (this.globalData.devMode) {
            this.setMockUser()
            return
        }

        // 生产模式：检查登录状态
        const token = wx.getStorageSync('token')
        if (token) {
            this.globalData.token = token
            this.getUserInfo()
        }
    },

    // 设置模拟用户（开发测试用）
    setMockUser() {
        const mockUser = {
            id: 1,
            emp_code: 'DEV001',
            full_name: '测试用户',
            admin_dept_name: '测试科室',
            staff_category: 'NURSE',
            staff_category_display: '护士',
            job_title: '护士'
        }
        this.globalData.userInfo = mockUser
        this.globalData.token = 'dev-mock-token'
        wx.setStorageSync('userInfo', mockUser)
        console.log('开发模式：已设置模拟用户', mockUser)
    },

    // 获取用户信息
    getUserInfo() {
        const userInfo = wx.getStorageSync('userInfo')
        if (userInfo) {
            this.globalData.userInfo = userInfo
        }
    },

    // 微信登录
    login() {
        // 开发模式不执行真实登录
        if (this.globalData.devMode) {
            this.setMockUser()
            return Promise.resolve({ user: this.globalData.userInfo })
        }

        return new Promise((resolve, reject) => {
            wx.login({
                success: res => {
                    if (res.code) {
                        // 发送 res.code 到后台换取 openId, sessionKey, unionId
                        this.request({
                            url: '/users/wechat_login/',
                            method: 'POST',
                            data: {
                                code: res.code
                            },
                            skipAuth: true  // 跳过认证检查
                        }).then(data => {
                            if (data.need_bind) {
                                // 需要绑定账号
                                wx.navigateTo({
                                    url: '/pages/bind/bind?openid=' + data.openid
                                })
                            } else {
                                // 已绑定，保存token和用户信息
                                wx.setStorageSync('token', data.token)
                                wx.setStorageSync('userInfo', data.user)
                                this.globalData.token = data.token
                                this.globalData.userInfo = data.user
                                resolve(data)
                            }
                        }).catch(reject)
                    } else {
                        reject(new Error('登录失败：' + res.errMsg))
                    }
                },
                fail: reject
            })
        })
    },

    // 统一请求方法
    request(options) {
        return new Promise((resolve, reject) => {
            wx.request({
                url: this.globalData.apiBase + options.url,
                method: options.method || 'GET',
                data: options.data || {},
                header: {
                    'Content-Type': 'application/json',
                    'Authorization': this.globalData.token ? 'Bearer ' + this.globalData.token : ''
                },
                success: (res) => {
                    if (res.statusCode === 200) {
                        resolve(res.data)
                    } else if (res.statusCode === 401 && !options.skipAuth) {
                        // Token过期，静默处理，不要循环登录
                        console.warn('认证失败，需要重新登录')
                        wx.removeStorageSync('token')
                        wx.removeStorageSync('userInfo')
                        this.globalData.token = ''
                        this.globalData.userInfo = null
                        reject(new Error('请先登录'))
                    } else {
                        const errMsg = res.data?.error || res.data?.detail || '请求失败'
                        reject(new Error(errMsg))
                    }
                },
                fail: (err) => {
                    console.error('请求失败:', err)
                    reject(new Error('网络请求失败'))
                }
            })
        })
    }
})
