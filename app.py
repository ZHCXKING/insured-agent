# %%
import os
import threading
import logging
import redis
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from AssistantAgent.agent import AssistantAgent
# %%
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("App")
app = Flask(__name__)
redis_url = os.getenv("REDIS_URL")
redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
ifa_agent = AssistantAgent()
# %%
def send_message(group_name: str, message_content: str):
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    robot_id = os.getenv("ROBOT_ID")
    # Query 参数
    params = {
        "robotId": robot_id
    }
    # 构建消息体结构
    message_item = {
        "type": 203,
        "titleList": [group_name],
        "receivedContent": message_content
    }
    payload = {
        "socketType": 2,
        "list": [message_item]
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
    response_data = response.json()
    if response.status_code == 200:
        logger.info(f"消息发送成功至群 [{group_name}]")
    else:
        logger.error(f"消息发送失败，接口返回: {response_data}")
# %%
def handle_message_ifa(data):
    try:
        print(data)
        spoken = data.get("spoken")
        sender = data.get("receivedName")
        group = data.get("groupName")
        at_me = data.get("atMe")
        text_type = data.get("textType")
        picture = data.get("filePath")
        if not spoken:
            return
        # 消息缓存
        cache_key = f"chat_cache:{group}"
        formatted_message = f"[{sender}]: {spoken}"
        redis_client.rpush(cache_key, formatted_message)
        redis_client.ltrim(cache_key, -200, -1) #只保留最近200条消息
        redis_client.expire(cache_key, 259200) #缓存日期保留3天
        # 判断是否触发机器人
        if at_me == 'false':
            return
        # 立刻发送一条消息进行响应
        # robot_id = os.getenv("IFA_ROBOT_ID")
        # ack_message = f"收到，正在为您处理，请稍等..."
        # send_message(group_name=group, message_content=ack_message)
        # 取出缓存记录，加锁并询问AI
        lock_key = f"lock:ifa_group:{group}"
        lock = redis_client.lock(lock_key, timeout=120, blocking_timeout=60)
        with lock:
            cached_history_list = redis_client.lrange(cache_key, 0, -1)
            cached_history_text = "\n".join(cached_history_list)
            reply = ifa_agent.process_messages(
                text=cached_history_text,
                sender=sender,
                group=group
            )
            redis_client.delete(cache_key)
        # 发送回复
        send_message(group_name=group, message_content=reply)
    except Exception as e:
        logger.error(f"处理消息失败: {e}")
# %%
@app.route('/ifa/thirdQa', methods=['POST'])
def third_qa():
    data = request.json
    if not data:
        return jsonify({"code": -1, "message": "无有效数据"}), 400
    thread = threading.Thread(target=handle_message_ifa, args=(data,))
    thread.start()
    return jsonify({
        "code": 0,
        "message": "success"
    })
if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    app.run(host='0.0.0.0', port=port, debug=False)