# %%
import os
import requests
from datetime import datetime
# %%
def match_client(id_number: str = "", hk_id_number: str = "") -> str:
    """
    通过身份证号或香港身份证号匹配客户。至少提供 id_number 或 hk_id_number 其中之一。
    如果匹配到客户，返回客户信息（含客户ID）；未匹配到则返回提示需要创建客户。
    参数:
        id_number: 内地身份证号
        hk_id_number: 香港身份证号
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
def search_users(search: str = "", role: str = "") -> str:
    """
    通过关键字模糊搜索机构内的用户列表。可按姓名/英文名/昵称/邮箱/手机号模糊匹配。
    参数:
        search: 搜索关键字（姓名/英文名/昵称/邮箱/手机号）
        role: 按角色精确过滤，可选值：admin/fin/hr/info/biz/proposal_it/sales/referrer/partner/signing_clerk/signing_manager
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
    if search:
        params["search"] = search
    if role:
        params["role"] = role
    response = requests.get(url, params=params, headers=headers, timeout=15)
    if response.status_code != 200:
        return f"错误：请求失败，HTTP {response.status_code}，响应：{response.text}"
    data = response.json()
    users = data.get("data", [])
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
# %%
def create_client(
    name: str = "",
    english_name: str = "",
    type: int = 1,
    gender: int = 0,
    id_number: str = "",
    hk_id_number: str = "",
    hk_macau_pass_id: str = "",
    phone: str = "",
    home_phone: str = "",
    office_phone: str = "",
    email: str = "",
    country: str = "",
    nationality: str = "",
    birth_country: str = "",
    tax_residency_country: str = "",
    residential_address: str = "",
    address: str = "",
    birthdate: str = "",
    height: int = 0,
    height_unit: str = "cm",
    weight: int = 0,
    weight_unit: str = "kg",
    smoke: bool = False,
    education: str = "",
    marital_status: str = "",
    employment_status: str = "",
    company: str = "",
    occupation: str = "",
    job_title: str = "",
    industry_category: str = "",
    company_address: str = "",
    dependents_count: int = 0,
    expected_retirement_age: int = 0,
    is_retired: bool = False,
    salary_income: int = 0,
    rental_income: int = 0,
    other_income: int = 0,
    personal_family_expense: int = 0,
    mortgage_loan_repayment: int = 0,
    insurance_premium_expense: int = 0,
    other_expense: int = 0,
    liquid_funds: int = 0,
    short_term_liabilities_total: int = 0,
    non_liquid_assets_total: int = 0,
    mortgage_liabilities: int = 0,
    personal_loan_liabilities: int = 0,
    other_liabilities: int = 0,
    total_liabilities: int = 0,
    channel_id: str = "",
    remark: str = "",
) -> str:
    """
    在指定机构下创建客户。至少应提供 name、type、gender、id_number 或 hk_id_number、phone 或 email、birthdate、country、nationality。
    参数:
        name: 姓名
        english_name: 英文姓名
        type: 客户类型，1=个人，2=企业
        gender: 性别，1=男，2=女
        id_number: 内地身份证号
        hk_id_number: 香港身份证号
        hk_macau_pass_id: 港澳通行证号
        phone: 主要电话
        home_phone: 住宅电话
        office_phone: 办公电话
        email: 邮箱
        country: 国家/地区
        nationality: 国籍
        birth_country: 出生国家
        tax_residency_country: 税务居民国家
        residential_address: 居住地址
        address: 通讯地址
        birthdate: 出生日期，格式 YYYY-MM-DD
        height: 身高
        height_unit: 身高单位，默认cm
        weight: 体重
        weight_unit: 体重单位，默认kg
        smoke: 是否吸烟
        education: 教育程度，可选：primary_or_below/secondary/post_secondary/university_or_above
        marital_status: 婚姻状况，可选：single/married/divorced/widowed
        employment_status: 就业情况
        company: 公司名称
        occupation: 职业类别
        job_title: 具体职位
        industry_category: 行业类别
        company_address: 公司地址
        dependents_count: 供养人数
        expected_retirement_age: 预期退休年龄
        is_retired: 是否已退休
        salary_income: 薪资收入
        rental_income: 租金收入
        other_income: 其他收入
        personal_family_expense: 个人及家庭开支
        mortgage_loan_repayment: 按揭或贷款还款
        insurance_premium_expense: 保费支出
        other_expense: 其他支出
        liquid_funds: 流动资金
        short_term_liabilities_total: 短期负债总额
        non_liquid_assets_total: 非流动资产总额
        mortgage_liabilities: 按揭贷款
        personal_loan_liabilities: 个人贷款
        other_liabilities: 其他负债
        total_liabilities: 总负债额
        channel_id: 归属渠道用户ID
        remark: 备注
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    if not name:
        return "错误：姓名（name）为必填项"
    url = f"{base_url}/open/organizations/{org_code}/clients"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    payload = {}
    if name:
        payload["name"] = name
    if english_name:
        payload["english_name"] = english_name
    if type:
        payload["type"] = type
    if gender:
        payload["gender"] = gender
    if id_number:
        payload["id_number"] = id_number
    if hk_id_number:
        payload["hk_id_number"] = hk_id_number
    if hk_macau_pass_id:
        payload["hk_macau_pass_id"] = hk_macau_pass_id
    if phone:
        payload["phone"] = phone
    if home_phone:
        payload["home_phone"] = home_phone
    if office_phone:
        payload["office_phone"] = office_phone
    if email:
        payload["email"] = email
    if country:
        payload["country"] = country
    if nationality:
        payload["nationality"] = nationality
    if birth_country:
        payload["birth_country"] = birth_country
    if tax_residency_country:
        payload["tax_residency_country"] = tax_residency_country
    if residential_address:
        payload["residential_address"] = residential_address
    if address:
        payload["address"] = address
    if birthdate:
        payload["birthdate"] = birthdate
    if height:
        payload["height"] = height
    if height_unit:
        payload["height_unit"] = height_unit
    if weight:
        payload["weight"] = weight
    if weight_unit:
        payload["weight_unit"] = weight_unit
    if smoke:
        payload["smoke"] = smoke
    if education:
        payload["education"] = education
    if marital_status:
        payload["marital_status"] = marital_status
    if employment_status:
        payload["employment_status"] = employment_status
    if company:
        payload["company"] = company
    if occupation:
        payload["occupation"] = occupation
    if job_title:
        payload["job_title"] = job_title
    if industry_category:
        payload["industry_category"] = industry_category
    if company_address:
        payload["company_address"] = company_address
    if dependents_count:
        payload["dependents_count"] = dependents_count
    if expected_retirement_age:
        payload["expected_retirement_age"] = expected_retirement_age
    if is_retired:
        payload["is_retired"] = is_retired
    if salary_income:
        payload["salary_income"] = salary_income
    if rental_income:
        payload["rental_income"] = rental_income
    if other_income:
        payload["other_income"] = other_income
    if personal_family_expense:
        payload["personal_family_expense"] = personal_family_expense
    if mortgage_loan_repayment:
        payload["mortgage_loan_repayment"] = mortgage_loan_repayment
    if insurance_premium_expense:
        payload["insurance_premium_expense"] = insurance_premium_expense
    if other_expense:
        payload["other_expense"] = other_expense
    if liquid_funds:
        payload["liquid_funds"] = liquid_funds
    if short_term_liabilities_total:
        payload["short_term_liabilities_total"] = short_term_liabilities_total
    if non_liquid_assets_total:
        payload["non_liquid_assets_total"] = non_liquid_assets_total
    if mortgage_liabilities:
        payload["mortgage_liabilities"] = mortgage_liabilities
    if personal_loan_liabilities:
        payload["personal_loan_liabilities"] = personal_loan_liabilities
    if other_liabilities:
        payload["other_liabilities"] = other_liabilities
    if total_liabilities:
        payload["total_liabilities"] = total_liabilities
    if channel_id:
        payload["channel_id"] = channel_id
    if remark:
        payload["remark"] = remark
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
def update_client(
    client_id: str,
    name: str = "",
    english_name: str = "",
    type: int = 0,
    gender: int = 0,
    id_number: str = "",
    hk_id_number: str = "",
    hk_macau_pass_id: str = "",
    phone: str = "",
    home_phone: str = "",
    office_phone: str = "",
    email: str = "",
    country: str = "",
    nationality: str = "",
    birth_country: str = "",
    tax_residency_country: str = "",
    residential_address: str = "",
    address: str = "",
    birthdate: str = "",
    height: int = 0,
    height_unit: str = "",
    weight: int = 0,
    weight_unit: str = "",
    smoke: bool = False,
    education: str = "",
    marital_status: str = "",
    employment_status: str = "",
    company: str = "",
    occupation: str = "",
    job_title: str = "",
    industry_category: str = "",
    company_address: str = "",
    dependents_count: int = 0,
    expected_retirement_age: int = 0,
    is_retired: bool = False,
    salary_income: int = 0,
    rental_income: int = 0,
    other_income: int = 0,
    personal_family_expense: int = 0,
    mortgage_loan_repayment: int = 0,
    insurance_premium_expense: int = 0,
    other_expense: int = 0,
    liquid_funds: int = 0,
    short_term_liabilities_total: int = 0,
    non_liquid_assets_total: int = 0,
    mortgage_liabilities: int = 0,
    personal_loan_liabilities: int = 0,
    other_liabilities: int = 0,
    total_liabilities: int = 0,
    channel_id: str = "",
    remark: str = "",
) -> str:
    """
    更新指定机构下已有客户的信息。只需传入需要修改的字段，未传字段保持原值。client_id 为必填。
    参数:
        client_id: 客户ID（必填）
        name: 姓名
        english_name: 英文姓名
        type: 客户类型，1=个人，2=企业
        gender: 性别，1=男，2=女
        id_number: 内地身份证号
        hk_id_number: 香港身份证号
        hk_macau_pass_id: 港澳通行证号
        phone: 主要电话
        home_phone: 住宅电话
        office_phone: 办公电话
        email: 邮箱
        country: 国家/地区
        nationality: 国籍
        birth_country: 出生国家
        tax_residency_country: 税务居民国家
        residential_address: 居住地址
        address: 通讯地址
        birthdate: 出生日期，格式 YYYY-MM-DD
        height: 身高
        height_unit: 身高单位
        weight: 体重
        weight_unit: 体重单位
        smoke: 是否吸烟
        education: 教育程度，可选：primary_or_below/secondary/post_secondary/university_or_above
        marital_status: 婚姻状况，可选：single/married/divorced/widowed
        employment_status: 就业情况
        company: 公司名称
        occupation: 职业类别
        job_title: 具体职位
        industry_category: 行业类别
        company_address: 公司地址
        dependents_count: 供养人数
        expected_retirement_age: 预期退休年龄
        is_retired: 是否已退休
        salary_income: 薪资收入
        rental_income: 租金收入
        other_income: 其他收入
        personal_family_expense: 个人及家庭开支
        mortgage_loan_repayment: 按揭或贷款还款
        insurance_premium_expense: 保费支出
        other_expense: 其他支出
        liquid_funds: 流动资金
        short_term_liabilities_total: 短期负债总额
        non_liquid_assets_total: 非流动资产总额
        mortgage_liabilities: 按揭贷款
        personal_loan_liabilities: 个人贷款
        other_liabilities: 其他负债
        total_liabilities: 总负债额
        channel_id: 归属渠道用户ID
        remark: 备注
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    if not client_id:
        return "错误：客户ID（client_id）为必填项"
    url = f"{base_url}/open/organizations/{org_code}/clients/{client_id}"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    payload = {}
    if name:
        payload["name"] = name
    if english_name:
        payload["english_name"] = english_name
    if type:
        payload["type"] = type
    if gender:
        payload["gender"] = gender
    if id_number:
        payload["id_number"] = id_number
    if hk_id_number:
        payload["hk_id_number"] = hk_id_number
    if hk_macau_pass_id:
        payload["hk_macau_pass_id"] = hk_macau_pass_id
    if phone:
        payload["phone"] = phone
    if home_phone:
        payload["home_phone"] = home_phone
    if office_phone:
        payload["office_phone"] = office_phone
    if email:
        payload["email"] = email
    if country:
        payload["country"] = country
    if nationality:
        payload["nationality"] = nationality
    if birth_country:
        payload["birth_country"] = birth_country
    if tax_residency_country:
        payload["tax_residency_country"] = tax_residency_country
    if residential_address:
        payload["residential_address"] = residential_address
    if address:
        payload["address"] = address
    if birthdate:
        payload["birthdate"] = birthdate
    if height:
        payload["height"] = height
    if height_unit:
        payload["height_unit"] = height_unit
    if weight:
        payload["weight"] = weight
    if weight_unit:
        payload["weight_unit"] = weight_unit
    if smoke:
        payload["smoke"] = smoke
    if education:
        payload["education"] = education
    if marital_status:
        payload["marital_status"] = marital_status
    if employment_status:
        payload["employment_status"] = employment_status
    if company:
        payload["company"] = company
    if occupation:
        payload["occupation"] = occupation
    if job_title:
        payload["job_title"] = job_title
    if industry_category:
        payload["industry_category"] = industry_category
    if company_address:
        payload["company_address"] = company_address
    if dependents_count:
        payload["dependents_count"] = dependents_count
    if expected_retirement_age:
        payload["expected_retirement_age"] = expected_retirement_age
    if is_retired:
        payload["is_retired"] = is_retired
    if salary_income:
        payload["salary_income"] = salary_income
    if rental_income:
        payload["rental_income"] = rental_income
    if other_income:
        payload["other_income"] = other_income
    if personal_family_expense:
        payload["personal_family_expense"] = personal_family_expense
    if mortgage_loan_repayment:
        payload["mortgage_loan_repayment"] = mortgage_loan_repayment
    if insurance_premium_expense:
        payload["insurance_premium_expense"] = insurance_premium_expense
    if other_expense:
        payload["other_expense"] = other_expense
    if liquid_funds:
        payload["liquid_funds"] = liquid_funds
    if short_term_liabilities_total:
        payload["short_term_liabilities_total"] = short_term_liabilities_total
    if non_liquid_assets_total:
        payload["non_liquid_assets_total"] = non_liquid_assets_total
    if mortgage_liabilities:
        payload["mortgage_liabilities"] = mortgage_liabilities
    if personal_loan_liabilities:
        payload["personal_loan_liabilities"] = personal_loan_liabilities
    if other_liabilities:
        payload["other_liabilities"] = other_liabilities
    if total_liabilities:
        payload["total_liabilities"] = total_liabilities
    if channel_id:
        payload["channel_id"] = channel_id
    if remark:
        payload["remark"] = remark
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
# %%
def create_appointment(
    time: str = "",
    type: int = 3,
    sales_id: str = "",
    channel_id: str = "",
    signing_clerk_id: str = "",
    signing_room_id: str = "",
    policyholder_ids: str = "",
    insured_ids: str = "",
    policy_ids: str = "",
    reject_reason: str = "",
    remark: str = "",
) -> str:
    """
    在指定机构下创建预约。至少需要提供 time、sales_id、policyholder_ids、insured_ids。
    参数:
        time: 预约日期，格式 YYYY-MM-DD
        type: 预约类型，0=个人预约，1=独立预约，2=文件协助，3=全程协助（默认3）
        sales_id: 业务代表用户ID
        channel_id: 转介人用户ID
        signing_clerk_id: 签单文员ID
        signing_room_id: 签单房间ID
        policyholder_ids: 投保人客户ID列表，多个用英文逗号分隔
        insured_ids: 受保人客户ID列表，多个用英文逗号分隔
        policy_ids: 关联保单ID列表，多个用英文逗号分隔
        reject_reason: 拒绝原因
        remark: 备注
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    url = f"{base_url}/open/organizations/{org_code}/appointments"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"status": 1, "process": 2, "type": type}
    if time:
        try:
            dt = datetime.strptime(time, "%Y-%m-%d")
            payload["time"] = int(dt.timestamp())
        except ValueError:
            return f"错误：日期格式不正确，请使用 YYYY-MM-DD 格式（如 2026-05-08）"
    if sales_id:
        payload["sales_id"] = sales_id
    if channel_id:
        payload["channel_id"] = channel_id
    if signing_clerk_id:
        payload["signing_clerk_id"] = signing_clerk_id
    if signing_room_id:
        payload["signing_room_id"] = signing_room_id
    if policyholder_ids:
        payload["policyholder_ids"] = [s.strip() for s in policyholder_ids.split(",")]
    if insured_ids:
        payload["insured_ids"] = [s.strip() for s in insured_ids.split(",")]
    if policy_ids:
        payload["policy_ids"] = [s.strip() for s in policy_ids.split(",")]
    if reject_reason:
        payload["reject_reason"] = reject_reason
    if remark:
        payload["remark"] = remark
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
def update_appointment(
    appointment_id: str,
    time: str = "",
    type: int = 3,
    sales_id: str = "",
    channel_id: str = "",
    signing_clerk_id: str = "",
    signing_room_id: str = "",
    policyholder_ids: str = "",
    insured_ids: str = "",
    policy_ids: str = "",
    reject_reason: str = "",
    remark: str = "",
) -> str:
    """
    更新指定机构下已有预约的信息。只需传入需要修改的字段，未传字段保持原值。appointment_id 为必填。
    参数:
        appointment_id: 预约ID（必填）
        time: 预约日期，格式 YYYY-MM-DD
        type: 预约类型，0=个人预约，1=独立预约，2=文件协助，3=全程协助（默认3）
        sales_id: 业务代表用户ID
        channel_id: 转介人用户ID
        signing_clerk_id: 签单文员ID
        signing_room_id: 签单房间ID
        policyholder_ids: 投保人客户ID列表，多个用英文逗号分隔
        insured_ids: 受保人客户ID列表，多个用英文逗号分隔
        policy_ids: 关联保单ID列表，多个用英文逗号分隔
        reject_reason: 拒绝原因
        remark: 备注
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    if not appointment_id:
        return "错误：预约ID（appointment_id）为必填项"
    url = f"{base_url}/open/organizations/{org_code}/appointments/{appointment_id}"
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
    }
    payload = {}
    if time:
        try:
            dt = datetime.strptime(time, "%Y-%m-%d")
            payload["time"] = int(dt.timestamp())
        except ValueError:
            return f"错误：日期格式不正确，请使用 YYYY-MM-DD 格式（如 2026-05-08）"
    if type:
        payload["type"] = type
    if sales_id:
        payload["sales_id"] = sales_id
    if channel_id:
        payload["channel_id"] = channel_id
    if signing_clerk_id:
        payload["signing_clerk_id"] = signing_clerk_id
    if signing_room_id:
        payload["signing_room_id"] = signing_room_id
    if policyholder_ids:
        payload["policyholder_ids"] = [s.strip() for s in policyholder_ids.split(",")]
    if insured_ids:
        payload["insured_ids"] = [s.strip() for s in insured_ids.split(",")]
    if policy_ids:
        payload["policy_ids"] = [s.strip() for s in policy_ids.split(",")]
    if reject_reason:
        payload["reject_reason"] = reject_reason
    if remark:
        payload["remark"] = remark
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