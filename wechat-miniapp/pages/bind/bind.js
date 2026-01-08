// pages/bind/bind.js
// 账号绑定页面 - 首次登录绑定工号
const app = getApp()

Page({
    data: {
        // 从登录页传来的openid
        openid: '',

        // 表单数据
        empCode: '',
        phone: '',

        // 状态
        loading: false
    },

    onLoad(options) {
        // 获取openid参数
        if (options.openid) {
            this.setData({ openid: options.openid })
        } else {
            wx.showToast({ title: '参数错误', icon: 'error' })
            setTimeout(() => wx.navigateBack(), 1500)
        }
    },

    // 输入工号
    onEmpCodeInput(e) {
        this.setData({ empCode: e.detail.value })
    },

    // 输入手机号
    onPhoneInput(e) {
        this.setData({ phone: e.detail.value })
    },

    // 提交绑定
    submitBind() {
        const { openid, empCode, phone } = this.data

        // 表单验证
        if (!empCode.trim()) {
            wx.showToast({ title: '请输入工号', icon: 'none' })
            return
        }

        this.setData({ loading: true })

        app.request({
            url: '/users/wechat_bind/',
            method: 'POST',
            data: {
                openid: openid,
                emp_code: empCode.trim(),
                phone: phone.trim() || ''
            }
        }).then(res => {
            wx.showToast({
                title: '绑定成功',
                icon: 'success'
            })

            // 保存用户信息
            if (res.user) {
                wx.setStorageSync('userInfo', res.user)
                app.globalData.userInfo = res.user
            }

            // 跳转到首页
            setTimeout(() => {
                wx.switchTab({ url: '/pages/index/index' })
            }, 1500)

        }).catch(err => {
            console.error('绑定失败:', err)
            wx.showToast({
                title: err.message || '绑定失败',
                icon: 'error'
            })
        }).finally(() => {
            this.setData({ loading: false })
        })
    },

    // 返回上一页
    goBack() {
        wx.navigateBack()
    }
})
