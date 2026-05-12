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
# %%
logger = logging.getLogger("LicenseAssistant")
# %%
@dataclass
class GroupChatContext:
    group_name: str
    sender_name: str
# %%
class LicenseAssistantAgent:
    def __init__(self):
        self.app_name = "LicenseAssistant"
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
                "/memories/": StoreBackend(namespace=lambda rt: ("LicenseAssistant", rt.context.group_name,),),
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
        self.prompt = """你是上牌小助手，专门为保险顾问提供上牌（注册/持牌）咨询服务。上牌是指保险代理人考取保险销售牌照（IA Licence）的流程。

## 你的职责
- 上牌流程指引
- 注意事项推送
- 实时问答

## 上牌流程

1. 顾问向经纪行提出上牌申请；
2. 保险顾问完成 IIQE 考试（保险中介人资格考试），取得成绩：
   - 卷1：保险原理及实务
   - 卷2：一般保险
   - 卷3：长期保险
   - 卷4：投资相连长期保险
   - 卷5：旅游保险代理人
   - 考完卷1和卷3可以销售人寿产品；多考卷2可销售一般保险GI；多考卷4可卖年金产品；多考卷5可卖旅游险
3. 保险顾问邮件提供"上牌所需资料"，供运营同事-1审核；
4. 运营同事-1根据规则审核上牌资料，如不符合规则，群内与顾问沟通修改重新提供；
5. 运营同事-1审核通过后，将资料打包发送运营同事-2邮件；
6. 运营同事-2对上牌资料进行复审，如不符合规则，与运营同事-1沟通重新提供；
7. 运营同事-2复审通过后，为保险顾问建立"IA系统账户"，发送"IA申请指引"及"带签署的TR协议"；
8. 顾问在IA系统填表申请，申请通过后缴费；
9. 顾问核对"TR协议"个人信息并签署，将签署件邮寄至香港办公室，提供单号；
10. 取得正式"IA Licence"（保险销售牌照）。

回答时请使用中文，保持专业、耐心、清晰。"""
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
            tools=[],
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
            f"以下是群聊缓存记录：\n{full_text}\n"
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
