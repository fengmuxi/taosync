"""
@Author：dr34m
@Date  ：2024/12/1 11:30 
"""
from concurrent.futures import ThreadPoolExecutor

from tornado.concurrent import run_on_executor

from controller.baseController import BaseHandler, handle_request
from service.feiniu import feiniuService


class FeiNiu(BaseHandler):
    executor = ThreadPoolExecutor(1)

    @run_on_executor
    @handle_request
    def get(self, req):
        # 根据请求参数判断是获取配置列表还是媒体库列表
        if 'mediaLibraries' in self.request.uri:
            # 获取媒体库列表
            feiniu_id = req.get('id')
            return feiniuService.getMediaLibraries(feiniu_id)
        elif 'failTasks' in self.request.uri:
            # 获取失败任务列表（兼容旧端点）
            page = int(req.get('page', 1))
            page_size = int(req.get('pageSize', 10))
            return feiniuService.getRefreshTasks(status=2, page=page, page_size=page_size)
        elif 'failTaskCount' in self.request.uri:
            # 获取失败任务数量（兼容旧端点）
            return {'count': feiniuService.getRefreshTaskCount(status=2)}
        elif 'refreshTasks' in self.request.uri:
            # 获取刷新任务列表
            status = req.get('status')
            status = int(status) if status is not None else None
            mediaLibraryId = req.get('mediaLibraryId', '')
            startTime = req.get('startTime')
            startTime = int(startTime) if startTime is not None else None
            endTime = req.get('endTime')
            endTime = int(endTime) if endTime is not None else None
            page = int(req.get('page', 1))
            page_size = int(req.get('pageSize', 10))
            return feiniuService.getRefreshTasks(
                status=status, 
                mediaLibraryId=mediaLibraryId, 
                startTime=startTime, 
                endTime=endTime, 
                page=page, 
                page_size=page_size
            )
        elif 'refreshTaskCount' in self.request.uri:
            # 获取刷新任务数量
            status = req.get('status')
            status = int(status) if status is not None else None
            mediaLibraryId = req.get('mediaLibraryId', '')
            startTime = req.get('startTime')
            startTime = int(startTime) if startTime is not None else None
            endTime = req.get('endTime')
            endTime = int(endTime) if endTime is not None else None
            return {'count': feiniuService.getRefreshTaskCount(
                status=status, 
                mediaLibraryId=mediaLibraryId, 
                startTime=startTime, 
                endTime=endTime
            )}
        else:
            # 获取配置列表，返回时解密密码用于前端显示
            client_list = feiniuService.getClientList()
            # 由于密码是MD5加密不可逆，这里返回空字符串给前端
            for client in client_list:
                client['password'] = ''
            return client_list

    @run_on_executor
    @handle_request
    def post(self, req):
        if 'test' in req and req['test']:
            # 测试连接
            success, message = feiniuService.testConnection(req)
            return {'success': success, 'message': message}
        feiniuService.addClient(req['feiniu'])

    @run_on_executor
    @handle_request
    def put(self, req):
        if 'retryFailTask' in self.request.uri:
            # 重试失败任务（兼容旧端点）
            task_id = req.get('id')
            feiniuService.retryRefreshTask(task_id)
        elif 'retryRefreshTask' in self.request.uri:
            # 重试刷新任务
            task_id = req.get('id')
            feiniuService.retryRefreshTask(task_id)
        else:
            # 更新飞牛配置
            feiniuService.updateClient(req['feiniu'])

    @run_on_executor
    @handle_request
    def delete(self, req):
        if 'failTask' in self.request.uri:
            # 删除失败任务（兼容旧端点）
            task_id = req.get('id')
            feiniuService.deleteRefreshTask(task_id)
        elif 'refreshTask' in self.request.uri:
            # 删除刷新任务
            task_id = req.get('id')
            feiniuService.deleteRefreshTask(task_id)
        else:
            # 删除飞牛配置
            feiniuService.removeClient(req['id'])
