# %%
import os
import requests
# %%
def reply_message(message: str, group_name: str) -> str:
    """向当前所在的群聊发送消息。"""
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    params = {"robotId": os.getenv("ROBOT_ID")}
    message_item = {
        "type": 203,
        "titleList": [group_name],
        "receivedContent": message
    }
    payload = {"socketType": 2, "list": [message_item]}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
    response_data = response.json()
    if response.status_code == 200:
        return f"消息发送成功"
    else:
        return f"消息发送失败，接口返回: {response_data}"