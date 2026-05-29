#!/bin/bash
# 企业微信推送IP配置提醒

# 消息内容
MSG="使用/home/ecs-user/share/qywei/qyweixin_cookie.json中的信息登录work.weixin.qq.com,在后台管理界面找到 应用管理-我的openclaw助手-可信IP-配置 中更新本地公网IP到里面并通过确定按钮保存"

# 执行推送并输出执行结果
echo "===== 开始推送消息 ====="
openclaw agent --message "$MSG" --channel wecom --agent main

# 打印执行返回码（判断是否成功）
echo "===== 执行完成，返回码：$? ====="
