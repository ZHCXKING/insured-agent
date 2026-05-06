# %%
import os
import requests
import redis
from datetime import datetime, timedelta
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
    print(f"消息发送成功：{message}")
    # TODO 测试的时候，直接将回复打印出来
    # response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
    # response_data = response.json()
    # if response.status_code == 200:
    #     return f"消息发送成功"
    # else:
    #     return f"消息发送失败，接口返回: {response_data}"
# %%
@tool
def schedule_message_delayed(message: str, delay_minutes: float, runtime: ToolRuntime) -> str:
    """
    在指定分钟数后向当前群聊发送消息。
    参数:
        message: 要发送的消息内容
        delay_minutes: 延迟发送的时间（分钟数，支持小数。例如10秒=0.166）
    """
    group_name = runtime.context.group_name
    run_date = datetime.now() + timedelta(minutes=delay_minutes)
    scheduler.add_job(
        execute_send_task,
        trigger='date',
        run_date=run_date,
        args=[group_name, message]
    )
    return f"任务已创建：将在 {delay_minutes} 分钟后向群发送消息。"