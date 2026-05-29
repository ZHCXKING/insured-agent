# %%
import os
import requests
from pydantic import BaseModel, Field
from langchain.tools import tool, ToolRuntime
# %%
class SendMessageInput(BaseModel):
    message: str = Field(
        ...,
        description="要发送的消息内容",
    )
# %%
@tool(args_schema=SendMessageInput)
def send_message(message: str, runtime: ToolRuntime) -> str:
    """调用这个工具可以发送消息。"""
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    params = {"robotId": os.getenv("AA_ROBOT_ID")}
    message_item = {
        "type": 203,
        "titleList": [runtime.context.group_name],
        "receivedContent": message
    }
    payload = {"socketType": 2, "list": [message_item]}
    headers = {"Content-Type": "application/json"}
    # todo 这里临时修改规则
    print(message)
    return f"消息发送成功"
    # response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
    # response_data = response.json()
    # if response.status_code == 200:
    #     return f"消息发送成功"
    # else:
    #     return f"消息发送失败，接口返回: {response_data}"