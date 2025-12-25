import request from '@/utils/request'

// 通知列表
export function getNotifyList() {
	return request({
		url: '/notify',
		headers: {
			isMask: false
		},
		method: 'get'
	})
}

// 新增/测试通知
export function postAddNotify(notify) {
	return request({
		url: '/notify',
		headers: {
			isMask: false
		},
		method: 'post',
		data: {
			notify
		}
	})
}

// 修改通知
export function putEditNotify(notify) {
	return request({
		url: '/notify',
		headers: {
			isMask: false
		},
		method: 'put',
		data: {
			notify
		}
	})
}

// 启用/禁用通知
export function putEnableNotify(notifyId, enable) {
	return request({
		url: '/notify',
		headers: {
			isMask: false
		},
		method: 'put',
		data: {
			notifyId,
			enable
		}
	})
}

// 删除通知
export function delNotify(notifyId) {
	return request({
		url: '/notify',
		headers: {
			isMask: false
		},
		method: 'delete',
		data: {
			notifyId
		}
	})
}

// 获取消息记录列表
export function getNotifyLogList(params) {
	return request({
		url: '/notify',
		headers: {
			isMask: false
		},
		method: 'get',
		params: params
	})
}

// 删除消息记录
export function deleteNotifyLog(logIds) {
	return request({
		url: '/notify',
		headers: {
			isMask: false
		},
		method: 'delete',
		data: {
			logIds
		}
	})
}

// 重新发送通知
export function resendNotify(logId) {
	return request({
		url: '/notify',
		headers: {
			isMask: false
		},
		method: 'post',
		data: {
			logId,
			resend: true
		}
	})
}

// 批量重新发送通知
export function batchResendNotify(logIds) {
	return request({
		url: '/notify',
		headers: {
			isMask: false
		},
		method: 'post',
		data: {
			logIds,
			resend: true
		}
	})
}

// 导出消息记录
export function exportNotifyLog(params) {
	return request({
		url: '/notify',
		headers: {
			isMask: false
		},
		method: 'get',
		params: {
			export: true,
			...params
		}
	})
}