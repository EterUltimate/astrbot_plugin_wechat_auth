"""
微信用户鉴权插件

让 AstrBot 能够自动识别微信用户并将指定用户设为管理员。
支持个人微信接入。
"""

from typing import Optional

from astrbot.api.star import Star, Context, register
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import filter, AstrMessageEvent

# KV 存储中的键名
KV_KEY_ADMIN_IDS = "admin_wechat_ids"


@register(
    "astrbot_plugin_wechat_auth",
    "EterUltimate",
    "自动识别微信用户并将指定用户设为管理员",
    "1.1.0",
    "https://github.com/EterUltimate/astrbot_plugin_wechat_auth",
)
class WeChatAuthPlugin(Star):
    """微信用户鉴权插件"""

    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config or {}

    async def _get_admin_ids(self) -> list:
        """获取管理员ID列表"""
        ids = await self.get_kv_data(KV_KEY_ADMIN_IDS, [])
        return ids if isinstance(ids, list) else []

    async def _save_admin_ids(self, admin_ids: list):
        """保存管理员ID列表"""
        await self.put_kv_data(KV_KEY_ADMIN_IDS, admin_ids)

    def _is_wechat_platform(self, event: AstrMessageEvent) -> bool:
        """判断是否为微信平台"""
        platform = event.unified_msg_origin or ""
        return platform.lower() in ["weixin_oc", "weixin", "wechat"]

    def _get_user_id(self, event: AstrMessageEvent) -> Optional[str]:
        """获取用户ID"""
        if hasattr(event, "sender") and event.sender:
            if hasattr(event.sender, "user_id"):
                return str(event.sender.user_id)
        return None

    def _get_user_nickname(self, event: AstrMessageEvent) -> str:
        """获取用户昵称"""
        if hasattr(event, "sender") and event.sender:
            if hasattr(event.sender, "nickname"):
                return str(event.sender.nickname)
        return "未知用户"

    async def _is_admin(self, user_id: str) -> bool:
        """检查是否为管理员"""
        admin_ids = await self._get_admin_ids()
        return str(user_id) in [str(uid) for uid in admin_ids]

    async def _add_admin(self, user_id: str) -> bool:
        """添加管理员"""
        admin_ids = await self._get_admin_ids()
        user_id_str = str(user_id)

        if user_id_str not in [str(uid) for uid in admin_ids]:
            admin_ids.append(user_id_str)
            await self._save_admin_ids(admin_ids)
            return True
        return False

    async def _remove_admin(self, user_id: str) -> bool:
        """移除管理员"""
        admin_ids = await self._get_admin_ids()
        user_id_str = str(user_id)

        new_admin_ids = [str(uid) for uid in admin_ids if str(uid) != user_id_str]
        if len(new_admin_ids) != len(admin_ids):
            await self._save_admin_ids(new_admin_ids)
            return True
        return False

    # ------------------------------------------------------------------ #
    #  插件生命周期
    # ------------------------------------------------------------------ #

    async def terminate(self):
        """插件卸载时清理资源"""
        logger.info("[微信鉴权] 插件已卸载")

    # ------------------------------------------------------------------ #
    #  事件处理
    # ------------------------------------------------------------------ #

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        """处理所有消息事件，自动鉴权微信用户"""
        if not self.config.get("auto_auth", True):
            return

        if not self._is_wechat_platform(event):
            return

        user_id = self._get_user_id(event)
        if not user_id:
            return

        # 自动设为管理员
        if self.config.get("auto_admin", True):
            if not await self._is_admin(user_id):
                if await self._add_admin(user_id):
                    logger.info(f"[微信鉴权] 用户 {user_id} 已自动设为管理员")

                    if self.config.get("notify_on_auth", True):
                        nickname = self._get_user_nickname(event)
                        yield event.plain_result(f"欢迎 {nickname}！您已被自动设为管理员。")

    # ------------------------------------------------------------------ #
    #  命令
    # ------------------------------------------------------------------ #

    @filter.command("获取ID", alias={"sid", "getid"})
    async def cmd_get_user_id(self, event: AstrMessageEvent):
        """获取当前用户ID"""
        user_id = self._get_user_id(event)
        nickname = self._get_user_nickname(event)

        if user_id:
            is_admin = "是管理员" if await self._is_admin(user_id) else "不是管理员"
            yield event.plain_result(
                f"您的用户ID: {user_id}\n"
                f"昵称: {nickname}\n"
                f"状态: {is_admin}"
            )
        else:
            yield event.plain_result("无法获取用户ID。")

    @filter.command("添加微信管理员", alias={"wxadmin add"})
    async def cmd_add_admin(self, event: AstrMessageEvent, user_id: str = ""):
        """添加微信管理员"""
        # 检查调用者权限
        caller_id = self._get_user_id(event)
        if caller_id and not await self._is_admin(caller_id):
            yield event.plain_result("您没有管理员权限。")
            return

        if not user_id:
            yield event.plain_result(
                "使用方法: /添加微信管理员 <用户ID>\n"
                "可通过 /获取ID 获取您的用户ID。"
            )
            return

        if await self._add_admin(user_id):
            yield event.plain_result(f"已将用户 {user_id} 设为管理员。")
        else:
            yield event.plain_result(f"用户 {user_id} 已经是管理员。")

    @filter.command("移除微信管理员", alias={"wxadmin remove"})
    async def cmd_remove_admin(self, event: AstrMessageEvent, user_id: str = ""):
        """移除微信管理员"""
        # 检查调用者权限
        caller_id = self._get_user_id(event)
        if caller_id and not await self._is_admin(caller_id):
            yield event.plain_result("您没有管理员权限。")
            return

        if not user_id:
            yield event.plain_result(
                "使用方法: /移除微信管理员 <用户ID>\n"
                "可通过 /获取ID 获取用户ID。"
            )
            return

        if await self._remove_admin(user_id):
            yield event.plain_result(f"已移除用户 {user_id} 的管理员权限。")
        else:
            yield event.plain_result(f"用户 {user_id} 不在管理员列表中。")

    @filter.command("微信管理员列表", alias={"wxadmin list"})
    async def cmd_list_admins(self, event: AstrMessageEvent):
        """查看微信管理员列表"""
        admin_ids = await self._get_admin_ids()

        if not admin_ids:
            yield event.plain_result("当前没有设置微信管理员。")
            return

        admin_list = "\n".join([f"- {uid}" for uid in admin_ids])
        yield event.plain_result(f"微信管理员列表：\n{admin_list}")
