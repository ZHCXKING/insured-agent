# %%
import os
import requests
from langchain.tools import tool, ToolRuntime
# %%
@tool
def send_message(message: str, runtime: ToolRuntime) -> str:
    """向当前所在的群聊发送消息。"""
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    params = {"robotId": os.getenv("ROBOT_ID")}
    message_item = {
        "type": 203,
        "titleList": [runtime.context.group_name],
        "receivedContent": message
    }
    payload = {"socketType": 2, "list": [message_item]}
    headers = {"Content-Type": "application/json"}
    # TODO 测试中，如果需要用worktool发送消息的话，将下面的注释去掉
    print(message)
    return f"消息发送成功"
    # response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
    # response_data = response.json()
    # if response.status_code == 200:
    #     return f"消息发送成功"
    # else:
    #     return f"消息发送失败，接口返回: {response_data}"