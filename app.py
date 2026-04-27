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
from utils import reply_message, send_image
# %%
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("App")
app = Flask(__name__)
redis_url = os.getenv("REDIS_URL")
redis_client = redis.from_url(redis_url, decode_responses=True)
AA_agent = AssistantAgent()
# %%
def handle_message(data):
    try:
        print(data)
        spoken = data.get("spoken")
        sender = data.get("receivedName")
        group = data.get("groupName")
        at_me = data.get("atMe")
        picture = data.get("fileBase64")
        # 消息缓存
        cache_key = f"chat_cache:{group}"
        message_obj = {
            "sender": sender,
            "spoken": spoken,
            "picture": picture
        }
        redis_client.rpush(cache_key, json.dumps(message_obj))
        redis_client.ltrim(cache_key, -200, -1) #只保留最近200条消息
        redis_client.expire(cache_key, 259200) #缓存日期保留3天
        # 判断是否触发机器人
        if at_me == 'true':
            # 取出缓存记录，加锁并询问AI
            lock_key = f"lock:AA_group:{group}"
            lock = redis_client.lock(lock_key, timeout=120, blocking_timeout=60)
            with lock:
                cached_history_list = redis_client.lrange(cache_key, 0, -1)
                cached_history_text = "\n".join(cached_history_list)
                reply = AA_agent.process_messages(
                    text=cached_history_text,
                    sender=sender,
                    group=group
                )
                redis_client.delete(cache_key)
            reply_message(reply, group)
        else:
            return
    except Exception as e:
        logger.error(f"处理消息失败: {e}")
# %%
@app.route('/message', methods=['POST'])
def third_qa():
    data = request.json
    if not data:
        return jsonify({"code": -1, "message": "无有效数据"}), 400
    thread = threading.Thread(target=handle_message, args=(data,))
    thread.start()
    return jsonify({
        "code": 0,
        "message": "success"
    })
# %%
@app.route('/QRcode', methods=['POST'])
def QRcode():
    data = request.json
    if not data:
        return jsonify({"code": -1, "message": "无有效数据"}), 400
    message_id = data.get('messageId')
    qr_link = data.get('qrCode')
    redis_key = f"creating_group:{message_id}"
    task_data_str = redis_client.get(redis_key)
    if task_data_str:
        redis_client.delete(redis_key)
        task_info = json.loads(task_data_str)
        original_group = task_info.get('original_group')
        new_group_name = task_info.get('new_group_name')
        encoded_link = urllib.parse.quote(qr_link)
        qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={encoded_link}"
        file_name = f"{new_group_name}_qrcode.png"
        extra_text = f"新群聊【{new_group_name}】创建成功！\n请扫码上方二维码加入"
        send_image(
            target_name=original_group,
            image_url=qr_image_url,
            file_name=file_name,
            extra_text=extra_text
        )
        return jsonify({"code": 0, "status": "success", "message": "二维码已成功回传给原群聊"})
    else:
        return jsonify({"code": -1, "status": "ignored", "message": "未知的 messageId 或任务已过期"})
if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    app.run(host='0.0.0.0', port=port, debug=False)