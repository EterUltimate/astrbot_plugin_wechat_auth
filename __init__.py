"""
微信用户鉴权插件
让 AstrBot 能够自动识别微信用户并将指定用户设为管理员
"""

from .main import WeChatAuthPlugin

__all__ = ["WeChatAuthPlugin"]
