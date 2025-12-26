import json
import os
from common.LNG import language
from common.config import getConfig
from controller.baseController import BaseHandler, handle_request, cookieName
from service.system import userService
from concurrent.futures import ThreadPoolExecutor


class Login(BaseHandler):
    @handle_request
    def post(self, req):
        cfg = getConfig()
        user = userService.checkPwd(None, req['passwd'], req['userName'])
        self.set_signed_cookie(cookieName, json.dumps(user),
                               expires_days=cfg['server']['expires'])
        userReturn = user.copy()
        del userReturn['passwd']
        del userReturn['sqlVersion']
        return userReturn

    @handle_request
    def put(self, req):
        return userService.resetPasswd(req['userName'], req['key'], req.get('passwd', None))

    @handle_request
    def delete(self, req):
        self.clear_cookie(cookieName)


class User(BaseHandler):
    @handle_request
    def get(self, req):
        user = req['__user']
        return user

    @handle_request
    def put(self, req):
        user = json.loads(self.get_signed_cookie(cookieName))
        userService.editPasswd(user['id'], req['passwd'], req['oldPasswd'])


class Language(BaseHandler):
    @handle_request
    def get(self, req):
        return language()

    @handle_request
    def post(self, req):
        language(req['language'])


class Log(BaseHandler):

    @handle_request
    def get(self, req):
        """返回指定目录下的文件名列表（不含子目录）"""
        path = "data/log"
        if not os.path.isdir(path):
            raise ValueError(f"路径不存在或不是目录: {path}")

        # 获取所有条目并过滤出文件
        return [f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))]

    @handle_request
    def post(self, req):
        path = req['path']
        file_path = f'data/log/{path}'
        """
            获取日志文件的内容并返回

            参数:
                file_path (str): 日志文件的完整路径
                search_text (str): 可选，只返回包含指定文本的行
                max_lines (int): 可选，限制返回的最大行数（0 表示无限制）

            返回:
                str: 日志文件的内容，或错误信息
            """
        try:
            # 验证文件存在性
            if not os.path.exists(file_path):
                return f"错误: 文件不存在 - {file_path}"

            # 验证文件类型
            if not os.path.isfile(file_path):
                return f"错误: 路径不是文件 - {file_path}"

            """读取普通文本日志文件"""
            content_lines = []
            count = 0

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    content_lines.append(line)
                    count += 1

            return ''.join(content_lines)

        except Exception as e:
            return f"错误: 无法读取文件 - {str(e)}"


class Version(BaseHandler):
    @handle_request
    def get(self, req):
        """
        获取系统版本号
        """
        try:
            with open('version.txt', 'r', encoding='utf-8') as f:
                version_line = f.readline().strip()
                version = version_line.split(',')[0]
                return version
        except Exception as e:
            return f"错误: 无法读取版本文件 - {str(e)}"
