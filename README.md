# 微信鉴权插件

基于 PR #6777 实现，支持个人微信（C2C）接入的自动鉴权功能。

## 功能

- ✅ 自动识别微信用户
- ✅ 首次使用时自动设为管理员
- ✅ 支持手动添加/移除管理员
- ✅ 支持查看管理员列表
- ✅ 获取当前用户ID

## 安装

1. 将 `wechat_auth_plugin` 文件夹复制到 AstrBot 的 `plugins` 目录
2. 重启 AstrBot

## 配置

配置文件位置：`{data_dir}/wechat_auth_config.json`

```json
{
    "admin_wechat_ids": [],
    "auto_auth": true,
    "auto_admin": true,
    "notify_on_auth": true
}
```

| 配置项 | 类型 | 说明 |
|--------|------|------|
| admin_wechat_ids | array | 管理员微信用户ID列表 |
| auto_auth | bool | 是否启用自动鉴权 |
| auto_admin | bool | 是否自动将首次用户设为管理员 |
| notify_on_auth | bool | 是否在自动鉴权时发送通知 |

## 命令

| 命令 | 说明 | 用法 |
|------|------|------|
| /获取ID | 获取当前用户ID | /获取ID |
| /添加微信管理员 | 添加管理员 | /添加微信管理员 <用户ID> |
| /移除微信管理员 | 移除管理员 | /移除微信管理员 <用户ID> |
| /微信管理员列表 | 查看管理员列表 | /微信管理员列表 |

## 微信平台标识

支持的平台标识：
- `weixin_oc` - 个人微信（PR #6777 新增）
- `weixin`
- `wechat`

## 使用流程

1. **配置个人微信**：
   - 在 AstrBot 管理面板添加平台，选择"个人微信"
   - 扫描二维码登录

2. **获取用户ID**：
   - 用户发送 `/获取ID` 获取自己的微信ID

3. **设置管理员**：
   - 管理员使用 `/添加微信管理员 <用户ID>` 添加

4. **自动鉴权**：
   - 首次使用自动添加用户到管理员列表

## PR 相关

- GitHub PR: [#6777](https://github.com/AstrBotDevs/AstrBot/pull/6777)
- 功能: 支持个人微信（WeChat C2C）私聊接入
