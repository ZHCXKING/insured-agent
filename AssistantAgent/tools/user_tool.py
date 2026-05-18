# %%
import os
import requests
from typing import Literal
from pydantic import BaseModel, Field
from langchain.tools import tool
# %%
class SearchUsersInput(BaseModel):
    search: str = Field(..., description="搜索关键字，后端自动在姓名/英文名/昵称/邮箱/手机号中匹配")
    role: Literal[
        "", "admin", "fin", "hr", "info", "biz",
        "proposal_it", "sales", "referrer", "partner",
        "signing_clerk", "signing_manager",
    ] = Field(
        default="",
        description="按角色精确过滤，可选值：admin=管理员, fin=财务, hr=人事, info=资料, biz=业管, proposal_it=自动计划书维护-IT, sales=业务代表, referrer=转介人, partner=合作方, signing_clerk=签单文员, signing_manager=签单管理",
    )
# %%
@tool(args_schema=SearchUsersInput)
def search_users(**kwargs) -> str:
    """
    通过关键字模糊搜索机构内的用户列表。传入一个关键字后，后端会在姓名、英文名、昵称、邮箱、手机号五个字段中同时进行OR模糊匹配，无需指定具体字段。
    例如传入"张"会同时匹配姓名含"张"的用户和手机号含"张"的用户。
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    url = f"{base_url}/open/organizations/{org_code}/users"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    params = {"page": 1, "page_size": 20}
    params.update({k: v for k, v in kwargs.items() if v})
    response = requests.get(url, params=params, headers=headers, timeout=15)
    if response.status_code != 200:
        return f"错误：请求失败，HTTP {response.status_code}，响应：{response.text}"
    data = response.json()
    users = data.get("Data_process", [])
    pagination = data.get("pagination", {})
    if not users:
        return "未搜索到匹配的用户。"
    _role_map = {
        "admin": "管理员", "fin": "财务", "hr": "人事", "info": "资料",
        "biz": "业管", "proposal_it": "自动计划书维护-IT", "sales": "业务代表",
        "referrer": "转介人", "partner": "合作方", "signing_clerk": "签单文员",
        "signing_manager": "签单管理",
    }
    _status_map = {1: "启用", -1: "封禁"}
    _channel_type_map = {"default": "未设置", "normal": "普通渠道", "ifa": "IFA渠道"}
    lines = []
    for u in users:
        user_lines = [
            f"  用户ID: {u.get('id')}",
            f"  姓名: {u.get('name', '')}",
            f"  英文名: {u.get('english_name', '')}",
            f"  角色: {_role_map.get(u.get('role', ''), u.get('role', ''))}",
            f"  状态: {_status_map.get(u.get('status', 0), '未知')}",
            f"  渠道类型: {_channel_type_map.get(u.get('channel_type', ''), u.get('channel_type', ''))}",
            f"  邮箱: {u.get('email', '')}",
            f"  电话: {u.get('phone', '')}",
        ]
        lines.append("\n".join(user_lines))
    total = pagination.get("total", len(users))
    header = f"共搜索到 {total} 条用户："
    return header + "\n" + "\n---\n".join(lines)
