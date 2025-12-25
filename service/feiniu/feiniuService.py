"""
@Author：dr34m
@Date  ：2024/12/1 11:00 
"""
import logging

from common.LNG import G
from mapper.feiniuMapper import getFeiniuById, addFeiniu, removeFeiniu, getFeiniuList, updateFeiniu, getEnabledFeiniu
from common.feiniu import FeiNiuClient
from common.commonUtils import passwd2md5
from common.config import getConfig
from common import sqlBase

# 飞牛客户端列表，key为feiniuId,value为FeiNiuClient
feiniuClientList = {}

def encrypt_password(password):
    """
    加密密码
    :param password: 明文密码
    :return: 加密后的密码
    """
    if not password:
        return password
    # 由于飞牛API需要明文密码，我们暂时不加密，直接返回明文密码
    return password

def decrypt_password(encrypted_password):
    """
    解密密码
    :param encrypted_password: 加密后的密码
    :return: 明文密码
    """
    return encrypted_password

def getClientList():
    """
    获取飞牛配置列表
    :return:
    """
    return getFeiniuList()


def getClientById(feiniuId):
    """
    通过id获取飞牛客户端
    :param feiniuId:
    :return:
    """
    global feiniuClientList
    if feiniuId not in feiniuClientList:
        feiniu = getFeiniuById(feiniuId)
        # 解密密码
        decrypted_password = decrypt_password(feiniu['password'])
        feiniuClientList[feiniuId] = FeiNiuClient(feiniu['host'], feiniu['username'], decrypted_password)
    return feiniuClientList[feiniuId]


def getEnabledClient():
    """
    获取启用的飞牛客户端
    :return:
    """
    feiniu = getEnabledFeiniu()
    if not feiniu:
        return None
    
    feiniuId = feiniu['id']
    return getClientById(feiniuId)


def updateClient(feiniu):
    """
    更新飞牛配置
    :param feiniu: {
        'id': 1,
        'remark': 'remark',
        'host': 'xxx',
        'username': 'xxx',
        'password': 'xxx',
        'enable': 1
    }
    """
    feiniuId = feiniu['id']
    if feiniu.get('remark') is not None and feiniu.get('remark').strip() == '':
        feiniu['remark'] = None
    
    if feiniu['host'].endswith('/'):
        feiniu['host'] = feiniu['host'][:-1]
    
    # 验证飞牛配置是否有效
    try:
        # 如果提供了新密码，使用新密码测试登录
        if feiniu.get('password'):
            client = FeiNiuClient(feiniu['host'], feiniu['username'], feiniu['password'])
            # 测试登录获取令牌
            if not client._get_token():
                raise Exception(G('feiniu_login_fail'))
        else:
            # 不修改密码时，跳过密码验证，直接使用现有客户端或创建新客户端
            # 注意：这里不需要测试登录，因为密码没有改变
            client = None
    except Exception as e:
        logger = logging.getLogger()
        logger.error(G('feiniu_config_test_fail').format(str(e)))
        raise Exception(G('feiniu_config_test_fail').format(str(e)))
    
    # 更新配置
    # 更新配置
    update_feiniu_data = {
        'id': feiniu['id'],
        'remark': feiniu.get('remark'),
        'host': feiniu['host'],
        'username': feiniu['username'],
        'enable': feiniu['enable']
    }
    
    # 如果提供了密码且不为空，则加密密码并添加到更新数据中
    if feiniu.get('password'):
        update_feiniu_data['password'] = encrypt_password(feiniu['password'])
    updateFeiniu(update_feiniu_data)
    
    # 更新客户端列表
    global feiniuClientList
    if feiniuId in feiniuClientList:
        if client:
            # 如果client不为None，直接使用新创建的客户端
            feiniuClientList[feiniuId] = client
        else:
            # 如果client为None，说明密码没有改变，但其他配置可能改变了
            # 使用现有密码创建新的客户端实例
            current_feiniu = getFeiniuById(feiniuId)
            new_client = FeiNiuClient(feiniu['host'], feiniu['username'], current_feiniu['password'])
            feiniuClientList[feiniuId] = new_client


def addClient(feiniu):
    """
    新增飞牛配置
    :param feiniu: {
        'remark': 'remark',
        'host': 'xxx',
        'userName': 'xxx',
        'password': 'xxx',
        'enable': 1
    }
    """
    if feiniu.get('remark') is not None and feiniu.get('remark').strip() == '':
        feiniu['remark'] = None
    
    if feiniu['host'].endswith('/'):
        feiniu['host'] = feiniu['host'][:-1]
    
    # 验证飞牛配置是否有效
    try:
        client = FeiNiuClient(feiniu['host'], feiniu['username'], feiniu['password'])
        # 测试登录获取令牌
        token = client._get_token()
        if not token:
            raise Exception(G('feiniu_login_fail'))
    except Exception as e:
        logger = logging.getLogger()
        logger.error(G('feiniu_config_test_fail').format(str(e)))
        raise Exception(e)
    
    # 加密密码
    encrypted_password = encrypt_password(feiniu['password'])
    
    # 新增配置
    try:
        feiniuId = addFeiniu({
            'remark': feiniu.get('remark'),
            'host': feiniu['host'],
            'username': feiniu['username'],
            'password': encrypted_password,
            'enable': feiniu.get('enable', 1)
        })
    except Exception as e:
        logger = logging.getLogger()
        logger.error(G('add_feiniu_client_fail').format(str(e)))
        raise Exception(e)
    
    # 添加到客户端列表
    global feiniuClientList
    feiniuClientList[feiniuId] = client


def removeClient(feiniuId):
    """
    删除飞牛配置
    :param feiniuId:
    """
    global feiniuClientList
    if feiniuId in feiniuClientList:
        del feiniuClientList[feiniuId]
    
    removeFeiniu(feiniuId)


def getMediaLibraries(feiniuId):
    """
    获取飞牛媒体库列表
    :param feiniuId: 飞牛配置ID
    :return: 媒体库列表
    """
    client = getClientById(feiniuId)
    return client.get_media_libraries()


def getFailTasks(page=1, page_size=10):
    """
    获取所有失败的刷新任务
    :param page: 页码，默认1
    :param page_size: 每页大小，默认10
    :return: 失败任务列表
    """
    from mapper.feiniuRefreshTaskMapper import getFeiniuRefreshTasks
    return getFeiniuRefreshTasks(status=2, page=page, page_size=page_size)


def getFailTaskCount():
    """
    获取失败任务数量
    :return: 失败任务数量
    """
    from mapper.feiniuRefreshTaskMapper import getFeiniuRefreshTaskCount
    return getFeiniuRefreshTaskCount(status=2)


def getRefreshTasks(status=None, mediaLibraryId='', startTime=None, endTime=None, page=1, page_size=10):
    """
    获取刷新任务列表
    :param status: 状态筛选（0-执行中，1-成功，2-失败），None-所有
    :param mediaLibraryId: 媒体库ID筛选，空字符串-所有
    :param startTime: 开始时间筛选，None-不限制
    :param endTime: 结束时间筛选，None-不限制
    :param page: 页码，默认1
    :param page_size: 每页大小，默认10
    :return: 任务列表
    """
    from mapper.feiniuRefreshTaskMapper import getFeiniuRefreshTasks
    return getFeiniuRefreshTasks(
        status=status, 
        mediaLibraryId=mediaLibraryId, 
        startTime=startTime, 
        endTime=endTime, 
        page=page, 
        page_size=page_size
    )


def getRefreshTaskCount(status=None, mediaLibraryId='', startTime=None, endTime=None):
    """
    获取刷新任务数量
    :param status: 状态筛选（0-执行中，1-成功，2-失败），None-所有
    :param mediaLibraryId: 媒体库ID筛选，空字符串-所有
    :param startTime: 开始时间筛选，None-不限制
    :param endTime: 结束时间筛选，None-不限制
    :return: 任务数量
    """
    from mapper.feiniuRefreshTaskMapper import getFeiniuRefreshTaskCount
    return getFeiniuRefreshTaskCount(
        status=status, 
        mediaLibraryId=mediaLibraryId, 
        startTime=startTime, 
        endTime=endTime
    )


def retryRefreshTask(taskId):
    """
    重试指定的刷新任务
    :param taskId: 刷新任务ID
    """
    from mapper.feiniuRefreshTaskMapper import getFeiniuRefreshTaskById
    from common.feiniu import feiniu_manager
    
    # 获取失败任务详情
    task = getFeiniuRefreshTaskById(taskId)
    if not task:
        raise Exception("刷新任务不存在")
    
    # 解析文件夹路径列表
    import json
    folder_paths = json.loads(task['folder_paths'])
    
    # 调用飞牛管理器的refresh_path方法重试
    feiniu_manager.refresh_path(
        folder_path=folder_paths,
        debounce_seconds=0,  # 立即执行，不使用防抖
        feiniu_id=task['feiniuId'],
        media_library_id=task['media_library_id'],
        job_id=task['jobId']
    )


def deleteRefreshTask(taskId):
    """
    删除指定的刷新任务
    :param taskId: 刷新任务ID
    """
    from mapper.feiniuRefreshTaskMapper import deleteFeiniuRefreshTask
    deleteFeiniuRefreshTask(taskId)


def testConnection(feiniu):
    """
    测试飞牛连接
    :param feiniu: {
        'id': 1
    } 或者 {
        'host': 'xxx',
        'username': 'xxx',
        'password': 'xxx'
    }
    :return: (bool, str) 连接结果和消息
    """
    try:
        # 检查是否传入了id，如果传入则从数据库获取完整配置
        if 'id' in feiniu:
            feiniuInfo = getFeiniuById(feiniu['id'])
            host = feiniuInfo['host'].rstrip('/')
            username = feiniuInfo['username']
            password = decrypt_password(feiniuInfo['password'])
        else:
            # 直接使用传入的配置
            host = feiniu['host'].rstrip('/')
            username = feiniu['username']
            password = feiniu['password']
        
        # 尝试创建客户端实例并获取令牌，这会自动调用登录验证
        client = FeiNiuClient(host, username, password)
        token = client._get_token()
        if token:
            # 尝试获取媒体库列表，进一步验证连接
            libraries = client.get_media_libraries()
            return True, f"连接成功，获取到 {len(libraries)} 个媒体库"
        else:
            return False, "连接失败：无法获取有效的认证令牌"
    except Exception as e:
        return False, f"连接失败：{str(e)}"
