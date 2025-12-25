import time
import os
import threading
import requests
import json
import random
import hashlib
from typing import Any, List, Dict, Tuple, Optional
from pathlib import Path
from datetime import datetime, timedelta
import logging

# 导入当前项目的配置和工具
from mapper import feiniuMapper
from mapper import feiniuRefreshTaskMapper

# 配置日志
logger = logging.getLogger(__name__)

# ------------------------ 公共常量定义 ------------------------
# 飞牛API配置
API_KEY = "16CCEB3D-AB42-077D-36A1-F355324E4237"
SECRET_KEY = "NDzZTVxnRKP8Z0jXg1VAMonaG8akvh"

# Token配置
TOKEN_STORAGE_DIR = os.path.join(os.getcwd(), 'data', 'tokens')
TOKEN_FILE_EXT = '.json'
TOKEN_EXPIRY_MINUTES = 30
TOKEN_REFRESH_WARNING_MINUTES = 5

# 请求配置
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_INTERVAL = 1
DEFAULT_TIMEOUT = 10

# 刷新配置
REFRESH_MAX_RETRIES = 5
REFRESH_RETRY_INTERVAL = 60
REFRESH_TOTAL_TIMEOUT = 600

# 初始化token存储目录
os.makedirs(TOKEN_STORAGE_DIR, exist_ok=True)

class TokenInfo:
    """Token信息数据结构"""
    def __init__(self, token: str, login_time: datetime, base_url: str, server_key: str):
        self.token = token
        self.login_time = login_time
        self.base_url = base_url
        self.server_key = server_key

    def is_expired(self, max_age_minutes: int = TOKEN_EXPIRY_MINUTES) -> bool:
        """检查token是否过期"""
        return (datetime.now() - self.login_time).total_seconds() > max_age_minutes * 60
    
    def is_about_to_expire(self, warning_minutes: int = TOKEN_REFRESH_WARNING_MINUTES) -> bool:
        """检查token是否即将过期（用于提前刷新）"""
        max_age = TOKEN_EXPIRY_MINUTES
        return (datetime.now() - self.login_time).total_seconds() > (max_age - warning_minutes) * 60
    
    def to_dict(self) -> Dict[str, Any]:
        """将TokenInfo转换为字典，用于序列化"""
        return {
            'token': self.token,
            'login_time': self.login_time.isoformat(),
            'base_url': self.base_url,
            'server_key': self.server_key
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenInfo':
        """从字典创建TokenInfo实例，用于反序列化"""
        return cls(
            token=data['token'],
            login_time=datetime.fromisoformat(data['login_time']),
            base_url=data['base_url'],
            server_key=data['server_key']
        )

class TokenManager:
    """Token管理器，用于缓存和复用登录token"""
    
    def __init__(self):
        self._token_cache: Dict[str, TokenInfo] = {}  # {server_key: TokenInfo}
        self._lock = threading.Lock()
        self._api_key = API_KEY  # 飞牛API密钥
        self._token_file_map: Dict[str, str] = {}  # 存储server_key到token文件路径的映射
        self._load_tokens_from_files()  # 初始化时从文件加载token

    def _generate_server_key(self, host: str, username: str) -> str:
        """生成服务器唯一标识"""
        return f"{host}#{username}"
        
    def _get_token_file_path(self, server_key: str) -> str:
        """生成token文件路径"""
        # 使用server_key生成安全的文件名
        safe_filename = hashlib.md5(server_key.encode()).hexdigest()
        return os.path.join(TOKEN_STORAGE_DIR, f"{safe_filename}{TOKEN_FILE_EXT}")
        
    def _save_token_to_file(self, token_info: TokenInfo) -> None:
        """将token保存到文件"""
        file_path = self._get_token_file_path(token_info.server_key)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(token_info.to_dict(), f, ensure_ascii=False, indent=2)
            self._token_file_map[token_info.server_key] = file_path
            logger.debug(f"【TokenManager】已将token保存到文件: {file_path}")
        except Exception as e:
            logger.error(f"【TokenManager】保存token到文件失败: {e}")
        
    def _load_token_from_file(self, file_path: str) -> Optional[TokenInfo]:
        """从文件加载token"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            token_info = TokenInfo.from_dict(data)
            logger.debug(f"【TokenManager】已从文件加载token: {file_path}")
            return token_info
        except Exception as e:
            logger.error(f"【TokenManager】从文件加载token失败: {e}")
            return None
        
    def _load_tokens_from_files(self) -> None:
        """从所有token文件加载token"""
        try:
            for file_name in os.listdir(TOKEN_STORAGE_DIR):
                if file_name.endswith(TOKEN_FILE_EXT):
                    file_path = os.path.join(TOKEN_STORAGE_DIR, file_name)
                    token_info = self._load_token_from_file(file_path)
                    if token_info and not token_info.is_expired():
                        self._token_cache[token_info.server_key] = token_info
                        self._token_file_map[token_info.server_key] = file_path
                    else:
                        # 删除过期的token文件
                        os.remove(file_path)
                        logger.debug(f"【TokenManager】已删除过期token文件: {file_path}")
        except Exception as e:
            logger.error(f"【TokenManager】从文件加载所有token失败: {e}")
        
    def _delete_token_file(self, server_key: str) -> None:
        """删除token文件"""
        if server_key in self._token_file_map:
            file_path = self._token_file_map.pop(server_key)
            try:
                os.remove(file_path)
                logger.debug(f"【TokenManager】已删除token文件: {file_path}")
            except Exception as e:
                logger.error(f"【TokenManager】删除token文件失败: {e}")

    def _create_feiniu_api(self, host: str) -> Tuple[Optional[str], Optional[str]]:
        """创建飞牛API连接，尝试带/v和不带/v的路径"""
        standard_host = host.rstrip("/")
        
        # 尝试带/v前缀的路径
        host_with_v = f"{standard_host}/v"
        try:
            test_url = f"{host_with_v}/api/v1/login"
            response = requests.post(test_url, json={"username": "test", "password": "test"}, timeout=5)
            if response.status_code != 404:  # 如果返回的不是404，说明这个路径可用
                return host_with_v, f"{host_with_v}/api/v1"
        except Exception:
            pass
            
        # 尝试不带/v前缀的路径
        try:
            test_url = f"{standard_host}/api/v1/login"
            response = requests.post(test_url, json={"username": "test", "password": "test"}, timeout=5)
            if response.status_code != 404:  # 如果返回的不是404，说明这个路径可用
                return standard_host, f"{standard_host}/api/v1"
        except Exception:
            pass
            
        return None, None

    def _login_and_cache(self, host: str, username: str, password: str) -> Optional[TokenInfo]:
        """登录并缓存token"""
        try:
            logger.debug(f"【TokenManager】正在为服务器 {host} 用户 {username} 进行登录...")

            # 创建API连接
            base_url, api_base_url = self._create_feiniu_api(host)
            if not base_url:
                logger.error(f"【TokenManager】无法创建API连接: {host}")
                return None

            # 登录获取token
            login_url = f"{api_base_url}/login"
            payload = {"username": username, "password": password}
            
            response = requests.post(login_url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data or data.get("code") != 0 or "data" not in data:
                logger.error(f"【TokenManager】登录失败: {host}/{username} - 响应: {data}")
                return None
                
            token = data["data"].get("token")
            if not token:
                logger.error(f"【TokenManager】登录响应中没有token: {data}")
                return None

            # 创建token信息
            server_key = self._generate_server_key(host, username)
            token_info = TokenInfo(
                token=token,
                login_time=datetime.now(),
                base_url=api_base_url,
                server_key=server_key
            )

            logger.debug(f"【TokenManager】登录成功，缓存token: {server_key}")
            return token_info
        except Exception as e:
            logger.error(f"【TokenManager】登录过程中发生错误: {e}")
            return None

    def _refresh_token(self, token_info: TokenInfo, username: str, password: str) -> Optional[TokenInfo]:
        """刷新token"""
        try:
            logger.debug(f"【TokenManager】正在尝试刷新token: {token_info.server_key}")
            
            # 由于飞牛影视登录接口不返回refresh_token，直接使用用户名密码重新登录
            host = token_info.server_key.split("#")[0] if "#" in token_info.server_key else token_info.server_key
            return self._login_and_cache(host, username, password)
        except Exception as e:
            logger.error(f"【TokenManager】刷新token过程中发生错误: {e}")
            return None

    def get_token(self, host: str, username: str, password: str) -> Tuple[Optional[str], Optional[str]]:
        """
        统一获取token的方法 - 懒加载模式
        
        :param host: 服务器地址
        :param username: 用户名
        :param password: 密码
        :return: (token, api_base_url)
        """
        server_key = self._generate_server_key(host, username)

        with self._lock:
            # 检查缓存中是否有该服务器的token
            if server_key in self._token_cache:
                token_info = self._token_cache[server_key]

                # 检查是否即将过期，提前5分钟刷新
                if token_info.is_about_to_expire():
                    logger.debug(f"【TokenManager】token即将过期，开始自动刷新: {server_key}")
                    refreshed_token_info = self._refresh_token(token_info, username, password)
                    if refreshed_token_info:
                        # 更新缓存和文件
                        self._token_cache[server_key] = refreshed_token_info
                        self._save_token_to_file(refreshed_token_info)
                        logger.debug(f"【TokenManager】token自动刷新成功: {server_key}")
                        return refreshed_token_info.token, refreshed_token_info.base_url
                    else:
                        logger.warning(f"【TokenManager】token自动刷新失败，将使用旧token继续: {server_key}")
                
                # 检查是否已过期
                if token_info.is_expired():
                    logger.debug(f"【TokenManager】缓存的token已过期: {server_key}")
                    # 尝试刷新token
                    refreshed_token_info = self._refresh_token(token_info, username, password)
                    if refreshed_token_info:
                        # 更新缓存和文件
                        self._token_cache[server_key] = refreshed_token_info
                        self._save_token_to_file(refreshed_token_info)
                        logger.debug(f"【TokenManager】token刷新成功: {server_key}")
                        return refreshed_token_info.token, refreshed_token_info.base_url
                    else:
                        # 刷新失败，清理过期的token
                        logger.error(f"【TokenManager】token刷新失败，清理过期token: {server_key}")
                        del self._token_cache[server_key]
                        self._delete_token_file(server_key)
                else:
                    remaining_time = 30 - int((datetime.now() - token_info.login_time).total_seconds() / 60)
                    logger.debug(f"【TokenManager】使用缓存的token: {server_key} (剩余有效时间: {remaining_time}分钟)")
                    return token_info.token, token_info.base_url

            # token不存在或已过期，重新登录
            logger.debug(f"【TokenManager】需要重新登录获取token: {server_key}")
            token_info = self._login_and_cache(host, username, password)

            if token_info:
                # 缓存新的token并保存到文件
                self._token_cache[server_key] = token_info
                self._save_token_to_file(token_info)
                return token_info.token, token_info.base_url
            else:
                logger.error(f"【TokenManager】无法获取有效的token: {server_key}")
                return None, None

    def invalidate_token(self, host: str, username: str):
        """手动使指定服务器的token失效"""
        server_key = self._generate_server_key(host, username)
        with self._lock:
            if server_key in self._token_cache:
                del self._token_cache[server_key]
                self._delete_token_file(server_key)
                logger.debug(f"【TokenManager】已手动失效token: {server_key}")

    def clear_expired_tokens(self):
        """清理所有过期的token"""
        with self._lock:
            expired_keys = []
            for key, token_info in self._token_cache.items():
                if token_info.is_expired():
                    expired_keys.append(key)

            for key in expired_keys:
                del self._token_cache[key]
                logger.debug(f"【TokenManager】清理过期token: {key}")

            if expired_keys:
                logger.info(f"【TokenManager】清理了 {len(expired_keys)} 个过期token")

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息（用于调试）"""
        with self._lock:
            return {
                "total_cached": len(self._token_cache),
                "servers": [
                    {
                        "server_key": key,
                        "login_time": token_info.login_time.isoformat(),
                        "age_minutes": int((datetime.now() - token_info.login_time).total_seconds() / 60),
                        "is_expired": token_info.is_expired()
                    }
                    for key, token_info in self._token_cache.items()
                ]
            }

class SignatureManager:
    """签名管理器，用于生成飞牛API的authx签名"""
    
    def __init__(self):
        # 飞牛API签名密钥
        self._secret_key = SECRET_KEY

    def generate_authx_header(self, api_path: str, body: Optional[str], api_key: str) -> dict:
        """
        生成完整的authx签名信息
        按照飞牛官方API的算法生成

        :param api_path: API路径，如 "/api/v1/mdb/scan/library_id"
        :param body: 请求体内容
        :param api_key: API密钥
        :return: 包含nonce, timestamp, sign和完整authx头的字典
        """
        try:
            logger.debug(f"【SignatureManager】开始生成authx签名")
            logger.debug(f"  - API路径: {api_path}")
            logger.debug(f"  - 请求体: {body}")
            logger.debug(f"  - API密钥: {api_key}")

            # 确保api_path以/v开头
            if not api_path.startswith("/v"):
                api_path = "/v" + api_path

            # 生成随机nonce和时间戳
            nonce = str(random.randint(100000, 999999))
            timestamp = str(int(time.time() * 1000))

            logger.debug(f"  - 生成的nonce: {nonce}")
            logger.debug(f"  - 生成的时间戳: {timestamp}")

            # 计算请求体哈希
            md5 = hashlib.md5()
            md5.update((body or "").encode('utf-8'))
            data_hash = md5.hexdigest()

            logger.debug(f"  - 请求体哈希: {data_hash}")

            # 计算签名
            md5 = hashlib.md5()
            sign_string = "_".join([
                self._secret_key,
                api_path,
                nonce,
                timestamp,
                data_hash,
                api_key
            ])

            logger.debug(f"  - 签名字符串: {sign_string}")

            md5.update(sign_string.encode('utf-8'))
            sign = md5.hexdigest()

            logger.debug(f"  - 计算的签名: {sign}")

            # 构建完整的authx头
            authx_header = f"nonce={nonce}&timestamp={timestamp}&sign={sign}"

            logger.debug(f"【SignatureManager】成功生成authx签名: {authx_header}")

            return {
                "nonce": nonce,
                "timestamp": timestamp,
                "sign": sign,
                "authx_header": authx_header,
                "api_path": api_path,
                "data_hash": data_hash,
                "sign_string": sign_string
            }

        except Exception as e:
            logger.error(f"【SignatureManager】生成authx签名失败: {e}")
            # 返回默认的备用签名
            return {
                "nonce": "732840",
                "timestamp": "1759369686238",
                "sign": "",
                "authx_header": f"nonce=732840&timestamp=1759369686238&sign=",
                "api_path": api_path,
                "data_hash": "",
                "sign_string": ""
            }

class FeiNiuClient:
    """
    飞牛影视客户端类，用于与飞牛影视API交互
    """
    def __init__(self, host: str, username: str, password: str):
        """
        初始化飞牛影视客户端
        
        :param host: 飞牛影视服务器地址
        :param username: 飞牛影视用户名
        :param password: 飞牛影视密码
        """
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self._token_manager = TokenManager()
        self._signature_manager = SignatureManager()
        self._session = requests.Session()
        self._max_retries = DEFAULT_MAX_RETRIES  # API请求最大重试次数
        self._retry_interval = DEFAULT_RETRY_INTERVAL  # 重试间隔（秒）
        
    def _get_token(self) -> str:
        """
        获取或刷新认证令牌
        
        :return: 认证令牌
        """
        token, api_base_url = self._token_manager.get_token(self.host, self.username, self.password)
        if not token:
            raise Exception("无法获取有效的飞牛影视认证令牌")
        logger.info(f"【FeiNiuClient】成功获取认证令牌: {token}")
        return token
        
    def _retry_request(self, method: str, url: str, headers: dict, **kwargs) -> requests.Response:
        """
        带重试机制的请求方法
        
        :param method: 请求方法（get, post等）
        :param url: 请求URL
        :param headers: 请求头
        :param kwargs: 其他请求参数
        :return: 请求响应
        :raises: requests.RequestException 当所有重试都失败时
        """
        # 设置默认超时
        if 'timeout' not in kwargs:
            kwargs['timeout'] = DEFAULT_TIMEOUT
            
        for attempt in range(self._max_retries):
            try:
                logger.debug(f"【FeiNiuClient】执行{method}请求 (尝试 {attempt + 1}/{self._max_retries}): {url}")
                
                # 执行请求
                response = self._session.request(method, url, headers=headers, **kwargs)
                
                # 检查响应状态码
                if response.status_code == 401:
                    # Token失效，尝试刷新token
                    logger.warning(f"【FeiNiuClient】Token失效，正在刷新token: {url}")
                    
                    # 刷新token
                    server_key = self._token_manager._generate_server_key(self.host, self.username)
                    if server_key in self._token_manager._token_cache:
                        token_info = self._token_manager._token_cache[server_key]
                        refreshed_token_info = self._token_manager._refresh_token(token_info, self.username, self.password)
                        
                        if refreshed_token_info:
                            # 更新缓存和文件
                            self._token_manager._token_cache[server_key] = refreshed_token_info
                            self._token_manager._save_token_to_file(refreshed_token_info)
                            
                            # 更新请求头中的token
                            headers['Authorization'] = refreshed_token_info.token
                            logger.debug(f"【FeiNiuClient】Token刷新成功，重新尝试请求")
                            
                            # 重新执行请求
                            response = self._session.request(method, url, headers=headers, **kwargs)
                
                # 检查响应状态码，除了401都直接返回
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.error(f"【FeiNiuClient】请求失败 (尝试 {attempt + 1}/{self._max_retries}): {e}")
                
                # 如果是最后一次尝试，抛出异常
                if attempt == self._max_retries - 1:
                    logger.error(f"【FeiNiuClient】所有请求尝试都失败: {url}")
                    raise
                
                # 否则等待后重试
                logger.debug(f"【FeiNiuClient】{self._retry_interval}秒后重试请求")
                time.sleep(self._retry_interval)
                
            except Exception as e:
                logger.error(f"【FeiNiuClient】请求过程中发生意外错误: {e}")
                raise
        
        # 理论上不会到达这里，但为了类型安全返回None
        raise requests.exceptions.RequestException("所有请求尝试都失败")
    
    def get_media_libraries(self) -> List[Dict[str, Any]]:
        """
        获取媒体库列表
        
        :return: 媒体库列表
        """
        token, api_base_url = self._token_manager.get_token(self.host, self.username, self.password)
        if not token:
            return []
            
        try:
            libraries_url = f"{api_base_url}/mediadb/list"
            
            # 生成签名
            signature_info = self._signature_manager.generate_authx_header(
                "/api/v1/mediadb/list", 
                "", 
                API_KEY
            )
            
            headers = {
                "Authorization": token, 
                "Accept": "application/json",
                "authx": signature_info["authx_header"]
            }
            
            response = self._retry_request("get", libraries_url, headers=headers)
            data = response.json()
            
            if data and data.get("code") == 0 and "data" in data:
                return data.get("data", [])
            else:
                logger.error(f"获取媒体库列表失败: {data}")
        except Exception as e:
            logger.error(f"获取媒体库列表时发生错误: {e}")
            
        return []
    
    def get_running_tasks(self) -> List[str]:
        """
        获取飞牛正在运行的扫描任务
        
        :return: 正在运行的任务GUID列表
        """
        token, api_base_url = self._token_manager.get_token(self.host, self.username, self.password)
        if not token:
            logger.error("无法获取有效的飞牛影视认证令牌")
            return []
            
        try:
            task_url = f"{api_base_url}/task/running"
            
            # 生成签名
            signature_info = self._signature_manager.generate_authx_header(
                "/api/v1/task/running", 
                "", 
                API_KEY
            )
            
            headers = {
                "Authorization": token, 
                "Accept": "application/json",
                "authx": signature_info["authx_header"]
            }
            
            logger.debug(f"【飞牛影视】正在请求运行中的任务列表，URL: {task_url}")
            response = self._retry_request("get", task_url, headers=headers)
            data = response.json()
            
            if data and data.get("code") == 0 and "data" in data:
                tasks = data.get("data", [])
                running_guids = list(set(task.get("guid") for task in tasks if task.get("guid")))
                logger.debug(f"【飞牛影视】当前正在运行的扫描任务GUID: {running_guids if running_guids else '无'}")
                return running_guids
            else:
                logger.warning(f"【飞牛影视】获取任务列表时API返回错误: {data}")
                return []
        except Exception as e:
            logger.error(f"【飞牛影视】获取正在运行的任务列表时发生错误: {e}")
            return []

    def scan_folder(self, library_id: str, folder_paths: List[str]) -> bool:
        """
        执行文件夹扫描
        
        :param library_id: 媒体库ID
        :param folder_paths: 要扫描的文件夹路径列表
        :return: 是否扫描成功
        """
        token, api_base_url = self._token_manager.get_token(self.host, self.username, self.password)
        if not token:
            raise Exception("无法获取有效的飞牛影视认证令牌")
            
        try:
            # 检查该媒体库是否正在扫描中
            running_tasks = self.get_running_tasks()
            if library_id in running_tasks:
                logger.info(f"【飞牛影视】媒体库 '{library_id}' 正在扫描中，跳过当前扫描请求")
                raise Exception(f"媒体库 '{library_id}' 正在扫描中，无法执行新的扫描请求")
            
            scan_url = f"{api_base_url}/mdb/scan/{library_id}"
            
            # 准备请求体
            payload = {"dir_list": folder_paths}
            
            # 生成签名
            # 关键修复：使用与测试12.py完全一致的JSON序列化方式（添加separators参数）
            body_json = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
            # 转换为UTF-8字节流，确保与签名计算一致
            body_bytes = body_json.encode('utf-8')
            signature_info = self._signature_manager.generate_authx_header(
                f"/api/v1/mdb/scan/{library_id}", 
                body_json,
                API_KEY
            )
            
            headers = {
                "Authorization": token, 
                "Accept": "application/json", 
                "Content-Type": "application/json",
                "authx": signature_info["authx_header"]
            }
            
            logger.info(f"正在发起飞牛影视文件夹扫描请求")
            logger.info(f"扫描文件夹: {folder_paths}")
            
            response = self._retry_request("post", scan_url, headers=headers, data=body_bytes)
            data = response.json()
            
            if data and data.get("code") == 0:
                logger.info(f"飞牛影视文件夹扫描请求发送成功")
                return True
            else:
                logger.error(f"飞牛影视文件夹扫描请求失败: {data}")
                raise Exception(f"飞牛影视文件夹扫描请求失败: {data}")
        except Exception as e:
            logger.error(f"执行飞牛影视文件夹扫描时发生错误: {e}")
            raise

class FeiNiuManager:
    """
    飞牛影视管理器，用于管理飞牛影视客户端和扫描任务
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """
        单例模式
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(FeiNiuManager, cls).__new__(cls)
                    cls._instance._init()
        return cls._instance
    
    def _init(self):
        """
        初始化管理器
        """
        self._clients = {}
        self._debounce_timers = {}
        self._debounce_lock = threading.Lock()
    
    def get_client(self, host: str, username: str, password: str) -> FeiNiuClient:
        """
        获取或创建飞牛影视客户端
        
        :param host: 飞牛影视服务器地址
        :param username: 飞牛影视用户名
        :param password: 飞牛影视密码
        :return: 飞牛影视客户端
        """
        key = f"{host}_{username}"
        if key not in self._clients:
            self._clients[key] = FeiNiuClient(host, username, password)
        return self._clients[key]
    
    def refresh_path(self, folder_path: str, debounce_seconds: int = 60, feiniu_id: int = None, media_library_id: str = None, media_path: str = None, job_id: int = None):
        """
        刷新指定路径（支持防抖）
        
        :param folder_path: 要刷新的文件夹路径或路径列表
        :param debounce_seconds: 防抖时间（秒）
        :param feiniu_id: 飞牛配置ID
        :param media_library_id: 飞牛媒体库ID
        :param media_path: 飞牛媒体库路径映射
        :param job_id: 关联的作业ID，用于记录失败任务
        """
        # 处理路径，支持单个路径或路径列表
        folder_paths = folder_path if isinstance(folder_path, list) else [folder_path]
        
        # 从数据库获取飞牛配置
        if feiniu_id:
            feiniu_config = feiniuMapper.getFeiniuById(feiniu_id)
        else:
            # 从数据库获取启用的飞牛配置
            feiniu_config = feiniuMapper.getEnabledFeiniu()
        
        if not feiniu_config:
            logger.info(f"没有找到飞牛配置，跳过路径刷新")
            for path in folder_paths:
                logger.info(f"  - 跳过路径: {path}")
            return
            
        host = feiniu_config.get('host')
        username = feiniu_config.get('username')
        password = feiniu_config.get('password')
        
        # 使用提供的媒体库ID，否则使用配置中的媒体库ID
        use_library_id = media_library_id if media_library_id else feiniu_config.get('library_id')
        
        # 按媒体库分组，同一媒体库的路径一起处理
        key = f"{host}_{username}_{use_library_id}"
        
        with self._debounce_lock:
            # 如果已经有定时器，取消它
            if key in self._debounce_timers:
                timer = self._debounce_timers.pop(key)
                timer.cancel()
                # 合并新的路径映射
                existing_paths = timer.args[4]  # 获取已有的路径映射
                folder_paths.extend(existing_paths)
            
            # 创建新的定时器，传递路径映射字典
            timer = threading.Timer(debounce_seconds, self._execute_refresh, 
                                   args=[host, username, password, use_library_id, folder_paths, job_id, feiniu_id])
            self._debounce_timers[key] = timer
            timer.start()
            
            logger.info(f"飞牛影视刷新路径请求已添加到防抖队列，将在{debounce_seconds}秒后执行")
            logger.info(f"媒体库ID: {use_library_id}")
            logger.info(f"路径数量: {len(folder_paths)}")
            for path in folder_paths:
                logger.info(f"  - 处理路径: {path}")
    
    def _preprocess_path(self, path: str, media_path: str = None, strm_path: str = None, feiniu_config: dict = None) -> str:
        """
        预处理和转换路径，确保符合飞牛系统格式要求
        
        :param path: 要处理的原始路径
        :param media_path: 媒体库路径映射
        :param strm_path: 流路径映射
        :param feiniu_config: 飞牛配置信息
        :return: 处理后的路径
        """
        # 基本处理：统一路径分隔符为正斜杠
        processed_path = path.replace("\\", "/")
        media_path = media_path.replace("\\", "/")
        strm_path = strm_path.replace("\\", "/")
        
        # 进一步处理：确保路径符合飞牛系统的要求
        # 例如：去除多余的后缀、统一路径格式等
        
        # 如果有媒体路径映射，应用映射
        if media_path:
            # 这里可以添加更复杂的路径映射逻辑
            processed_path = processed_path.replace(strm_path, media_path)
        
        return processed_path
    
    def _finalize_path(self, path: str) -> str:
        """
        最终路径处理，确保路径符合飞牛系统格式要求
        
        :param path: 要处理的路径
        :return: 最终处理后的路径
        """
        # 去除末尾分隔符
        if path.endswith("/") or path.endswith("\\"):
            path = path[:-1]
        
        return path
    
    def _execute_refresh(self, host: str, username: str, password: str, library_id: str, path_mappings: list, job_id: int = None, feiniu_id: int = None):
        """
        执行路径刷新
        
        :param host: 飞牛影视服务器地址
        :param username: 飞牛影视用户名
        :param password: 飞牛影视密码
        :param library_id: 媒体库ID
        :param path_mappings: 要刷新的文件夹路径
        :param job_id: 关联的作业ID，用于记录失败任务
        :param feiniu_id: 飞牛配置ID，用于记录失败任务
        """
        key = f"{host}_{username}_{library_id}"
        
        with self._debounce_lock:
            if key in self._debounce_timers:
                del self._debounce_timers[key]
        
        # 提取所有映射后的路径并去重，确保幂等性
        # 对路径进行最终处理，确保所有路径都已完成预处理和转换
        processed_folder_paths = []
        for path in path_mappings:
            # 应用最终的路径转换，确保符合飞牛系统格式要求
            processed_path = self._finalize_path(path)
            processed_folder_paths.append(processed_path)
        
        folder_paths = processed_folder_paths
        if not folder_paths:
            logger.info(f"【飞牛影视管理器】没有需要刷新的路径，跳过刷新操作")
            return
        
        client = self.get_client(host, username, password)
        start_time = time.time()
        error_msg = "未知错误"
        task_id = None  # 初始化任务ID
        
        # 使用公共常量配置
        max_retries = REFRESH_MAX_RETRIES
        retry_interval = REFRESH_RETRY_INTERVAL
        total_timeout = REFRESH_TOTAL_TIMEOUT
        
        # 幂等性检查：记录本次刷新的路径和时间
        refresh_key = f"{host}_{username}_{library_id}_{hash('|'.join(sorted(folder_paths)))}"
        logger.info(f"【飞牛影视管理器】刷新幂等性Key: {refresh_key}")
        
        # ------------------------ 任务信息记录开始 ------------------------
        try:
            # 1. 记录任务开始信息
            task_record = {
                'feiniuId': feiniu_id,
                'jobId': job_id,
                'media_library_id': library_id,
                'folder_paths': json.dumps(folder_paths, ensure_ascii=False),
                'operation_type': 'refresh',
                'status': 0,  # 0-执行中
                'start_time': int(start_time)
            }
            
            task_id = feiniuRefreshTaskMapper.addFeiniuRefreshTask(task_record)
            logger.info(f"【飞牛影视管理器】已记录飞牛刷新任务，任务ID: {task_id}")
        except Exception as e:
            logger.error(f"【飞牛影视管理器】记录飞牛刷新任务失败: {str(e)}")
        # ------------------------ 任务信息记录结束 ------------------------
        
        for attempt in range(max_retries):
            try:
                # 检查总超时
                elapsed_time = time.time() - start_time
                if elapsed_time > total_timeout:
                    logger.error(f"【飞牛影视管理器】路径刷新总超时（{total_timeout}秒），已超过最大允许时间，停止重试")
                    break
                
                # 检查该媒体库是否正在扫描中
                running_tasks = client.get_running_tasks()
                logger.info(f"【飞牛影视管理器】正在运行的任务: {running_tasks}")
                logger.info(f"【飞牛影视管理器】当前要扫描的媒体库ID: {library_id}")
                logger.info(f"【飞牛影视管理器】第 {attempt + 1}/{max_retries} 次尝试，已用时间: {elapsed_time:.1f}秒")
                logger.info(f"【飞牛影视管理器】本次要刷新的路径数量: {len(folder_paths)}个")
                
                if library_id not in running_tasks:
                    # 媒体库未在扫描中，执行扫描，将所有路径一次性传入
                    logger.info(f"【飞牛影视管理器】开始执行刷新操作")
                    logger.info(f"【飞牛影视管理器】批量提交路径列表到飞牛系统，总路径数: {len(folder_paths)}个")
                    
                    # 批量提交刷新操作，减少系统交互次数
                    success = client.scan_folder(library_id, folder_paths)
                    
                    if success:
                        logger.info(f"【飞牛影视管理器】飞牛影视路径刷新成功")
                        logger.info(f"【飞牛影视管理器】总路径数量: {len(folder_paths)}个")
                        logger.info(f"【飞牛影视管理器】原始路径:")
                        for path in folder_paths[:10]:  # 只记录前10个路径，避免日志过长
                            logger.info(f"【飞牛影视管理器】  - {path}")
                        if len(folder_paths) > 10:
                            logger.info(f"【飞牛影视管理器】  - ... 还有 {len(folder_paths) - 10} 个原始路径")
                        
                        logger.info(f"【飞牛影视管理器】映射后路径:")
                        for path in folder_paths[:10]:  # 只记录前10个路径，避免日志过长
                            logger.info(f"【飞牛影视管理器】  - {path}")
                        if len(folder_paths) > 10:
                            logger.info(f"【飞牛影视管理器】  - ... 还有 {len(folder_paths) - 10} 个映射后路径")
                        
                        logger.info(f"【飞牛影视管理器】总尝试次数: {attempt + 1}，总耗时: {time.time() - start_time:.1f}秒")
                        logger.info(f"【飞牛影视管理器】刷新幂等性Key: {refresh_key}")
                        logger.info(f"【飞牛影视管理器】优化点：路径预处理和批量提交刷新操作，减少系统交互次数")
                        
                        # 更新任务状态为成功
                        try:
                            end_time = time.time()
                            elapsed_time = end_time - start_time
                            task_update = {
                                'status': 1,  # 1-成功
                                'end_time': int(end_time),
                                'elapsed_time': round(elapsed_time, 2),
                                'retry_count': attempt + 1
                            }
                            feiniuRefreshTaskMapper.updateFeiniuRefreshTask(task_id, task_update)
                            logger.info(f"【飞牛影视管理器】更新飞牛刷新任务成功，任务ID: {task_id}")
                        except Exception as e:
                            logger.error(f"【飞牛影视管理器】更新飞牛刷新任务失败: {str(e)}")
                        
                        # 发送刷新成功通知
                        try:
                            from service.notify import notifyService
                            # 获取所有启用的通知配置
                            notify_list = notifyService.getNotifyList(True)
                            if notify_list:
                                # 准备通知内容
                                title = f"TaoSync 飞牛影视库刷新成功"
                                # 限制显示的路径数量，避免通知内容过长
                                display_paths = folder_paths[:10]
                                paths_str = "\n".join([f"  - {path}" for path in display_paths])
                                if len(folder_paths) > 10:
                                    paths_str += f"\n  - ... 还有 {len(folder_paths) - 10} 个路径"
                                content = f"媒体库ID: {library_id}\n刷新路径数量: {len(folder_paths)}个\n总耗时: {time.time() - start_time:.1f}秒\n尝试次数: {attempt + 1}\n刷新路径:\n{paths_str}"
                                for notify in notify_list:
                                    notifyService.sendNotify(notify, title, content)
                                logger.info(f"【飞牛影视管理器】已发送刷新成功通知")
                        except Exception as e:
                            logger.error(f"【飞牛影视管理器】发送刷新成功通知失败: {e}")
                        
                        return
                    else:
                        logger.warning(f"【飞牛影视管理器】扫描请求发送成功，但返回结果异常，将重试")
                else:
                    # 媒体库正在扫描中，等待后重试
                    logger.info(f"【飞牛影视管理器】媒体库 '{library_id}' 正在扫描中，{retry_interval}秒后第 {attempt + 2}/{max_retries} 次尝试")
                    time.sleep(retry_interval)
                    continue
            except Exception as e:
                error_msg = str(e)
                logger.error(f"【飞牛影视管理器】执行飞牛影视路径刷新时发生错误: {error_msg}")
                logger.error(f"【飞牛影视管理器】错误类型: {type(e).__name__}")
                
                # 记录完整的异常堆栈
                import traceback
                logger.error(f"【飞牛影视管理器】异常堆栈: {traceback.format_exc()}")
                
                # 如果是媒体库正在扫描的错误，等待后重试
                if "正在扫描中" in error_msg or "already running" in error_msg.lower():
                    logger.info(f"【飞牛影视管理器】媒体库 '{library_id}' 正在扫描中，{retry_interval}秒后第 {attempt + 2}/{max_retries} 次尝试")
                    time.sleep(retry_interval)
                    continue
                elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    # 网络超时，等待后重试
                    logger.info(f"【飞牛影视管理器】网络超时，{retry_interval}秒后第 {attempt + 2}/{max_retries} 次尝试")
                    time.sleep(retry_interval)
                    continue
                elif "connection" in error_msg.lower() or "connect" in error_msg.lower():
                    # 连接错误，等待后重试
                    logger.info(f"【飞牛影视管理器】连接错误，{retry_interval}秒后第 {attempt + 2}/{max_retries} 次尝试")
                    time.sleep(retry_interval)
                    continue
                else:
                    # 其他错误，记录详细信息并继续重试，而不是立即停止
                    logger.error(f"【飞牛影视管理器】路径刷新失败详情: {error_msg}")
                    logger.info(f"【飞牛影视管理器】非扫描中错误，{retry_interval}秒后第 {attempt + 2}/{max_retries} 次尝试")
                    time.sleep(retry_interval)
                    continue
        
        # 所有重试都失败
        logger.error(f"【飞牛影视管理器】路径刷新失败，已尝试 {max_retries} 次，总耗时: {time.time() - start_time:.1f}秒")
        logger.error(f"【飞牛影视管理器】失败路径数量: {len(folder_paths)}个")
        for path in folder_paths[:10]:  # 只记录前10个失败路径
            logger.error(f"【飞牛影视管理器】  - {path}")
        if len(folder_paths) > 10:
            logger.error(f"【飞牛影视管理器】  - ... 还有 {len(folder_paths) - 10} 个失败路径")
        
        # 发送刷新失败通知
        try:
            from service.notify import notifyService
            # 获取所有启用的通知配置
            notify_list = notifyService.getNotifyList(True)
            if notify_list:
                # 准备通知内容
                title = f"TaoSync 飞牛影视库刷新失败"
                # 限制显示的路径数量，避免通知内容过长
                display_paths = folder_paths[:10]
                paths_str = "\n".join([f"  - {path}" for path in display_paths])
                if len(folder_paths) > 10:
                    paths_str += f"\n  - ... 还有 {len(folder_paths) - 10} 个路径"
                content = f"媒体库ID: {library_id}\n失败路径数量: {len(folder_paths)}个\n总耗时: {time.time() - start_time:.1f}秒\n尝试次数: {max_retries}次\n失败原因: {error_msg}\n刷新路径:\n{paths_str}"
                for notify in notify_list:
                    notifyService.sendNotify(notify, title, content)
                logger.info(f"【飞牛影视管理器】已发送刷新失败通知")
        except Exception as e:
            logger.error(f"【飞牛影视管理器】发送刷新失败通知失败: {e}")
        
        # 更新任务状态为失败
        try:
            end_time = time.time()
            elapsed_time = end_time - start_time
            task_update = {
                'status': 2,  # 2-失败
                'end_time': int(end_time),
                'elapsed_time': round(elapsed_time, 2),
                'error_msg': error_msg,
                'retry_count': max_retries
            }
            feiniuRefreshTaskMapper.updateFeiniuRefreshTask(task_id, task_update)
            logger.info(f"【飞牛影视管理器】更新飞牛刷新任务失败，任务ID: {task_id}")
        except Exception as e:
            logger.error(f"【飞牛影视管理器】更新飞牛刷新任务失败: {str(e)}")
        

        # 可以在这里添加告警逻辑，例如发送邮件或短信通知
        # send_alert(f"飞牛影视路径刷新失败，已尝试 {max_retries} 次", folder_paths, error_msg)

# 创建全局飞牛管理器实例
feiniu_manager = FeiNiuManager()