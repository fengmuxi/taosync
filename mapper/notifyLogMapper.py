from common import sqlBase


def addNotifyLog(notify_log):
    """
    添加消息记录
    :param notify_log: 消息记录字典
    :return: 插入的记录ID
    """
    sql = """
    INSERT INTO notify_log (notify_id, user_id, message_type, title, content, send_time, status, message, device_info)
    VALUES (:notify_id, :user_id, :message_type, :title, :content, :send_time, :status, :message, :device_info)
    """
    return sqlBase.execute_insert(sql, notify_log)


def getNotifyLogList(params):
    """
    获取消息记录列表（支持分页、搜索、筛选）
    :param params: 查询参数，包括：
        - pageNum: 页码
        - pageSize: 每页条数
        - user_id: 用户ID
        - notify_id: 通知配置ID
        - message_type: 消息类型
        - status: 消息状态（0-失败，1-成功）
        - start_time: 开始时间（时间戳）
        - end_time: 结束时间（时间戳）
        - keyword: 关键词搜索（标题或内容）
    :return: 消息记录列表和总数
    """
    # 只选择必要的列，避免选择所有列
    sql = "SELECT id, notify_id, user_id, message_type, title, content, send_time, status, message, device_info FROM notify_log WHERE 1=1"
    query_params = {}
    
    # 添加筛选条件
    if 'user_id' in params and params['user_id'] is not None:
        sql += " AND user_id = :user_id"
        query_params['user_id'] = params['user_id']
    
    if 'notify_id' in params and params['notify_id'] is not None:
        sql += " AND notify_id = :notify_id"
        query_params['notify_id'] = params['notify_id']
    
    if 'message_type' in params and params['message_type']:
        sql += " AND message_type = :message_type"
        query_params['message_type'] = params['message_type']
    
    if 'status' in params and params['status'] is not None:
        sql += " AND status = :status"
        query_params['status'] = params['status']
    
    if 'start_time' in params and params['start_time'] is not None:
        sql += " AND send_time >= :start_time"
        query_params['start_time'] = params['start_time']
    
    if 'end_time' in params and params['end_time'] is not None:
        sql += " AND send_time <= :end_time"
        query_params['end_time'] = params['end_time']
    
    if 'keyword' in params and params['keyword']:
        sql += " AND (title LIKE :keyword OR content LIKE :keyword)"
        query_params['keyword'] = f"%{params['keyword']}%"
    
    # 添加排序
    sql += " ORDER BY send_time DESC"
    
    # 添加分页参数
    if 'pageNum' in params and 'pageSize' in params:
        query_params['pageNum'] = params['pageNum']
        query_params['pageSize'] = params['pageSize']
    
    return sqlBase.fetchall_to_page(sql, query_params)


def updateNotifyLogStatus(log_id, status, message=None):
    """
    更新消息记录状态
    :param log_id: 消息记录ID
    :param status: 新状态（0-失败，1-成功）
    :param message: 状态消息
    :return: None
    """
    sql = "UPDATE notify_log SET status = :status"
    params = {'status': status, 'id': log_id}
    
    if message is not None:
        sql += ", message = :message"
        params['message'] = message
    
    sql += " WHERE id = :id"
    sqlBase.execute_update(sql, params)


def batchUpdateNotifyLogStatus(log_ids, status, message=None):
    """
    批量更新消息记录状态
    :param log_ids: 消息记录ID列表
    :param status: 新状态（0-失败，1-成功）
    :param message: 状态消息
    :return: None
    """
    if not log_ids:
        return
    
    # 使用参数化查询批量更新
    sql = "UPDATE notify_log SET status = ?"
    params = [status]
    
    if message is not None:
        sql += ", message = ?"
        params.append(message)
    
    sql += " WHERE id IN (" + ",".join(["?"] * len(log_ids)) + ")"
    params.extend(log_ids)
    
    sqlBase.execute_update(sql, params)


def deleteNotifyLog(log_ids):
    """
    删除消息记录
    :param log_ids: 消息记录ID列表
    :return: None
    """
    if not log_ids:
        return
    
    sql = "DELETE FROM notify_log WHERE id IN (" + ",".join(["?"] * len(log_ids)) + ")"
    sqlBase.execute_update(sql, log_ids)


def getNotifyLogById(log_id):
    """
    根据ID获取消息记录
    :param log_id: 消息记录ID
    :return: 消息记录字典
    """
    sql = "SELECT * FROM notify_log WHERE id = ?"
    result = sqlBase.fetchall_to_table(sql, (log_id,))
    return result[0] if result else None


def getNotifyLogForExport(params):
    """
    获取消息记录用于导出
    :param params: 查询参数（同getNotifyLogList）
    :return: 消息记录列表
    """
    # 只选择必要的列，避免选择所有列
    sql = "SELECT id, notify_id, user_id, message_type, title, content, send_time, status, message, device_info FROM notify_log WHERE 1=1"
    query_params = {}
    
    # 添加筛选条件
    if 'user_id' in params and params['user_id'] is not None:
        sql += " AND user_id = :user_id"
        query_params['user_id'] = params['user_id']
    
    if 'notify_id' in params and params['notify_id'] is not None:
        sql += " AND notify_id = :notify_id"
        query_params['notify_id'] = params['notify_id']
    
    if 'message_type' in params and params['message_type']:
        sql += " AND message_type = :message_type"
        query_params['message_type'] = params['message_type']
    
    if 'status' in params and params['status'] is not None:
        sql += " AND status = :status"
        query_params['status'] = params['status']
    
    if 'start_time' in params and params['start_time'] is not None:
        sql += " AND send_time >= :start_time"
        query_params['start_time'] = params['start_time']
    
    if 'end_time' in params and params['end_time'] is not None:
        sql += " AND send_time <= :end_time"
        query_params['end_time'] = params['end_time']
    
    if 'keyword' in params and params['keyword']:
        sql += " AND (title LIKE :keyword OR content LIKE :keyword)"
        query_params['keyword'] = f"%{params['keyword']}%"
    
    # 添加排序
    sql += " ORDER BY send_time DESC"
    
    # 不使用分页，获取所有符合条件的记录
    return sqlBase.fetchall_to_table(sql, query_params)
