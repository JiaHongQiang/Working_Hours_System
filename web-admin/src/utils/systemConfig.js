import axios from 'axios'

// 系统配置缓存
let systemConfig = {
    system_name: '考勤系统',
    system_name_en: 'Attendance System'
}

/**
 * 获取系统配置
 * @returns {Promise<Object>} 系统配置对象
 */
export async function fetchSystemConfig() {
    try {
        const response = await axios.get('/api/system/public/')
        systemConfig = response.data
        return systemConfig
    } catch (error) {
        console.error('获取系统配置失败', error)
        return systemConfig  // 返回默认值
    }
}

/**
 * 获取系统配置（同步）
 * @returns {Object} 系统配置对象
 */
export function getSystemConfig() {
    return systemConfig
}

/**
 * 设置系统配置
 * @param {Object} config 配置对象
 */
export function setSystemConfig(config) {
    systemConfig = { ...systemConfig, ...config }
}

export default {
    fetchSystemConfig,
    getSystemConfig,
    setSystemConfig
}
