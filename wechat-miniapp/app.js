// app.js
App({
    globalData: {
        userInfo: null,
        token: '',
        apiBase: 'http://192.168.2.213:8000/api'  // 远程服务器地址
    },

    onLaunch() {
        // 检查登录状态
        const token = wx.getStorageSync('token')
        if (token) {
            this.globalData.token = token
            this.getUserInfo()
        }
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
                            }
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
                    'Authorization': 'Bearer ' + this.globalData.token
                },
                success: (res) => {
                    if (res.statusCode === 200) {
                        resolve(res.data)
                    } else if (res.statusCode === 401) {
                        // Token过期，重新登录
                        wx.removeStorageSync('token')
                        wx.removeStorageSync('userInfo')
                        this.login()
                        reject(new Error('登录已过期'))
                    } else {
                        reject(new Error(res.data.error || '请求失败'))
                    }
                },
                fail: reject
            })
        })
    }
})
