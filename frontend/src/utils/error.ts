import { message } from 'ant-design-vue'

/**
 * 统一处理API错误
 * @param error 错误对象
 * @param defaultMessage 默认错误消息
 */
export const handleError = (error: any, defaultMessage = '操作失败') => {
  const errorMessage = error?.response?.data?.error || error?.message || defaultMessage
  message.error(errorMessage)
  console.error('操作错误:', error)
}
