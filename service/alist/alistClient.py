"""
@Author：dr34m
@Date  ：2024/7/4 13:57 
"""
import os
import time
import re

import requests

from common.LNG import G


def checkExs(path, rts, spec, wantSpec, strmSpec, ignore_path):
    """
    检查并排除排除项
    :param path: 所在路径
    :param rts: 内容列表，例如
        {
            "test1-1/": {},  # key以/结尾表示目录
            "test1.txt": 4  # 不以/结尾，表示文件，存文件大小
        }
    :param spec: 排除规则
    :param strmSpec: 刮削文件规则
    :param wantSpec: 需要规则
    :return: 排除后的内容列表
    """
    rtsNew = rts.copy()
    for rtsItem in rts.keys():
        spec_del = True
        ignore_path_del = True
        want_spec_del = True
        strm_spec_del = True
        strm_del = True
        file_del = True
        # 匹配不扫描文件存在不保留
        if spec:
            if not spec.match_file(path + rtsItem):
                spec_del = False
        else:
            spec_del = False

        if ignore_path:
            ignore_path_del = is_path_prefix(rtsItem, ignore_path)
        else:
            ignore_path_del = False

        if not rtsItem.endswith("/"):
            # 匹配需要生成strm文件存在保留
            if wantSpec:
                if re.search(wantSpec, rtsItem):
                    want_spec_del = False
            # 匹配刮削文件存在保留
            if strmSpec:
                if re.search(strmSpec, rtsItem):
                    strm_spec_del = False
            # 匹配strm文件存在保留
            if re.search("\.(strm)$", rtsItem):
                strm_del = False
        else:
            file_del = False
        # 判断删除内容
        if spec_del or ignore_path_del or (want_spec_del and strm_spec_del and strm_del and file_del):
            del rtsNew[rtsItem]
    return rtsNew


def is_path_prefix(file_path, prefix_list):
    """更安全的路径前缀检查，处理结尾分隔符"""
    for prefix in prefix_list:
        # 统一添加路径分隔符防止误匹配
        # safe_prefix = prefix.rstrip(os.sep) + os.sep
        if file_path.startswith(prefix):
            return True

        # 额外检查精确匹配的情况
        if file_path == prefix or file_path == prefix.rstrip(os.sep):
            return True

    return False


class AlistClient:
    def __init__(self, url, token, alistId=None):
        """
        初始化
        :param url: 请求地址，例如'http://localhost:5244'，注意结尾不要/
        :param alistId: 存在数据库中的id
        :param token: 登录鉴权信息
        """
        self.url = url
        self.user = None
        self.alistId = alistId
        self.token = token
        # key-根目录，val-上次操作时间，或计划下次操作时间，用于间隔等待
        self.waits = {}
        self.getUser()

    def req(self, method, url, data=None, params=None):
        """
        通用请求
        :param method: get/post
        :param url: 请求地址，/api/xxx
        :param data: 需要放在请求体中用json传的数据
        :param params: 在url中的请求参数
        :return: 200返回res['data']，401自动登录后重试，失败抛出异常
        """
        res = {
            'code': 500,
            'message': None,
            'data': None
        }
        headers = None
        if self.token is not None:
            headers = {
                'Authorization': self.token
            }
        try:
            r = requests.request(method, self.url + url, json=data, params=params, headers=headers, timeout=(10, 300))
            if r.status_code == 200:
                res = r.json()
            else:
                res['code'] = r.status_code
                res['message'] = G('code_not_200')
        except Exception as e:
            if 'Invalid URL' in str(e):
                raise Exception(G('address_incorrect'))
            elif 'Max retries' in str(e):
                raise Exception(G('alist_connect_fail'))
            raise Exception(e)
        if res['code'] != 200:
            if res['code'] == 401:
                raise Exception(G('alist_un_auth'))
            raise Exception(G('alist_fail_code_reason').format(res['code'], res['message']))
        return res['data']

    def post(self, url, data=None, params=None):
        """
        发送post请求
        :param url: 请求地址，/api/xxx
        :param data: 需要放在请求体中用json传的数据
        :param params: 放在url中的请求参数
        :return: 200返回res['data']，401自动登录后重试，失败抛出异常
        """
        return self.req('post', url, data, params)

    def get(self, url, params=None):
        """
        发送get请求
        :param url: 请求地址，/api/xxx
        :param params: 放在url中的请求参数
        :return: 200返回res['data']，401自动登录后重试，失败抛出异常
        """
        return self.req('get', url, params=params)

    def getUser(self):
        """
        获取当前用户
        :return:
        """
        self.user = self.get('/api/me')['username']

    def updateAlistId(self, alistId):
        """
        更新alistId
        :param alistId:
        :return:
        """
        self.alistId = alistId

    def checkWait(self, path, scanInterval=0):
        """
        检查是否等待
        :param path: 路径
        :param scanInterval: 间隔
        :return:
        """
        if scanInterval != 0:
            pathFirst = path.split('/', maxsplit=2)[1]
            if pathFirst in self.waits:
                timeC = time.time() - self.waits[pathFirst]
                if timeC < scanInterval:
                    self.waits[pathFirst] = time.time() + timeC
                    time.sleep(scanInterval - timeC)
                    return
            self.waits[pathFirst] = time.time()

    def fileListApi(self, path, useCache=0, scanInterval=0, spec=None, wantSpec=None, strmSpec=None, rootPath=None, ignore_path=None):
        """
        目录列表
        :param path: 目录，以/开头并以/结尾
        :param useCache: 是否使用缓存，0-不使用，1-使用
        :param scanInterval: 目录扫描间隔，单位秒
        :param spec: 排除项规则
        :param wantSpec: 需要项规则
        :param strmSpec: 刮削文件规则
        :return: {
            "test1-1/": {},  # key以/结尾表示目录
            "test1.txt": 4  # 不以/结尾，表示文件，存文件大小
        }
        :param rootPath: 同步根目录
        """
        self.checkWait(path, scanInterval)
        res = self.post('/api/fs/list', data={
            'path': path,
            'refresh': useCache != 1
        })['content']
        if res is not None:
            rts = {
                f"{item['name']}/" if item['is_dir'] else item['name']: {} if item['is_dir']
                else {'size': item['size'], 'sign': item['sign']} for item in res
            }
        else:
            rts = {}
        if (spec or wantSpec) and rts:
            if rootPath is None:
                rootPath = path
            rts = checkExs(path[len(rootPath):], rts, spec, wantSpec, strmSpec, ignore_path)
        return rts

    def filePathList(self, path):
        """
        通过路径获取其下路径列表
        :param path:
        :return:
        """
        res = self.post('/api/fs/list', data={
            'path': path,
            'refresh': True
        })['content']
        if res is not None:
            return [{'path': item['name']} for item in res if item['is_dir']]
        else:
            return []

    def allFileList(self, path, useCache=0, scanInterval=0, spec=None, strmSpec=None, rootPath=None):
        """
        递归获取文件列表，暂时弃用
        :param path: 根路径
        :param useCache: 是否使用缓存，0-不使用，1-使用
        :param scanInterval: 目录扫描间隔，单位秒
        :param spec: 排除项规则
        :param strmSpec: 刮削文件规则
        :param rootPath: 同步根目录
        :return: {
            "test1-1/": {
                "test1-3/": {
                    "test1.txt": 4
                },
                "test1.txt": 4
            },
            "test1.txt": 4
        }
        """
        if rootPath is None:
            rootPath = path
        fList = self.fileListApi(path, useCache, scanInterval, spec, strmSpec, rootPath)
        for key in fList.keys():
            if key.endswith('/'):
                fList[key] = self.allFileList(f"{path}/{key[:-1]}", useCache, scanInterval, spec, strmSpec, rootPath)
        return fList

    def mkdir(self, path, scanInterval=0):
        """
        创建目录
        :param path: 路径
        :param scanInterval:
        """
        self.checkWait(path, scanInterval)
        return self.post('/api/fs/mkdir', data={
            'path': path
        })

    def deleteFile(self, path, names, scanInterval=0):
        """
        删除文件或目录
        :param path: 路径
        :param names: 文件/目录名，列表
        :param scanInterval:
        """
        self.checkWait(path, scanInterval)
        self.post('/api/fs/remove', data={
            'names': names,
            'dir': path
        })

    def copyFile(self, srcDir, dstDir, name):
        """
        复制文件
        :param srcDir: 源目录
        :param dstDir: 目标目录
        :param name: 文件名
        :return: 任务id
        """
        tasks = self.post('/api/fs/copy', data={
            'src_dir': srcDir,
            'dst_dir': dstDir,
            'overwrite': True,
            'names': [
                name
            ]
        })['tasks']
        if tasks:
            return tasks[0]['id']
        else:
            return None

    def moveFile(self, srcDir, dstDir, name):
        """
        移动文件
        :param srcDir: 源目录
        :param dstDir: 目标目录
        :param name: 文件名
        :return: 任务id
        """
        tasks = self.post('/api/fs/move', data={
            'src_dir': srcDir,
            'dst_dir': dstDir,
            'overwrite': True,
            'names': [
                name
            ]
        })['tasks']
        if tasks:
            return tasks[0]['id']
        else:
            return None

    def taskInfo(self, taskId):
        """
        任务详情
        :param taskId: 任务id
        :return: {
            "id": "26GQSD1mZHDlDq1V1Lf7G",
            "name": "copy [/test1](/test1/test1.txt) to [/test2](/)",
            "state": 2, # 0-等待中，1-进行中，2-成功
            "status": "getting src object",
            "progress": 0, # 进度
            "error": ""
        }
        """
        return self.post('/api/admin/task/copy/info', params={
            'tid': taskId
        })

    def copyTaskDone(self):
        """
        已完成的复制任务
        :return: [{
            "id": "26GQSD1mZHDlDq1V1Lf7G",
            "name": "copy [/test1](/test1/test1.txt) to [/test2](/)",
            "state": 2, # 0-等待中，1-进行中，2-成功
            "status": "getting src object",
            "progress": 0, # 进度
            "error": ""
        }]
        """
        return self.get('/api/admin/task/copy/done')

    def copyTaskUnDone(self):
        """
        未完成的复制任务
        :return: [{
            "id": "26GQSD1mZHDlDq1V1Lf7G",
            "name": "copy [/test1](/test1/test1.txt) to [/test2](/)",
            "state": 1, # 0-等待中，1-进行中，2-成功
            "status": "getting src object",
            "progress": 0, # 进度
            "error": ""
        }]
        """
        return self.get('/api/admin/task/copy/undone')

    def copyTaskRetry(self, taskId):
        """
        重试复制任务
        :param taskId: 任务id
        """
        self.post('/api/admin/task/copy/retry', params={
            'tid': taskId
        })

    def copyTaskClearSucceeded(self):
        """
        清除已成功的复制任务
        """
        self.post('/api/admin/task/copy/clear_succeeded')

    def copyTaskDelete(self, taskId):
        """
        删除复制任务
        :param taskId: 任务id
        """
        self.post('/api/admin/task/copy/delete', params={
            'tid': taskId
        })

    def copyTaskCancel(self, taskId):
        """
        取消复制任务
        :param taskId: 任务id
        """
        self.post('/api/admin/task/copy/cancel', params={
            'tid': taskId
        })

    def getFileApi(self, path, useCache=0, scanInterval=0):
        """
        获取文件信息
        :param path: 目录，以/开头并以/结尾
        :param useCache: 是否使用缓存，0-不使用，1-使用
        :param scanInterval: 目录扫描间隔，单位秒
        :return: {
            "name": "Alist V3.md",
            "size": 2618,
            "is_dir": false,
            "modified": "2024-05-17T16:05:36.4651534+08:00",
            "created": "2024-05-17T16:05:29.2001008+08:00",
            "sign": "",
            "thumb": "",
            "type": 4,
            "hashinfo": "null",
            "hash_info": null,
            "raw_url": "http://127.0.0.1:5244/p/local/Alist%20V3.md",
            "readme": "",
            "header": "",
            "provider": "Local",
            "related": null
        }
        """
        self.checkWait(path, scanInterval)
        res = self.post('/api/fs/get', data={
            'path': path,
            'refresh': useCache != 1
        })
        if res is not None:
            rts = res
        else:
            rts = {}
        return rts
