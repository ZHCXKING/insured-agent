import os
import requests
import logging
from dotenv import load_dotenv
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestWorkTool")
def test_send_message():
    load_dotenv()

    # 1. 检查环境变量
    robot_id = os.getenv("IFA_ROBOT_ID")
    if not robot_id:
        logger.error("错误: 未在 .env 文件中找到 WORKTOOL_ROBOT_ID")
        return

    # 2. 准备测试数据
    url = "https://api.worktool.ymdyes.cn/wework/sendRawMessage"
    params = {"robotId": robot_id}

    # 测试消息：发送给你自己的群名
    test_group_name = "ZHCX"  # 确保这个群名在你的企业微信里是真实存在的
    test_content = "这是一条来自 Python 脚本的自动测试消息。"

    message_item = {
        "type": 203,
        "titleList": [test_group_name],
        "receivedContent": test_content
    }
    payload = {
        "socketType": 2,
        "list": [message_item]
    }
    headers = {"Content-Type": "application/json"}

    logger.info(f"正在发送请求至 RobotID: {robot_id} ...")

    try:
        # 3. 执行请求
        response = requests.post(url, params=params, json=payload, headers=headers, timeout=15)

        # 4. 打印原始响应信息（关键排错步骤）
        print("-" * 30)
        print(f"HTTP 状态码: {response.status_code}")
        print(f"响应内容 (Raw Text): '{response.text}'")
        print("-" * 30)

        # 5. 尝试解析 JSON
        if not response.text.strip():
            logger.error("失败: 接口返回内容为空，可能服务器未响应或路径错误。")
            return

        try:
            response_data = response.json()
        except ValueError:
            logger.error("失败: 接口返回的不是有效的 JSON 格式。")
            return

        # 6. 业务逻辑判断
        if response.status_code == 200 and response_data.get("code") == 0:
            logger.info("🎉 测试成功！消息已成功提交至 WorkTool 队列。")
        else:
            logger.warning(f"❌ 业务逻辑失败: {response_data}")

    except requests.exceptions.Timeout:
        logger.error("失败: 请求超时，请检查网络或 API 地址。")
    except requests.exceptions.RequestException as e:
        logger.error(f"失败: 发生网络异常: {e}")
if __name__ == "__main__":
    test_send_message()