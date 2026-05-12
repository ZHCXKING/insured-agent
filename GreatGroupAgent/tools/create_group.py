# %%
import os
import json
import redis
import requests
from typing import List
from pydantic import BaseModel, Field
from langchain.tools import tool, ToolRuntime
# %%
redis_url = os.getenv("REDIS_URL")
redis_client = redis.from_url(redis_url, decode_responses=True)
# %%
class CreateGroupInput(BaseModel):
    appointment_time: str = Field(
        ...,
        description="预约日期，必须符合 YYYY.M.D 格式，例如 2026.4.23",
        pattern=r"^\d{4}\.\d{1,2}\.\d{1,2}$",
    )
    client_name: str = Field(
        ...,
        description="客户的姓名",
    )
    insurance_companies: List[str] = Field(
        ...,
        description="保险公司名称列表。",
    )
    applicant_name: str = Field(
        ...,
        description="申请预约的人员（顾问）名称",
    )
# todo 这里是拉群的固定成员
_FIXED_MEMBERS = ["白`~`灰", "ZHCX"]
# %%
@tool(args_schema=CreateGroupInput)
def create_group(appointment_time: str, client_name: str, insurance_companies: List[str], applicant_name: str, runtime: ToolRuntime) -> str:
    """
    为客户预约创建专属服务群聊。如果有多个日期，需要多次调用此工具。创建成功后，稍后会自动将新群的二维码发回本群。
    """
    new_group_name = f"{appointment_time}{client_name}{'+'.join(insurance_companies)}"
    members = [applicant_name] + _FIXED_MEMBERS
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    params = {"robotId": os.getenv("GGA_ROBOT_ID")}
    message_item = {
        "type": 206,
        "groupName": new_group_name,
        "selectList": members,
        "groupAnnouncement": f"欢迎加入【{client_name}】的专属服务群！"
    }
    payload = {"socketType": 2, "list": [message_item]}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
    response_data = response.json()
    if response_data.get("code") == 200:
        original_group = runtime.context.group_name
        task_info = {
            "original_group": original_group,
            "new_group_name": new_group_name
        }
        redis_key = f"creating_group:{new_group_name}"
        redis_client.setex(redis_key, 3600, json.dumps(task_info))
        return f"已向后台下发创建【{new_group_name}】的指令，正在等待生成群二维码，请稍候..."
    else:
        return f"创建群聊失败，接口返回: {response_data}"