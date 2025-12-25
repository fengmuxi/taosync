"""
@Author：dr34m
@Date  ：2024/12/1 10:00 
"""
from common import sqlBase
from common.LNG import G

def getFeiniuList():
    return sqlBase.fetchall_to_table("select * from feiniu_list")


def getFeiniuById(feiniuId):
    rst = sqlBase.fetchall_to_table("select * from feiniu_list where id=?", (feiniuId,))
    if rst:
        return rst[0]
    else:
        raise Exception(G('feiniu_not_found'))


def getEnabledFeiniu():
    rst = sqlBase.fetchall_to_table("select * from feiniu_list where enable=1")
    if rst:
        return rst[0]
    else:
        return None


def addFeiniu(feiniu):
    return sqlBase.execute_insert("insert into feiniu_list (remark, host, username, password, enable) "
                                  "values (:remark, :host, :username, :password, :enable)", feiniu)


def updateFeiniu(feiniu):
    # 动态构建更新语句，只在有密码字段时才更新密码
    base_fields = ['remark', 'host', 'username', 'enable']
    update_fields = []
    params = {}
    
    # 添加基础字段
    for field in base_fields:
        if field in feiniu:
            update_fields.append(f"{field}=:{field}")
            params[field] = feiniu[field]
    
    # 只在有密码字段时才更新密码
    if 'password' in feiniu:
        update_fields.append("password=:password")
        params['password'] = feiniu['password']
    
    # 必须包含id
    params['id'] = feiniu['id']
    
    if not update_fields:
        raise Exception("没有提供任何需要更新的字段")
    
    sql = f"update feiniu_list set {', '.join(update_fields)} where id=:id"
    sqlBase.execute_update(sql, params)


def removeFeiniu(feiniuId):
    sqlBase.execute_update("delete from feiniu_list where id=?", (feiniuId,))
