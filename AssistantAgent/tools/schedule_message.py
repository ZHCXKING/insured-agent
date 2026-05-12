# %%
import os
import requests
import redis
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.tools import tool, ToolRuntime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
# %%
redis_url = os.getenv("REDIS_URL")
redis_client = redis.from_url(redis_url)
jobstores = {
    'default': RedisJobStore(
        host=redis_client.connection_pool.connection_kwargs.get('host'),
        port=redis_client.connection_pool.connection_kwargs.get('port'),
        db=0,
        jobs_key='scheduler:jobs',
        run_times_key='scheduler:run_times'
    )
}
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()
# %%
def execute_send_task(group_name: str, message: str):
    """具体的发送动作"""
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    params = {"robotId": os.getenv("AA_ROBOT_ID")}
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
# %%
class ScheduleMessageInput(BaseModel):
    message: str = Field(
        ...,
        description="要发送的消息内容",
    )
    scheduled_time: str = Field(
        ...,
        description="计划发送的时间，格式 YYYY-MM-DD HH:mm（如 2026-05-16 14:30）",
        pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$",
    )
# %%
@tool(args_schema=ScheduleMessageInput)
def schedule_message_delayed(message: str, scheduled_time: str, runtime: ToolRuntime) -> str:
    """在指定时间向当前群聊发送消息。"""
    group_name = runtime.context.group_name
    run_date = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
    if run_date <= datetime.now():
        return "错误：计划发送时间必须晚于当前时间"
    scheduler.add_job(
        execute_send_task,
        trigger='date',
        run_date=run_date,
        misfire_grace_time=600,
        args=[group_name, message]
    )
    return f"任务已创建：将在 {scheduled_time} 向群发送消息。"