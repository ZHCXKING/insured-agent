# %%
import os
import json
import redis
import requests
from langchain.tools import tool, ToolRuntime
# %%
redis_url = os.getenv("REDIS_URL")
redis_client = redis.from_url(redis_url, decode_responses=True)
# %%
@tool
def create_group(new_group_name: str, members: list[str], runtime: ToolRuntime) -> str:
    """创建一个指定名称的群聊，并拉入指定成员。创建成功后，稍后会自动将新群的二维码发回本群。"""
    # TODO 在正式使用的时候，需要补全members
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    params = {"robotId": os.getenv("ROBOT_ID")}
    message_item = {
        "type": 206,
        "groupName": new_group_name,
        "selectList": members,
        "groupAnnouncement": "欢迎加入本群！"
    }
    payload = {"socketType": 2, "list": [message_item]}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
    response_data = response.json()
    if response_data.get("code") == 200:
        message_id = response_data.get("data")
        original_group = runtime.context.group_name
        task_info = {
            "original_group": original_group,
            "new_group_name": new_group_name
        }
        redis_key = f"creating_group:{message_id}"
        redis_client.setex(redis_key, 3600, json.dumps(task_info))
        return f"已向后台下发创建【{new_group_name}】的指令，正在等待生成群二维码，请稍候..."
    else:
        return f"创建群聊失败，接口返回: {response_data}"