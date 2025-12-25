import json
import time

import requests

from common.LNG import G
from mapper import notifyMapper, notifyLogMapper
from service.notify import sc, email


def getNotifyList(needEnable=False):
    """
    获取通知配置列表
    :param needEnable: 是否启用
    :return:
    """
    return notifyMapper.getNotifyList(needEnable)


def addNewNotify(notify):
    """
    新增通知配置
    :param notify:
    :return:
    """
    notifyMapper.addNotify(notify)


def editNotify(notify):
    """
    编辑通知配置
    :param notify:
    :return:
    """
    notifyMapper.editNotify(notify)


def updateNotifyStatus(notifyId, enable):
    """
    更新通知配置启用状态
    :param notifyId:
    :param enable:
    :return:
    """
    notifyMapper.updateNotifyStatus(notifyId, enable)


def deleteNotify(notifyId):
    """
    删除
    :param notifyId:
    :return:
    """
    notifyMapper.deleteNotify(notifyId)


def testNotify(notify):
    """
    测试通知配置
    :return:
    """
    sendNotify(notify, 'TaoSync Test',
               G('notify_test_msg'))


def sendNotify(notify, title, content, needNotSync=False, user_id=0, message_type='', device_info=''):
    """
    发送通知
    :param notify: 通知配置 {'id': 1, 'enable': 1, 'method': 0, // 0-自定义；1-server酱；2-钉钉群机器人；3-邮件通知；待扩展更多
    'params': None, 'createTime': 1732179402}
    :param title: 通知标题
    :param content: 通知内容
    :param needNotSync: 是否是无需同步
    :param user_id: 用户ID（默认0，表示系统）
    :param message_type: 消息类型（默认空）
    :param device_info: 设备信息（默认空）
    :return: 发送结果
    method: 不同方法params结构
        0: {'url': 'http://xxx.xx/api', 'method': 'POST', 'contentType': 'application/json',
            'needContent': True, 'titleName': 'title', 'contentName': 'content', 'notSendNull': False}
        1: {'sendKey': 'xxx', 'notSendNull': False}
        2: {'url': '', 'notSendNull': False}
        3: {'sendKey': 'xxx', 'notSendNull': False} // 邮件通知
    """
    timeout = (10, 30)
    params = json.loads(notify['params'])
    # 如果配置了不发送空消息，并且当前状态为无需同步，则不发送通知
    if 'notSendNull' in params and params['notSendNull'] and needNotSync:
        return
    
    # 记录发送时间
    send_time = int(time.time())
    
    try:
        if notify['method'] == 0:
            reqData = {
                params['titleName']: title
            }
            if params['needContent']:
                reqData[params['contentName']] = content
            if params['method'] == 'GET':
                r = requests.get(params['url'], params=reqData, timeout=timeout)
            elif params['method'] == 'POST' or params['method'] == 'PUT':
                if params['contentType'] == 'application/json':
                    r = requests.request(params['method'], params['url'], json=reqData, timeout=timeout)
                elif params['contentType'] == 'application/x-www-form-urlencoded':
                    r = requests.request(params['method'], params['url'], data=reqData, timeout=timeout)
                else:
                    raise Exception("ContentType not allowed")
            else:
                raise Exception("Method not supported")
            if r.status_code != 200:
                raise Exception(r.text)
        elif notify['method'] == 1:
            # server酱
            sc.send(params['sendKey'], title, timeout, content)
        elif notify['method'] == 2:
            # 钉钉群机器人
            r = requests.post(params['url'], json={
                'msgtype': 'text',
                'text': {
                    'content': f'{title}\n\n{content}'
                }
            }, timeout=timeout)
            rst = r.json()
            if rst['errcode'] != 0:
                raise Exception(rst['errmsg'])
        elif notify['method'] == 3:
            # 邮件通知
            success, message = email.send_email(title, content, params)
            if not success:
                raise Exception(message)
        else:
            raise Exception("Wrong method")
        
        # 发送成功，记录日志
        notify_log = {
            'notify_id': notify['id'] if notify['id'] else 0,
            'user_id': user_id,
            'message_type': message_type,
            'title': title,
            'content': content,
            'send_time': send_time,
            'status': 1,  # 成功
            'message': '发送成功',
            'device_info': device_info
        }
        notifyLogMapper.addNotifyLog(notify_log)
        return True
    except Exception as e:
        # 发送失败，记录日志
        notify_log = {
            'notify_id': notify['id'],
            'user_id': user_id,
            'message_type': message_type,
            'title': title,
            'content': content,
            'send_time': send_time,
            'status': 0,  # 失败
            'message': str(e),
            'device_info': device_info
        }
        notifyLogMapper.addNotifyLog(notify_log)
        return False


def getNotifyLogList(params):
    """
    获取消息记录列表
    :param params: 查询参数
    :return: 消息记录列表和总数
    """
    # 权限控制：如果不是管理员，只能查看自己的消息记录
    if params.get('__user') and params['__user']['userName'] != 'admin':
        # 如果没有指定user_id，或者指定的user_id不是当前用户ID，则设置为当前用户ID
        params['user_id'] = params['__user']['id']
    
    return notifyLogMapper.getNotifyLogList(params)


def updateNotifyLogStatus(log_id, status, message=None):
    """
    更新消息记录状态
    :param log_id: 消息记录ID
    :param status: 新状态（0-失败，1-成功）
    :param message: 状态消息
    :return: None
    """
    notifyLogMapper.updateNotifyLogStatus(log_id, status, message)


def batchUpdateNotifyLogStatus(log_ids, status, message=None):
    """
    批量更新消息记录状态
    :param log_ids: 消息记录ID列表
    :param status: 新状态（0-失败，1-成功）
    :param message: 状态消息
    :return: None
    """
    notifyLogMapper.batchUpdateNotifyLogStatus(log_ids, status, message)


def deleteNotifyLog(log_ids):
    """
    删除消息记录
    :param log_ids: 消息记录ID列表
    :return: None
    """
    notifyLogMapper.deleteNotifyLog(log_ids)


def resendNotify(log_id):
    """
    重新发送通知
    :param log_id: 消息记录ID
    :return: 发送结果
    """
    # 获取消息记录
    notify_log = notifyLogMapper.getNotifyLogById(log_id)
    if not notify_log:
        raise Exception("消息记录不存在")
    
    # 获取通知配置
    notify_list = notifyMapper.getNotifyList()
    notify_config = None
    for notify in notify_list:
        if notify['id'] == notify_log['notify_id']:
            notify_config = notify
            break
    
    if not notify_config:
        raise Exception("通知配置不存在")
    
    # 重新发送通知
    result = sendNotify(
        notify_config,
        notify_log['title'],
        notify_log['content'],
        user_id=notify_log['user_id'],
        message_type=notify_log['message_type'],
        device_info=notify_log['device_info']
    )
    
    # 更新消息记录状态
    if result:
        notifyLogMapper.updateNotifyLogStatus(log_id, 1, "重新发送成功")
    else:
        # 状态已经在sendNotify中更新，这里不需要再次更新
        pass
    
    return result


def batchResendNotify(log_ids):
    """
    批量重新发送通知
    :param log_ids: 消息记录ID列表
    :return: 成功和失败的数量
    """
    success_count = 0
    fail_count = 0
    
    for log_id in log_ids:
        try:
            result = resendNotify(log_id)
            if result:
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            fail_count += 1
            # 更新消息记录状态为失败
            notifyLogMapper.updateNotifyLogStatus(log_id, 0, f"重新发送失败: {str(e)}")
    
    return {
        'success': success_count,
        'fail': fail_count
    }


def getNotifyLogForExport(params):
    """
    获取消息记录用于导出
    :param params: 查询参数
    :return: 消息记录列表
    """
    # 权限控制：如果不是管理员，只能导出自己的消息记录
    if params.get('__user') and params['__user']['userName'] != 'admin':
        params['user_id'] = params['__user']['id']
    
    return notifyLogMapper.getNotifyLogForExport(params)
