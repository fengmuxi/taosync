"""
@Author：dr34m
@Date  ：2024/7/11 12:14 
"""
import itertools
import json
import logging
import threading
import time
import os
import re
from pathlib import Path
from collections import defaultdict

from apscheduler.schedulers.background import BackgroundScheduler
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

from common.LNG import G
from mapper import jobMapper
from service.alist import alistService
from service.syncJob import taskService
import hashlib
import secrets
import string
from common.feiniu import feiniu_manager
from service.notify.notifyService import sendNotify, getNotifyList


class CopyItem:
    def __init__(self, srcPath, dstPath, fileName, fileSize, method, jobTask):
        self.jobTask = jobTask
        self.alistClient = self.jobTask.alistClient
        self.taskId = self.jobTask.taskId
        self.srcPath = srcPath
        self.dstPath = dstPath
        self.fileName = fileName
        self.fileSize = fileSize
        self.copyType = 0 if method != 2 else 2
        self.alistTaskId = None
        self.status = 0
        self.progress = 0.0
        self.errMsg = None
        self.createTime = int(time.time())
        self.doingKey = None

    def doByThread(self):
        doThread = threading.Thread(target=self.doIt, name='复制项目线程')
        doThread.start()

    def doIt(self):
        try:
            if self.jobTask.breakFlag:
                self.status = 4
            else:
                self.alistTaskId = self.alistClient.copyFile(self.srcPath, self.dstPath, self.fileName)
        except Exception as e:
            self.errMsg = str(e)
            self.status = 7
        else:
            if self.alistTaskId is None:
                self.status = 2
            elif self.status != 4:
                self.checkAndGetStatus()
        self.endIt()

    def checkAndGetStatus(self):
        """
        不断检查状态并更新
        :return:
        """
        while True:
            if self.jobTask.breakFlag:
                self.status = 4
                if self.alistTaskId is not None:
                    try:
                        self.alistClient.copyTaskCancel(self.alistTaskId)
                        self.alistClient.copyTaskDelete(self.alistTaskId)
                    except Exception as e:
                        self.status = 7
                        self.errMsg = str(e)
                break
            cuTime = time.time()
            time.sleep(0.61 if cuTime - self.jobTask.lastWatching < 3 else 2.93)
            try:
                taskInfo = self.alistClient.taskInfo(self.alistTaskId)
            except Exception as e:
                logger = logging.getLogger()
                logger.exception(e)
                eMsg = str(e)
                if '404' in eMsg:
                    eMsg = (G('task_may_delete'))
                taskInfo = {
                    'state': 7,
                    'progress': None,
                    'error': eMsg
                }
            if taskInfo['state'] == self.status and taskInfo['progress'] == self.progress:
                continue
            self.status = taskInfo['state']
            # 修复进度显示NAN问题，确保progress始终是有效的数字
            self.progress = taskInfo['progress']
            if self.progress is None or self.progress == '':
                self.progress = 0.0
            self.progress = float(self.progress)
            self.errMsg = taskInfo['error'] if taskInfo['error'] else None
            # 删除结束的任务
            if taskInfo['state'] in [2, 4, 7]:
                try:
                    self.alistClient.copyTaskDelete(self.alistTaskId)
                    break
                except Exception:
                    break

    def endIt(self):
        if self.copyType == 2 and self.status == 2:
            try:
                self.alistClient.deleteFile(self.srcPath, [self.fileName], self.jobTask.job['scanIntervalS'])
            except Exception as e:
                self.status = 7
                self.errMsg = G('copy_success_but_delete_fail').format(str(e))
        self.jobTask.copyHook(self.srcPath, self.dstPath, self.fileName, self.fileSize, self.alistTaskId, self.status,
                              errMsg=self.errMsg, copyType=self.copyType, createTime=self.createTime)
        del self.jobTask.doing[self.doingKey]


class CreateStrmItem:
    def __init__(self, strmPath, srcPath, srcRootPath, strmName, raw_url, jobTask):
        self.jobTask = jobTask
        self.taskId = self.jobTask.taskId
        self.srcPath = srcPath
        self.dstPath = strmPath
        self.srcRootPath = srcRootPath
        self.copyType = 3
        self.fileName = strmName
        self.fileSize = 0
        self.raw_url = raw_url
        self.alistTaskId = None
        self.status = 0
        self.progress = 0.0
        self.errMsg = None
        self.createTime = int(time.time())
        self.doingKey = None

    def doByThread(self):
        doThread = threading.Thread(target=self.doIt, name='创建strm线程')
        doThread.start()

    def doIt(self):
        try:
            if self.jobTask.breakFlag:
                self.status = 4
            else:
                self.alistTaskId = self.jobTask.create_strm_file(self.dstPath, self.srcPath,
                                                                 self.srcRootPath, self.fileName, self.raw_url)
        except Exception as e:
            self.errMsg = str(e)
            self.status = 7
        else:
            if self.alistTaskId:
                self.status = 2
        self.endIt()

    def endIt(self):
        self.jobTask.copyHook(self.srcPath, self.dstPath, self.fileName, self.fileSize, self.alistTaskId, self.status,
                              errMsg=self.errMsg, copyType=self.copyType, createTime=self.createTime)
        del self.jobTask.doing[self.doingKey]


class JobTask:
    def __init__(self, taskId, vm):
        """
        作业任务类
        :param taskId: 任务id
        :param vm: 作业上下文
        """
        self.taskId = taskId
        self.jobClient = vm
        self.job = self.jobClient.job
        self.alistClient = alistService.getClientById(self.job['alistId'])
        self.createTime = time.time()
        # 已完成（包含成功或者失败）
        self.finish = []
        # 已经提交到alist的任务
        self.doing = {}
        # 等待提交到alist的任务
        self.waiting = []
        # 上次查看详情的时间戳，低于3秒表示正在看，在看则快速检查状态，否则低速检查以节约开销
        self.lastWatching = 0.0
        # 队列序号，用作复制任务的doingKey
        self.queueNum = 0
        # sync全部任务加入队列标识
        self.scanFinish = False
        # 首个文件开始同步时间
        self.firstSync = None
        # 手动中止标识
        self.breakFlag = False
        # 保存需要刷新的飞牛路径集合
        self.feiniu_refresh_paths = set()
        syncThread = threading.Thread(target=self.sync, name=f'同步线程{taskId}')
        syncThread.start()
        self.currentTasks = {}
        submitThread = threading.Thread(target=self.taskSubmit, name=f'任务提交线程{taskId}')
        submitThread.start()
        threading.Thread(target=self.monitor_threads, daemon=True, name=f'线程看门狗{taskId}').start()

    def getCurrent(self):
        """
        总结并返回详情（高实时性）
        {
            'srcPath': 来源目录,
            'dstPath': 目标目录,
            'fileName': 文件名,
            'fileSize': 文件大小,
            'status': 状态,
            'type': 方式，0-复制（对于目录则是创建），1-删除，2-移动,
            'progress': 进度,
            'errMsg': 错误信息,
            'createTime': 创建时间
        }
        :return: {
            'scanFinish': True,
            'doingTask': [{
                'srcPath': 来源目录,
                'dstPath': 目标目录,
                'fileName': 文件名,
                'fileSize': 文件大小,
                'status': 状态,
                'type': 方式，0-复制（对于目录则是创建），1-删除，2-移动,
                'progress': 进度,
                'errMsg': 错误信息,
                'createTime': 创建时间
            }],
            'createTime': int(self.createTime),
            'duration': int(self.lastWatching - self.createTime),
            'firstSync': int(self.firstSync) if self.firstSync is not None else None,
            'num': {
                'wait': 0,
                'running': 1,
                'success': 2,
                'fail': 7,
                'other': 0
            },
            'size': {
                'wait': 0,
                'running': 1,
                'success': 2,
                'fail': 7,
                'other': 0
            }
        }
        """
        self.lastWatching = time.time()
        waits = [{
            'srcPath': waitItem.srcPath,
            'dstPath': waitItem.dstPath,
            'isPath': 0,
            'fileName': waitItem.fileName,
            'fileSize': waitItem.fileSize,
            'status': waitItem.status,
            'type': waitItem.copyType,
            'progress': waitItem.progress,
            'errMsg': waitItem.errMsg,
            'createTime': waitItem.createTime
        } for waitItem in self.waiting]
        dos = [{
            'srcPath': doItem.srcPath,
            'dstPath': doItem.dstPath,
            'isPath': 0,
            'fileName': doItem.fileName,
            'fileSize': doItem.fileSize,
            'status': doItem.status,
            'type': doItem.copyType,
            'progress': doItem.progress,
            'errMsg': doItem.errMsg,
            'createTime': doItem.createTime
        } for doItem in self.doing.values()]
        allTask = list(itertools.chain(waits, dos, self.finish))
        keyValSpace = {
            'wait': 0,
            'running': 1,
            'success': 2,
            'fail': 7,
            'other': -1
        }
        currentTasks = {}
        for val in keyValSpace.values():
            currentTasks[val] = []
        # 其他类型数组
        otk = []
        otkStatus = [3, 4, 5, 6, 8, 9]
        grouped = defaultdict(list)
        for taskItem in allTask:
            grouped[taskItem['status']].append(taskItem)
        for status, tasks in grouped.items():
            tasks.sort(key=lambda x: x['createTime'])
            if status in otkStatus:
                otk.extend(tasks)
            else:
                currentTasks[status] = tasks
        currentTasks[-1] = otk
        for key in currentTasks.keys():
            if key == 0:
                continue
            currentTasks[key] = list(reversed(currentTasks[key]))
        self.currentTasks = currentTasks
        result = {
            'scanFinish': self.scanFinish,
            'doingTask': self.currentTasks[1],
            'createTime': int(self.createTime),
            'duration': int(self.lastWatching - self.createTime),
            'firstSync': int(self.firstSync) if self.firstSync is not None else None,
            'num': {},
            'size': {}
        }
        for key, val in keyValSpace.items():
            result['num'][key] = len(currentTasks[val])
            result['size'][key] = sum(
                item['fileSize'] for item in currentTasks[val] if item['fileSize'] is not None and item['type'] != 1)
        return result

    def getCurrentByStatus(self, status, pageNum=1, pageSize=10):
        return self.advanced_paginate(self.currentTasks[status], page=pageNum, page_size=pageSize)

    def taskSubmit(self):
        """
        队列检验与提交
        :return:
        """
        while True:
            if self.breakFlag:
                break
            time.sleep(0.5)
            doingNums = len(self.doing.keys())
            waitingNums = len(self.waiting)
            if not self.scanFinish or doingNums != 0 or waitingNums != 0:
                try:
                    while doingNums < 20:
                        if self.breakFlag:
                            break
                        # if self.waiting:
                        #     item = self.waiting[0]
                        #     if int(time.time()) - item.createTime > 30 * 60:
                        #         self.waiting = []
                        #         self.doing = {}
                        #         break

                        for key in list(self.doing.keys()):
                            doing = self.doing.get(key)
                            if doing:
                                if int(time.time()) - doing.startTime > 30 * 60:
                                    del self.doing[key]
                        if waitingNums == 0:
                            break
                        else:
                            if self.firstSync is None:
                                self.firstSync = time.time()
                            self.queueNum += 1
                            self.doing[self.queueNum] = self.waiting.pop(0)
                            self.doing[self.queueNum].doingKey = self.queueNum
                            self.doing[self.queueNum].startTime = int(time.time())
                            try:
                                self.doing[self.queueNum].doByThread()
                            except Exception as e:
                                logger = logging.getLogger()
                                errMsg = G('do_job_err').format(G('src'), '执行任务错误：', str(e))
                                logger.error(errMsg)
                                logger.exception(e)
                                del self.doing[self.queueNum]
                            doingNums = len(self.doing.keys())
                            waitingNums = len(self.waiting)
                except Exception as e:
                    import traceback
                    logger = logging.getLogger()
                    logger.info(f"提交任务进程异常: {e}\n{traceback.format_exc()}")
            else:
                break
        tryTime = 0
        while len(self.doing.keys()) > 0:
            tryTime += 1
            time.sleep(.5)
            if tryTime > 3:
                break
        jobMapper.addJobTaskItemMany(self.finish)
        
        # 任务结束后，统一处理飞牛刷新路径
        if self.feiniu_refresh_paths:
            # 提取必要数据，避免线程持有self引用，确保手动终止时能立即执行
            refresh_paths = self.feiniu_refresh_paths.copy()
            job_data = dict(self.job)
            task_id = self.taskId
            
            # 使用异步线程处理飞牛刷新路径，不阻塞job任务结束流程
            def async_feiniu_refresh(paths, job, task_id):
                logger = logging.getLogger()
                logger.info(f"开始异步处理飞牛刷新路径，共有 {len(paths)} 个路径")
                
                # 获取启用的通知配置
                enabled_notifies = []
                try:
                    enabled_notifies = getNotifyList(needEnable=True)
                    logger.info(f"获取到 {len(enabled_notifies)} 个启用的通知配置")
                except Exception as e:
                    logger.warning(f"获取通知配置失败: {str(e)}")
                
                # 定义发送通知的辅助函数
                def send_notification(title, content, message_type='error'):
                    if not enabled_notifies:
                        logger.info("没有启用的通知配置，跳过发送通知")
                        return
                    
                    for notify in enabled_notifies:
                        try:
                            logger.info(f"使用通知配置 {notify['id']} 发送通知")
                            sendNotify(
                                notify,
                                title,
                                content,
                                message_type=message_type,
                                device_info=f"task_id:{task_id}"
                            )
                            logger.info(f"通知发送成功")
                        except Exception as e:
                            logger.error(f"发送通知失败: {str(e)}")
                            import traceback
                            logger.error(f"  - 异常堆栈: {traceback.format_exc()}")
                
                try:
                    # 路径处理：由于self.feiniu_refresh_paths本身就是set，且添加时已进行格式统一，直接转换为列表即可
                    if not paths:
                        logger.info(f"没有需要处理的路径，跳过处理")
                        return

                    # ------------------------ 路径合并优化 ------------------------
                    # 按规则合并路径：合并"/1/2/3"和"/1/2"为"/1/2"，但不合并"/1/2/3"和"/1/2/4"
                    def merge_paths(paths):
                        """按规则合并路径，保留最上级目录
                        
                        例如：
                        - ["/1/2/3", "/1/2", "/1/2/4", "/1/3"] → ["/1/2", "/1/3"]
                        - ["/a/b/c", "/a/b", "/a/b/d", "/a/c/e"] → ["/a/b", "/a/c/e"]
                        """
                        if not paths:
                            return []
                        
                        # 排序路径，按长度从小到大
                        paths = list(paths)
                        paths.sort(key=len)
                        
                        # 保留最上级目录，去除所有子目录
                        merged = []
                        for path in paths:
                            # 检查当前路径是否是已保留路径的子目录
                            is_subdir = any(parent in path and path[len(parent)] == '/' for parent in merged)
                            if not is_subdir:
                                # 同时检查是否已有子目录在结果中，如果有则替换为当前更高级的目录
                                # 先移除所有以当前路径为前缀的子目录
                                merged = [p for p in merged if not (path in p and p[len(path)] == '/')]
                                merged.append(path)
                        
                        return merged
                    
                    # 执行路径合并
                    merged_folder_paths = merge_paths(paths)
                    
                    # 记录路径合并的详细信息
                    logger.info(f"【飞牛影视管理器】路径合并优化：")
                    logger.info(f"【飞牛影视管理器】  - 合并前路径数: {len(paths)}个")
                    logger.info(f"【飞牛影视管理器】  - 合并后路径数: {len(merged_folder_paths)}个")
                    
                    if len(paths) != len(merged_folder_paths):
                        logger.info(f"【飞牛影视管理器】  - 合并前路径:")
                        for path in sorted(paths)[:10]:
                            logger.info(f"【飞牛影视管理器】      {path}")
                        if len(paths) > 10:
                            logger.info(f"【飞牛影视管理器】      ... 还有 {len(paths) - 10} 个路径")
                        
                        logger.info(f"【飞牛影视管理器】  - 合并后路径:")
                        for path in sorted(merged_folder_paths)[:10]:
                            logger.info(f"【飞牛影视管理器】      {path}")
                        if len(merged_folder_paths) > 10:
                            logger.info(f"【飞牛影视管理器】      ... 还有 {len(merged_folder_paths) - 10} 个路径")
                    # ------------------------ 路径合并优化结束 ------------------------
                    
                    # 解析多路径映射关系
                    def parse_path_mappings(job):
                        """解析作业配置中的多路径映射关系
                        
                        支持三种格式：
                        1. 旧格式1：单个映射，使用strm_path、feiniu_library_id、feiniu_media_path字段
                        
                        返回格式：[{"strm_path": "", "library_id": "", "media_path": ""}]
                        """
                        mappings = []
                        
                        # 1. 尝试从新的统一字段解析（飞牛媒体库路径映射）
                        strm_path_mapping = job.get('strm_path_mapping')
                        if strm_path_mapping:
                            # 新格式：多个映射，用|分隔
                            mapping_pairs = strm_path_mapping.split('|')
                            for mapping in mapping_pairs:
                                parts = mapping.split(':')
                                if len(parts) == 3:
                                    # 完整格式：strm_path:library_id:media_path
                                    strm_path = parts[0].strip()
                                    library_id = parts[1].strip()
                                    media_path = parts[2].strip()
                                    
                                    # 验证映射关系的完整性
                                    if strm_path and library_id:
                                        mappings.append({
                                            "strm_path": strm_path,
                                            "library_id": library_id,
                                            "media_path": media_path
                                        })
                                    else:
                                        logger.warning(f"跳过无效的路径映射关系（缺少必要字段）: {mapping}")
                        
                        # 验证映射关系的唯一性
                        unique_mappings = []
                        seen = set()
                        for mapping in mappings:
                            key = f"{mapping['strm_path']}|{mapping['library_id']}"
                            if key not in seen:
                                seen.add(key)
                                unique_mappings.append(mapping)
                            else:
                                logger.warning(f"跳过重复的路径映射关系: {mapping}")
                        
                        return unique_mappings
                    
                    # 获取路径映射关系
                    path_mappings = parse_path_mappings(job)
                    logger.info(f"解析到 {len(path_mappings)} 个路径映射关系")
                    for mapping in path_mappings:
                        logger.info(f"  - 映射关系: {mapping['strm_path']} -> 媒体库ID: {mapping['library_id']}, 媒体路径: {mapping['media_path']}")
                    
                    # 按媒体库分组路径
                    library_paths = {} 
                    unmatched_paths = []
                    
                    for path in merged_folder_paths:
                        # 找到匹配的映射关系
                        matched = False
                        # 按strm_path长度降序排序，确保最长匹配优先
                        sorted_mappings = sorted(path_mappings, key=lambda x: len(x['strm_path']), reverse=True)
                        
                        for mapping in sorted_mappings:
                            strm_path = mapping['strm_path']
                            # 标准化路径分隔符
                            normalized_path = path.replace('\\', '/')
                            normalized_strm_path = strm_path.replace('\\', '/')
                            
                            # 检查路径是否以strm_path开头
                            if normalized_path.startswith(normalized_strm_path):
                                # 将路径映射到对应的媒体库
                                if mapping['library_id'] not in library_paths:
                                    library_paths[mapping['library_id']] = {
                                        'paths': [],
                                        'mapping': mapping
                                    }
                                # 计算相对路径并映射到媒体库路径
                                relative_path = normalized_path[len(normalized_strm_path):].lstrip('/')
                                # 保持媒体路径的原始分隔符
                                media_path = mapping['media_path']
                                if '\\' in media_path:
                                    mapped_path = os.path.join(media_path, relative_path.replace('/', '\\'))
                                else:
                                    mapped_path = os.path.join(media_path, relative_path)
                                
                                # 应用统一的路径预处理
                                mapped_path = feiniu_manager._preprocess_path(mapped_path, media_path, strm_path, None)
                                
                                library_paths[mapping['library_id']]['paths'].append(mapped_path)
                                matched = True
                                logger.debug(f"路径 '{path}' 匹配到映射关系: {mapping['strm_path']} -> 媒体库ID: {mapping['library_id']}, 映射路径: {mapped_path}")
                                break
                        
                        if not matched:
                            # 没有映射关系，跳过
                            unmatched_paths.append(path)
                            logger.warning(f"路径 '{path}' 没有找到对应的映射关系，跳过刷新")
                    
                    # 记录未匹配到映射关系的路径
                    if unmatched_paths:
                        logger.info(f"共有 {len(unmatched_paths)} 个路径未匹配到映射关系，跳过刷新")
                        for path in unmatched_paths:
                            logger.info(f"  - 跳过路径: {path}")
                    
                    # 调用飞牛刷新路径，按媒体库分组刷新
                    for library_id, data in library_paths.items():
                        try:
                            mapping = data['mapping']
                            # 对路径进行去重，确保幂等性
                            paths = list(set(data['paths']))
                            
                            if not paths:
                                logger.info(f"媒体库 {library_id} 没有需要刷新的路径，跳过刷新")
                                continue
                            
                            logger.info(f"调用飞牛刷新媒体库 {library_id} 的 {len(paths)} 个路径")
                            logger.info(f"  - 媒体库ID: {library_id}")
                            logger.info(f"  - 映射关系: {mapping['strm_path']} -> {mapping['media_path']}")
                            for i, path in enumerate(paths, 1):
                                logger.info(f"  - 待刷新路径 {i}: {path}")
                            
                            # 调用飞牛刷新路径，将所有路径一次性传入
                            feiniu_id = job.get('feiniuId')
                            logger.info(f"  - 飞牛配置ID: {feiniu_id}")
                            
                            # 调用飞牛刷新路径
                            feiniu_manager.refresh_path(
                                paths, 
                                feiniu_id=feiniu_id,
                                media_library_id=library_id,
                                media_path=mapping['media_path'],
                                job_id=job.get('id'),
                            )
                            
                            logger.info(f"飞牛刷新媒体库 {library_id} 成功，共刷新 {len(paths)} 个路径")
                            logger.info(f"  - 刷新触发条件: 作业任务执行完毕")
                            logger.info(f"  - 映射匹配结果: 成功匹配 {len(data['paths'])} 个路径")
                        except Exception as e:
                            logger.error(f"飞牛刷新媒体库 {library_id} 失败: {str(e)}")
                            logger.error(f"  - 失败原因: {str(e)}")
                            logger.error(f"  - 媒体库ID: {library_id}")
                            logger.error(f"  - 待刷新路径数量: {len(paths)}")
                            # 记录异常堆栈信息
                            import traceback
                            error_stack = traceback.format_exc()
                            logger.error(f"  - 异常堆栈: {error_stack}")
                            
                            # 格式化异常信息，发送通知
                            import datetime
                            error_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            title = f"【飞牛刷新失败】媒体库 {library_id} 刷新路径失败"
                            content = f"""TaoSync 飞牛刷新媒体库失败通知

                            任务ID: {task_id}
                            作业ID: {job.get('id', '未知')}
                            媒体库ID: {library_id}
                            映射关系: {mapping['strm_path']} -> {mapping['media_path']}
                            失败时间: {error_time}
                            失败原因: {str(e)}
                            待刷新路径数量: {len(paths)}

                            异常堆栈:
                            {error_stack}
                            """
                            
                            try:
                                send_notification(title, content, message_type='feiniu_refresh_error')
                                logger.info("飞牛刷新失败通知发送成功")
                            except Exception as notify_e:
                                logger.error(f"发送飞牛刷新失败通知失败: {str(notify_e)}")
                            
                            # 对于刷新失败的情况，我们已经在feiniu_manager.refresh_path中实现了重试机制
                            # 所以这里只需要记录日志和发送通知即可
                except Exception as e:
                    logger.error(f"异步处理飞牛刷新路径时发生错误: {str(e)}")
                    # 记录异常堆栈信息
                    import traceback
                    error_stack = traceback.format_exc()
                    logger.error(f"  - 异常堆栈: {error_stack}")
                    
                    # 格式化异常信息，发送通知
                    import datetime
                    error_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    title = f"【飞牛刷新异常】任务 {task_id} 异步处理失败"
                    content = f"""TaoSync 飞牛刷新路径处理异常通知
                    
                    任务ID: {task_id}
                    作业ID: {job.get('id', '未知')}
                    失败时间: {error_time}
                    失败原因: {str(e)}
                    处理路径数量: {len(paths)}

                    异常堆栈:
                    {error_stack}
                    """
                    
                    try:
                        send_notification(title, content, message_type='feiniu_refresh_error')
                        logger.info("飞牛刷新异常通知发送成功")
                    except Exception as notify_e:
                        logger.error(f"发送飞牛刷新异常通知失败: {str(notify_e)}")
                finally:
                    logger.info(f"异步处理飞牛刷新路径完成")
            
            # 启动异步线程处理飞牛刷新路径，传递必要数据而非持有self引用
            refresh_thread = threading.Thread(
                target=async_feiniu_refresh, 
                args=(refresh_paths, job_data, task_id),
                name=f'飞牛异步刷新线程{task_id}'
            )
            refresh_thread.daemon = True  # 设置为守护线程，确保程序退出时线程自动终止
            logger = logging.getLogger()
            refresh_thread.start()
            logger.info(f"已启动异步线程处理飞牛刷新路径，不影响job任务结束流程")
        
        self.updateTaskStatus()
        self.jobClient.jobDoing = False
        self.jobClient.currentJobTask = None

    def retryJob(self):
        """
        重试失败作业
        """
        return

    def monitor_threads(self):
        logger = logging.getLogger()
        while True:
            time.sleep(10)
            alive_threads = [(t.name, t.is_alive()) for t in threading.enumerate()]
            logger.info(f"定时检查线程状态返回，正常的运行状态名称如下: {alive_threads}")


    def copyHook(self, srcPath, dstPath, name, size, alistTaskId=None, status=0, errMsg=None, isPath=0,
                 copyType=0, createTime=int(time.time())):
        """
        复制文件回调
        :param srcPath: 来源目录
        :param dstPath: 目标目录
        :param name: 文件名
        :param size: 文件大小
        :param alistTaskId: alist任务id
        :param status: 0-等待中，1-运行中，2-成功，3-取消中，4-已取消，5-出错（将重试），6-失败中，
                        7-已失败，8-等待重试中，9-等待重试回调执行中，10-目录扫描失败，11-目录创建失败
        :param errMsg: 错误信息
        :param isPath: 是否是目录，0-文件，1-目录
        :param copyType: 0-复制，2-移动
        :param createTime:
        """
        self.finish.append({
            'taskId': self.taskId,
            'srcPath': srcPath,
            'dstPath': dstPath,
            'isPath': isPath,
            'fileName': name,
            'fileSize': size,
            'type': copyType,
            'alistTaskId': alistTaskId,
            'status': status,
            'errMsg': errMsg,
            'createTime': createTime
        })

    def delHook(self, dstPath, name, size, status=2, errMsg=None, isPath=0, createTime=int(time.time())):
        """
        删除文件回调
        :param dstPath: 目标目录
        :param name: 文件名
        :param size: 文件大小
        :param status: 2-成功、7-失败
        :param errMsg: 错误信息
        :param isPath: 是否是目录，0-文件，1-目录
        :param createTime: 创建时间
        """
        self.finish.append({
            'taskId': self.taskId,
            'srcPath': None,
            'dstPath': dstPath,
            'isPath': isPath,
            'fileName': name,
            'fileSize': size,
            'type': 1,
            'alistTaskId': None,
            'status': status,
            'errMsg': errMsg,
            'createTime': createTime
        })

    def sync(self):
        """
        同步方法
        """
        srcPath = self.job['srcPath']
        jobExclude = self.job['exclude']
        includeRegex = self.job['include_regex']
        wantSpec = self.job['possess']
        strmSpec = self.job['strm_nfo']
        strmPath = self.job['strm_path']
        spec = None
        if jobExclude is not None:
            spec = PathSpec.from_lines(GitWildMatchPattern, jobExclude.split(':'))

        ignore_path = None
        if self.job['ignore_path'] is not None:
            ignore_path = self.job['ignore_path'].split(':')

        strm_create_cover_possess = None
        if self.job['strm_create_cover_possess'] is not None:
            strm_create_cover_possess = self.job['strm_create_cover_possess'].split(':')

        strm_src_sync_cover_possess = None
        if self.job['strm_src_sync_cover_possess'] is not None:
            strm_src_sync_cover_possess = self.job['strm_src_sync_cover_possess'].split(':')

        if not srcPath.endswith('/'):
            srcPath = srcPath + '/'
        dstPathList = self.job['dstPath'].split(':')
        i = 0
        for dstItem in dstPathList:
            i += 1
            self.syncWithHave(srcPath, dstItem, spec, wantSpec, strmSpec, strmPath, srcPath, dstItem, i == 1,
                              ignore_path, strm_create_cover_possess, strm_src_sync_cover_possess, includeRegex)
        self.scanFinish = True

    def copyFile(self, srcPath, dstPath, fileName, fileSize):
        """
        复制文件
        vm.job['method']: 0-仅新增，1-全同步，2-移动模式
        vm.job['copyHook']: 复制文件回调，（srcPath, dstPath, name, size, alistTaskId=None, status=0, errMsg=None, isPath=0）
        vm.job['delHook']: 删除文件回调，（dstPath, name, size, status=2:2-成功、7-失败, errMsg=None, isPath=0）
        :param srcPath: 源目录
        :param dstPath: 目标目录
        :param fileName: 文件名
        :param fileSize: 文件大小
        :return:
        """
        if self.breakFlag:
            return
        copyItem = CopyItem(srcPath, dstPath, fileName, fileSize, self.job['method'], self)
        self.waiting.append(copyItem)

    def delFile(self, path, fileName, size):
        """
        删除文件（或目录）
        self.job['method']: 0-仅新增，1-全同步，2-移动模式
        self.copyHook: 复制文件回调，（srcPath, dstPath, name, size, alistTaskId=None, status=0, errMsg=None, isPath=0, createTime）More actions
        self.delHook: 删除文件回调，（dstPath, name, size, status=2:2-成功、7-失败, errMsg=None, isPath=0, createTime）
        :param path: 所在路径
        :param fileName: 文件名（或目录名）
        :param size: 大小（文件）或空对象（目录）
        :return:
        """
        if self.breakFlag:
            return
        isPath = fileName.endswith('/')
        status = 2
        errMsg = None
        createTime = int(time.time())
        try:
            self.alistClient.deleteFile(path, [fileName if not isPath else fileName[:-1]], self.job['scanIntervalT'])
        except Exception as e:
            status = 7
            errMsg = str(e)
        self.delHook(path, fileName, None if isPath else size, status, errMsg, isPath, createTime)

    def listDir(self, path, firstDst, spec, wantSpec, strmSpec, rootPath, ignore_path, includeRegex, isSrc=True):
        """
        列出目录
        self.job['useCacheT']: 扫描目标目录时，是否使用缓存，0-不使用，1-使用
        self.job['scanIntervalT']: 目标目录扫描间隔，单位秒
        self.job['useCacheS']: 扫描源目录时，是否使用缓存，0-不使用，1-使用
        self.job['scanIntervalS']: 源目录扫描间隔，单位秒
        :param path:
        :param firstDst: 是否是第一个目标目录（如果是，将完整扫描源目录，否则使用缓存扫描源目录）
        :param spec:
        :param wantSpec:
        :param strmSpec: 刮削文件规则
        :param rootPath:
        :param isSrc:
        :return:
        """
        useCache = 1 if isSrc and not firstDst else self.job[f"useCache{'S' if isSrc else 'T'}"]
        scanInterval = self.job[f"scanInterval{'S' if isSrc else 'T'}"]
        try:
            return self.alistClient.fileListApi(path, useCache, scanInterval, spec, wantSpec, strmSpec, rootPath, ignore_path, includeRegex)
        except Exception as e:
            logger = logging.getLogger()
            errMsg = G('scan_error').format(G('src' if isSrc else 'dst'), str(e))
            logger.error(errMsg)
            logger.exception(e)
            self.copyHook(path if isSrc else None, None if isSrc else path, None, None, status=7, errMsg=errMsg,
                          isPath=1)
            raise e

    def getFileInfo(self, path, firstDst, spec, wantSpec, rootPath, isSrc=True):
        """
        列出目录
        self.job['useCacheT']: 扫描目标目录时，是否使用缓存，0-不使用，1-使用
        self.job['scanIntervalT']: 目标目录扫描间隔，单位秒
        self.job['useCacheS']: 扫描源目录时，是否使用缓存，0-不使用，1-使用
        self.job['scanIntervalS']: 源目录扫描间隔，单位秒
        :param path:
        :param firstDst: 是否是第一个目标目录（如果是，将完整扫描源目录，否则使用缓存扫描源目录）
        :param spec:
        :param wantSpec:
        :param rootPath:
        :param isSrc:
        :return:
        """
        useCache = 1 if isSrc and not firstDst else self.job[f"useCache{'S' if isSrc else 'T'}"]
        scanInterval = self.job[f"scanInterval{'S' if isSrc else 'T'}"]
        try:
            return self.alistClient.getFileApi(path, useCache, scanInterval)
        except Exception as e:
            logger = logging.getLogger()
            errMsg = f"获取{'源' if isSrc else '目标'}文件信息失败: {str(e)}"
            logger.error(errMsg)
            logger.exception(e)
            self.copyHook(path if isSrc else None, None if isSrc else path, None, None, status=7, errMsg=errMsg,
                          isPath=1)
            raise e

    def smart_extension_replace(self, path, new_extension):
        """智能后缀替换，处理多种情况"""
        path = Path(path)

        # 处理点号开头问题
        new_extension = new_extension.strip()
        if new_extension and not new_extension.startswith('.'):
            new_extension = '.' + new_extension

        # 特殊情况处理
        if new_extension == '.':
            new_extension = ''  # 移除所有扩展名

        # 替换后缀
        return str(path.with_suffix(new_extension))

    def replace_in_path(self, src_path, old_string, new_string):
        """处理字符串或Path对象的替换函数"""
        # 统一转换为字符串
        src_str = str(src_path)
        old_str = str(old_string)
        new_str = str(new_string)

        return src_str.replace(old_str, new_str)

    def create_strm_path(self, strmPath, srcPath, srcRootPath, strmName):
        """
        创建STRM文件路径（完整修复版本）

        :param strmPath: STRM文件基础目录
        :param srcPath: 源媒体文件路径
        :param srcRootPath: 要替换的根路径部分
        :param strmName: STRM文件名（含扩展名）
        :return: 完整的STRM文件路径（Path对象）
        """
        # 安全处理所有路径输入
        base_path = Path(strmPath)
        src_path = Path(srcPath) if not isinstance(srcPath, Path) else srcPath
        src_root = Path(srcRootPath) if not isinstance(srcRootPath, Path) else srcRootPath

        # 获取相对路径部分并进行替换
        relative_part = self.replace_in_path(src_path, src_root, '')

        # 清理路径中的多余斜杠
        relative_part = relative_part.replace('\\', '/').strip('/')

        # 构建目标路径（使用Path操作符）
        strm_path = base_path / relative_part / strmName

        return strm_path

    def create_strm_file(self, strmPath, srcPath, srcRootPath, strmName, raw_url):
        """
        创建STRM文件路径（完整修复版本）

        :param strmPath: STRM文件基础目录
        :param srcPath: 源媒体文件路径
        :param srcRootPath: 要替换的根路径部分
        :param strmName: STRM文件名（含扩展名）
        :return: 完整的STRM文件路径（Path对象）
        """
        msg = None
        logger = logging.getLogger()
        try:
            strm_path = self.create_strm_path(strmPath, srcPath, srcRootPath, strmName)
            logger.info(f'strm保存信息路径[{strm_path}],保存内容[{raw_url}]')
            # 创建父目录（如果需要）
            Path(strm_path).parent.mkdir(parents=True, exist_ok=True)

            # 写入文件
            with open(strm_path, "w", encoding="utf-8") as f:
                f.write(raw_url)
            logger.info(f"文件已成功保存到: {strm_path}")
            logger.info(f"文件大小: {os.path.getsize(strm_path)} 字节")
            
            # 保存需要刷新的路径，任务结束后统一处理
            try:
                # 获取strm文件所在的目录路径
                strm_dir = os.path.dirname(strm_path)
                path = strm_dir.replace('\\', '/')
                # 将路径添加到集合中，自动去重
                self.feiniu_refresh_paths.add(path)
                logger.info(f"保存需要刷新的路径: {strm_dir} -> 处理后: {path}")
            except Exception as e:
                logger.error(f"保存刷新路径失败: {strm_dir}, 错误: {str(e)}")
            
            msg = str(strm_path)

        except PermissionError as e:
            errMsg = G('strm_file_error').format(G('src'), '错误：没有写入权限，请尝试其他目录', str(e))
            logger.error(errMsg)
            logger.exception(e)
            self.copyHook(srcPath, None, None, None, status=7,
                          errMsg=errMsg,
                          isPath=0)
        except FileNotFoundError as e:
            errMsg = G('strm_file_error').format(G('src'), '错误：路径无效，请检查格式', str(e))
            logger.error(errMsg)
            logger.exception(e)
            self.copyHook(srcPath, None, None, None, status=7,
                          errMsg=errMsg,
                          isPath=0)
        except Exception as e:
            errMsg = G('strm_file_error').format(G('src'), '发生未知错误', str(e))
            logger.error(errMsg)
            logger.exception(e)
            self.copyHook(srcPath, None, None, None, status=7,
                          errMsg=errMsg,
                          isPath=0)
        finally:
            return msg

    def createFile(self, strmPath, srcPath, srcRootPath, strmName, raw_url):
        """
        创建文件
        :param srcPath: 源目录
        :param dstPath: 目标目录
        :param fileName: 文件名
        :param fileSize: 文件大小
        :return:
        """
        if self.breakFlag:
            return
        createStrmItem = CreateStrmItem(strmPath, srcPath, srcRootPath, strmName, raw_url, self)
        self.waiting.append(createStrmItem)

    def is_path_prefix(self, file_path, prefix_list):
        """更安全的路径前缀检查，处理结尾分隔符"""
        # 处理prefix_list为None或空的情况
        if not prefix_list:
            return False
            
        for prefix in prefix_list:
            if not prefix.endswith("/"):
                prefix = prefix + "/"
            # 统一添加路径分隔符防止误匹配
            # safe_prefix = prefix.rstrip(os.sep) + os.sep
            if file_path.startswith(prefix):
                return True

            # 额外检查精确匹配的情况
            if file_path == prefix or file_path == prefix.rstrip(os.sep):
                return True

        return False

    def update_file_if_changed(self, new_content, file_path):
        """
        比较内容并仅在更改时写入文件

        参数:
            new_content (str): 要写入的新内容
            file_path (str): 目标文件路径

        返回:
            bool: 是否进行了更新
        """
        try:
            # 如果文件不存在，直接创建
            if not os.path.exists(file_path):
                logging.info(f"文件不存在，创建: {file_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True

            # 读取现有文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            # 比较内容哈希值
            existing_hash = hashlib.md5(existing_content.encode('utf-8')).hexdigest()
            new_hash = hashlib.md5(new_content.encode('utf-8')).hexdigest()

            # 内容相同时跳过
            if existing_hash == new_hash:
                logging.debug(f"内容未变化，跳过: {file_path}")
                return False

            # 内容不同则更新
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logging.info(f"内容已更新: {file_path}")
            return True

        except Exception as e:
            logging.error(f"处理文件出错 {file_path}: {str(e)}")
            raise

    def syncWithHave(self, srcPath, dstPath, spec, wantSpec, strmSpec, strmPath, srcRootPath, dstRootPath, firstDst,
                              ignore_path, strm_create_cover_possess, strm_src_sync_cover_possess, includeRegex):
        """
        扫描并同步-目标目录存在目录（意味着要继续扫描目标目录）
        :param srcPath: 来源路径，以/结尾
        :param dstPath: 目标路径，以/结尾
        :param spec: 排除项规则
        :param wantSpec: 需要项规则
        :param strmSpec: strm刮削项规则
        :param strmPath: strm文件存放地址
        :param srcRootPath: 来源目录根目录，以/结尾
        :param dstRootPath: 目标目录根目录，以/结尾
        :param firstDst: 是否是第一个目标目录（如果是，将完整扫描源目录，否则使用缓存扫描源目录）
        :return:
        """
        if self.breakFlag:
            return
        try:
            srcFiles = self.listDir(srcPath, firstDst, spec, wantSpec, strmSpec, srcRootPath, ignore_path, includeRegex)
            dstFiles = self.listDir(dstPath, firstDst, spec, wantSpec, strmSpec, dstRootPath, ignore_path, includeRegex, False)
        except Exception:
            # 已在listDir做出日志打印等操作，此处啥都不用做
            return
        logger = logging.getLogger()
        # 创建一个集合来记录已处理的源文件
        processed_src_files = set()
        # 判断将刮削文件同步至源目录
        if self.job['method'] == 3 and self.job['strm_src_sync'] == 1 and strmSpec:
            for key in dstFiles.keys():
                # 如果是文件
                if not key.endswith('/') and re.search(strmSpec, key):
                    logger.info(f'[{dstPath + key}]符合刮削文件同步正则')
                    # 目标目录没有这个文件或文件大小不匹配(即需要同步)
                    if key not in srcFiles or dstFiles[key]['size'] != srcFiles[key]['size'] \
                            or (self.job['strm_src_sync_cover'] == 1
                                and self.is_path_prefix(srcPath, strm_src_sync_cover_possess)):
                        logger.info(f'[{dstPath + key}]源目录没有这个文件或该目录需要强制同步(即需要同步)')
                        self.copyFile(dstPath, srcPath, key, dstFiles[key]['size'])
                        processed_src_files.add(key)

        # 判断删除目标目录在源目录不存在的文件
        if self.job['method'] == 3 and self.job['strm_dst_sync'] == 1:
            for dstKey in dstFiles.keys():
                if dstKey not in srcFiles:
                    logger.info(f'[{dstPath + dstKey}]源目录没有这个文件或文件夹需要删除')
                    if dstKey.endswith('/'):
                        logger.info(f'[{dstPath + dstKey}]源目录没有这个文件夹删除')
                        self.delFile(dstPath, dstKey, dstFiles[dstKey]['size'])
                    else:
                        if re.search("\.(strm)$", dstKey):
                            logger.info(f'[{dstPath + dstKey}]源目录没有这个strm文件删除')
                            self.delFile(dstPath, dstKey, dstFiles[dstKey]['size'])

        for key in srcFiles.keys():
            # 如果是文件
            if not key.endswith('/'):
                if self.job['method'] == 3:
                    if strmSpec:
                        logger.info(f'存在下载规则{strmSpec}正在为[{srcPath + key}]匹配......')
                        if re.search(strmSpec, key):
                            logger.info(f'[{srcPath + key}]符合下载文件正则')
                            # 检查是否已处理过此文件
                            if key in processed_src_files:
                                logger.info(f'[{srcPath + key}]已处理过，跳过下载')
                                continue
                            # 目标目录没有这个文件或文件大小不匹配(即需要同步)
                            if key not in dstFiles or dstFiles[key]['size'] != srcFiles[key]['size']:
                                logger.info(f'[{srcPath + key}]目标目录没有这个文件或文件大小不匹配(即需要同步)')
                                self.copyFile(srcPath, dstPath, key, srcFiles[key]['size'])
                        else:
                            logger.info(f'[{srcPath + key}]不符合下载文件正则')

                    if wantSpec:
                        if re.search(wantSpec, key):
                            strmName = self.smart_extension_replace(key, '.strm')
                            logger.info(f'strm文件名[{srcPath + strmName}]')
                            strm_url_prefix = self.alistClient.url
                            if self.job['strm_url_prefix']:
                                strm_url_prefix = self.job['strm_url_prefix']
                            raw_url = strm_url_prefix + '/d' + srcPath + key
                            if srcFiles[key]['sign']:
                                raw_url = raw_url + '?sign=' + srcFiles[key]['sign']

                            if (self.job['strm_create_cover'] == 1 and self.is_path_prefix(srcPath, strm_create_cover_possess)) or strmName not in dstFiles:
                                logger.info(f'不存在[{srcPath + strmName}]开始创建......')
                                self.createFile(strmPath, srcPath, srcRootPath, strmName, raw_url)
                            else:
                                if self.job['strm_create_cover'] == 1 and self.is_path_prefix(srcPath, strm_create_cover_possess):
                                    self.update_file_if_changed(raw_url, strmPath + strmName)
                                logger.info(f'存在strm文件[{srcPath + strmName}]跳过生成......')
                else:
                    # 目标目录没有这个文件或文件大小不匹配(即需要同步)
                    if key not in dstFiles or dstFiles[key]['size'] != srcFiles[key]['size']:
                        self.copyFile(srcPath, dstPath, key, srcFiles[key]['size'])
            # 如果是目录
            else:
                # 目标目录没有这个目录
                if key not in dstFiles:
                    self.syncWithOutHave(srcPath + key, dstPath + key, spec, wantSpec, strmSpec, strmPath, srcRootPath,
                                         dstRootPath, firstDst, ignore_path, strm_create_cover_possess,
                                         strm_src_sync_cover_possess, includeRegex)
                # 目标目录有这个目录，继续递归
                else:
                    self.syncWithHave(srcPath + key, dstPath + key, spec, wantSpec, strmSpec, strmPath, srcRootPath,
                                      dstRootPath, firstDst, ignore_path, strm_create_cover_possess,
                                      strm_src_sync_cover_possess, includeRegex)
        if self.job['method'] == 1:
            for dstKey in dstFiles.keys():
                if dstKey not in srcFiles:
                    self.delFile(dstPath, dstKey, dstFiles[dstKey]['size'])

    def syncWithOutHave(self, srcPath, dstPath, spec, wantSpec, strmSpec, strmPath, srcRootPath, dstRootPath, firstDst,
                        ignore_path, strm_create_cover_possess, strm_src_sync_cover_possess, includeRegex):
        """
        扫描并同步-目标目录为空
        :param srcPath: 来源路径，以/结尾
        :param dstPath: 目标路径，以/结尾
        :param spec:
        :param wantSpec:
        :param strmSpec: strm刮削项规则
        :param strmPath: strm文件存放地址
        :param srcRootPath:
        :param dstRootPath:
        :param firstDst:
        :param includeRegex: 包含的正则表达式
        :return:
        """
        if self.breakFlag:
            return
        status = 2
        errMsg = None
        try:
            self.alistClient.mkdir(dstPath, self.job['scanIntervalT'])
        except Exception as e:
            status = 7
            errMsg = str(e)
        # 目录回调
        self.copyHook(srcPath, dstPath, None, None, status=status, errMsg=errMsg, isPath=1)
        if status != 2:
            return
        try:
            srcFiles = self.listDir(srcPath, firstDst, spec, wantSpec, strmSpec, srcRootPath, ignore_path, includeRegex)
        except Exception:
            # 已在listDir做出日志打印等操作，此处啥都不用做
            return
        for key in srcFiles.keys():
            if self.breakFlag:
                break
            if key.endswith('/'):
                self.syncWithOutHave(srcPath + key, dstPath + key, spec, wantSpec, strmSpec, strmPath, srcRootPath,
                                     dstRootPath, firstDst, ignore_path, strm_create_cover_possess,
                                     strm_src_sync_cover_possess, includeRegex)
            else:
                if self.job['method'] == 3:
                    logger = logging.getLogger()
                    if strmSpec:
                        logger.info(f'存在下载规则[{strmSpec}]正在为[{srcPath + key}]匹配......')
                        if re.search(strmSpec, key):
                            logger.info(f'[{srcPath + key}]符合下载文件正则直接下载')
                            # 目标目录没有这个文件或文件大小不匹配(即需要同步)
                            self.copyFile(srcPath, dstPath, key, srcFiles[key]['size'])

                    if wantSpec:
                        if re.search(wantSpec, key):
                            strmName = self.smart_extension_replace(key, '.strm')
                            logger.info(f'strm文件名[{srcPath + strmName}]')
                            strm_url_prefix = self.alistClient.url
                            if self.job['strm_url_prefix']:
                                strm_url_prefix = self.job['strm_url_prefix']
                            raw_url = strm_url_prefix + '/d' + srcPath + key
                            if srcFiles[key]['sign']:
                                raw_url = raw_url + '?sign=' + srcFiles[key]['sign']
                            self.createFile(strmPath, srcPath, srcRootPath, strmName, raw_url)
                else:
                    self.copyFile(srcPath, dstPath, key, srcFiles[key]['size'])

    def updateTaskStatus(self):
        """
        所有任务完成后，最终更新任务状态
        """
        self.getCurrent()
        failOrOtherNum = len(self.currentTasks[7]) + len(self.currentTasks[-1])
        status = 7 if self.breakFlag else 2 if failOrOtherNum == 0 else 3
        taskService.updateJobTaskStatus(self.taskId, status, taskList=self.currentTasks, createTime=self.createTime)

    def advanced_paginate(self, data: list, page: int = 1, page_size: int = 10,
                          allow_empty: bool = False, include_all: bool = False) -> dict:
        """
        高级列表分页函数

        参数:
            data: 需要分页的数据列表
            page: 当前页码(默认为1)
            page_size: 每页大小(默认10)
            allow_empty: 是否允许返回空页(默认False，返回最后一页)
            include_all: 是否添加所有数据的总列表(默认False)
        """
        total_items = len(data)

        # 处理无效输入
        if page < 1 or page_size < 1 or not isinstance(data, list):
            raise ValueError("Invalid input parameters")

        # 计算总页数
        total_pages = max(1, (total_items + page_size - 1) // page_size)  # 确保至少有1页

        # 处理超出范围的页码
        if page > total_pages:
            if allow_empty:
                return {
                    'data': [],
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages,
                    'total_items': total_items
                }
            else:
                page = total_pages  # 返回最后一页

        # 计算分页切片
        start = (page - 1) * page_size
        end = min(start + page_size, total_items)  # 防止索引越界

        # 构建返回结果
        result = {
            'data': data[start:end],
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'total_items': total_items,
            'start_index': start + 1,  # 基于1的起始索引
            'end_index': end,  # 结束索引
        }

        # 可选：包含完整数据(谨慎使用，大数据集可能影响性能)
        if include_all:
            result['all_data'] = data.copy()

        return result


class JobClient:
    def __init__(self, job, isInit=False):
        """
        初始化job
        :param job: {id(新增时不需要), enable, srcPath, dstPath, alistId, useCacheT, scanIntervalT, useCacheS, scanIntervalS, method, interval, exclude, cron相关}
        """
        addJobId = 0
        if 'enable' not in job:
            job['enable'] = 1
        if 'method' not in job:
            job['method'] = 0
        if 'copy' in job:
            job['remark'] = f'{job["remark"]}-copy{"".join(secrets.choice(string.digits) for _ in range(6))}'
            job['srcPath'] = f'{job["srcPath"]}copy{"".join(secrets.choice(string.digits) for _ in range(6))}'
            job['dstPath'] = f'{job["dstPath"]}copy{"".join(secrets.choice(string.digits) for _ in range(6))}'
            addJobId = jobMapper.addJob(job)
            job = jobMapper.getJobById(addJobId)
        if 'id' not in job:
            addJobId = jobMapper.addJob(job)
            job = jobMapper.getJobById(addJobId)
        self.jobId = job['id']
        self.job = job
        self.scheduled = None
        self.scheduledJob = None
        self.jobDoing = False
        # 正在执行中的作业信息；仅在内存中，不入库，高速读写；执行完毕后批量入库，如果遇到异常终止，不会补偿入库
        # 单项结构 {
        #   'taskId':   所属任务id
        #   'alistTaskId': alist任务id
        #   'srcPath':  来源路径
        #   'dstPath':  目标路径
        #   'fileName': 文件名或者文件目录名
        #   'fileSize': 文件大小
        #   'status':   状态 0-等待中，1-运行中，2-成功，3-取消中，4-已取消，5-出错（将重试），
        #               6-失败中，7-已失败，8-等待重试中，9-等待重试回调执行中
        #   'progress': 进度
        #   'errMsg':   失败原因
        # }
        self.currentJobTask = None
        try:
            self.doByTime()
        except Exception as e:
            if isInit or addJobId != 0:
                # 仅在初始化和新增任务时删除错误的任务
                logger = logging.getLogger()
                logger.error(G('del_job_course_error').format(json.dumps(self.job)))
                jobMapper.deleteJob(self.jobId)
            raise e

    def doJob(self):
        """
        执行作业
        :return:
        """
        while self.jobDoing:
            if self.job['enable'] == 0:
                return
            time.sleep(10)
        self.jobDoing = True
        taskId = None
        try:
            taskId = jobMapper.addJobTask({
                'jobId': self.jobId,
                'runTime': int(time.time())
            })
            if self.job['enable'] == 0:
                raise Exception("abort")
            self.currentJobTask = JobTask(taskId, self)
        except Exception as e:
            self.jobDoing = False
            logger = logging.getLogger()
            errMsg = G('do_job_err').format(str(e))
            logger.error(errMsg)
            if taskId is not None:
                taskService.updateJobTaskStatus(taskId, 6, errMsg)
            logger.exception(e)

    def doManual(self):
        """
        手动执行作业
        :return:
        """
        if self.jobDoing:
            raise Exception(G('job_running'))
        doJobThread = threading.Thread(target=self.doJob, name=f'手动触发任务线程{self.jobId}')
        doJobThread.start()

    def doByTime(self):
        params = {
            'func': self.doJob,
            'trigger': 'interval' if self.job['isCron'] == 0 else 'cron'
        }
        if self.job['isCron'] == 0:
            interval = self.job['interval']
            if interval is not None and str(interval).strip() != '':
                params['minutes'] = interval
            else:
                raise Exception(G('interval_lost'))
        elif self.job['isCron'] == 1:
            flag = 0
            for item in ['year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second', 'start_date',
                         'end_date']:
                if item in self.job and self.job[item] is not None and self.job[item] != '':
                    flag += 1
                    params[item] = self.job[item]
            if flag == 0:
                raise Exception(G('cron_lost'))
        else:
            return
        self.scheduled = BackgroundScheduler()
        self.scheduledJob = self.scheduled.add_job(**params)
        self.scheduled.start()
        if self.job['enable'] == 0:
            self.scheduledJob.pause()

    def resumeJob(self):
        """
        恢复作业
        :return:
        """
        if self.scheduledJob is None:
            raise Exception(G('cannot_resume_lost_job'))
        else:
            jobMapper.updateJobEnable(self.jobId, 1)
            self.job['enable'] = 1
            self.scheduledJob.resume()

    def abortJob(self):
        """
        中止作业
        :return:
        """
        if self.currentJobTask:
            self.currentJobTask.breakFlag = True

    def retryJob(self):
        """
        重试作业
        :return:
        """
        if self.currentJobTask:
            self.currentJobTask.retryJob()

    def stopJob(self, remove=False):
        """
        停止作业（适用于修改enable）
        :param remove: 是否删除作业，否一般用于禁用作业
        :return:
        """
        self.job['enable'] = 0
        if self.currentJobTask:
            self.currentJobTask.breakFlag = True
        if remove:
            if self.scheduled is not None:
                try:
                    self.scheduled.shutdown(wait=False)
                except Exception as e:
                    logger = logging.getLogger()
                    logger.warning(G('stop_fail').format(str(e)))
                    logger.exception(e)
                self.scheduled = None
        else:
            if self.scheduledJob is not None:
                try:
                    self.scheduledJob.pause()
                except Exception as e:
                    logger = logging.getLogger()
                    logger.warning(G('disable_fail').format(str(e)))
                    logger.exception(e)
        self.jobDoing = False
        if not remove:
            jobMapper.updateJobEnable(self.jobId, 0)
            jobMapper.updateJobTaskStatusByStatusAndJobId(self.jobId)
