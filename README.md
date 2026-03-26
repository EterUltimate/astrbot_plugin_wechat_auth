# 微信鉴权插件

自动识别微信用户并将指定用户设为管理员，支持个人微信接入。

---

## 功能特性

- ✅ 自动识别微信用户
- ✅ 首次使用时自动设为管理员
- ✅ 支持手动添加/移除管理员
- ✅ 支持查看管理员列表
- ✅ 获取当前用户ID

---

## 安装

1. 将 `astrbot_plugin_wechat_auth` 文件夹复制到 AstrBot 的 `data/plugins/` 目录
2. 在 AstrBot WebUI 的插件管理页面中启用插件
3. 重启 AstrBot

---

## 配置

在 AstrBot 插件配置中可设置：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| admin_wechat_ids | array | [] | 管理员微信用户ID列表 |
| auto_auth | bool | true | 是否启用自动鉴权 |
| auto_admin | bool | true | 是否自动将首次用户设为管理员 |
| notify_on_auth | bool | true | 是否在自动鉴权时发送通知 |

---

## 命令

| 命令 | 别名 | 说明 |
|------|------|------|
| `/获取ID` | `/sid`, `/getid` | 获取当前用户ID |
| `/添加微信管理员 <用户ID>` | `/wxadmin add` | 添加管理员 |
| `/移除微信管理员 <用户ID>` | `/wxadmin remove` | 移除管理员 |
| `/微信管理员列表` | `/wxadmin list` | 查看管理员列表 |

---

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

---

## 目录结构

```
astrbot_plugin_wechat_auth/
├── __init__.py         # 包入口
├── main.py             # 插件主体
├── metadata.yaml       # 插件元数据
├── _conf_schema.json   # 配置 Schema
└── README.md           # 说明文档
```

---

## License

MIT
