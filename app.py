# %%
import os
import threading
import logging
import redis
import urllib.parse
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()
from AssistantAgent.agent import AssistantAgent
from GreatGroupAgent.agent import GreatGroupAgent
from utils import reply_message, send_image
# %%
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("App")
app = Flask(__name__)
redis_url = os.getenv("REDIS_URL")
redis_client = redis.from_url(redis_url, decode_responses=True)
AA_agent = AssistantAgent()
AA_agent.robot_id = os.getenv("AA_ROBOT_ID")
GGA_agent = GreatGroupAgent()
GGA_agent.robot_id = os.getenv("GGA_ROBOT_ID")
# %%
def handle_message(data, agent):
    try:
        print(data)
        spoken = data.get("spoken")
        sender = data.get("receivedName")
        group = data.get("groupName")
        at_me = data.get("atMe")
        picture = data.get("fileBase64")
        cache_key = f"chat_cache:{agent.app_name}:{group}"
        message_obj = {
            "sender": sender,
            "spoken": spoken,
            "picture": picture
        }
        if at_me != 'true':
            redis_client.rpush(cache_key, json.dumps(message_obj))
            redis_client.ltrim(cache_key, -200, -1)
            redis_client.expire(cache_key, 259200)
            return
        lock_key = f"lock:{agent.app_name}_group:{group}"
        lock = redis_client.lock(lock_key, timeout=120, blocking_timeout=60)
        with lock:
            cached_history_list = redis_client.lrange(cache_key, 0, -1)
            redis_client.ltrim(cache_key, len(cached_history_list), -1)
            cached_history_list.append(json.dumps(message_obj))
            cached_history_text = "\n".join(cached_history_list)
            reply = agent.process_messages(
                text=cached_history_text,
                sender=sender,
                group=group
            )
        reply_message(reply, group, agent.robot_id)
    except Exception as e:
        logger.error(f"处理消息失败: {e}")
# %%
@app.route('/assistant/message', methods=['POST'])
def assistant_message():
    data = request.json
    if not data:
        return jsonify({"code": -1, "message": "无有效数据"}), 400
    thread = threading.Thread(target=handle_message, args=(data, AA_agent))
    thread.start()
    return jsonify({
        "code": 0,
        "message": "success"
    })
# %%
@app.route('/greatgroup/message', methods=['POST'])
def greatgroup_message():
    data = request.json
    if not data:
        return jsonify({"code": -1, "message": "无有效数据"}), 400
    thread = threading.Thread(target=handle_message, args=(data, GGA_agent))
    thread.start()
    return jsonify({
        "code": 0,
        "message": "success"
    })
# %%
@app.route('/QRcode', methods=['POST'])
def QRcode():
    data = request.json
    print(data)
    if not data:
        return jsonify({"code": -1, "message": "无有效数据"}), 400
    group_name = data.get('groupName')
    qr_link = data.get('qrCode')
    redis_key = f"creating_group:{group_name}"
    task_data_str = redis_client.get(redis_key)
    if task_data_str:
        redis_client.delete(redis_key)
        task_info = json.loads(task_data_str)
        original_group = task_info.get('original_group')
        new_group_name = task_info.get('new_group_name')
        encoded_link = urllib.parse.quote(qr_link)
        qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={encoded_link}"
        file_name = f"{new_group_name}_qrcode.png"
        extra_text = f"新群聊【{new_group_name}】创建成功！"
        send_image(
            target_name=original_group,
            image_url=qr_image_url,
            file_name=file_name,
            extra_text=extra_text,
            robot_id=os.getenv("GGA_ROBOT_ID")
        )
        return jsonify({"code": 0, "status": "success", "message": "二维码已成功回传给原群聊"})
    else:
        return jsonify({"code": -1, "status": "ignored", "message": "未知的 messageId 或任务已过期"})
# %%
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})
# %%
if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    app.run(host='0.0.0.0', port=port, debug=False)