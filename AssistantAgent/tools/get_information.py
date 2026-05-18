# %%
import json
import os
import requests
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from langchain.tools import tool
# %%
class GetInformationInput(BaseModel):
    appointment_id: str = Field(default="", description="预约ID")
    client_id: str = Field(default="", description="客户ID")
    user_id: str = Field(default="", description="用户ID")
    policy_id: str = Field(default="", description="保单ID")
    @model_validator(mode='after')
    def check_at_least_one(self) -> 'GetInformationInput':
        if not self.appointment_id and not self.client_id and not self.user_id and not self.policy_id:
            raise ValueError("至少需要提供 appointment_id、client_id、user_id 或 policy_id 中的一个")
        return self
# %%
@tool(args_schema=GetInformationInput)
def get_information(**kwargs) -> str:
    """
    根据ID查询各类业务信息的详细内容。支持四种查询：客户信息(client_id)、用户信息(user_id)、预约信息(appointment_id)、保单信息(policy_id)。
    同时传入多个ID时会一并查询所有对应信息并合并返回。
    """
    base_url = os.getenv("ORGANIZATION_URL")
    api_key = os.getenv("ORGANIZATION_KEY")
    org_code = os.getenv("ORG_CODE")
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Accept": "application/json",
    }
    _status_map = {0: "草稿", 1: "审核中", 2: "预约中", 3: "确认预约", 4: "签单完成", 5: "取消投保", 6: "拒绝申请"}
    _process_map = {0: "基础信息", 1: "客户信息", 2: "保单信息"}
    _type_map = {0: "个人预约", 1: "独立预约", 2: "文件协助", 3: "全程协助"}
    _policy_status_map = {
        1: "等待进入保司系统", 2: "待查询进度",         3: "欠费", 4: "待处理中",
        5: "再次出现待处理", 6: "已递交待处理", 7: "需要体检或报告", 8: "等待生效",
        9: "已生效", 10: "有不保事项/加费", 11: "已拒保/被搁置", 12: "保司自动取消投保",
        13: "取消投保-客人要求", 14: "于冷静期退保", 15: "保单失效",
    }
    _gender_map = {0: "未设置", 1: "男", 2: "女"}
    _education_map = {"primary_or_below": "小学程度或以下", "secondary": "中学", "post_secondary": "大专(非学位)", "university_or_above": "大学学位或以上"}
    _marital_status_map = {"single": "未婚", "married": "已婚", "divorced": "离异", "widowed": "丧偶"}
    _employment_status_map = {"employed": "在职", "self_employed": "自雇", "unemployed": "失业", "retired": "退休", "student": "学生"}
    _renewal_plan_map = {"Single": "一次性", "Monthly": "月缴", "Annually": "年缴", "Annual": "年缴", "Quarterly": "季缴", "HalfYearly": "半年缴"}
    _payment_mode_map = {"premium": "按保费", "coverage": "按保额"}
    _role_map = {"sales": "业务代表", "referrer": "转介人", "signing_manager": "签单文员"}
    _user_role_map = {
        "admin": "管理员", "fin": "财务", "hr": "人事", "info": "资料",
        "biz": "业管", "proposal_it": "自动计划书维护-IT", "sales": "业务代表",
        "referrer": "转介人", "partner": "合作方", "signing_clerk": "签单文员",
        "signing_manager": "签单管理",
    }
    _user_status_map = {1: "启用", -1: "封禁"}
    _user_channel_type_map = {"default": "未设置", "normal": "普通渠道", "ifa": "IFA渠道"}
    _relation_map = {1: "本人", 2: "父母", 3: "子女", 4: "配偶", 5: "兄弟姐妹", 6: "祖父母(外)", 7: "雇员", 8: "其他"}
    def _fmt_ts(ts):
        if not ts:
            return ""
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    def _do_get(path):
        resp = requests.get(f"{base_url}/open/organizations/{org_code}/{path}", headers=headers, timeout=15)
        if resp.status_code != 200:
            return None, f"错误：请求失败，HTTP {resp.status_code}，响应：{resp.text}"
        data = resp.json()
        return data.get("data", data), None
    def _query_appointment(appointment_id):
        data, err = _do_get(f"appointments/{appointment_id}")
        if err:
            return err
        def _parse_user(u):
            if not u:
                return None
            return {
                "姓名": u.get("name", ""),
                "英文名": u.get("english_name", ""),
                "ID": u.get("id", ""),
                "电话": u.get("phone", ""),
                "邮箱": u.get("email", ""),
                "角色": _role_map.get(u.get("role", ""), u.get("role", "")),
            }
        def _parse_room(r):
            if not r:
                return None
            return {
                "名称": r.get("name", ""),
                "位置": r.get("location", ""),
                "ID": r.get("id", ""),
                "是否启用": r.get("is_active", ""),
                "备注": r.get("notes", ""),
            }
        def _parse_client(c):
            if not c:
                return None
            return {
                "姓名": c.get("name", ""),
                "英文名": c.get("english_name", ""),
                "ID": c.get("id", ""),
                "性别": _gender_map.get(c.get("gender", 0), "未知"),
                "出生日期": c.get("birthdate", ""),
                "国家": c.get("country", ""),
                "国籍": c.get("nationality", ""),
                "内地身份证": c.get("id_number", ""),
                "香港身份证": c.get("hk_id_number", ""),
                "电话": c.get("phone", ""),
                "邮箱": c.get("email", ""),
                "居住地址": c.get("residential_address", ""),
                "教育程度": _education_map.get(c.get("education", ""), c.get("education", "")),
                "婚姻状况": _marital_status_map.get(c.get("marital_status", ""), c.get("marital_status", "")),
                "就业状况": _employment_status_map.get(c.get("employment_status", ""), c.get("employment_status", "")) or "未设置",
                "公司": c.get("company", ""),
                "职业": c.get("occupation", ""),
                "职位": c.get("job_title", ""),
                "行业": c.get("industry_category", ""),
                "供养人数": c.get("dependents_count", 0),
                "月收入": c.get("monthly_income", 0),
                "月支出": c.get("monthly_expense", 0),
                "月可支配收入": c.get("monthly_disposable_income", 0),
                "估计净流动资产": c.get("estimated_net_liquid_assets", 0),
                "估计净资产": c.get("estimated_net_assets", 0),
            }
        def _parse_policy(p):
            if not p:
                return None
            company = p.get("product_company", {})
            sku_product = p.get("product_sku", {}).get("product", {})
            product_sku = p.get("product_sku", {})
            policy_type = p.get("type")
            type_str = "正式" if policy_type == 1 else ("托管" if policy_type == 2 else str(policy_type or ""))
            result = {
                "保单ID": p.get("id", ""),
                "保单号": p.get("no", ""),
                "状态": _policy_status_map.get(p.get("status", 0), "未知"),
                "类型": type_str,
                "保险公司": company.get("name", ""),
                "产品": sku_product.get("name", ""),
                "保费": p.get("premium", ""),
                "币种": p.get("currency", ""),
                "缴费模式": _payment_mode_map.get(p.get("payment_mode", ""), p.get("payment_mode", "")),
                "续保计划": _renewal_plan_map.get(p.get("renewal_plan", ""), p.get("renewal_plan", "")),
                "供款年期": product_sku.get("period", ""),
                "保额": p.get("sum_assured", ""),
                "签单日": _fmt_ts(p.get("applied_at", 0)),
                "保单日期": _fmt_ts(p.get("policy_date", 0)),
                "投保人与受保人关系": _relation_map.get(p.get("insured_policyholder_relation", 0), str(p.get("insured_policyholder_relation", ""))),
                "是否DDA": p.get("dda", False),
                "备注": p.get("remark", ""),
            }
            return result
        sales = data.get("sales")
        channel = data.get("channel")
        signing_clerk = data.get("signing_clerk")
        signing_room = data.get("signing_room")
        policyholders = data.get("policyholders", [])
        insureds = data.get("insureds", [])
        policies = data.get("policies", [])
        return {
            "预约信息": {
                "预约ID": data.get("id", ""),
                "创建时间": _fmt_ts(data.get("created_at", 0)),
                "更新时间": _fmt_ts(data.get("updated_at", 0)),
                "预约时间": _fmt_ts(data.get("time", 0)),
                "状态": _status_map.get(data.get("status", 0), "未知"),
                "流程节点": _process_map.get(data.get("process", 0), "未知"),
                "预约类型": _type_map.get(data.get("type", 0), "未知"),
                "是否快速创建": data.get("is_quick_create", False),
                "业务代表": _parse_user(sales),
                "转介人": _parse_user(channel),
                "签单文员": _parse_user(signing_clerk),
                "签单房间": _parse_room(signing_room),
                "拒绝原因": data.get("reject_reason", ""),
                "备注": data.get("remark", ""),
                "是否有未读变更": data.get("has_unread_changes", False),
                "投保人列表": [_parse_client(ph) for ph in policyholders],
                "受保人列表": [_parse_client(ins) for ins in insureds],
                "关联保单列表": [_parse_policy(pol) for pol in policies],
            }
        }
    def _query_client(client_id):
        data, err = _do_get(f"clients/{client_id}")
        if err:
            return err
        c = data
        return {
            "客户信息": {
                "客户ID": c.get("id", ""),
                "姓名": c.get("name", ""),
                "英文名": c.get("english_name", ""),
                "性别": _gender_map.get(c.get("gender", 0), "未知"),
                "出生日期": c.get("birthdate", ""),
                "国家": c.get("country", ""),
                "出生国家": c.get("birth_country", ""),
                "国籍": c.get("nationality", ""),
                "税务居民": c.get("tax_residency_country", ""),
                "内地身份证": c.get("id_number", ""),
                "香港身份证": c.get("hk_id_number", ""),
                "港澳通行证": c.get("hk_macau_pass_id", ""),
                "电话": c.get("phone", ""),
                "住宅电话": c.get("home_phone", ""),
                "办公电话": c.get("office_phone", ""),
                "邮箱": c.get("email", ""),
                "居住地址": c.get("residential_address", ""),
                "通讯地址": c.get("address", ""),
                "身高": c.get("height", ""),
                "体重": c.get("weight", ""),
                "吸烟": c.get("smoke", ""),
                "教育程度": _education_map.get(c.get("education", ""), c.get("education", "")),
                "婚姻状况": _marital_status_map.get(c.get("marital_status", ""), c.get("marital_status", "")),
                "就业状况": _employment_status_map.get(c.get("employment_status", ""), c.get("employment_status", "")) or "未设置",
                "公司": c.get("company", ""),
                "职业": c.get("occupation", ""),
                "职位": c.get("job_title", ""),
                "行业": c.get("industry_category", ""),
                "公司地址": c.get("company_address", ""),
                "供养人数": c.get("dependents_count", 0),
                "已退休": c.get("is_retired", False),
                "预期退休年龄": c.get("expected_retirement_age", 0),
                "是否历史客户": c.get("is_historical_client", False),
                "人寿保险保额": c.get("life_insurance_coverage", 0),
                "重疾险保额": c.get("critical_illness_coverage", 0),
                "意外险保额": c.get("accident_insurance_coverage", 0),
                "医疗保险类型": c.get("medical_insurance_type", ""),
                "医疗保险保额": c.get("medical_insurance_coverage", 0),
                "其他保障描述": c.get("other_coverage_description", ""),
                "其他保障金额": c.get("other_coverage_amount", 0),
                "薪资收入": c.get("salary_income", 0),
                "租金收入": c.get("rental_income", 0),
                "其他收入": c.get("other_income", 0),
                "月收入": c.get("monthly_income", 0),
                "个人家庭支出": c.get("personal_family_expense", 0),
                "房贷还款": c.get("mortgage_loan_repayment", 0),
                "保险费支出": c.get("insurance_premium_expense", 0),
                "其他支出": c.get("other_expense", 0),
                "月支出": c.get("monthly_expense", 0),
                "月可支配收入": c.get("monthly_disposable_income", 0),
                "流动资金": c.get("liquid_funds", 0),
                "短期负债": c.get("short_term_liabilities_total", 0),
                "估计净流动资产": c.get("estimated_net_liquid_assets", 0),
                "非流动资产": c.get("non_liquid_assets_total", 0),
                "房贷负债": c.get("mortgage_liabilities", 0),
                "个人贷款负债": c.get("personal_loan_liabilities", 0),
                "其他负债": c.get("other_liabilities", 0),
                "总负债": c.get("total_liabilities", 0),
                "估计净资产": c.get("estimated_net_assets", 0),
            }
        }
    def _query_user(user_id):
        data, err = _do_get(f"users/{user_id}")
        if err:
            return err
        u = data
        return {
            "用户信息": {
                "用户ID": u.get("id", ""),
                "姓名": u.get("name", ""),
                "英文名": u.get("english_name", ""),
                "角色": _user_role_map.get(u.get("role", ""), u.get("role", "")),
                "状态": _user_status_map.get(u.get("status", 0), "未知"),
                "渠道类型": _user_channel_type_map.get(u.get("channel_type", ""), u.get("channel_type", "")),
                "邮箱": u.get("email", ""),
                "电话": u.get("phone", ""),
            }
        }
    def _query_policy(policy_id):
        data, err = _do_get(f"policies/{policy_id}")
        if err:
            return err
        p = data
        company = p.get("product_company", {})
        sku_product = p.get("product_sku", {}).get("product", {})
        product_sku = p.get("product_sku", {})
        policy_type = p.get("type")
        type_str = "正式" if policy_type == 1 else ("托管" if policy_type == 2 else str(policy_type or ""))
        result = {
            "保单信息": {
                "保单ID": p.get("id", ""),
                "保单号": p.get("no", ""),
                "状态": _policy_status_map.get(p.get("status", 0), "未知"),
                "类型": type_str,
                "保险公司": {
                    "名称": company.get("name", ""),
                    "英文名": company.get("english_name", ""),
                    "ID": company.get("id", ""),
                },
                "产品": {
                    "名称": sku_product.get("name", ""),
                    "英文名": sku_product.get("english_name", ""),
                    "ID": sku_product.get("id", ""),
                },
                "SKU": product_sku.get("sku", ""),
                "序列号": product_sku.get("serial_number", ""),
                "供款年期": product_sku.get("period", ""),
                "保费": p.get("premium", ""),
                "币种": p.get("currency", ""),
                "缴费模式": _payment_mode_map.get(p.get("payment_mode", ""), p.get("payment_mode", "")),
                "续保计划": _renewal_plan_map.get(p.get("renewal_plan", ""), p.get("renewal_plan", "")),
                "续保金额": p.get("renewal_amount", ""),
                "供款期": p.get("payment_period", ""),
                "保单年期": p.get("policy_term", ""),
                "保额": p.get("sum_assured", ""),
                "coverage保额": p.get("coverage", ""),
                "折后含征费": p.get("premium_inc_levy", ""),
                "原保费不含征费": p.get("premium_excl_levy", ""),
                "签单日": _fmt_ts(p.get("applied_at", 0)),
                "应缴日": _fmt_ts(p.get("premium_time", 0)),
                "下次缴费日": _fmt_ts(p.get("next_premium_time", 0)),
                "投保人与受保人关系": _relation_map.get(p.get("insured_policyholder_relation", 0), str(p.get("insured_policyholder_relation", ""))),
                "是否DDA": p.get("dda", False),
                "是否追溯": p.get("backtrack", False),
                "是否预缴保费": p.get("prepaid_premium", False),
                "冷静期截止日": _fmt_ts(p.get("cooling_off_end_at", 0)),
                "完成时间": _fmt_ts(p.get("completed_at", 0)),
                "申请收到时间": _fmt_ts(p.get("application_received_at", 0)),
                "申请发出时间": _fmt_ts(p.get("application_sent_at", 0)),
                "保单收到时间": _fmt_ts(p.get("policy_received_at", 0)),
                "保单发出时间": _fmt_ts(p.get("policy_sent_at", 0)),
                "保单领取方式": p.get("policy_pickup_way", ""),
                "保单日期": _fmt_ts(p.get("policy_date", 0)),
                "投资者类型": p.get("investor_type", ""),
                "是否归档": p.get("archived", False),
                "是否已提交保险公司": p.get("submitted_to_insurer", False),
                "是否历史保单": p.get("is_historical", False),
                "受益人分配模式": "按比例" if p.get("beneficiary_distribution_mode") == 1 else "按顺位",
                "受益人列表": [
                    {
                        "姓名": b.get("name", ""),
                        "英文名": b.get("english_name", ""),
                        "证件号": b.get("id_number", ""),
                        "关系": b.get("relationship", ""),
                        "比例": b.get("proportion", ""),
                    }
                    for b in (p.get("beneficiaries") or [])
                ],
                "备注": p.get("remark", ""),
            }
        }
        return result
    result = {}
    errors = []
    if kwargs.get("appointment_id"):
        r = _query_appointment(kwargs["appointment_id"])
        if isinstance(r, str):
            errors.append(f"预约查询失败: {r}")
        else:
            result.update(r)
    if kwargs.get("client_id"):
        r = _query_client(kwargs["client_id"])
        if isinstance(r, str):
            errors.append(f"客户查询失败: {r}")
        else:
            result.update(r)
    if kwargs.get("user_id"):
        r = _query_user(kwargs["user_id"])
        if isinstance(r, str):
            errors.append(f"用户查询失败: {r}")
        else:
            result.update(r)
    if kwargs.get("policy_id"):
        r = _query_policy(kwargs["policy_id"])
        if isinstance(r, str):
            errors.append(f"保单查询失败: {r}")
        else:
            result.update(r)
    if not result:
        return "错误：" + "；".join(errors)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if errors:
        output += "\n\n警告：" + "；".join(errors)
    return output
