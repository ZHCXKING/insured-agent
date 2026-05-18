# %%
import os
import requests
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, model_validator
from langchain.tools import tool
# %%
class SearchCompaniesInput(BaseModel):
    name: str = Field(..., description="保险公司名称（模糊匹配中文名/英文名）")
# %%
class SearchProductsInput(BaseModel):
    name: str = Field(..., description="产品名称（模糊匹配中文名/英文名）")
    company_id: str = Field(default="", description="保险公司ID（精确过滤，可通过 search_companies 获取）")
# %%
class BeneficiaryInput(BaseModel):
    name: str = Field(default="", description="受益人中文姓名")
    english_name: str = Field(default="", description="受益人拼音或英文名")
    id_number: str = Field(default="", description="受益人证件号")
    relationship: str = Field(default="", description="与受保人关系")
    proportion: Optional[float] = Field(default=None, description="分配比例0~1，按比例模式时必填", ge=0, le=1)
    client_id: str = Field(default="", description="关联客户ID（如该受益人已存在于客户库）")
# %%
class CreatePolicyInput(BaseModel):
    product_company_id: str = Field(..., description="保险公司ID（通过 search_companies 获取）")
    product_sku_id: str = Field(..., description="产品SKU ID（通过 search_products 获取产品详情后取得）")
    premium: float = Field(..., description="当期保费", ge=0)
    payment_period: int = Field(..., description="供款年期", ge=1)
    prepaid_premium: bool = Field(..., description="是否预缴保费")
    no: str = Field(default="", description="保单号")
    applicant_id: str = Field(..., description="投保人客户ID")
    insurant_id: str = Field(..., description="受保人客户ID")
    insured_policyholder_relation: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8] = Field(
        default=0,
        description="受保人与投保人关系，0=未设置，1=本人，2=父母，3=子女，4=配偶，5=兄弟姐妹，6=祖父母，7=雇员，8=其他",
    )
    signing_clerk_id: str = Field(default="", description="签单文员用户ID")
    channel_id: str = Field(default="", description="转介人用户ID")
    sales_id: str = Field(..., description="业务代表用户ID")
    applied_at: str = Field(
        default="",
        description="签单日，格式 YYYY-MM-DD",
        pattern=r"^$|^\d{4}-\d{2}-\d{2}$",
    )
    premium_time: str = Field(
        default="",
        description="当前应缴日，格式 YYYY-MM-DD",
        pattern=r"^$|^\d{4}-\d{2}-\d{2}$",
    )
    currency: str = Field(default="HKD", description="币种，如 HKD/USD/CNY")
    renewal_plan: Literal["", "Single", "Annual", "HalfYearly", "Quarterly"] = Field(
        default="",
        description="续保计划，Single=一次性，Annual=年缴，HalfYearly=半年缴，Quarterly=季缴",
    )
    sum_assured: float = Field(default=0, description="保额", ge=0)
    beneficiary_distribution_mode: Literal[1, 2] = Field(
        default=1,
        description="受益人分配模式，1=按比例，2=按顺位",
    )
    beneficiaries: List[BeneficiaryInput] = Field(default_factory=list, description="受益人列表")
    remark: str = Field(default="", description="备注")
# %%
class UpdatePolicyInput(CreatePolicyInput):
    policy_id: str = Field(..., description="保单ID（必填）")
    product_company_id: str = Field(default="", description="保险公司ID")
    product_sku_id: str = Field(default="", description="产品SKU ID")
    applicant_id: str = Field(default="", description="投保人客户ID")
    premium: Optional[float] = Field(default=None, description="当期保费", ge=0)
    payment_period: Optional[int] = Field(default=None, description="供款年期", ge=1)
    prepaid_premium: Optional[bool] = Field(default=None, description="是否预缴保费")
# %%
@tool(args_schema=SearchCompaniesInput)
def search_companies(**kwargs) -> str:
    """
    按名称模糊搜索机构下的保险公司，返回公司ID、名称、缩写等信息。用于创建保单前查找 product_company_id。
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    url = f"{base_url}/open/organizations/{org_code}/companies"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Accept": "application/json",
    }
    params = {"page": 1, "page_size": 20}
    params.update({k: v for k, v in kwargs.items() if v})
    response = requests.get(url, params=params, headers=headers, timeout=15)
    if response.status_code != 200:
        return f"错误：请求失败，HTTP {response.status_code}，响应：{response.text}"
    data = response.json()
    companies = data.get("data", [])
    if not companies:
        return "未搜索到匹配的保险公司。"
    lines = []
    for c in companies:
        company_lines = [
            f"  公司ID: {c.get('id')}",
            f"  中文名: {c.get('name', '')}",
            f"  英文名: {c.get('english_name', '')}",
            f"  缩写: {c.get('abbreviation', '')}",
            f"  计划书标识: {c.get('proposal_identifier', '')}",
        ]
        lines.append("\n".join(company_lines))
    total = data.get("pagination", {}).get("total", len(companies))
    header = f"共搜索到 {total} 家保险公司："
    return header + "\n" + "\n---\n".join(lines)
# %%
@tool(args_schema=SearchProductsInput)
def search_products(**kwargs) -> str:
    """
    按产品名称和保险公司ID搜索产品，返回产品ID、名称、SKU列表等信息。用于创建保单前查找 product_sku_id。
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    url = f"{base_url}/open/organizations/{org_code}/products"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Accept": "application/json",
    }
    params = {"page": 1, "page_size": 20}
    params.update({k: v for k, v in kwargs.items() if v})
    response = requests.get(url, params=params, headers=headers, timeout=15)
    if response.status_code != 200:
        return f"错误：请求失败，HTTP {response.status_code}，响应：{response.text}"
    data = response.json()
    products = data.get("data", [])
    if not products:
        return "未搜索到匹配的产品。"
    lines = []
    for p in products:
        company = p.get("company") or {}
        product_lines = [
            f"  产品SKU ID: {p.get('id')}",
            f"  中文名: {p.get('name', '')}",
            f"  英文名: {p.get('english_name', '')}",
            f"  类型: {p.get('type', '')}",
            f"  续保计划: {p.get('renewal_plan', '')}",
            f"  状态: {p.get('status', '')}",
            f"  保险公司: {company.get('name', '')} (ID: {p.get('company_id', '')})",
        ]
        lines.append("\n".join(product_lines))
    total = data.get("pagination", {}).get("total", len(products))
    header = f"共搜索到 {total} 个产品："
    return header + "\n" + "\n---\n".join(lines)
# %%
@tool(args_schema=CreatePolicyInput)
def create_policy(**kwargs) -> str:
    """
    在指定机构下创建保单。必填：保险公司ID、产品SKU ID、保费、供款年期、是否预缴、投保人ID、受保人ID、业务代表ID。
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    url = f"{base_url}/open/organizations/{org_code}/policies"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    beneficiaries = kwargs.pop("beneficiaries", [])
    applied_at = kwargs.pop("applied_at", "")
    premium_time = kwargs.pop("premium_time", "")
    formatted_beneficiaries = []
    for b in beneficiaries:
        fb = {}
        if b.name:
            fb["name"] = b.name
        if b.relationship:
            fb["relationship"] = b.relationship
        if b.english_name:
            fb["english_name"] = b.english_name
        if b.id_number:
            fb["id_number"] = b.id_number
        if b.proportion is not None:
            fb["proportion"] = b.proportion
        if b.client_id:
            fb["client_id"] = b.client_id
        if fb:
            formatted_beneficiaries.append(fb)
    payload = {k: v for k, v in kwargs.items() if v}
    if formatted_beneficiaries:
        payload["beneficiaries"] = formatted_beneficiaries
    if applied_at:
        dt = datetime.strptime(applied_at, "%Y-%m-%d")
        payload["applied_at"] = int(dt.timestamp())
    if premium_time:
        dt = datetime.strptime(premium_time, "%Y-%m-%d")
        payload["premium_time"] = int(dt.timestamp())
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    if response.status_code != 200:
        return f"错误：请求失败，HTTP {response.status_code}，响应：{response.text}"
    data = response.json()
    _status_map = {
        1: "等待进入保司系统", 2: "待查询进度", 3: "欠费", 4: "待处理中",
        5: "再次出现待处理", 6: "已递交待处理", 7: "需要体检或报告", 8: "等待生效",
        9: "已生效", 10: "有不保事项/加费", 11: "已拒保/被搁置", 12: "保司自动取消",
        13: "客人要求取消", 14: "冷静期退保", 15: "保单失效",
    }
    _type_map = {0: "默认", 1: "正式保单", 2: "托管保单"}
    info_lines = [
        f"保单ID: {data.get('id')}",
        f"保单号: {data.get('no', '')}",
        f"状态: {_status_map.get(data.get('status', 0), '未知')}",
        f"类型: {_type_map.get(data.get('type', 0), '未知')}",
        f"投保人ID: {data.get('applicant_id', '')}",
        f"受保人ID: {data.get('insurant_id', '')}",
        f"保费: {data.get('premium', '')} {data.get('currency', '')}",
        f"保额: {data.get('sum_assured', '')}",
        f"续保计划: {data.get('renewal_plan', '')}",
        f"供款年期: {data.get('payment_period', '')}",
        f"是否预缴: {data.get('prepaid_premium', False)}",
        f"签单文员ID: {data.get('signing_clerk_id', '')}",
        f"转介人ID: {data.get('channel_id', '')}",
        f"业务代表ID: {data.get('sales_id', '')}",
        f"受益人: {data.get('beneficiaries', [])}",
        f"创建时间: {data.get('created_at', '')}",
    ]
    return "保单创建成功：\n" + "\n".join(info_lines)
# %%
@tool(args_schema=UpdatePolicyInput)
def update_policy(**kwargs) -> str:
    """
    更新指定机构下已有保单的信息。只需传入需要修改的字段，未传字段保持原值。policy_id 为必填。
    """
    policy_id = kwargs.pop("policy_id")
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    url = f"{base_url}/open/organizations/{org_code}/policies/{policy_id}"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    beneficiaries = kwargs.pop("beneficiaries", [])
    applied_at = kwargs.pop("applied_at", "")
    premium_time = kwargs.pop("premium_time", "")
    formatted_beneficiaries = []
    for b in beneficiaries:
        fb = {}
        if b.name:
            fb["name"] = b.name
        if b.relationship:
            fb["relationship"] = b.relationship
        if b.english_name:
            fb["english_name"] = b.english_name
        if b.id_number:
            fb["id_number"] = b.id_number
        if b.proportion is not None:
            fb["proportion"] = b.proportion
        if b.client_id:
            fb["client_id"] = b.client_id
        if fb:
            formatted_beneficiaries.append(fb)
    payload = {k: v for k, v in kwargs.items() if v}
    if formatted_beneficiaries:
        payload["beneficiaries"] = formatted_beneficiaries
    if applied_at:
        dt = datetime.strptime(applied_at, "%Y-%m-%d")
        payload["applied_at"] = int(dt.timestamp())
    if premium_time:
        dt = datetime.strptime(premium_time, "%Y-%m-%d")
        payload["premium_time"] = int(dt.timestamp())
    if not payload:
        return "错误：未提供任何需要更新的字段"
    response = requests.patch(url, json=payload, headers=headers, timeout=15)
    if response.status_code != 200:
        return f"错误：请求失败，HTTP {response.status_code}，响应：{response.text}"
    data = response.json()
    _status_map = {
        1: "等待进入保司系统", 2: "待查询进度", 3: "欠费", 4: "待处理中",
        5: "再次出现待处理", 6: "已递交待处理", 7: "需要体检或报告", 8: "等待生效",
        9: "已生效", 10: "有不保事项/加费", 11: "已拒保/被搁置", 12: "保司自动取消",
        13: "客人要求取消", 14: "冷静期退保", 15: "保单失效",
    }
    _type_map = {0: "默认", 1: "正式保单", 2: "托管保单"}
    info_lines = [
        f"保单ID: {data.get('id')}",
        f"保单号: {data.get('no', '')}",
        f"状态: {_status_map.get(data.get('status', 0), '未知')}",
        f"类型: {_type_map.get(data.get('type', 0), '未知')}",
        f"投保人ID: {data.get('applicant_id', '')}",
        f"受保人ID: {data.get('insurant_id', '')}",
        f"保费: {data.get('premium', '')} {data.get('currency', '')}",
        f"保额: {data.get('sum_assured', '')}",
        f"续保计划: {data.get('renewal_plan', '')}",
        f"供款年期: {data.get('payment_period', '')}",
        f"是否预缴: {data.get('prepaid_premium', False)}",
        f"签单文员ID: {data.get('signing_clerk_id', '')}",
        f"转介人ID: {data.get('channel_id', '')}",
        f"业务代表ID: {data.get('sales_id', '')}",
        f"受益人: {data.get('beneficiaries', [])}",
        f"更新时间: {data.get('updated_at', '')}",
    ]
    return "保单更新成功：\n" + "\n".join(info_lines)