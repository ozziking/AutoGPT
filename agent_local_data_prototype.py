#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent与本地数据交互权限控制原型
演示如何实现安全的Agent数据访问机制
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import secrets
from pathlib import Path
import re

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Permission:
    """权限定义"""
    path: str
    operations: List[str]  # read, write, delete, execute
    sensitive_keywords: List[str] = None
    require_confirmation: bool = False
    audit_level: str = "medium"  # low, medium, high


@dataclass
class AuditEvent:
    """审计事件"""
    timestamp: datetime
    agent_id: str
    operation: str
    file_path: str
    success: bool
    details: Dict[str, Any]


class DataClassifier:
    """数据分类器 - 识别敏感数据"""
    
    def __init__(self):
        self.sensitive_patterns = {
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'password': r'password["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        }
    
    def classify_content(self, content: str) -> Dict[str, List[str]]:
        """分类内容中的敏感信息"""
        results = {}
        
        for category, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                results[category] = matches
        
        return results
    
    def is_sensitive_file(self, file_path: str) -> bool:
        """判断文件是否敏感"""
        sensitive_extensions = {'.key', '.pem', '.p12', '.pfx', '.crt', '.pwd'}
        sensitive_names = {'password', 'secret', 'private', 'config', '.env'}
        
        path_lower = file_path.lower()
        
        # 检查文件扩展名
        if any(ext in path_lower for ext in sensitive_extensions):
            return True
        
        # 检查文件名
        if any(name in path_lower for name in sensitive_names):
            return True
        
        return False


class SecureFileAccess:
    """安全文件访问控制器"""
    
    def __init__(self, permissions: List[Permission]):
        self.permissions = permissions
        self.audit_log: List[AuditEvent] = []
        self.classifier = DataClassifier()
        self.session_id = secrets.token_hex(16)
    
    def can_access(self, file_path: str, operation: str) -> bool:
        """检查是否有权限访问文件"""
        for permission in self.permissions:
            if self._path_matches(file_path, permission.path):
                if operation in permission.operations:
                    return True
        return False
    
    def _path_matches(self, file_path: str, permission_path: str) -> bool:
        """检查文件路径是否匹配权限路径"""
        file_path = os.path.abspath(file_path)
        permission_path = os.path.abspath(permission_path)
        
        return file_path.startswith(permission_path)
    
    def read_file(self, agent_id: str, file_path: str) -> Optional[Dict[str, Any]]:
        """安全读取文件"""
        if not self.can_access(file_path, 'read'):
            self._log_audit_event(agent_id, 'read', file_path, False, 
                                {"error": "Permission denied"})
            return None
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self._log_audit_event(agent_id, 'read', file_path, False,
                                    {"error": "File not found"})
                return None
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查敏感内容
            sensitive_info = self.classifier.classify_content(content)
            
            # 如果发现敏感信息，进行脱敏处理
            if sensitive_info:
                content = self._sanitize_content(content, sensitive_info)
            
            result = {
                'content': content,
                'file_size': len(content),
                'sensitive_info_detected': bool(sensitive_info),
                'sensitive_categories': list(sensitive_info.keys()) if sensitive_info else []
            }
            
            self._log_audit_event(agent_id, 'read', file_path, True, result)
            return result
            
        except Exception as e:
            self._log_audit_event(agent_id, 'read', file_path, False,
                                {"error": str(e)})
            return None
    
    def _sanitize_content(self, content: str, sensitive_info: Dict[str, List[str]]) -> str:
        """脱敏处理内容"""
        sanitized = content
        
        for category, matches in sensitive_info.items():
            for match in matches:
                if category == 'credit_card':
                    # 保留最后4位数字
                    sanitized = sanitized.replace(match, '*' * (len(match) - 4) + match[-4:])
                elif category == 'email':
                    # 部分隐藏邮箱
                    parts = match.split('@')
                    if len(parts) == 2:
                        username, domain = parts
                        if len(username) > 2:
                            sanitized = sanitized.replace(match, 
                                username[:2] + '*' * (len(username) - 2) + '@' + domain)
                elif category == 'phone':
                    # 隐藏中间数字
                    sanitized = sanitized.replace(match, 
                        match[:3] + '*' * (len(match) - 6) + match[-3:])
                else:
                    # 通用脱敏
                    sanitized = sanitized.replace(match, '*' * len(match))
        
        return sanitized
    
    def _log_audit_event(self, agent_id: str, operation: str, file_path: str, 
                        success: bool, details: Dict[str, Any]):
        """记录审计事件"""
        event = AuditEvent(
            timestamp=datetime.now(),
            agent_id=agent_id,
            operation=operation,
            file_path=file_path,
            success=success,
            details=details
        )
        self.audit_log.append(event)
        logger.info(f"Audit: {agent_id} {operation} {file_path} - {'SUCCESS' if success else 'FAILED'}")


class AgentSandbox:
    """Agent沙箱执行环境"""
    
    def __init__(self, file_access: SecureFileAccess, allowed_operations: List[str]):
        self.file_access = file_access
        self.allowed_operations = allowed_operations
        self.agent_id = secrets.token_hex(8)
        self.execution_log = []
    
    def execute_agent_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agent请求"""
        operation = request.get('operation')
        file_path = request.get('file_path')
        
        # 检查操作是否被允许
        if operation not in self.allowed_operations:
            return {
                'success': False,
                'error': f'Operation {operation} not allowed'
            }
        
        # 执行相应的操作
        if operation == 'read_file':
            result = self.file_access.read_file(self.agent_id, file_path)
            if result:
                return {
                    'success': True,
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to read file'
                }
        
        return {
            'success': False,
            'error': f'Unknown operation: {operation}'
        }


class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        self.permissions = []
        self.load_default_permissions()
    
    def load_default_permissions(self):
        """加载默认权限配置"""
        # 示例权限配置
        self.permissions = [
            Permission(
                path="/home/user/documents",
                operations=["read", "write"],
                sensitive_keywords=["password", "secret"],
                require_confirmation=False,
                audit_level="medium"
            ),
            Permission(
                path="/home/user/financial",
                operations=["read"],
                sensitive_keywords=["credit_card", "bank_account", "ssn"],
                require_confirmation=True,
                audit_level="high"
            ),
            Permission(
                path="/home/user/private",
                operations=["none"],
                sensitive_keywords=[],
                require_confirmation=True,
                audit_level="high"
            )
        ]
    
    def get_permissions_for_path(self, path: str) -> Optional[Permission]:
        """获取指定路径的权限"""
        for permission in self.permissions:
            if self._path_matches(path, permission.path):
                return permission
        return None
    
    def _path_matches(self, file_path: str, permission_path: str) -> bool:
        """检查路径匹配"""
        file_path = os.path.abspath(file_path)
        permission_path = os.path.abspath(permission_path)
        return file_path.startswith(permission_path)


def demo_agent_data_interaction():
    """演示Agent与本地数据交互"""
    print("=== Agent与本地数据交互权限控制演示 ===\n")
    
    # 初始化权限管理器
    permission_manager = PermissionManager()
    
    # 创建安全文件访问控制器
    file_access = SecureFileAccess(permission_manager.permissions)
    
    # 创建Agent沙箱
    sandbox = AgentSandbox(file_access, ['read_file'])
    
    # 模拟不同的文件访问场景
    test_scenarios = [
        {
            'name': '访问公开文档',
            'file_path': '/home/user/documents/readme.txt',
            'content': '这是一个公开的文档，包含一些基本信息。'
        },
        {
            'name': '访问包含敏感信息的文档',
            'file_path': '/home/user/documents/account.txt',
            'content': '我的邮箱是 user@example.com，信用卡号是 1234-5678-9012-3456'
        },
        {
            'name': '访问受限区域',
            'file_path': '/home/user/private/secret.txt',
            'content': '这是私密信息'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n--- {scenario['name']} ---")
        
        # 创建测试文件
        test_file = Path(scenario['file_path'])
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(scenario['content'], encoding='utf-8')
        
        # 尝试访问文件
        request = {
            'operation': 'read_file',
            'file_path': str(test_file)
        }
        
        result = sandbox.execute_agent_request(request)
        
        if result['success']:
            print(f"✓ 成功访问文件")
            data = result['data']
            print(f"  文件大小: {data['file_size']} 字符")
            print(f"  检测到敏感信息: {data['sensitive_info_detected']}")
            if data['sensitive_categories']:
                print(f"  敏感信息类型: {', '.join(data['sensitive_categories'])}")
            print(f"  内容预览: {data['content'][:100]}...")
        else:
            print(f"✗ 访问失败: {result['error']}")
        
        # 清理测试文件
        test_file.unlink(missing_ok=True)
    
    # 显示审计日志
    print(f"\n=== 审计日志 ===")
    for event in file_access.audit_log:
        status = "✓" if event.success else "✗"
        print(f"{status} {event.timestamp.strftime('%H:%M:%S')} "
              f"Agent:{event.agent_id} {event.operation} {event.file_path}")


if __name__ == "__main__":
    demo_agent_data_interaction()