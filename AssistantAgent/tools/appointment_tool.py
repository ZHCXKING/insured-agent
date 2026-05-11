# %%
import os
import requests
from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field
from langchain.tools import tool
# %%
class CreateAppointmentInput(BaseModel):
    sales_id: str = Field(..., description="业务代表用户ID", min_length=1)
    policyholder_ids: List[str] = Field(..., description="投保人客户ID列表", min_length=1)
    insured_ids: List[str] = Field(..., description="受保人客户ID列表", min_length=1)
    policy_ids: List[str] = Field(..., description="关联保单ID列表", min_length=1)
    type: Literal[0, 1, 2, 3] = Field(default=3, description="预约类型，0=个人预约，1=独立预约，2=文件协助，3=全程协助")
    time: str = Field(
        default="",
        description="预约时间，格式 YYYY-MM-DD HH:mm（如 2026-05-08 14:30）",
        pattern=r"^$|^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$",
    )
    channel_id: str = Field(default="", description="转介人用户ID")
    signing_clerk_id: str = Field(default="", description="签单文员ID")
    signing_room_id: str = Field(default="", description="签单房间ID")
    reject_reason: str = Field(default="", description="拒绝原因")
    remark: str = Field(default="", description="备注")
# %%
class UpdateAppointmentInput(CreateAppointmentInput):
    appointment_id: str = Field(..., description="预约ID（必填）", min_length=1)
    sales_id: str = Field(default="", description="业务代表用户ID")
    policyholder_ids: List[str] = Field(default_factory=list, description="投保人客户ID列表")
    insured_ids: List[str] = Field(default_factory=list, description="受保人客户ID列表")
    policy_ids: List[str] = Field(default_factory=list, description="关联保单ID列表")
# %%
@tool(args_schema=CreateAppointmentInput)
def create_appointment(**kwargs) -> str:
    """
    在指定机构下创建预约。必填：业务代表ID、投保人ID列表、受保人ID列表、关联保单ID列表，预约时间。
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    url = f"{base_url}/open/organizations/{org_code}/appointments"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    time_str = kwargs.pop("time", "")
    payload = {"status": 1, "process": 0}
    payload.update({k: v for k, v in kwargs.items() if v})
    if time_str:
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        payload["time"] = int(dt.timestamp())
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    if response.status_code != 200:
        return f"错误：请求失败，HTTP {response.status_code}，响应：{response.text}"
    data = response.json()
    _status_map = {0: "草稿", 1: "审核中", 2: "预约中", 3: "确认预约", 4: "签单完成", 5: "取消投保", 6: "拒绝申请"}
    _process_map = {0: "基础信息", 1: "客户信息", 2: "保单信息"}
    _type_map = {0: "个人预约", 1: "独立预约", 2: "文件协助", 3: "全程协助"}
    info_lines = [
        f"预约ID: {data.get('id')}",
        f"预约时间: {data.get('time', 0)}",
        f"状态: {_status_map.get(data.get('status', 0), '未知')}",
        f"流程节点: {_process_map.get(data.get('process', 0), '未知')}",
        f"预约类型: {_type_map.get(data.get('type', 0), '未知')}",
        f"业务代表ID: {data.get('sales_id', '')}",
        f"转介人ID: {data.get('channel_id', '')}",
        f"签单文员ID: {data.get('signing_clerk_id', '')}",
        f"签单房间ID: {data.get('signing_room_id', '')}",
        f"投保人ID: {data.get('policyholder_ids', [])}",
        f"受保人ID: {data.get('insured_ids', [])}",
        f"关联保单ID: {data.get('policy_ids', [])}",
        f"备注: {data.get('remark', '')}",
        f"创建时间: {data.get('created_at', '')}",
    ]
    return "预约创建成功：\n" + "\n".join(info_lines)
# %%
@tool(args_schema=UpdateAppointmentInput)
def update_appointment(**kwargs) -> str:
    """
    更新指定机构下已有预约的信息。只需传入需要修改的字段，未传字段保持原值。appointment_id 为必填。
    """
    appointment_id = kwargs.pop("appointment_id")
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    url = f"{base_url}/open/organizations/{org_code}/appointments/{appointment_id}"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    time_str = kwargs.pop("time", "")
    payload = {}
    payload.update({k: v for k, v in kwargs.items() if v})
    if time_str:
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        payload["time"] = int(dt.timestamp())
    if not payload:
        return "错误：未提供任何需要更新的字段"
    response = requests.patch(url, json=payload, headers=headers, timeout=15)
    if response.status_code != 200:
        return f"错误：请求失败，HTTP {response.status_code}，响应：{response.text}"
    data = response.json()
    _status_map = {0: "草稿", 1: "审核中", 2: "预约中", 3: "确认预约", 4: "签单完成", 5: "取消投保", 6: "拒绝申请"}
    _process_map = {0: "基础信息", 1: "客户信息", 2: "保单信息"}
    _type_map = {0: "个人预约", 1: "独立预约", 2: "文件协助", 3: "全程协助"}
    info_lines = [
        f"预约ID: {data.get('id')}",
        f"预约时间: {data.get('time', 0)}",
        f"状态: {_status_map.get(data.get('status', 0), '未知')}",
        f"流程节点: {_process_map.get(data.get('process', 0), '未知')}",
        f"预约类型: {_type_map.get(data.get('type', 0), '未知')}",
        f"业务代表ID: {data.get('sales_id', '')}",
        f"转介人ID: {data.get('channel_id', '')}",
        f"签单文员ID: {data.get('signing_clerk_id', '')}",
        f"签单房间ID: {data.get('signing_room_id', '')}",
        f"投保人ID: {data.get('policyholder_ids', [])}",
        f"受保人ID: {data.get('insured_ids', [])}",
        f"关联保单ID: {data.get('policy_ids', [])}",
        f"备注: {data.get('remark', '')}",
        f"更新时间: {data.get('updated_at', '')}",
    ]
    return "预约更新成功：\n" + "\n".join(info_lines)