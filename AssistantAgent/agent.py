# %%
import os
import logging
import atexit
import json
from dataclasses import dataclass
from deepagents import create_deep_agent, FilesystemPermission
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from deepagents.backends.filesystem import FilesystemBackend
from langgraph.checkpoint.redis import RedisSaver
from langgraph.store.postgres import PostgresStore
from langchain.chat_models import init_chat_model
from psycopg_pool import ConnectionPool
from utils import get_image_type
from AssistantAgent.tools import send_message, schedule_message_delayed, get_current_time, get_appointment_information
from AssistantAgent.subagents import appointment_subagent
# %%
logger = logging.getLogger("Assistant")
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
        self._setup_store()
        self._setup_backend()
        self._setup_model()
        self._setup_prompt()
        self._create_agent()
    # %%
    def _setup_directories(self):
        """准备本地持久化目录"""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.skills_dir = os.path.join(self.base_dir, "skills")
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
    def _setup_store(self):
        """配置 PostgreSQL 作为长期记忆的存储"""
        pg_url = os.getenv("POSTGRES_URL")
        pool = ConnectionPool(pg_url, kwargs={"autocommit": True},)
        atexit.register(pool.close)
        self.store = PostgresStore(pool)
        self.store.setup()
    # %%
    def _setup_backend(self):
        """配置文件系统后端，映射虚拟路径到物理路径"""
        self.backend = CompositeBackend(
            default=StateBackend(),
            routes={
                "/memories/": StoreBackend(namespace=lambda rt: ("Assistant", rt.context.group_name,),),
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
    def _setup_prompt(self):
        prompt_path = os.path.join(self.base_dir, "prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt = f.read()
    # %%
    def _create_agent(self):
        """组合上述组件，创建核心 Deep Agent"""
        system_prompt = self.prompt
        self.agent = create_deep_agent(
            model=self.model,
            backend=self.backend,
            store=self.store,
            checkpointer=self.checkpointer,
            context_schema=GroupChatContext,
            tools=[send_message, schedule_message_delayed, get_current_time, get_appointment_information],
            subagents=[appointment_subagent],
            skills=["/skills/"],
            system_prompt=system_prompt,
            permissions = [
                FilesystemPermission(operations=["write"],paths=["/skills/**"],mode="deny"),
            ]
        )
    # %%
    def process_message(self, text: str, sender: str, group: str) -> str:
        """处理单条数据"""
        context = GroupChatContext(group_name=group, sender_name=sender)
        config = {"configurable": {"thread_id": f"{self.app_name}_{group}"}, "recursion_limit": 15}
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": text}]},
            context=context,
            config=config
        )
        reply_content = result["messages"][-1].content
        return reply_content
    # %%
    def process_messages(self, text: str, sender: str, group: str) -> str:
        history_data = [json.loads(line) for line in text.splitlines()]
        combined_content = []
        history_text_lines = []
        for entry in history_data:
            history_text_lines.append(f"[{entry['sender']}]: {entry['spoken']}")
            if entry.get("picture"):
                mime_type, clean_b64 = get_image_type(entry["picture"])
                combined_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{clean_b64}"}
                })
        full_text = "\n".join(history_text_lines)
        prompt = (
            f"以下是缓存记录：\n{full_text}\n"
            f"请解答（{sender}）最后提出的问题或请求。"
        )
        combined_content.insert(0, {"type": "text", "text": prompt})
        messages = [{"role": "user", "content": combined_content}]
        context = GroupChatContext(group_name=group, sender_name=sender)
        config = {"configurable": {"thread_id": f"{self.app_name}_{group}"}, "recursion_limit": 15}
        result = self.agent.invoke(
            {"messages": messages},
            context=context,
            config=config
        )
        return result["messages"][-1].content