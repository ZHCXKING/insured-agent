import os
import base64
from dotenv import load_dotenv
import requests

load_dotenv()

API_BASE = "http://localhost:5000"

AGENTS = {
    "assistant": "/assistant/message",
    "greatgroup": "/greatgroup/message",
}


def main():
    print("Agent 交互测试")
    print("输入 /exit 退出\n")
    print("命令：")
    print("  /agent <名称>  - 切换Agent (assistant / greatgroup)")
    print("  /img <图片路径>  - 发送图片")
    print("  /user <身份>    - 切换身份")
    print("  /group <群名>  - 切换群聊\n")

    agent_name = input(f"请选择Agent ({'/'.join(AGENTS.keys())}，默认 assistant): ").strip().lower() or "assistant"
    if agent_name not in AGENTS:
        print(f"未知Agent: {agent_name}，使用默认 assistant")
        agent_name = "assistant"

    group = input("请输入群聊名称（默认 TestGroup）: ").strip() or "TestGroup"
    sender = input("请输入你的身份（默认 Alice）: ").strip() or "Alice"

    print(f"\n当前Agent: [{agent_name}] 身份: [{sender}] @ 群聊 [{group}]")
    print("开始聊天吧！\n")

    while True:
        try:
            user_input = input(f"[{sender}@{agent_name}] > ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["/exit", "exit", "quit"]:
                print("已退出")
                break

            if user_input.startswith("/agent "):
                new_agent = user_input.replace("/agent ", "").strip().lower()
                if new_agent in AGENTS:
                    agent_name = new_agent
                    print(f"已切换Agent为: {agent_name}")
                else:
                    print(f"未知Agent: {new_agent}，可选: {'/'.join(AGENTS.keys())}")
                continue

            if user_input.startswith("/img "):
                image_path = user_input.replace("/img ", "").strip()
                if not os.path.exists(image_path):
                    print(f"文件不存在: {image_path}")
                    continue
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                payload = {
                    "spoken": "图片",
                    "receivedName": sender,
                    "groupName": group,
                    "atMe": "true",
                    "fileBase64": image_data
                }
                response = requests.post(f"{API_BASE}{AGENTS[agent_name]}", json=payload, timeout=60)
                if response.status_code == 200:
                    print(f"\n图片已发送\n")
                else:
                    print(f"\n发送失败: {response.status_code}\n")
                continue

            if user_input.startswith("/user "):
                sender = user_input.replace("/user ", "").strip()
                print(f"已切换身份为: {sender}")
                continue

            if user_input.startswith("/group "):
                group = user_input.replace("/group ", "").strip()
                print(f"已切换群聊为: {group}")
                continue

            payload = {
                "spoken": user_input,
                "receivedName": sender,
                "groupName": group,
                "atMe": "true"
            }

            response = requests.post(f"{API_BASE}{AGENTS[agent_name]}", json=payload, timeout=60)
            if response.status_code == 200:
                print(f"\nAgent: 请求已发送\n")
            else:
                print(f"\n请求失败: {response.status_code}\n")

        except KeyboardInterrupt:
            print("\n手动中断退出")
            break
        except Exception as e:
            print(f"\n出错: {e}\n")


if __name__ == "__main__":
    main()
