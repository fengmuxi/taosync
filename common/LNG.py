"""
@Author：dr34m
@Date  ：2024/8/16 13:52 
"""
from common.commonUtils import readOrSet

sysLanguage = None
allLng = {
    'zh_cn': {
        'success': '操作成功',
        'lost_part': '入参不全',
        'same_exists': '已存在相同数据，请检查！',
        'sign_in': '请登录',
        'login_expired': '登录失效',
        'alist_not_found': '未找到alist，可能已经被删除',
        'del_job_course_error': '作业启动过程中报错，将自动删除作业，任务为 {}',
        'job_not_found': '未找到作业，可能已经被删除',
        'task_not_found': '未找到任务，可能已经被删除',
        'user_not_found': '用户不存在',
        'alist_connect_fail': 'alist连接失败，请检查是否填写正确',
        'address_incorrect': 'alist地址格式有误',
        'code_not_200': '状态码非200',
        'alist_un_auth': 'AList鉴权失败，可能是令牌已失效',
        'alist_fail_code_reason': 'AList返回{}错误，原因为：{}',
        'without_token': '地址改变时令牌必填',
        'add_alist_client_fail': '新增alist客户端时失败，原因为：{}',
        'task_may_delete': '任务未找到。可能是您手动到AList中删除了复制任务；或者Alist因手动/异常奔溃被重启，导致任务记录丢失',
        'do_job_err': '执行任务失败，原因为：{}',
        'src': '来源',
        'dst': '目标',
        'scan_error': '{}目录扫描失败，原因为: {}',
        'copy_success_but_delete_fail': '文件复制成功，但删除源文件失败，删除失败的原因是：{}',
        'no_job_for_run': '没有可供执行的作业',
        'job_running': '当前有任务执行中，请稍后再试',
        'interval_lost': '创建间隔型作业时，间隔必填',
        'cron_lost': '创建cron型任务时，至少有一项不为空',
        'cannot_resume_lost_job': '作业不存在无法恢复，请删除后重新创建',
        'stop_fail': '停止定时任务失败，原因为：{}',
        'disable_fail': '禁用定时任务失败，原因为：{}',
        'cancel_fail': '取消任务过程中失败，原因为：{}',
        'disable_then_edit': '请先禁用任务才能编辑',
        'disabled_job_cannot_run': '禁用的作业不能运行',
        'cannot_disable_manual_job': '不可禁用仅手动任务',
        'log_del_success': '日志文件{}已被成功删除',
        'log_del_fail': '日志文件{}删除失败，原因为：{}',
        'log_rename_start': '日志定时更名任务启动成功',
        'keep_all_log': '日志保留时间为0，将保留所有日志',
        'keep_all_task': '任务保留时间为0，将保留所有任务',
        'clear_task_start': '定时清理任务启动成功',
        'passwd_wrong': '密码错误',
        'key_wrong': '加密秘钥错误',
        'passwd_wrong_max_time': '5分钟内密码错误超过3次，请稍后再试',
        'task_status': ['等待中', '进行中', '成功', '完成（部分失败）', '因重启而中止', '超时', '失败', '手动中止', '无需同步'],
        'task_end_msg_title': '{} - TaoSync',
        'task_end_msg_content': '来源目录为 {} 、目标目录为 {} 的作业执行结束。\n\n共 {} 个需要同步的文件，成功 {} 个，失败 {} 个。',
        'task_end_msg_content_ext': '\n\n本次同步共耗时：{}，成功同步 {} 文件。',
        'hms': '{} 小时 {} 分 {} 秒',
        'task_end_msg_error': '失败原因为：{}',
        'notify_error': '发送通知过程中失败，原因为：{}',
        'notify_test_msg': '这是一条由您自己发送的TaoSync测试消息，当你看到这条消息，说明你的配置是正确可用的。',
        'strm_file_error': '获取生成strm文件失败来源目录为：{} 提示信息：{} 原因为：{}'
    },
    'eng': {
        'success': 'success',
        'lost_part': 'Incomplete participation',
        'same_exists': 'The same data already exists, please check!',
        'sign_in': 'Please sign in',
        'login_expired': 'Login expired',
        'alist_not_found': 'Alist not found, may have been deleted',
        'del_job_course_error': 'An error occurred during job startup and the job will be automatically deleted. The job is {}',
        'job_not_found': 'The job was not found and may have been deleted',
        'task_not_found': 'Task not found, may have been deleted',
        'user_not_found': 'User does not exist',
        'alist_connect_fail': 'Alist connection failed, please check whether it is filled in correctly',
        'address_incorrect': 'The alist address format is incorrect',
        'code_not_200': 'Code not 200',
        'alist_un_auth': 'AList authentication failed, possibly because the token has expired',
        'alist_fail_code_reason': 'AList returns {}, reason: {}',
        'without_token': 'Token is required when address changes',
        'add_alist_client_fail': 'Failed to add alist client, reason: {}',
        'task_may_delete': 'task not found. You may have manually deleted the replication task in AList; or Alist was restarted manually or abnormally, resulting in the loss of task records',
        'do_job_err': 'Task execution failed due to: {}',
        'src': 'source',
        'dst': 'target',
        'scan_error': '{} directory scan failed due to: {}',
        'copy_success_but_delete_fail': 'The file was copied successfully, but the source file failed to be deleted due to: {}',
        'no_job_for_run': 'No jobs available to execute',
        'job_running': 'There is a task currently being executed, please try again later',
        'interval_lost': 'When creating an interval job, the interval is required',
        'cron_lost': 'When creating a cron job, at least one of the following items must be non-empty',
        'cannot_resume_lost_job': 'The job does not exist and cannot be restored. Please delete it and create it again',
        'stop_fail': 'Failed to stop the scheduled task due to: {}',
        'disable_fail': 'Failed to pause the scheduled task due to: {}',
        'cancel_fail': 'The task cancellation process failed due to: {}',
        'disable_then_edit': 'Please disable the job before editing it',
        'disabled_job_cannot_run': 'Disabled jobs cannot be run.',
        'cannot_disable_manual_job': 'Manual-only jobs cannot be disabled',
        'log_del_success': 'The log file {} has been successfully deleted',
        'log_del_fail': 'Failed to delete log file {}, reason: {}',
        'log_rename_start': 'The log scheduled renaming task was started successfully',
        'keep_all_log': 'The log retention time is 0, all logs will be retained',
        'keep_all_task': 'The task retention time is 0, all tasks will be retained',
        'clear_task_start': 'The scheduled cleanup task was started successfully',
        'passwd_wrong': 'Wrong password',
        'key_wrong': 'Wrong key',
        'passwd_wrong_max_time': 'The password was incorrect more than 3 times within 5 minutes. Please try again later',
        'task_status': ['waiting', 'in progress', 'success', 'complete (partially failed)',
                        'Aborted due to reboot', 'timeout', 'failed', 'Aborted by manual', 'No files need sync'],
        'task_end_msg_title': '{} - TaoSync',
        'task_end_msg_content': 'The job with source directory {} and target directory {} has completed execution.\n\n'
                                'There are {} files that need to be synchronized, {} of them succeeded and {} failed.',
        'task_end_msg_content_ext': '\n\nThis synchronization took a total of {} and successfully synchronized {} of files.',
        'hms': '{} hours {} minutes {} seconds',
        'task_end_msg_error': 'Failed due to {}',
        'notify_error': 'Failed to send notification due to: {}',
        'notify_test_msg': 'This is a TaoSync test message sent by yourself. '
                           'When you see this message, it means your configuration is correct and available.',
        'strm_file_error': 'Failed to obtain the source directory for generating the Strm file：{} msg：{} Failed due to：{}'
    }
}


def language(lang=None):
    """
    获取或修改语言
    :param lang: 语言，不填为读取，否则是修改
    :return: 读取时为值，否则空
    """
    global sysLanguage
    fileName = 'data/language.txt'
    if lang is None:
        if sysLanguage is None:
            sysLanguage = readOrSet(fileName, 'zh_cn')
        return sysLanguage
    else:
        if lang not in allLng:
            raise Exception(f"no {lang}")
        sysLanguage = lang
        readOrSet(fileName, lang, True)


def G(params):
    """
    根据语言获取文字
    :param params: 文字关键字
    :return:
    """
    cu = allLng[language()]
    return cu[params]
