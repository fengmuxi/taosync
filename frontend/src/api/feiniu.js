import request from '@/utils/request'

// 飞牛配置列表
export function getFeiniuList() {
	return request({
		url: '/feiniu',
		headers: {
			isMask: false
		},
		method: 'get'
	})
}

// 新增飞牛配置
export function postAddFeiniu(feiniu) {
	return request({
		url: '/feiniu',
		headers: {
			isMask: false
		},
		method: 'post',
		data: {
			feiniu
		}
	})
}

// 修改飞牛配置
export function putEditFeiniu(feiniu) {
	return request({
		url: '/feiniu',
		headers: {
			isMask: false
		},
		method: 'put',
		data: {
			feiniu
		}
	})
}

// 删除飞牛配置
export function delFeiniu(feiniuId) {
	return request({
		url: '/feiniu',
		headers: {
			isMask: false
		},
		method: 'delete',
		data: {
			id: feiniuId
		}
	})
}

// 获取飞牛媒体库列表
export function getFeiniuMediaLibraries(feiniuId) {
	return request({
		url: '/feiniu/mediaLibraries',
		headers: {
			isMask: false
		},
		method: 'get',
		params: {
			id: feiniuId
		}
	})
}

// 获取飞牛刷新任务列表
export function getFeiniuRefreshTasks(filters = {}, page = 1, pageSize = 10) {
	return request({
		url: '/feiniu/refreshTasks',
		headers: {
			isMask: false
		},
		method: 'get',
		params: {
			...filters,
			page,
			pageSize
		}
	})
}

// 获取飞牛刷新任务数量
export function getFeiniuRefreshTaskCount(filters = {}) {
	return request({
		url: '/feiniu/refreshTaskCount',
		headers: {
			isMask: false
		},
		method: 'get',
		params: {
			...filters
		}
	})
}

// 重试飞牛刷新任务
export function retryFeiniuRefreshTask(taskId) {
	return request({
		url: '/feiniu/retryRefreshTask',
		headers: {
			isMask: false
		},
		method: 'put',
		data: {
			id: taskId
		}
	})
}

// 删除飞牛刷新任务
export function deleteFeiniuRefreshTask(taskId) {
	return request({
		url: '/feiniu/refreshTask',
		headers: {
			isMask: false
		},
		method: 'delete',
		data: {
			id: taskId
		}
	})
}
