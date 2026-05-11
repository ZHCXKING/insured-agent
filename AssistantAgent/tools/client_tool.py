# %%
import os
import requests
from typing import Literal, List
from pydantic import BaseModel, Field, model_validator
from langchain.tools import tool
# %%
class MatchClientInput(BaseModel):
    id_number: str = Field(default="", description="内地身份证号")
    hk_id_number: str = Field(default="", description="香港身份证号")
    @model_validator(mode='after')
    def check_at_least_one_id(self) -> 'MatchClientInput':
        if not self.id_number and not self.hk_id_number:
            raise ValueError("参数验证失败：'内地身份证号和香港身份证号不能同时为空，至少必须提供其中一个！")
        return self
# %%
class ClientBaseInput(BaseModel):
    # 基本信息
    name: str = Field(default="", description="姓名")
    english_name: str = Field(default="", description="英文姓名")
    type: Literal[0, 1, 2] = Field(default=0, description="客户类型，0=未设置，1=个人，2=企业")
    gender: Literal[0, 1, 2] = Field(default=0, description="性别，0=未设置，1=男，2=女")
    id_number: str = Field(default="", description="内地身份证号")
    hk_id_number: str = Field(default="", description="香港身份证号")
    hk_macau_pass_id: str = Field(default="", description="港澳通行证号")
    phone: str = Field(default="", description="主要电话")
    home_phone: str = Field(default="", description="住宅电话")
    office_phone: str = Field(default="", description="办公电话")
    email: str = Field(default="", description="邮箱")
    country: str = Field(default="", description="国家/地区")
    nationality: str = Field(default="", description="国籍")
    birth_country: str = Field(default="", description="出生国家")
    tax_residency_country: str = Field(default="", description="税务居民国家")
    residential_address: str = Field(default="", description="居住地址")
    address: str = Field(default="", description="通讯地址")
    birthdate: str = Field(
        default="",
        description="出生日期，格式 YYYY-MM-DD",
        pattern=r"^$|^\d{4}-\d{2}-\d{2}$",
    )
    height: int = Field(default=0, description="身高", ge=0)
    height_unit: str = Field(default="cm", description="身高单位")
    weight: int = Field(default=0, description="体重", ge=0)
    weight_unit: str = Field(default="kg", description="体重单位")
    smoke: bool = Field(default=False, description="是否吸烟")
    # 教育与职业
    education: Literal["", "primary_or_below", "secondary", "post_secondary", "university_or_above"] = Field(
        default="",
        description="教育程度",
    )
    marital_status: Literal["", "single", "married", "divorced", "widowed"] = Field(
        default="",
        description="婚姻状况",
    )
    employment_status: str = Field(default="", description="就业情况")
    company: str = Field(default="", description="公司名称")
    occupation: str = Field(default="", description="职业类别")
    job_title: str = Field(default="", description="具体职位")
    industry_category: str = Field(default="", description="行业类别")
    company_address: str = Field(default="", description="公司地址")
    # 家庭及规划
    dependents_count: int = Field(default=0, description="供养人数", ge=0)
    expected_retirement_age: int = Field(default=0, description="预期退休年龄", ge=0)
    is_retired: bool = Field(default=False, description="是否已退休")
    # 现有保障情况
    life_insurance_coverage: int = Field(default=0, description="人寿保险保额", ge=0)
    critical_illness_coverage: int = Field(default=0, description="重疾保险保额", ge=0)
    accident_insurance_coverage: int = Field(default=0, description="意外保险保额", ge=0)
    medical_insurance_type: str = Field(default="", description="医疗保险类型")
    medical_insurance_coverage: int = Field(default=0, description="医疗保险金额", ge=0)
    other_coverage_description: str = Field(default="", description="其他保障说明")
    other_coverage_amount: int = Field(default=0, description="其他保障金额", ge=0)
    # 财务收支
    salary_income: int = Field(default=0, description="薪资收入", ge=0)
    rental_income: int = Field(default=0, description="租金收入", ge=0)
    other_income: int = Field(default=0, description="其他收入", ge=0)
    personal_family_expense: int = Field(default=0, description="个人及家庭开支", ge=0)
    mortgage_loan_repayment: int = Field(default=0, description="按揭或贷款还款", ge=0)
    insurance_premium_expense: int = Field(default=0, description="保费支出", ge=0)
    other_expense: int = Field(default=0, description="其他支出", ge=0)
    # 资产负债
    liquid_funds: int = Field(default=0, description="流动资金", ge=0)
    short_term_liabilities_total: int = Field(default=0, description="短期负债总额", ge=0)
    non_liquid_assets_total: int = Field(default=0, description="非流动资产总额", ge=0)
    mortgage_liabilities: int = Field(default=0, description="按揭贷款", ge=0)
    personal_loan_liabilities: int = Field(default=0, description="个人贷款", ge=0)
    other_liabilities: int = Field(default=0, description="其他负债", ge=0)
    total_liabilities: int = Field(default=0, description="总负债额", ge=0)
    # 补充字段
    init_payment_method: List[str] = Field(default_factory=list, description="首期供款付款方式")
    channel_id: str = Field(default="", description="归属渠道用户ID")
    remark: str = Field(default="", description="备注")
# %%
class CreateClientInput(ClientBaseInput):
    name: str = Field(..., description="姓名")
    @model_validator(mode='after')
    def check_required_fields(self) -> 'CreateClientInput':
        if not self.id_number and not self.hk_id_number:
            raise ValueError("创建客户必须提供内地身份证号(id_number)或香港身份证号(hk_id_number)，至少提供一个")
        return self
# %%
class UpdateClientInput(ClientBaseInput):
    client_id: str = Field(..., description="客户ID")
# %%
@tool(args_schema=MatchClientInput)
def match_client(id_number: str = "", hk_id_number: str = "") -> str:
    """
    通过身份证号或香港身份证号匹配客户。至少提供 id_number 或 hk_id_number 其中之一。
    如果匹配到客户，返回客户信息（含客户ID）；未匹配到则返回提示需要创建客户。
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    url = f"{base_url}/open/organizations/{org_code}/clients/match"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    payload = {}
    if id_number:
        payload["id_number"] = id_number
    if hk_id_number:
        payload["hk_id_number"] = hk_id_number
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    if response.status_code != 200:
        return f"错误：请求失败，HTTP {response.status_code}，响应：{response.text}"
    data = response.json()
    if data.get("id") in ("0", "", None):
        return f"未匹配到客户。该机构下不存在身份证号为 {id_number or hk_id_number} 的客户，请先创建客户。"
    _client_type_map = {0: "未设置", 1: "个人", 2: "企业"}
    _gender_map = {0: "未设置", 1: "男", 2: "女"}
    info_lines = [
        f"客户ID: {data.get('id')}",
        f"姓名: {data.get('name', '')}",
        f"英文名: {data.get('english_name', '')}",
        f"客户类型: {_client_type_map.get(data.get('type', 0), '未知')}",
        f"性别: {_gender_map.get(data.get('gender', 0), '未知')}",
        f"电话: {data.get('phone', '')}",
        f"邮箱: {data.get('email', '')}",
        f"渠道ID: {data.get('channel_id', '')}",
    ]
    return "已匹配到客户：\n" + "\n".join(info_lines)
# %%
@tool(args_schema=CreateClientInput)
def create_client(**kwargs) -> str:
    """
    在指定机构下创建客户。至少应提供 name，id_number或者hk_id_number。
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    url = f"{base_url}/open/organizations/{org_code}/clients"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    payload = {k: v for k, v in kwargs.items() if v}
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    if response.status_code != 200:
        return f"错误：请求失败，HTTP {response.status_code}，响应：{response.text}"
    data = response.json()
    _client_type_map = {0: "未设置", 1: "个人", 2: "企业"}
    _gender_map = {0: "未设置", 1: "男", 2: "女"}
    info_lines = [
        f"客户ID: {data.get('id')}",
        f"姓名: {data.get('name', '')}",
        f"英文名: {data.get('english_name', '')}",
        f"客户类型: {_client_type_map.get(data.get('type', 0), '未知')}",
        f"性别: {_gender_map.get(data.get('gender', 0), '未知')}",
        f"电话: {data.get('phone', '')}",
        f"邮箱: {data.get('email', '')}",
        f"月收入: {data.get('monthly_income', 0)}",
        f"月支出: {data.get('monthly_expense', 0)}",
        f"月可支配收入: {data.get('monthly_disposable_income', 0)}",
        f"估计净流动资产: {data.get('estimated_net_liquid_assets', 0)}",
        f"估计净资产: {data.get('estimated_net_assets', 0)}",
        f"渠道ID: {data.get('channel_id', '')}",
        f"创建时间: {data.get('created_at', '')}",
    ]
    return "客户创建成功：\n" + "\n".join(info_lines)
# %%
@tool(args_schema=UpdateClientInput)
def update_client(**kwargs) -> str:
    """
    更新指定机构下已有客户的信息。只需传入需要修改的字段，未传字段保持原值。client_id 为必填。
    """
    client_id = kwargs.pop("client_id")
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    url = f"{base_url}/open/organizations/{org_code}/clients/{client_id}"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    payload = {k: v for k, v in kwargs.items() if v}
    if not payload:
        return "错误：未提供任何需要更新的字段"
    response = requests.patch(url, json=payload, headers=headers, timeout=15)
    if response.status_code != 200:
        return f"错误：请求失败，HTTP {response.status_code}，响应：{response.text}"
    data = response.json()
    _client_type_map = {0: "未设置", 1: "个人", 2: "企业"}
    _gender_map = {0: "未设置", 1: "男", 2: "女"}
    info_lines = [
        f"客户ID: {data.get('id')}",
        f"姓名: {data.get('name', '')}",
        f"英文名: {data.get('english_name', '')}",
        f"客户类型: {_client_type_map.get(data.get('type', 0), '未知')}",
        f"性别: {_gender_map.get(data.get('gender', 0), '未知')}",
        f"电话: {data.get('phone', '')}",
        f"邮箱: {data.get('email', '')}",
        f"月收入: {data.get('monthly_income', 0)}",
        f"月支出: {data.get('monthly_expense', 0)}",
        f"月可支配收入: {data.get('monthly_disposable_income', 0)}",
        f"更新时间: {data.get('updated_at', '')}",
    ]
    return "客户更新成功：\n" + "\n".join(info_lines)
