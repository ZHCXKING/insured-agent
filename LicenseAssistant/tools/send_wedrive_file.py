# %%
import os
import requests
from typing import List
from pydantic import BaseModel, Field
from langchain.tools import tool, ToolRuntime
# %%
class SendWeDriveFileInput(BaseModel):
    file_names: List[str] = Field(
        ...,
        description="要推送的微盘文件名称列表",
    )
    extra_text: str = Field(
        default="",
        description="附加留言，选填",
    )
# %%
@tool(args_schema=SendWeDriveFileInput)
def send_wedrive_file(file_names: List[str], extra_text: str, runtime: ToolRuntime) -> str:
    """推送微盘文件到当前群聊。可以推送一个或多个微盘文件。当顾问需要资料文件时使用此工具。"""
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    params = {"robotId": os.getenv("LA_ROBOT_ID")}
    headers = {"Content-Type": "application/json"}
    results = []
    for i, object_name in enumerate(file_names):
        message_item = {
            "type": 209,
            "titleList": [runtime.context.group_name],
            "objectName": object_name,
        }
        if i == 0 and extra_text:
            message_item["extraText"] = extra_text
        payload = {"socketType": 2, "list": [message_item]}
        response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
        response_data = response.json()
        if response_data.get("code") == 200:
            results.append(f"【{object_name}】推送成功")
        else:
            results.append(f"【{object_name}】推送失败: {response_data}")
    return "\n".join(results)
