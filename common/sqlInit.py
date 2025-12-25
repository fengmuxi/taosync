from common import commonUtils
from common import sqlBase


@sqlBase.connect_sql
def init_sql(conn):
    cuVersion = 251219  # 更新版本号，添加飞牛刷新任务表
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE name='user_list'")
    passwd = None
    if cursor.fetchone() is None:
        passwd = commonUtils.generatePasswd()
        cursor.execute("create table user_list("
                       "id integer primary key autoincrement,"
                       "userName text,"                             # 用户名
                       "passwd text,"                               # 密码
                       f"sqlVersion integer DEFAULT {cuVersion},"   # 数据库版本
                       "createTime integer DEFAULT (strftime('%s', 'now'))"
                       ")")
        cursor.execute("insert into user_list(userName, passwd) values ('admin', ?)",
                       (commonUtils.passwd2md5(passwd), ))
        cursor.execute("create table alist_list("
                       "id integer primary key autoincrement,"
                       "remark text,"       # 备注
                       "url text,"          # 地址，例如http://localhost:5244
                       "userName text,"     # 用户名
                       "token text,"        # 令牌
                       "createTime integer DEFAULT (strftime('%s', 'now')),"
                       " unique (url, userName))")
        cursor.execute("create table job("
                       "id integer primary key autoincrement,"
                       "enable integer DEFAULT 1,"          # 启用，1-启用，0-停用
                       "remark text,"                       # 备注
                       "srcPath text,"                      # 来源目录，结尾有无斜杠都可，建议有斜杠
                       "dstPath text,"                      # 目标目录，结尾有无斜杠都可，建议有斜杠，多个以英文冒号[:]分隔
                       "alistId integer,"                   # 引擎id，alist_list.id
                       "useCacheT integer DEFAULT 0,"       # 扫描目标目录时，是否使用缓存，0-不使用，1-使用
                       "scanIntervalT integer DEFAULT 0,"   # 目标目录扫描间隔，单位秒
                       "useCacheS integer DEFAULT 0,"       # 扫描源目录时，是否使用缓存，0-不使用，1-使用
                       "scanIntervalS integer DEFAULT 0,"   # 源目录扫描间隔，单位秒
                       "method integer,"                    # 同步方式，0-仅新增，1-全同步，2-移动模式
                       "interval integer,"                  # 同步间隔，单位：分钟
                       "isCron integer DEFAULT 0,"          # 是否使用cron，0-使用interval, 1-使用cron，2-仅手动
                       "year text DEFAULT NULL,"            # 四位数的年份
                       "month text DEFAULT NULL,"           # 1-12月
                       "day text DEFAULT NULL,"             # 1-31日
                       "week text DEFAULT NULL,"            # 1-53
                       "day_of_week text DEFAULT NULL,"     # 0-6
                       "hour text DEFAULT NULL,"            # 0-23
                       "minute text DEFAULT NULL,"          # 0-59
                       "second text DEFAULT NULL,"          # 0-59
                       "start_date text DEFAULT NULL,"      # 开始时间
                       "end_date text DEFAULT NULL,"        # 结束时间
                       "exclude text DEFAULT NULL,"         # 排除无需同步项，类似gitignore语法，英文冒号分隔多个规则
                       "ignore_path text DEFAULT NULL,"     # 排除无需同步项路径前缀，英文冒号分隔多个规则
                       "include_regex text DEFAULT NULL,"   # 匹配同步文件夹的全路径正则表达式
                       "possess text DEFAULT NULL,"         # 文件匹配正则
                       "strm_nfo text DEFAULT NULL,"        # 筛选strm刮削文件同步项，文件匹配正则
                       "strm_path text DEFAULT NULL,"       # strm文件保存路径
                       "strm_url_prefix text DEFAULT NULL," # strm文件保存内容前缀
                       "strm_create_cover integer DEFAULT 0," # strm文件生成是否覆盖更新本地原有文件
                       "strm_create_cover_possess text DEFAULT NULL," # strm文件生成是否覆盖更新本地原有文件路径匹配项，留空则全匹配
                       "strm_src_sync integer DEFAULT 0,"   # 生成strm文件时同步目录，是否允许刮削文件同步至源目录，0-不使用，1-使用
                       "strm_src_sync_cover integer DEFAULT 0,"   # 生成strm文件时同步目录，是否允许刮削文件同步至源目录并覆盖，0-不使用，1-使用
                       "strm_src_sync_cover_possess text DEFAULT NULL," # 生成strm文件时同步目录，允许刮削文件同步至源目录并覆盖路径匹配项，留空则全匹配
                       "strm_dst_sync integer DEFAULT 0,"   # 生成strm文件时同步目录，是否允许删除目标目录多余strm文件，0-不使用，1-使用
                       "feiniuId integer DEFAULT NULL,"      # 飞牛配置ID
                       "feiniu_library_id text DEFAULT NULL," # 飞牛媒体库ID
                       "feiniu_media_path text DEFAULT NULL," # 飞牛媒体库路径映射
                       "createTime integer DEFAULT (strftime('%s', 'now')),"
                       " unique (srcPath, dstPath, alistId))")
        cursor.execute("create table job_task("
                       "id integer primary key autoincrement,"
                       "jobId integer,"             # 所属工作id，job.id
                       "status integer DEFAULT 1,"  # 状态，0-等待中，1-进行中，2-成功，3-完成（部分失败），4-因重启而中止，5-超时，6-失败，7-手动终止
                       "errMsg text,"               # 失败原因
                       "runTime integer,"           # 开始时间，秒级时间戳
                       "taskNum text,"              # 结果数量json字符串
                       "createTime integer DEFAULT (strftime('%s', 'now'))"
                       ")")
        cursor.execute("create table job_task_item("
                       "id integer primary key autoincrement,"
                       "taskId integer,"            # 所属任务id，job_task.id
                       "srcPath text,"              # 来源路径
                       "dstPath text,"              # 目标路径
                       "isPath integer DEFAULT 0,"  # 是否是目录，0-文件，1-目录
                       "fileName text,"             # 文件名
                       "fileSize integer,"          # 文件大小
                       "type integer,"              # 操作类型，0-复制，1-删除，2-移动
                       "alistTaskId text,"          # alist任务id，仅限复制任务，否则为空
                       "status integer DEFAULT 0,"  # 状态，0-等待中，1-运行中，2-成功，3-取消中，4-已取消，5-出错（将重试），6-失败中
                                                    # ，7-已失败，8-等待重试中，9-等待重试回调执行中
                                                    # 对于删除任务，只有0-等待、2-成功、7-失败
                       "progress real,"             # 进度，仅限复制任务，否则为空
                       "errMsg text,"               # 失败原因
                       "createTime integer DEFAULT (strftime('%s', 'now'))"
                       ")")
        cursor.execute("create table notify( "
                       "id integer primary key autoincrement, "
                       "enable integer DEFAULT 1,"  # 启用，1-启用，0-停用
                       "method integer,"            # 方式：0-自定义；1-server酱；2-钉钉；待扩展更多
                       "params text,"               # 以json字符串存储参数
                       "createTime integer DEFAULT (strftime('%s', 'now'))"
                       ")")
        cursor.execute("create table feiniu_list( "
                       "id integer primary key autoincrement, "
                       "host text,"                  # 飞牛影视服务地址
                       "username text,"              # 用户名
                       "password text,"              # 密码
                       "library_id text,"            # 媒体库ID
                       "enable integer DEFAULT 1,"   # 是否启用，1-启用，0-停用
                       "remark text,"                # 备注
                       "createTime integer DEFAULT (strftime('%s', 'now'))"
                       ")")
        # 创建飞牛刷新任务表
        cursor.execute("create table feiniu_refresh_task(" 
                       "id integer primary key autoincrement," 
                       "feiniuId integer,"            # 飞牛配置ID
                       "jobId integer,"               # 关联的作业ID
                       "media_library_id text,"       # 媒体库ID
                       "folder_paths text,"           # 刷新路径列表（JSON格式）
                       "operation_type text,"         # 操作类型（refresh）
                       "status integer DEFAULT 0,"    # 状态（0-执行中，1-成功，2-失败）
                       "start_time integer,"          # 开始时间戳
                       "end_time integer,"            # 结束时间戳
                       "elapsed_time real,"           # 耗时（秒）
                       "error_msg text,"              # 错误信息
                       "retry_count integer DEFAULT 0" # 重试次数
                       ")")
        # 创建消息记录表
        cursor.execute('''
            CREATE TABLE notify_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notify_id INTEGER NOT NULL,
            user_id INTEGER DEFAULT 0,
            message_type TEXT DEFAULT '',
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            send_time INTEGER NOT NULL,
            status INTEGER NOT NULL DEFAULT 0, -- 0: 失败, 1: 成功
            message TEXT DEFAULT '',
            device_info TEXT DEFAULT '',
            create_time INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
        )
        ''')
        # 创建消息记录表索引
        cursor.execute('CREATE INDEX idx_notify_log_notify_id ON notify_log(notify_id)')
        cursor.execute('CREATE INDEX idx_notify_log_user_id ON notify_log(user_id)')
        cursor.execute('CREATE INDEX idx_notify_log_send_time ON notify_log(send_time)')
        cursor.execute('CREATE INDEX idx_notify_log_status ON notify_log(status)')
        cursor.execute('CREATE INDEX idx_notify_log_message_type ON notify_log(message_type)')
        conn.commit()
    else:
        try:
            cursor.execute("SELECT sqlVersion FROM user_list limit 1")
            sqlVersion = cursor.fetchone()[0]
        except Exception as e:
            sqlVersion = 0
            if 'sqlVersion' not in str(e):
                import logging
                logger = logging.getLogger()
                logger.exception(e)
        if sqlVersion < cuVersion:
            if sqlVersion < 240731:
                cursor.execute(f"alter table user_list add column sqlVersion integer default {cuVersion}")
                cursor.execute("alter table job_task add column errMsg text")
            if sqlVersion < 240813:
                cursor.execute("alter table job drop column cron")
                cursor.execute("alter table job add column isCron integer DEFAULT 0")
                cursor.execute("alter table job add column year text DEFAULT NULL")
                cursor.execute("alter table job add column month text DEFAULT NULL")
                cursor.execute("alter table job add column day text DEFAULT NULL")
                cursor.execute("alter table job add column week text DEFAULT NULL")
                cursor.execute("alter table job add column day_of_week text DEFAULT NULL")
                cursor.execute("alter table job add column hour text DEFAULT NULL")
                cursor.execute("alter table job add column minute text DEFAULT NULL")
                cursor.execute("alter table job add column second text DEFAULT NULL")
                cursor.execute("alter table job add column start_date text DEFAULT NULL")
                cursor.execute("alter table job add column end_date text DEFAULT NULL")
            if sqlVersion < 240905:
                cursor.execute("alter table job add column exclude text DEFAULT NULL")
            if sqlVersion < 241014:
                cursor.execute("create table notify("
                               "id integer primary key autoincrement,"
                               "enable integer DEFAULT 1,"
                               "method integer,"
                               "params text,"
                               "createTime integer DEFAULT (strftime('%s', 'now'))"
                               ")")
            if sqlVersion < 250307:
                cursor.execute("alter table job_task add column taskNum text")
            if sqlVersion < 250416:
                cursor.execute("alter table job add column remark text")
            if sqlVersion < 250520:
                cursor.execute("alter table job_task_item add column isPath integer DEFAULT 0")
            if sqlVersion < 250608:
                cursor.execute("alter table job rename column speed to useCacheT")
                cursor.execute("alter table job add column scanIntervalT integer DEFAULT 0")
                cursor.execute("alter table job add column useCacheS integer DEFAULT 0")
                cursor.execute("alter table job add column scanIntervalS integer DEFAULT 0")
                cursor.execute("alter table job add column possess text DEFAULT NULL")
                cursor.execute("alter table job add column strm_nfo text DEFAULT NULL")
                cursor.execute("alter table job add column strm_path text DEFAULT NULL")
                cursor.execute("update job set scanIntervalT = 10, useCacheT = 0 where useCacheT = 2")
            if sqlVersion < 250618:
                cursor.execute("alter table job add column strm_url_prefix text DEFAULT NULL")
            if sqlVersion < 250619:
                cursor.execute("alter table job add column strm_src_sync integer DEFAULT 0")
                cursor.execute("alter table job add column strm_dst_sync integer DEFAULT 0")
            if sqlVersion < 250625:
                cursor.execute("alter table job add column ignore_path text DEFAULT NULL")
                cursor.execute("alter table job add column strm_create_cover integer DEFAULT 0")
                cursor.execute("alter table job add column strm_create_cover_possess text DEFAULT NULL")
                cursor.execute("alter table job add column strm_src_sync_cover integer DEFAULT 0")
                cursor.execute("alter table job add column strm_src_sync_cover_possess text DEFAULT NULL")
            if sqlVersion < 251201:
                cursor.execute("alter table job add column include_regex text DEFAULT NULL")
            if sqlVersion < 251202:
                cursor.execute("create table feiniu_list( "
                               "id integer primary key autoincrement, "
                               "host text,"                  # 飞牛影视服务地址
                               "username text,"              # 用户名
                               "password text,"              # 密码
                               "library_id text,"            # 媒体库ID
                               "enable integer DEFAULT 1,"   # 是否启用，1-启用，0-停用
                               "remark text,"                # 备注
                               "createTime integer DEFAULT (strftime('%s', 'now'))"
                               ")")
            if sqlVersion < 251212:
                # 添加飞牛配置相关字段到job表
                cursor.execute("alter table job add column feiniuId integer DEFAULT NULL")
                cursor.execute("alter table job add column feiniu_library_id text DEFAULT NULL")
                cursor.execute("alter table job add column feiniu_media_path text DEFAULT NULL")
            if sqlVersion < 251213:
                # 添加统一路径映射字段
                cursor.execute("alter table job add column strm_path_mapping text DEFAULT NULL")
            if sqlVersion < 251216:
                # 创建消息记录表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS notify_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notify_id INTEGER NOT NULL,
                    user_id INTEGER DEFAULT 0,
                    message_type TEXT DEFAULT '',
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    send_time INTEGER NOT NULL,
                    status INTEGER NOT NULL DEFAULT 0, -- 0: 失败, 1: 成功
                    message TEXT DEFAULT '',
                    device_info TEXT DEFAULT '',
                    create_time INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
                )
                ''')
                # 创建消息记录表索引
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notify_log_notify_id ON notify_log(notify_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notify_log_user_id ON notify_log(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notify_log_send_time ON notify_log(send_time)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notify_log_status ON notify_log(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notify_log_message_type ON notify_log(message_type)')
            if sqlVersion < 251219:
                # 创建飞牛刷新任务表
                cursor.execute("create table feiniu_refresh_task( "
                               "id integer primary key autoincrement, "
                               "feiniuId integer,"            # 飞牛配置ID
                               "jobId integer,"               # 关联的作业ID
                               "media_library_id text,"       # 媒体库ID
                               "folder_paths text,"           # 刷新路径列表（JSON格式）
                               "operation_type text,"         # 操作类型（refresh）
                               "status integer DEFAULT 0,"    # 状态（0-执行中，1-成功，2-失败）
                               "start_time integer,"          # 开始时间戳
                               "end_time integer,"            # 结束时间戳
                               "elapsed_time real,"           # 耗时（秒）
                               "error_msg text,"              # 错误信息
                               "retry_count integer DEFAULT 0" # 重试次数
                               ")")
            cursor.execute(f"update user_list set sqlVersion={cuVersion}")
            conn.commit()
    cursor.close()
    return passwd
