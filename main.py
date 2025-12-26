import asyncio
import logging
import os
import sys

from tornado.web import Application, RequestHandler, StaticFileHandler

from common.config import getConfig
from controller import systemController, jobController, notifyController, feiniuController
from service.system import onStart


class MainIndex(RequestHandler):
    def get(self):
        self.render(os.path.join(frontendPath, "front/index.html"))


def make_app():
    # 以/svr/noAuth开头的请求无需鉴权，例如登录等
    return Application([
        (r"/svr/noAuth/login", systemController.Login),
        (r"/svr/user", systemController.User),
        (r"/svr/language", systemController.Language),
        (r"/svr/log", systemController.Log),
        (r"/svr/version", systemController.Version),
        (r"/svr/alist", jobController.Alist),
        (r"/svr/job", jobController.Job),
        (r"/svr/notify", notifyController.Notify),
        (r"/svr/feiniu.*", feiniuController.FeiNiu),
        (r"/", MainIndex),
        (r"/(.*)", StaticFileHandler,
         {"path": os.path.join(frontendPath, "front")})
    ], cookie_secret=server['passwdStr'])


async def main():
    app = make_app()
    logger = logging.getLogger()
    app.listen(server['port'])
    successMsg = f"启动成功_/_Running at http://127.0.0.1:{server['port']}/"
    logger.critical(successMsg)
    await asyncio.Event().wait()


def get_version():
    """
    从version.txt文件中获取版本号
    """
    try:
        # 获取正确的文件路径，支持pyinstaller打包
        import sys
        version_file_path = 'version.txt'
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件，使用sys._MEIPASS获取资源文件路径
            version_file_path = os.path.join(sys._MEIPASS, 'version.txt')
        with open(version_file_path, 'r', encoding='utf-8') as f:
            version_line = f.readline().strip()
            # 只取第一个版本号，忽略,latest等后续内容
            version = version_line.split(',')[0]
            return version
    except Exception as e:
        logging.error(f"读取版本号失败: {e}")
        return "unknown"


if __name__ == "__main__":
    # 获取版本号
    version = get_version()
    
    onStart.init()
    cfg = getConfig()
    frontendPath = sys._MEIPASS if getattr(sys, 'frozen', False) else '.'
    # 后端配置
    server = cfg['server']
    
    # 显示启动信息和版本号
    logging.critical(f"TaoSync 版本: {version}")
    asyncio.run(main())
