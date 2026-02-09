"""
@Author：dr34m
@Date  ：2024/7/10 12:10 
"""
import re
from concurrent.futures import ThreadPoolExecutor

from tornado.concurrent import run_on_executor

from controller.baseController import BaseHandler, handle_request
from service.alist import alistService
from service.syncJob import jobService, taskService


class Alist(BaseHandler):
    executor = ThreadPoolExecutor(1)

    @run_on_executor
    @handle_request
    def get(self, req):
        if 'alistId' in req and 'path' in req:
            return alistService.getChildPath(int(req['alistId']), req['path'])
        return alistService.getClientList()

    @run_on_executor
    @handle_request
    def post(self, req):
        if 'test' in req and req['test']:
            # 测试连接
            success, message = alistService.testConnection(req)
            return {'success': success, 'message': message}
        alistService.addClient(req)

    @run_on_executor
    @handle_request
    def put(self, req):
        alistService.updateClient(req)

    @run_on_executor
    @handle_request
    def delete(self, req):
        alistService.removeClient(req['id'])


class Job(BaseHandler):
    executor = ThreadPoolExecutor(4)

    @run_on_executor
    @handle_request
    def get(self, req):
        if 'id' in req:
            if 'current' in req:
                return jobService.getJobCurrent(req['id'], req.get('status', None), int(req.get('pageNum', 1)), int(req.get('pageSize', 10)))
            return taskService.getTaskList(req)
        elif 'taskId' in req:
            return taskService.getTaskItemList(req)
        return jobService.getJobList(req)

    def validateRegex(self, req):
        """
        验证正则表达式
        :param req: 请求参数，包含 regex 和 testPaths
        :return: 验证结果
        """
        try:
            regex_pattern = req.get('regex', '')
            test_paths = req.get('testPaths', [])
            is_case_sensitive = req.get('caseSensitive', True)
            is_global = req.get('globalMatch', True)
            
            if not regex_pattern:
                return {
                    'success': False,
                    'message': '正则表达式不能为空',
                    'results': []
                }
            
            # 编译正则表达式
            flags = 0
            if not is_case_sensitive:
                flags |= re.IGNORECASE
            if is_global:
                flags |= re.MULTILINE
            
            try:
                compiled_regex = re.compile(regex_pattern, flags)
            except Exception as e:
                return {
                    'success': False,
                    'message': f'正则表达式编译失败: {str(e)}',
                    'results': []
                }
            
            # 测试路径
            results = []
            for path in test_paths:
                try:
                    # 查找所有匹配
                    matches = list(compiled_regex.finditer(path))
                    matched = len(matches) > 0
                    
                    # 准备匹配数据
                    match_data = []
                    for match in matches:
                        # 获取所有捕获组
                        groups = {
                            'fullMatch': match.group()
                        }
                        # 添加命名捕获组
                        if match.groupdict():
                            groups['namedGroups'] = match.groupdict()
                        # 添加编号捕获组
                        for i in range(1, match.re.groups + 1):
                            groups[f'group{i}'] = match.group(i)
                        
                        match_data.append({
                            'text': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'groups': groups
                        })
                    
                    results.append({
                        'path': path,
                        'matched': matched,
                        'matchedCount': len(matches),
                        'matches': match_data,
                        'matchedText': matches[0].group() if matched else None
                    })
                except Exception as e:
                    results.append({
                        'path': path,
                        'matched': False,
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'message': '验证成功',
                'results': results
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'验证过程出错: {str(e)}',
                'results': []
            }

    @run_on_executor
    @handle_request
    def post(self, req):
        if 'validateRegex' in req:
            # 验证正则表达式
            return self.validateRegex(req)
        if 'id' in req:
            if 'copy' in req:
                jobService.copyJobClient(req)
            else:
                jobService.editJobClient(req)
        else:
            jobService.addJobClient(req)

    @run_on_executor
    @handle_request
    def put(self, req):
        if req['pause'] is None:
            if 'id' in req:
                # 手动执行作业
                jobService.doJobManual(req['id'])
            else:
                # 手动执行所有作业
                jobService.doAllJobManual()
        elif req['pause'] is True:
            # 禁用作业
            if 'abort' in req:
                jobService.abortJob(req['id'])
            else:
                jobService.pauseJob(req['id'])
        elif req['retry'] is True:
            # 重试失败的作业
            jobService.retryJob(req['id'])
        else:
            # 启用作业
            jobService.continueJob(req['id'])

    @run_on_executor
    @handle_request
    def delete(self, req):
        if 'id' in req:
            jobService.removeJobClient(req['id'])
        elif 'taskId' in req:
            taskService.removeTask(req['taskId'])
