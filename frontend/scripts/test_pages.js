#!/usr/bin/env node

/**
 * 前端页面 API 测试脚本
 * 
 * 用途：验证后端 API 端点的功能完整性
 * 运行方式：node scripts/test_pages.js
 * 
 * 依赖安装：
 * npm install axios chalk
 */

import axios from 'axios'
import chalk from 'chalk'

// 配置
const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:8000/api/v1'
const TEST_USERNAME = process.env.TEST_USERNAME || 'admin'
const TEST_PASSWORD = process.env.TEST_PASSWORD || 'admin123'

// 测试结果统计
const results = {
  passed: 0,
  failed: 0,
  total: 0,
  errors: [],
}

// 认证 Token
let authToken = ''

/**
 * 打印测试结果
 */
function printResult(name, passed, error = null, data = null) {
  results.total++
  if (passed) {
    results.passed++
    console.log(`  ${chalk.green('✓')} ${name}`)
  } else {
    results.failed++
    const errorInfo = error ? {
      message: error.message || String(error),
      response: error.response?.data,
      status: error.response?.status
    } : null
    results.errors.push({ name, error: errorInfo })
    console.log(`  ${chalk.red('✗')} ${name}`)
    if (errorInfo) {
      console.log(`    ${chalk.red('错误：')} ${errorInfo.message}`)
      if (errorInfo.status) {
        console.log(`    ${chalk.red('状态码：')} ${errorInfo.status}`)
      }
    }
  }
}

/**
 * 打印分隔线
 */
function printSection(title) {
  console.log(`\n${chalk.bold.cyan('='.repeat(60))}`)
  console.log(chalk.bold.cyan(title))
  console.log(chalk.bold.cyan('='.repeat(60)))
}

/**
 * 打印摘要
 */
function printSummary() {
  console.log(`\n${chalk.bold('测试摘要：')}`)
  console.log(`  总测试数：${results.total}`)
  console.log(`  ${chalk.green('通过：')} ${results.passed}`)
  console.log(`  ${chalk.red('失败：')} ${results.failed}`)
  console.log(`  通过率：${((results.passed / results.total) * 100).toFixed(1)}%`)
  
  if (results.errors.length > 0) {
    console.log(`\n${chalk.bold.red('失败详情：')}`)
    results.errors.forEach(({ name, error }) => {
      console.log(`  ${chalk.red('✗')} ${name}`)
      if (error) {
        console.log(`    ${chalk.red('错误：')} ${error.message || String(error)}`)
        if (error.status) {
          console.log(`    ${chalk.red('状态码：')} ${error.status}`)
        }
        if (error.response) {
          console.log(`    ${chalk.red('响应：')} ${JSON.stringify(error.response)}`)
        }
      }
    })
  }
}

/**
 * 测试：健康检查
 */
async function testHealthCheck() {
  printSection('1. 健康检查 API')
  
  try {
    const response = await axios.get(`${BASE_URL}/health`)
    printResult(
      'GET /api/v1/health - 健康检查',
      response.status === 200 && response.data.status === 'healthy',
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/health - 健康检查', false, error)
  }
}

/**
 * 测试：认证 API
 */
async function testAuth() {
  printSection('2. 认证 API')
  
  // 2.1 成功登录
  try {
    const response = await axios.post(`${BASE_URL}/auth/login`, {
      username: TEST_USERNAME,
      password: TEST_PASSWORD,
    })
    
    const passed = response.status === 200 && response.data.access_token
    printResult(
      'POST /api/v1/auth/login - 成功登录',
      passed,
      null,
      response.data
    )
    
    if (passed) {
      authToken = response.data.access_token
      console.log(`    ${chalk.gray('Token: ')}${chalk.gray(authToken.substring(0, 20) + '...')}`)
    }
  } catch (error) {
    printResult('POST /api/v1/auth/login - 成功登录', false, error)
  }
  
  // 2.2 失败登录（错误密码）
  try {
    await axios.post(`${BASE_URL}/auth/login`, {
      username: TEST_USERNAME,
      password: 'wrongpassword',
    })
    printResult('POST /api/v1/auth/login - 失败登录（错误密码）', false, new Error('应该返回 401'))
  } catch (error) {
    printResult(
      'POST /api/v1/auth/login - 失败登录（错误密码）',
      error.response?.status === 401,
      error
    )
  }
  
  // 2.3 失败登录（空用户名）
  try {
    await axios.post(`${BASE_URL}/auth/login`, {
      username: '',
      password: TEST_PASSWORD,
    })
    printResult('POST /api/v1/auth/login - 失败登录（空用户名）', false, new Error('应该返回 400 或 422'))
  } catch (error) {
    printResult(
      'POST /api/v1/auth/login - 失败登录（空用户名）',
      [400, 422].includes(error.response?.status),
      error
    )
  }
}

/**
 * 测试：用户 API
 */
async function testUsers() {
  printSection('3. 用户管理 API')
  
  if (!authToken) {
    console.log(chalk.yellow('  ⚠ 跳过用户 API 测试（未获取到 Token）'))
    return
  }
  
  const headers = { Authorization: `Bearer ${authToken}` }
  
  // 3.1 获取当前用户信息
  try {
    const response = await axios.get(`${BASE_URL}/users/me`, { headers })
    printResult(
      'GET /api/v1/users/me - 获取当前用户信息',
      response.status === 200,
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/users/me - 获取当前用户信息', false, error)
  }
  
  // 3.2 获取用户列表
  try {
    const response = await axios.get(`${BASE_URL}/users`, { headers })
    const passed = response.status === 200 && (Array.isArray(response.data) || (response.data && response.data.items))
    printResult(
      'GET /api/v1/users - 获取用户列表',
      passed,
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/users - 获取用户列表', false, error)
  }
  
  // 3.3 搜索用户
  try {
    const response = await axios.get(`${BASE_URL}/users?search=admin`, { headers })
    printResult(
      'GET /api/v1/users?search=admin - 搜索用户',
      response.status === 200,
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/users?search=admin - 搜索用户', false, error)
  }
  
  // 3.4 无认证访问
  try {
    await axios.get(`${BASE_URL}/users`)
    printResult('GET /api/v1/users - 无认证访问', false, new Error('应该返回 401'))
  } catch (error) {
    printResult(
      'GET /api/v1/users - 无认证访问',
      error.response?.status === 401,
      error
    )
  }
}

/**
 * 测试：角色 API
 */
async function testRoles() {
  printSection('4. 角色权限 API')
  
  if (!authToken) {
    console.log(chalk.yellow('  ⚠ 跳过角色 API 测试（未获取到 Token）'))
    return
  }
  
  const headers = { Authorization: `Bearer ${authToken}` }
  
  // 4.1 获取角色列表
  try {
    const response = await axios.get(`${BASE_URL}/roles`, { headers })
    printResult(
      'GET /api/v1/roles - 获取角色列表',
      response.status === 200 && Array.isArray(response.data),
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/roles - 获取角色列表', false, error)
  }
  
  // 4.2 获取权限列表
  try {
    const response = await axios.get(`${BASE_URL}/permissions`, { headers })
    printResult(
      'GET /api/v1/permissions - 获取权限列表',
      response.status === 200 && Array.isArray(response.data),
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/permissions - 获取权限列表', false, error)
  }
}

/**
 * 测试：客户 API
 */
async function testCustomers() {
  printSection('5. 客户管理 API')
  
  if (!authToken) {
    console.log(chalk.yellow('  ⚠ 跳过客户 API 测试（未获取到 Token）'))
    return
  }
  
  const headers = { Authorization: `Bearer ${authToken}` }
  
  // 5.1 获取客户列表
  try {
    const response = await axios.get(`${BASE_URL}/customers`, { headers })
    printResult(
      'GET /api/v1/customers - 获取客户列表',
      response.status === 200 && response.data.data && Array.isArray(response.data.data),
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/customers - 获取客户列表', false, error)
  }
  
  // 5.2 搜索客户
  try {
    const response = await axios.get(`${BASE_URL}/customers?search=test`, { headers })
    printResult(
      'GET /api/v1/customers?search=test - 搜索客户',
      response.status === 200,
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/customers?search=test - 搜索客户', false, error)
  }
  
  // 5.3 筛选客户（按状态）
  try {
    const response = await axios.get(`${BASE_URL}/customers?status=active`, { headers })
    printResult(
      'GET /api/v1/customers?status=active - 筛选客户',
      response.status === 200,
      null,
      response.data
    )
  } catch (error) {
    // 如果是枚举类型错误，说明后端有问题，但仍然记录为失败
    const isEnumError = error.response?.data?.message?.includes('invalid input value for enum')
    printResult(
      'GET /api/v1/customers?status=active - 筛选客户',
      false,
      isEnumError ? new Error(`数据库枚举类型错误：请检查后端代码中枚举值的使用`) : error
    )
  }
  
  // 5.4 分页测试
  try {
    const response = await axios.get(`${BASE_URL}/customers?page=1&pageSize=10`, { headers })
    printResult(
      'GET /api/v1/customers?page=1&pageSize=10 - 分页测试',
      response.status === 200 && response.data.data,
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/customers?page=1&pageSize=10 - 分页测试', false, error)
  }
  
  // 5.5 获取行业列表
  try {
    const response = await axios.get(`${BASE_URL}/customers/industries`, { headers })
    printResult(
      'GET /api/v1/customers/industries - 获取行业列表',
      response.status === 200 && Array.isArray(response.data),
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/customers/industries - 获取行业列表', false, error)
  }
  
  // 5.6 获取客户等级列表
  try {
    const response = await axios.get(`${BASE_URL}/customers/levels`, { headers })
    printResult(
      'GET /api/v1/customers/levels - 获取客户等级列表',
      response.status === 200 && Array.isArray(response.data),
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/customers/levels - 获取客户等级列表', false, error)
  }
}

/**
 * 测试：Dashboard API
 */
async function testDashboard() {
  printSection('6. Dashboard API')
  
  if (!authToken) {
    console.log(chalk.yellow('  ⚠ 跳过 Dashboard API 测试（未获取到 Token）'))
    return
  }
  
  const headers = { Authorization: `Bearer ${authToken}` }
  
  // 6.1 获取概览数据
  try {
    const response = await axios.get(`${BASE_URL}/dashboard/overview`, { headers })
    printResult(
      'GET /api/v1/dashboard/overview - 获取概览数据',
      response.status === 200 && response.data,
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/dashboard/overview - 获取概览数据', false, error)
  }
  
  // 6.2 获取快速操作
  try {
    const response = await axios.get(`${BASE_URL}/dashboard/quick-actions`, { headers })
    printResult(
      'GET /api/v1/dashboard/quick-actions - 获取快速操作',
      response.status === 200 && Array.isArray(response.data),
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/dashboard/quick-actions - 获取快速操作', false, error)
  }
  
  // 6.3 获取最新动态
  try {
    const response = await axios.get(`${BASE_URL}/dashboard/recent-activities?limit=5`, { headers })
    printResult(
      'GET /api/v1/dashboard/recent-activities?limit=5 - 获取最新动态',
      response.status === 200 && Array.isArray(response.data),
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/dashboard/recent-activities?limit=5 - 获取最新动态', false, error)
  }
}

/**
 * 测试：数据分析 API
 */
async function testAnalytics() {
  printSection('7. 数据分析 API')
  
  if (!authToken) {
    console.log(chalk.yellow('  ⚠ 跳过数据分析 API 测试（未获取到 Token）'))
    return
  }
  
  const headers = { Authorization: `Bearer ${authToken}` }
  
  // 7.1 获取用量趋势
  try {
    const response = await axios.get(`${BASE_URL}/analytics/usage-trend?months=6`, { headers })
    printResult(
      'GET /api/v1/analytics/usage-trend?months=6 - 获取用量趋势',
      response.status === 200 && response.data,
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/analytics/usage-trend?months=6 - 获取用量趋势', false, error)
  }
  
  // 7.2 获取收入预测
  try {
    const response = await axios.get(`${BASE_URL}/analytics/revenue-forecast`, { headers })
    printResult(
      'GET /api/v1/analytics/revenue-forecast - 获取收入预测',
      response.status === 200 && response.data,
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/analytics/revenue-forecast - 获取收入预测', false, error)
  }
  
  // 7.3 获取客户分布
  try {
    const response = await axios.get(`${BASE_URL}/analytics/customer-distribution`, { headers })
    printResult(
      'GET /api/v1/analytics/customer-distribution - 获取客户分布',
      response.status === 200 && response.data,
      null,
      response.data
    )
  } catch (error) {
    printResult('GET /api/v1/analytics/customer-distribution - 获取客户分布', false, error)
  }
}

/**
 * 主函数
 */
async function main() {
  console.log(chalk.bold.cyan('\n╔══════════════════════════════════════════════════════════╗'))
  console.log(chalk.bold.cyan('║          客户运营中台系统 - 前端页面 API 测试                    ║'))
  console.log(chalk.bold.cyan('╚══════════════════════════════════════════════════════════╝'))
  console.log(`\n${chalk.gray('基础 URL：')} ${BASE_URL}`)
  console.log(`${chalk.gray('测试用户：')} ${TEST_USERNAME}`)
  console.log(`${chalk.gray('开始时间：')} ${new Date().toLocaleString('zh-CN')}`)
  
  try {
    // 执行测试
    await testHealthCheck()
    await testAuth()
    await testUsers()
    await testRoles()
    await testCustomers()
    await testDashboard()
    await testAnalytics()
    
    // 打印摘要
    printSummary()
    
    // 退出码
    process.exit(results.failed > 0 ? 1 : 0)
  } catch (error) {
    console.error(chalk.red('\n测试执行失败：'), error)
    process.exit(1)
  }
}

// 运行测试
main()
