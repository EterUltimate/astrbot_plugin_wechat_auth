"""
微信用户鉴权插件
让 AstrBot 能够自动识别微信用户并将指定用户设为管理员

基于 PR #6777: 支持个人微信接入

安装方法：
1. 将此文件夹放入 AstrBot 的 plugins 目录
2. 重启 AstrBot
3. 配置管理员微信 ID

配置示例：
```json
{
    "admin_wechat_ids": ["wx_user_id_1", "wx_user_id_2"],
    "auto_auth": true,
    "auto_admin": true,
    "notify_on_auth": true
}
```
"""

import json
import os
from typing import List, Optional

from astrbot.api import star, register_star
from astrbot.api.event import AstrMessageEvent, MessageChain, MessageEventResult
from astrbot.core.star import Context


@register_star("微信鉴权插件")
class WeChatAuthPlugin(star.Star):
    """微信用户鉴权插件"""
    
    metadata = {
        "name": "微信鉴权插件",
        "description": "自动识别微信用户并将指定用户设为管理员",
        "version": "1.0.0",
        "author": "EterUltimate"
    }
    
    def __init__(self, context: Context):
        super().__init__(context)
        self._load_config()
    
    def _get_config_path(self) -> str:
        """获取配置文件路径"""
        data_dir = self.context.get_config().get("data_dir", "")
        return os.path.join(data_dir, "wechat_auth_config.json")
    
    def _load_config(self):
        """加载配置"""
        config_path = self._get_config_path()
        default_config = {
            "admin_wechat_ids": [],
            "auto_auth": True,
            "auto_admin": True,
            "notify_on_auth": True
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception:
                self.config = default_config
        else:
            self.config = default_config
    
    def _save_config(self):
        """保存配置"""
        config_path = self._get_config_path()
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.context.logger.error(f"保存微信鉴权配置失败: {e}")
    
    def _is_wechat_platform(self, event: AstrMessageEvent) -> bool:
        """判断是否为微信平台"""
        platform = event.unified_msg_origin or ""
        return platform.lower() in ["weixin_oc", "weixin", "wechat"]
    
    def _get_user_id(self, event: AstrMessageEvent) -> Optional[str]:
        """获取用户ID"""
        if hasattr(event, 'sender') and event.sender:
            if hasattr(event.sender, 'user_id'):
                return str(event.sender.user_id)
        return None
    
    def _get_user_nickname(self, event: AstrMessageEvent) -> str:
        """获取用户昵称"""
        if hasattr(event, 'sender') and event.sender:
            if hasattr(event.sender, 'nickname'):
                return str(event.sender.nickname)
        return "未知用户"
    
    def _is_admin(self, user_id: str) -> bool:
        """检查是否为管理员"""
        admin_ids = self.config.get("admin_wechat_ids", [])
        return str(user_id) in [str(uid) for uid in admin_ids]
    
    def _add_admin(self, user_id: str) -> bool:
        """添加管理员"""
        admin_ids = self.config.get("admin_wechat_ids", [])
        user_id_str = str(user_id)
        
        if user_id_str not in [str(uid) for uid in admin_ids]:
            admin_ids.append(user_id_str)
            self.config["admin_wechat_ids"] = admin_ids
            self._save_config()
            return True
        return False
    
    def _remove_admin(self, user_id: str) -> bool:
        """移除管理员"""
        admin_ids = self.config.get("admin_wechat_ids", [])
        user_id_str = str(user_id)
        
        new_admin_ids = [str(uid) for uid in admin_ids if str(uid) != user_id_str]
        if len(new_admin_ids) != len(admin_ids):
            self.config["admin_wechat_ids"] = new_admin_ids
            self._save_config()
            return True
        return False
    
    @star.on_message()
    async def on_message(self, event: AstrMessageEvent):
        """处理消息事件"""
        if not self.config.get("auto_auth", True):
            return
        
        if not self._is_wechat_platform(event):
            return
        
        user_id = self._get_user_id(event)
        if not user_id:
            return
        
        # 自动设为管理员
        if self.config.get("auto_admin", True):
            if not self._is_admin(user_id):
                if self._add_admin(user_id):
                    self.context.logger.info(f"微信用户 {user_id} 已自动设为管理员")
                    
                    if self.config.get("notify_on_auth", True):
                        nickname = self._get_user_nickname(event)
                        await event.send(
                            MessageChain().message(
                                f"欢迎 {nickname}！您已被自动设为管理员。"
                            )
                        )
        
        # 检查管理员权限
        if self._is_admin(user_id):
            # 可以在这里添加额外的管理员权限处理逻辑
            pass
    
    @star.command("添加微信管理员", alias=["wxadmin add"])
    async def add_wechat_admin(self, event: AstrMessageEvent, user_id: str = ""):
        """添加微信管理员"""
        # 检查调用者权限
        caller_id = self._get_user_id(event)
        if caller_id and not self._is_admin(caller_id):
            event.set_result(
                MessageEventResult().message("您没有管理员权限。")
            )
            return
        
        if not user_id:
            event.set_result(
                MessageEventResult().message(
                    "使用方法: /添加微信管理员 <用户ID>\n"
                    "可通过 /获取ID 获取您的用户ID。"
                )
            )
            return
        
        if self._add_admin(user_id):
            event.set_result(
                MessageEventResult().message(f"已将用户 {user_id} 设为管理员。")
            )
        else:
            event.set_result(
                MessageEventResult().message(f"用户 {user_id} 已经是管理员。")
            )
    
    @star.command("移除微信管理员", alias=["wxadmin remove"])
    async def remove_wechat_admin(self, event: AstrMessageEvent, user_id: str = ""):
        """移除微信管理员"""
        # 检查调用者权限
        caller_id = self._get_user_id(event)
        if caller_id and not self._is_admin(caller_id):
            event.set_result(
                MessageEventResult().message("您没有管理员权限。")
            )
            return
        
        if not user_id:
            event.set_result(
                MessageEventResult().message(
                    "使用方法: /移除微信管理员 <用户ID>\n"
                    "可通过 /获取ID 获取用户ID。"
                )
            )
            return
        
        if self._remove_admin(user_id):
            event.set_result(
                MessageEventResult().message(f"已移除用户 {user_id} 的管理员权限。")
            )
        else:
            event.set_result(
                MessageEventResult().message(f"用户 {user_id} 不在管理员列表中。")
            )
    
    @star.command("微信管理员列表", alias=["wxadmin list"])
    async def list_wechat_admins(self, event: AstrMessageEvent):
        """查看微信管理员列表"""
        admin_ids = self.config.get("admin_wechat_ids", [])
        
        if not admin_ids:
            event.set_result(
                MessageEventResult().message("当前没有设置微信管理员。")
            )
            return
        
        admin_list = "\n".join([f"- {uid}" for uid in admin_ids])
        event.set_result(
            MessageEventResult().message(f"微信管理员列表：\n{admin_list}")
        )
    
    @star.command("获取ID", alias=["sid", "getid"])
    async def get_user_id(self, event: AstrMessageEvent):
        """获取当前用户ID"""
        user_id = self._get_user_id(event)
        nickname = self._get_user_nickname(event)
        
        if user_id:
            is_admin = "是管理员" if self._is_admin(user_id) else "不是管理员"
            event.set_result(
                MessageEventResult().message(
                    f"您的用户ID: {user_id}\n"
                    f"昵称: {nickname}\n"
                    f"状态: {is_admin}"
                )
            )
        else:
            event.set_result(
                MessageEventResult().message("无法获取用户ID。")
            )
