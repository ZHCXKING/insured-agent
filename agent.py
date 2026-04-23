# %%
import os
import logging
from dataclasses import dataclass
from deepagents import create_deep_agent, FilesystemPermission
from deepagents.backends import CompositeBackend, StateBackend
from deepagents.backends.filesystem import FilesystemBackend
from langgraph.checkpoint.redis import RedisSaver
from langchain.chat_models import init_chat_model
# %%
logger = logging.getLogger("IFA Assistant")
# %%
@dataclass
class GroupChatContext:
    group_name: str
    sender_name: str
# %%
class AssistantAgent:
    def __init__(self):
        self.app_name = "Assistant"
        self._setup_directories()
        self._setup_checkpointer()
        self._setup_backend()
        self._setup_model()
        self._create_agent()
    # %%
    def _setup_directories(self):
        """准备本地持久化目录"""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.memories_dir = os.path.join(self.base_dir, "memories")
        self.skills_dir = os.path.join(self.base_dir, "skills")
        os.makedirs(self.memories_dir, exist_ok=True)
        os.makedirs(self.skills_dir, exist_ok=True)
    # %%
    def _setup_checkpointer(self):
        """配置 Redis 作为短期记忆(线程状态)的存储"""
        redis_url = os.getenv("REDIS_URL")
        self.checkpointer = RedisSaver(
            redis_url=redis_url,
            checkpoint_write_prefix=f"checkpoints:{self.app_name}",
        )
        self.checkpointer.setup()
    # %%
    def _setup_backend(self):
        """配置文件系统后端，映射虚拟路径到物理路径"""
        self.backend = CompositeBackend(
            default=StateBackend(),
            routes={
                "/memories/": FilesystemBackend(root_dir=self.memories_dir, virtual_mode=True),
                "/skills/": FilesystemBackend(root_dir=self.skills_dir, virtual_mode=True),
            }
        )
    # %%
    def _setup_model(self):
        """初始化大语言模型"""
        self.model = init_chat_model(
            model=os.getenv("API_MODEL"),
            model_provider="openai",
            base_url=os.getenv("API_BASE"),
            api_key=os.getenv("API_KEY"),
            max_retries=3,
            timeout=120
        )
    # %%
    def _create_agent(self):
        """组合上述组件，创建核心 Deep Agent"""
        system_prompt = "你是 IFA Assistant，一个专业的许可助手。"
        self.agent = create_deep_agent(
            model=self.model,
            backend=self.backend,
            checkpointer=self.checkpointer,
            context_schema=GroupChatContext,
            skills=["/skills/"],
            memory=["/memories/AGENTS.md"],
            system_prompt=system_prompt,
            permissions = [
                FilesystemPermission(
                    operations=["write"],
                    paths=["/**"],
                    mode="deny"
                ),
            ]
        )
    # %%
    def process_message(self, text: str, sender: str, group: str) -> str:
        """处理单条数据"""
        context = GroupChatContext(group_name=group, sender_name=sender)
        config = {"configurable": {"thread_id": f"{self.app_name}_{group}"}}
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": text}]},
            context=context,
            config=config
        )
        reply_content = result["messages"][-1].content
        return reply_content
    # %%
    def process_messages(self, text: str, sender: str, group: str) -> str:
        context = GroupChatContext(group_name=group, sender_name=sender)
        config = {"configurable": {"thread_id": f"{self.app_name}_{group}"}}
        enhanced_prompt = (
            f"以下是缓存的近期聊天记录：\n"
            f"{text}\n"
            f"请根据上述记录，重点解答（{sender}）最后提出的问题或请求。"
        )
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": enhanced_prompt}]},
            context=context,
            config=config
        )
        reply_content = result["messages"][-1].content
        return reply_content