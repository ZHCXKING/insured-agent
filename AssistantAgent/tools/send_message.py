# %%
import os
import requests
from langchain.tools import tool, ToolRuntime
# %%
@tool
def send_message(message: str, runtime: ToolRuntime) -> str:
    """向当前所在的群聊发送消息。"""
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    params = {"robotId": os.getenv("AA_ROBOT_ID")}
    message_item = {
        "type": 203,
        "titleList": [runtime.context.group_name],
        "receivedContent": message
    }
    payload = {"socketType": 2, "list": [message_item]}
    headers = {"Content-Type": "application/json"}
    print(f"消息发送成功：{message}")
    # TODO 测试的时候，直接将回复打印出来
    # response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
    # response_data = response.json()
    # if response.status_code == 200:
    #     return f"消息发送成功"
    # else:
    #     return f"消息发送失败，接口返回: {response_data}"