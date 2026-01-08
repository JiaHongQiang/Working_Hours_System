// pages/overtime/overtime.js
// 加班页面 - 加班申报与记录查看
const app = getApp()

Page({
    data: {
        // 当前Tab
        activeTab: 'apply', // 'apply' 或 'records'

        // 申报表单
        form: {
            workDate: '',
            actualStart: '',
            actualEnd: '',
            reason: ''
        },

        // 日期/时间选择器
        showDatePicker: false,
        showStartTimePicker: false,
        showEndTimePicker: false,
        minDate: new Date(new Date().getFullYear(), new Date().getMonth(), 1).getTime(),
        maxDate: new Date().getTime(),

        // 加班记录
        records: [],

        // 状态
        loading: false,
        submitting: false
    },

    onLoad() {
        // 默认日期为今天
        this.setData({
            'form.workDate': this.formatDate(new Date())
        })
        this.loadRecords()
    },

    onShow() {
        if (this.data.activeTab === 'records') {
            this.loadRecords()
        }
    },

    // 切换Tab
    switchTab(e) {
        const tab = e.currentTarget.dataset.tab
        this.setData({ activeTab: tab })
        if (tab === 'records') {
            this.loadRecords()
        }
    },

    // ========== 日期时间选择器 ==========

    // 显示日期选择器
    showDateSelector() {
        this.setData({ showDatePicker: true })
    },

    // 确认日期选择
    onConfirmDate(e) {
        const date = new Date(e.detail)
        this.setData({
            'form.workDate': this.formatDate(date),
            showDatePicker: false
        })
    },

    // 关闭日期选择器
    onCloseDatePicker() {
        this.setData({ showDatePicker: false })
    },

    // 显示开始时间选择器
    showStartTimeSelector() {
        this.setData({ showStartTimePicker: true })
    },

    // 确认开始时间
    onConfirmStartTime(e) {
        this.setData({
            'form.actualStart': e.detail,
            showStartTimePicker: false
        })
    },

    // 关闭开始时间选择器
    onCloseStartTimePicker() {
        this.setData({ showStartTimePicker: false })
    },

    // 显示结束时间选择器
    showEndTimeSelector() {
        this.setData({ showEndTimePicker: true })
    },

    // 确认结束时间
    onConfirmEndTime(e) {
        this.setData({
            'form.actualEnd': e.detail,
            showEndTimePicker: false
        })
    },

    // 关闭结束时间选择器
    onCloseEndTimePicker() {
        this.setData({ showEndTimePicker: false })
    },

    // ========== 表单处理 ==========

    // 输入加班原因
    onReasonInput(e) {
        this.setData({ 'form.reason': e.detail.value })
    },

    // 提交申报
    submitApply() {
        const { workDate, actualStart, actualEnd, reason } = this.data.form

        // 表单验证
        if (!workDate) {
            wx.showToast({ title: '请选择日期', icon: 'none' })
            return
        }
        if (!actualStart) {
            wx.showToast({ title: '请选择开始时间', icon: 'none' })
            return
        }
        if (!actualEnd) {
            wx.showToast({ title: '请选择结束时间', icon: 'none' })
            return
        }
        if (!reason.trim()) {
            wx.showToast({ title: '请填写加班原因', icon: 'none' })
            return
        }

        // 开发模式直接成功
        if (app.globalData.devMode) {
            wx.showToast({ title: '申报成功', icon: 'success' })
            this.setData({
                form: {
                    workDate: this.formatDate(new Date()),
                    actualStart: '',
                    actualEnd: '',
                    reason: ''
                }
            })
            setTimeout(() => {
                this.setData({ activeTab: 'records' })
                this.loadRecords()
            }, 1500)
            return
        }

        // 构造datetime格式
        const actualStartDT = `${workDate}T${actualStart}:00`
        const actualEndDT = `${workDate}T${actualEnd}:00`

        this.setData({ submitting: true })

        app.request({
            url: '/overtime/apply/',
            method: 'POST',
            data: {
                work_date: workDate,
                actual_start: actualStartDT,
                actual_end: actualEndDT,
                reason: reason
            }
        }).then(res => {
            wx.showToast({
                title: '申报成功',
                icon: 'success'
            })
            // 重置表单
            this.setData({
                form: {
                    workDate: this.formatDate(new Date()),
                    actualStart: '',
                    actualEnd: '',
                    reason: ''
                }
            })
            // 切换到记录Tab
            setTimeout(() => {
                this.setData({ activeTab: 'records' })
                this.loadRecords()
            }, 1500)
        }).catch(err => {
            console.error('申报失败:', err)
            wx.showToast({
                title: err.message || '申报失败',
                icon: 'error'
            })
        }).finally(() => {
            this.setData({ submitting: false })
        })
    },

    // ========== 记录加载 ==========

    // 加载加班记录
    loadRecords() {
        // 开发模式使用模拟数据
        if (app.globalData.devMode) {
            this.loadMockRecords()
            return
        }

        this.setData({ loading: true })

        // 获取最近3个月的记录
        const now = new Date()
        const startDate = this.formatDate(new Date(now.getFullYear(), now.getMonth() - 3, 1))
        const endDate = this.formatDate(now)

        app.request({
            url: `/overtime/?start_date=${startDate}&end_date=${endDate}`,
            method: 'GET'
        }).then(records => {
            // 按日期倒序排列
            records.sort((a, b) => new Date(b.work_date) - new Date(a.work_date))
            this.setData({ records })
        }).catch(err => {
            console.error('加载记录失败:', err)
        }).finally(() => {
            this.setData({ loading: false })
        })
    },

    // 加载模拟记录（开发模式）
    loadMockRecords() {
        const mockRecords = [
            {
                id: 1,
                work_date: '2026-01-07',
                actual_start: '18:00',
                actual_end: '22:00',
                raw_ot_duration: 4,
                approved_ot_duration: 4,
                multiplier: 1.5,
                final_pay_amount: 120,
                status: 'APPROVED',
                reason: '紧急手术值班'
            },
            {
                id: 2,
                work_date: '2026-01-05',
                actual_start: '17:00',
                actual_end: '21:00',
                raw_ot_duration: 4,
                approved_ot_duration: 4,
                multiplier: 1.5,
                final_pay_amount: 120,
                status: 'PENDING',
                reason: '科室会议'
            }
        ]
        this.setData({ records: mockRecords, loading: false })
    },

    // ========== 工具方法 ==========

    // 格式化日期
    formatDate(date) {
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
    },

    // 下拉刷新
    onPullDownRefresh() {
        this.loadRecords()
        wx.stopPullDownRefresh()
    }
})
