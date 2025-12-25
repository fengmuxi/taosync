"""
@Author：dr34m
@Date  ：2024/11/21 20:05
"""
from concurrent.futures import ThreadPoolExecutor

from tornado.concurrent import run_on_executor

from controller.baseController import BaseHandler, handle_request
from service.notify import notifyService


class Notify(BaseHandler):
    executor = ThreadPoolExecutor(1)

    @run_on_executor
    @handle_request
    def get(self, req):
        if 'log' in req:
            # 获取消息记录列表
            return notifyService.getNotifyLogList(req)
        elif 'export' in req:
            # 导出消息记录
            return notifyService.getNotifyLogForExport(req)
        else:
            # 获取通知配置列表
            return notifyService.getNotifyList()

    @run_on_executor
    @handle_request
    def post(self, req):
        if 'notify' in req:
            if 'enable' in req['notify']:
                notifyService.addNewNotify(req['notify'])
            else:
                notifyService.testNotify(req['notify'])
        elif 'logIds' in req and 'resend' in req:
            # 批量重新发送通知
            return notifyService.batchResendNotify(req['logIds'])
        elif 'logId' in req and 'resend' in req:
            # 重新发送通知
            return notifyService.resendNotify(req['logId'])
        else:
            # Handle case where neither notify nor resend parameters are provided
            pass

    @run_on_executor
    @handle_request
    def put(self, req):
        if 'notifyId' in req and 'enable' in req:
            notifyService.updateNotifyStatus(req['notifyId'], req['enable'])
        elif 'logId' in req and 'status' in req:
            # 更新消息记录状态
            notifyService.updateNotifyLogStatus(req['logId'], req['status'], req.get('message'))
        elif 'logIds' in req and 'status' in req:
            # 批量更新消息记录状态
            notifyService.batchUpdateNotifyLogStatus(req['logIds'], req['status'], req.get('message'))
        elif 'notify' in req:
            notifyService.editNotify(req['notify'])

    @run_on_executor
    @handle_request
    def delete(self, req):
        if 'logIds' in req:
            # 删除消息记录
            notifyService.deleteNotifyLog(req['logIds'])
        elif 'notifyId' in req:
            notifyService.deleteNotify(req['notifyId'])
