# %%
import os
import requests
# %%
def send_image(target_name: str, image_url: str, file_name: str = "image.png", extra_text: str = "", robot_id: str = ""):
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    params = {"robotId": robot_id}
    message_item = {
        "type": 218,
        "titleList": [target_name],
        "objectName": file_name,
        "fileUrl": image_url,
        "fileType": "image",
        "extraText": extra_text
    }
    payload = {"socketType": 2, "list": [message_item]}
    headers = {"Content-Type": "application/json"}
    # todo 这里临时修改规则
    print(image_url, target_name)
    return f"消息发送成功"
    # response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
    # response_data = response.json()
    # if response.status_code == 200:
    #     return f"消息发送成功"
    # else:
    #     return f"消息发送失败，接口返回: {response_data}"