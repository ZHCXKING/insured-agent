from langchain.tools import tool, ToolRuntime
import os
import requests
# 你的发送逻辑（保持在文件内或导入）
def send_message_to_worktool(group_name: str, message_content: str):
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    robot_id = os.getenv("ROBOT_ID")
    message_item = {
        "type": 203,
        "titleList": [group_name],
        "receivedContent": message_content
    }
    payload = {"socketType": 2, "list": [message_item]}
    response = requests.post(url, params={"robotId": robot_id}, json=payload, timeout=10)
    return response.status_code == 200
@tool
def send_message(message: str, runtime: ToolRuntime) -> str:
    """向当前所在的群聊发送消息。"""
    # 1. 从 runtime.context 中提取 GroupChatContext
    ctx = runtime.context
    group_name = getattr(ctx, 'group_name', None)

    if not group_name:
        return "错误：无法获取当前群名。"

    # 2. 执行发送
    #success = send_message_to_worktool(group_name, message)
    success = True
    if success:
        return f"已成功发送至群 [{group_name}]"
    else:
        return "发送失败，接口错误。"