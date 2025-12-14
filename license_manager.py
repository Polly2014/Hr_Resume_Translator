"""
License Manager - Supabase 授权码管理模块
使用 Supabase 作为后端验证授权码，支持配额管理和过期检查
"""

import os
import json
import requests
import threading
import platform
import socket
from datetime import datetime
from pathlib import Path

# 应用版本号
APP_VERSION = "2.0.0"

import os
import json
import requests
import threading
import platform
import socket
from datetime import datetime
from pathlib import Path

# 应用版本号
APP_VERSION = "2.0.0"

# Supabase 配置
SUPABASE_URL = "https://otugqwtiphxzqezvijee.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90dWdxd3RpcGh4enFlenZpamVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU2OTkxNzgsImV4cCI6MjA4MTI3NTE3OH0.YdAXwUd_B-iFi-NPxiV393YjXm84AFscr7LOLFBMs0Y"

# 本地配置文件路径
CONFIG_DIR = Path.home() / ".cyber_resume_parser"
LICENSE_FILE = CONFIG_DIR / "license.json"


class LicenseManager:
    """授权码管理器"""
    
    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.supabase_key = SUPABASE_ANON_KEY
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    def _supabase_request(self, method: str, endpoint: str, data: dict = None, retries: int = 3) -> dict:
        """发送 Supabase REST API 请求，带重试机制"""
        url = f"{self.supabase_url}/rest/v1/{endpoint}"
        
        for attempt in range(retries):
            try:
                if method == "GET":
                    response = requests.get(url, headers=self.headers, timeout=30)
                elif method == "PATCH":
                    response = requests.patch(url, headers=self.headers, json=data, timeout=30)
                elif method == "POST":
                    response = requests.post(url, headers=self.headers, json=data, timeout=30)
                else:
                    return {"error": f"Unsupported method: {method}"}
                
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                elif response.status_code == 201:
                    # 201 Created - POST 成功创建
                    return {"success": True, "data": response.json()}
                elif response.status_code == 204:
                    return {"success": True, "data": []}
                else:
                    return {"error": f"HTTP {response.status_code}: {response.text}"}
            except requests.exceptions.ConnectionError:
                if attempt < retries - 1:
                    import time
                    time.sleep(1)  # 等待1秒后重试
                    continue
                return {"error": "无法连接到服务器，请检查网络连接"}
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    continue
                return {"error": "请求超时，请稍后重试"}
            except Exception as e:
                return {"error": str(e)}
    
    def validate_license(self, license_code: str) -> dict:
        """
        验证授权码
        返回: {
            "valid": bool,
            "message": str,
            "license_info": dict (如果有效)
        }
        """
        if not license_code or not license_code.strip():
            return {"valid": False, "message": "请输入授权码"}
        
        license_code = license_code.strip().upper()
        
        # 查询授权码
        endpoint = f"licenses?code=eq.{license_code}&is_active=eq.true&select=*"
        result = self._supabase_request("GET", endpoint)
        
        if "error" in result:
            return {"valid": False, "message": result["error"]}
        
        licenses = result.get("data", [])
        if not licenses:
            return {"valid": False, "message": "无效的授权码"}
        
        license_info = licenses[0]
        
        # 检查是否过期
        if license_info.get("expires_at"):
            expires_at = datetime.fromisoformat(license_info["expires_at"].replace("Z", "+00:00"))
            if datetime.now(expires_at.tzinfo) > expires_at:
                return {"valid": False, "message": "授权码已过期"}
        
        # 检查配额（无限配额跳过检查）
        if not license_info.get("is_unlimited", False):
            used = license_info.get("used_quota", 0)
            total = license_info.get("total_quota", 0)
            if used >= total:
                return {"valid": False, "message": f"配额已用完 ({used}/{total})"}
        
        # 计算剩余配额显示
        if license_info.get("is_unlimited"):
            remaining_display = "∞ 无限"
        else:
            remaining = license_info.get("total_quota", 0) - license_info.get("used_quota", 0)
            remaining_display = f"{remaining} 次"
        
        return {
            "valid": True,
            "message": "授权码有效 ✓",
            "license_info": {
                "code": license_info["code"],
                "owner_name": license_info.get("owner_name", "未知"),
                "is_unlimited": license_info.get("is_unlimited", False),
                "remaining_quota": remaining_display,
                "used_quota": license_info.get("used_quota", 0),
                "total_quota": license_info.get("total_quota", 0),
                "expires_at": license_info.get("expires_at"),
            }
        }
    
    def consume_quota(self, license_code: str, amount: int = 1) -> dict:
        """
        消耗配额
        返回: {"success": bool, "message": str, "remaining": int/str, "remaining_quota": str}
        """
        license_code = license_code.strip().upper()
        
        # 先验证授权码
        validation = self.validate_license(license_code)
        if not validation["valid"]:
            return {"success": False, "message": validation["message"]}
        
        license_info = validation["license_info"]
        
        # 无限配额不需要扣减
        if license_info.get("is_unlimited"):
            return {
                "success": True,
                "message": "无限配额，无需扣减",
                "remaining": "∞ 无限",
                "remaining_quota": "∞ 无限"
            }
        
        # 计算新的使用量
        new_used = license_info["used_quota"] + amount
        remaining = license_info["total_quota"] - new_used
        
        if remaining < 0:
            return {
                "success": False,
                "message": "配额不足",
                "remaining": 0,
                "remaining_quota": "0 次"
            }
        
        # 更新数据库
        endpoint = f"licenses?code=eq.{license_code}"
        update_data = {
            "used_quota": new_used,
            "last_used_at": datetime.utcnow().isoformat()
        }
        result = self._supabase_request("PATCH", endpoint, update_data)
        
        if "error" in result:
            return {"success": False, "message": result["error"]}
        
        # 记录使用日志
        self._log_usage(license_code, amount)
        
        # 格式化剩余配额显示
        remaining_display = f"{remaining} 次"
        
        return {
            "success": True,
            "message": f"已使用 {amount} 次配额",
            "remaining": remaining,
            "remaining_quota": remaining_display
        }
    
    def _log_usage(self, license_code: str, amount: int):
        """记录配额消耗日志（异步后台执行）"""
        def _async_log():
            try:
                # 获取 license_id
                endpoint = f"licenses?code=eq.{license_code}&select=id"
                result = self._supabase_request("GET", endpoint)
                if "error" not in result and result.get("data"):
                    license_id = result["data"][0]["id"]
                    log_data = {
                        "license_id": license_id,
                        "action": "consume",
                        "app_version": APP_VERSION,
                        "client_info": self._get_client_info()
                    }
                    self._supabase_request("POST", "usage_logs", log_data)
            except:
                pass  # 日志记录失败不影响主流程
        
        # 后台线程异步执行
        thread = threading.Thread(target=_async_log, daemon=True)
        thread.start()
    
    def _get_client_info(self) -> dict:
        """获取客户端信息（返回字典，用于 JSONB 字段）"""
        try:
            return {
                "os": platform.system(),
                "os_version": platform.release(),
                "machine": platform.machine(),
                "hostname": socket.gethostname()[:20]  # 限制长度
            }
        except:
            return {}
    
    def log_resume_result(
        self,
        license_code: str,
        filename: str,
        result_json: dict,
        status: str = "success",
        error_message: str = None
    ):
        """
        后台异步上传解析结果到云端
        
        参数:
            license_code: 授权码
            filename: 原始文件名
            result_json: 解析结果 JSON
            status: 状态 (success/error)
            error_message: 错误信息
        """
        def _async_upload():
            try:
                # 获取 license_id
                endpoint = f"licenses?code=eq.{license_code}&select=id,owner_name"
                result = self._supabase_request("GET", endpoint)
                if "error" in result or not result.get("data"):
                    return
                
                license_id = result["data"][0]["id"]
                owner_name = result["data"][0].get("owner_name", "Unknown")
                
                # 从解析结果中提取候选人信息
                basic_info = result_json.get("基本信息", {}) or result_json.get("basic_info", {})
                personal_info = result_json.get("个人信息", {}) or result_json.get("personal_info", {})
                
                candidate_name = basic_info.get("姓名") or basic_info.get("name") or "未知"
                candidate_phone = personal_info.get("电话") or personal_info.get("phone") or ""
                candidate_email = personal_info.get("邮箱") or personal_info.get("email") or ""
                
                # 构建日志数据
                log_data = {
                    "license_id": license_id,
                    "action": "parse_resume",
                    "filename": filename[:255],  # 限制长度
                    "candidate_name": candidate_name[:100],
                    "candidate_phone": candidate_phone[:50],
                    "candidate_email": candidate_email[:100],
                    "result_json": result_json,  # 直接传字典，Supabase 会转为 JSONB
                    "status": status,
                    "error_message": error_message[:500] if error_message else None,
                    "app_version": APP_VERSION,
                    "client_info": self._get_client_info()
                }
                
                # 上传到 Supabase
                upload_result = self._supabase_request("POST", "usage_logs", log_data)
                
                if "error" not in upload_result:
                    print(f"📤 [后台] 已上传解析结果: {candidate_name}")
                else:
                    print(f"⚠️ [后台] 上传失败: {upload_result.get('error')}")
                    
            except Exception as e:
                print(f"⚠️ [后台] 上传异常: {e}")
        
        # 后台线程异步执行，不阻塞主流程
        thread = threading.Thread(target=_async_upload, daemon=True)
        thread.start()
    
    def get_license_status(self, license_code: str) -> dict:
        """获取授权码状态"""
        return self.validate_license(license_code)
    
    # ========== 本地配置管理 ==========
    
    def save_license_locally(self, license_code: str) -> bool:
        """保存授权码到本地"""
        try:
            config = {
                "license_code": license_code.strip().upper(),
                "saved_at": datetime.now().isoformat()
            }
            with open(LICENSE_FILE, "w") as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"保存授权码失败: {e}")
            return False
    
    def load_license_locally(self) -> str:
        """从本地加载授权码"""
        try:
            if LICENSE_FILE.exists():
                with open(LICENSE_FILE, "r") as f:
                    config = json.load(f)
                return config.get("license_code", "")
        except Exception as e:
            print(f"加载授权码失败: {e}")
        return ""
    
    def clear_local_license(self) -> bool:
        """清除本地保存的授权码"""
        try:
            if LICENSE_FILE.exists():
                LICENSE_FILE.unlink()
            return True
        except Exception as e:
            print(f"清除授权码失败: {e}")
            return False
    
    def has_valid_local_license(self) -> dict:
        """检查是否有有效的本地授权码"""
        local_code = self.load_license_locally()
        if local_code:
            validation = self.validate_license(local_code)
            if validation["valid"]:
                return {"has_license": True, **validation}
        return {"has_license": False, "valid": False, "message": "请输入授权码激活应用"}


# 单例实例
_license_manager = None

def get_license_manager() -> LicenseManager:
    """获取授权码管理器单例"""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager


# ========== 便捷函数 ==========

def validate_license(code: str) -> dict:
    """验证授权码"""
    return get_license_manager().validate_license(code)

def consume_quota(code: str, amount: int = 1) -> dict:
    """消耗配额"""
    return get_license_manager().consume_quota(code, amount)

def get_local_license() -> str:
    """获取本地保存的授权码"""
    return get_license_manager().load_license_locally()

def save_local_license(code: str) -> bool:
    """保存授权码到本地"""
    return get_license_manager().save_license_locally(code)

def check_startup_license() -> dict:
    """启动时检查授权状态"""
    return get_license_manager().has_valid_local_license()


def log_resume_result(
    license_code: str,
    filename: str,
    result_json: dict,
    status: str = "success",
    error_message: str = None
):
    """
    后台异步上传解析结果（便捷函数）
    
    参数:
        license_code: 授权码
        filename: 原始文件名
        result_json: 解析结果 JSON
        status: 状态 (success/error)
        error_message: 错误信息
    """
    return get_license_manager().log_resume_result(
        license_code, filename, result_json, status, error_message
    )


if __name__ == "__main__":
    # 测试代码
    print("🔐 License Manager 测试\n")
    
    manager = LicenseManager()
    
    # 测试验证授权码
    test_codes = ["QIWANG-LOVE-2025", "DEMO-100-TEST", "INVALID-CODE"]
    
    for code in test_codes:
        print(f"测试授权码: {code}")
        result = manager.validate_license(code)
        print(f"  结果: {result}\n")
