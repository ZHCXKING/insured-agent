# %%
import os
from AssistantAgent.tools import (
    match_client,
    create_client,
    update_client,
    search_users,
    search_companies,
    search_products,
    create_policy,
    update_policy,
    create_appointment,
    update_appointment,
)
# %%
_prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "appointment_subagent_prompt.txt")
with open(_prompt_path, "r", encoding="utf-8") as f:
    _system_prompt = f.read()
# %%
appointment_subagent = {
    "name": "appointment_agent",
    "description": "处理客户、保单、预约等业务信息的创建和更新操作：匹配/创建/更新客户、搜索用户、搜索保险公司/产品、创建/更新保单、创建/更新预约。当用户需要新建或修改任何业务信息（客户、保单、预约等）时，委派给此子代理。",
    "system_prompt": _system_prompt,
    "tools": [
        match_client,
        create_client,
        update_client,
        search_users,
        search_companies,
        search_products,
        create_policy,
        update_policy,
        create_appointment,
        update_appointment,
    ],
}
