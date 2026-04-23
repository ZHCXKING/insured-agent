from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from agent import IFAAssistantAgent # 替换为你的文件名


def main():
    print("🚀 IFA Assistant 交互测试")
    print("输入 /exit 退出\n")

    # 初始化 Agent
    agent = IFAAssistantAgent()

    # 初始化上下文（可随时修改）
    group = input("请输入群聊名称（默认 TestGroup）: ").strip() or "TestGroup"
    sender = input("请输入你的身份（默认 Alice）: ").strip() or "Alice"

    print(f"\n✅ 当前身份: [{sender}] @ 群聊 [{group}]")
    print("💬 开始聊天吧！\n")

    while True:
        try:
            user_input = input(f"[{sender}] > ").strip()

            if not user_input:
                continue

            # 退出
            if user_input.lower() in ["/exit", "exit", "quit"]:
                print("👋 已退出")
                break

            # 切换身份
            if user_input.startswith("/user "):
                sender = user_input.replace("/user ", "").strip()
                print(f"🔄 已切换身份为: {sender}")
                continue

            # 切换群聊
            if user_input.startswith("/group "):
                group = user_input.replace("/group ", "").strip()
                print(f"🔄 已切换群聊为: {group}")
                continue

            # 调用 Agent
            response = agent.process_message(
                text=user_input,
                sender=sender,
                group=group
            )

            print(f"\n🤖 Agent: {response}\n")

        except KeyboardInterrupt:
            print("\n👋 手动中断退出")
            break
        except Exception as e:
            print(f"\n❌ 出错: {e}\n")


if __name__ == "__main__":
    main()