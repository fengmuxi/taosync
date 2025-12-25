"""
@Author：dr34m
@Date  ：2025/12/19 16:00 
"""
from common import sqlBase


def addFeiniuRefreshTask(task):
    """
    添加飞牛刷新任务记录
    
    :param task: 任务信息，包含以下字段：
                - feiniuId: 飞牛配置ID
                - jobId: 关联的作业ID
                - media_library_id: 媒体库ID
                - folder_paths: 刷新路径列表（JSON格式）
                - operation_type: 操作类型（refresh）
                - status: 初始状态（0-执行中）
                - start_time: 开始时间戳
    :return: 插入的任务ID
    """
    return sqlBase.execute_insert(
        "insert into feiniu_refresh_task (feiniuId, jobId, media_library_id, folder_paths, operation_type, status, start_time) "
        "values (:feiniuId, :jobId, :media_library_id, :folder_paths, :operation_type, :status, :start_time)", 
        task
    )


def updateFeiniuRefreshTask(task_id, task):
    """
    更新飞牛刷新任务记录
    
    :param task_id: 任务ID
    :param task: 任务信息，包含以下字段：
                - status: 状态（1-成功，2-失败）
                - end_time: 结束时间戳
                - elapsed_time: 耗时（秒）
                - error_msg: 错误信息（可选）
                - retry_count: 重试次数
    :return: 更新结果
    """
    sql = "update feiniu_refresh_task set "
    update_fields = []
    params = {}
    
    # 添加需要更新的字段
    if 'status' in task:
        update_fields.append("status=:status")
        params['status'] = task['status']
    if 'end_time' in task:
        update_fields.append("end_time=:end_time")
        params['end_time'] = task['end_time']
    if 'elapsed_time' in task:
        update_fields.append("elapsed_time=:elapsed_time")
        params['elapsed_time'] = task['elapsed_time']
    if 'error_msg' in task:
        update_fields.append("error_msg=:error_msg")
        params['error_msg'] = task['error_msg']
    if 'retry_count' in task:
        update_fields.append("retry_count=:retry_count")
        params['retry_count'] = task['retry_count']
    
    # 必须包含id
    params['id'] = task_id
    
    if not update_fields:
        raise Exception("没有提供任何需要更新的字段")
    
    sql += ", ".join(update_fields) + " where id=:id"
    return sqlBase.execute_update(sql, params)


def getFeiniuRefreshTasks(page=1, page_size=10, status=None, mediaLibraryId='', startTime=None, endTime=None):
    """
    获取飞牛刷新任务列表
    
    :param page: 页码，默认1
    :param page_size: 每页大小，默认10
    :param status: 状态筛选，0-执行中，1-成功，2-失败，None-所有
    :param mediaLibraryId: 媒体库ID筛选，空字符串-所有
    :param startTime: 开始时间筛选，None-不限制
    :param endTime: 结束时间筛选，None-不限制
    :return: 任务列表
    """
    offset = (page - 1) * page_size
    
    # 构建查询条件
    conditions = []
    params = []
    
    if status is not None:
        conditions.append("status=?")
        params.append(status)
    
    if mediaLibraryId:
        conditions.append("media_library_id=?")
        params.append(mediaLibraryId)
    
    if startTime is not None:
        conditions.append("start_time >= ?")
        params.append(startTime)
    
    if endTime is not None:
        conditions.append("start_time <= ?")
        params.append(endTime)
    
    # 构建完整的SQL查询
    if conditions:
        sql = "select * from feiniu_refresh_task where " + " and ".join(conditions) + " order by start_time desc limit ? offset ?"
        params.extend([page_size, offset])
    else:
        sql = "select * from feiniu_refresh_task order by start_time desc limit ? offset ?"
        params = [page_size, offset]
    
    return sqlBase.fetchall_to_table(sql, tuple(params))


def getFeiniuRefreshTaskById(task_id):
    """
    根据ID获取飞牛刷新任务
    
    :param task_id: 任务ID
    :return: 任务信息
    """
    rst = sqlBase.fetchall_to_table(
        "select * from feiniu_refresh_task where id=?", 
        (task_id,) 
    )
    if rst:
        return rst[0]
    else:
        return None


def getFeiniuRefreshTasksByJobId(job_id):
    """
    根据作业ID获取飞牛刷新任务
    
    :param job_id: 作业ID
    :return: 任务列表
    """
    return sqlBase.fetchall_to_table(
        "select * from feiniu_refresh_task where jobId=? order by start_time desc", 
        (job_id,) 
    )


def getFeiniuRefreshTasksByFeiniuId(feiniu_id, page=1, page_size=10):
    """
    根据飞牛配置ID获取飞牛刷新任务
    
    :param feiniu_id: 飞牛配置ID
    :param page: 页码，默认1
    :param page_size: 每页大小，默认10
    :return: 任务列表
    """
    offset = (page - 1) * page_size
    return sqlBase.fetchall_to_table(
        "select * from feiniu_refresh_task where feiniuId=? order by start_time desc limit ? offset ?", 
        (feiniu_id, page_size, offset) 
    )


def deleteFeiniuRefreshTask(task_id):
    """
    删除飞牛刷新任务
    
    :param task_id: 任务ID
    :return: 删除结果
    """
    return sqlBase.execute_update(
        "delete from feiniu_refresh_task where id=?", 
        (task_id,) 
    )


def deleteFeiniuRefreshTasksByJobId(job_id):
    """
    根据作业ID删除飞牛刷新任务
    
    :param job_id: 作业ID
    :return: 删除结果
    """
    return sqlBase.execute_update(
        "delete from feiniu_refresh_task where jobId=?", 
        (job_id,) 
    )


def getFeiniuRefreshTaskStatistics(start_time=None, end_time=None):
    """
    获取飞牛刷新任务统计信息
    
    :param start_time: 开始时间戳（可选）
    :param end_time: 结束时间戳（可选）
    :return: 统计信息
    """
    if start_time and end_time:
        return sqlBase.fetchall_to_table(
            "select status, count(*) as count from feiniu_refresh_task "
            "where start_time >= ? and start_time <= ? "
            "group by status", 
            (start_time, end_time) 
        )
    elif start_time:
        return sqlBase.fetchall_to_table(
            "select status, count(*) as count from feiniu_refresh_task "
            "where start_time >= ? "
            "group by status", 
            (start_time,) 
        )
    elif end_time:
        return sqlBase.fetchall_to_table(
            "select status, count(*) as count from feiniu_refresh_task "
            "where start_time <= ? "
            "group by status", 
            (end_time,) 
        )
    else:
        return sqlBase.fetchall_to_table(
            "select status, count(*) as count from feiniu_refresh_task "
            "group by status"
        )


def getFailTaskCount():
    """
    获取失败任务数量
    
    :return: 失败任务数量
    """
    rst = sqlBase.fetchall_to_table(
        "select count(*) as count from feiniu_refresh_task where status=2"
    )
    if rst:
        return rst[0]['count']
    else:
        return 0


def getFeiniuRefreshTaskCount(status=None, mediaLibraryId='', startTime=None, endTime=None):
    """
    获取飞牛刷新任务数量
    
    :param status: 状态筛选，0-执行中，1-成功，2-失败，None-所有
    :param mediaLibraryId: 媒体库ID筛选，空字符串-所有
    :param startTime: 开始时间筛选，None-不限制
    :param endTime: 结束时间筛选，None-不限制
    :return: 任务数量
    """
    # 构建查询条件
    conditions = []
    params = []
    
    if status is not None:
        conditions.append("status=?")
        params.append(status)
    
    if mediaLibraryId:
        conditions.append("media_library_id=?")
        params.append(mediaLibraryId)
    
    if startTime is not None:
        conditions.append("start_time >= ?")
        params.append(startTime)
    
    if endTime is not None:
        conditions.append("start_time <= ?")
        params.append(endTime)
    
    # 构建完整的SQL查询
    if conditions:
        sql = "select count(*) as count from feiniu_refresh_task where " + " and ".join(conditions)
    else:
        sql = "select count(*) as count from feiniu_refresh_task"
    
    rst = sqlBase.fetchall_to_table(sql, tuple(params))
    
    if rst:
        return rst[0]['count']
    else:
        return 0



