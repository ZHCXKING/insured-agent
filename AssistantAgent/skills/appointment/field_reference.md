# 预约系统字段参考

本文件列出所有工具涉及的字段定义，供子代理在解析自然语言时参考。

---

## 客户相关

### match_client — 匹配客户

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id_number | str | 否（与hk_id_number至少填一个） | 内地身份证号，18位数字，末位可能X |
| hk_id_number | str | 否（与id_number至少填一个） | 香港身份证号，1位英文字母+6位数字+(校验码) |

### create_client — 创建客户

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | **是** | 姓名 |
| id_number | str | 否（与hk_id_number至少填一个） | 内地身份证号 |
| hk_id_number | str | 否（与id_number至少填一个） | 香港身份证号 |
| english_name | str | 否 | 英文姓名/拼音 |
| type | int | 否 | 客户类型：0=未设置，1=个人，2=企业。默认0 |
| gender | int | 否 | 性别：0=未设置，1=男，2=女。默认0 |
| hk_macau_pass_id | str | 否 | 港澳通行证号 |
| phone | str | 否 | 主要电话 |
| home_phone | str | 否 | 住宅电话 |
| office_phone | str | 否 | 办公电话 |
| email | str | 否 | 邮箱 |
| country | str | 否 | 国家/地区 |
| nationality | str | 否 | 国籍 |
| birth_country | str | 否 | 出生国家 |
| tax_residency_country | str | 否 | 税务居民国家 |
| residential_address | str | 否 | 居住地址 |
| address | str | 否 | 通讯地址 |
| birthdate | str | 否 | 出生日期，格式 YYYY-MM-DD |
| height | int | 否 | 身高，≥0。默认0 |
| height_unit | str | 否 | 身高单位。默认"cm" |
| weight | int | 否 | 体重，≥0。默认0 |
| weight_unit | str | 否 | 体重单位。默认"kg" |
| smoke | bool | 否 | 是否吸烟。默认False |
| education | str | 否 | 教育程度：""=未设置, primary_or_below=小学或以下, secondary=中学, post_secondary=大专, university_or_above=大学或以上 |
| marital_status | str | 否 | 婚姻状况：""=未设置, single=未婚, married=已婚, divorced=离异, widowed=丧偶 |
| employment_status | str | 否 | 就业情况：employed=在职, self_employed=自雇, unemployed=失业, retired=退休, student=学生 |
| company | str | 否 | 公司名称 |
| occupation | str | 否 | 职业类别 |
| job_title | str | 否 | 具体职位 |
| industry_category | str | 否 | 行业类别 |
| company_address | str | 否 | 公司地址 |
| dependents_count | int | 否 | 供养人数，≥0。默认0 |
| expected_retirement_age | int | 否 | 预期退休年龄，≥0。默认0 |
| is_retired | bool | 否 | 是否已退休。默认False |
| life_insurance_coverage | int | 否 | 人寿保险保额，≥0。默认0 |
| critical_illness_coverage | int | 否 | 重疾保险保额，≥0。默认0 |
| accident_insurance_coverage | int | 否 | 意外保险保额，≥0。默认0 |
| medical_insurance_type | str | 否 | 医疗保险类型 |
| medical_insurance_coverage | int | 否 | 医疗保险金额，≥0。默认0 |
| other_coverage_description | str | 否 | 其他保障说明 |
| other_coverage_amount | int | 否 | 其他保障金额，≥0。默认0 |
| salary_income | int | 否 | 薪资收入，≥0。默认0 |
| rental_income | int | 否 | 租金收入，≥0。默认0 |
| other_income | int | 否 | 其他收入，≥0。默认0 |
| personal_family_expense | int | 否 | 个人及家庭开支，≥0。默认0 |
| mortgage_loan_repayment | int | 否 | 按揭或贷款还款，≥0。默认0 |
| insurance_premium_expense | int | 否 | 保费支出，≥0。默认0 |
| other_expense | int | 否 | 其他支出，≥0。默认0 |
| liquid_funds | int | 否 | 流动资金，≥0。默认0 |
| short_term_liabilities_total | int | 否 | 短期负债总额，≥0。默认0 |
| non_liquid_assets_total | int | 否 | 非流动资产总额，≥0。默认0 |
| mortgage_liabilities | int | 否 | 按揭贷款，≥0。默认0 |
| personal_loan_liabilities | int | 否 | 个人贷款，≥0。默认0 |
| other_liabilities | int | 否 | 其他负债，≥0。默认0 |
| total_liabilities | int | 否 | 总负债额，≥0。默认0 |
| init_payment_method | list[str] | 否 | 首期供款付款方式 |
| channel_id | str | 否 | 归属渠道用户ID |
| remark | str | 否 | 备注 |

### update_client — 更新客户

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| client_id | str | **是** | 客户ID |
| 其余字段 | 同create_client | 否 | 只需传入需要修改的字段，未传字段保持不变 |

---

## 用户搜索

### search_users — 搜索用户

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| search | str | **是** | 搜索关键字，后端自动在姓名/英文名/昵称/邮箱/手机号中匹配 |
| role | str | 否 | 按角色精确过滤。可选值：admin=管理员, fin=财务, hr=人事, info=资料, biz=业管, proposal_it=自动计划书维护-IT, sales=业务代表, referrer=转介人, partner=合作方, signing_clerk=签单文员, signing_manager=签单管理 |

---

## 保险公司与产品

### search_companies — 搜索保险公司

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| search | str | **是** | 保险公司名称（模糊匹配中文名/英文名） |

### search_products — 搜索产品

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| search | str | **是** | 产品名称（模糊匹配中文名/英文名） |
| company_id | str | 否 | 保险公司ID（精确过滤，通过search_companies获取） |

---

## 保单相关

### create_policy — 创建保单

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_company_id | str | **是** | 保险公司ID（通过search_companies获取） |
| product_sku_id | str | **是** | 产品SKU ID（通过search_products获取） |
| premium | float | **是** | 当期保费，≥0。只填数字，不含货币符号 |
| currency | str | **是** | 币种：HKD=港币, USD=美元, CNY=人民币 |
| payment_period | int | **是** | 供款年期，≥1 |
| prepaid_premium | bool | **是** | 是否预缴保费 |
| applicant_id | str | **是** | 投保人客户ID |
| insurant_id | str | **是** | 受保人客户ID |
| sales_id | str | **是** | 业务代表用户ID |
| no | str | 否 | 保单号 |
| insured_policyholder_relation | int | 否 | 受保人与投保人关系：0=未设置, 1=本人, 2=父母, 3=子女, 4=配偶, 5=兄弟姐妹, 6=祖父母, 7=雇员, 8=其他。默认0 |
| signing_clerk_id | str | 否 | 签单文员用户ID |
| channel_id | str | 否 | 转介人用户ID |
| applied_at | str | 否 | 签单日，格式 YYYY-MM-DD |
| premium_time | str | 否 | 当前应缴日，格式 YYYY-MM-DD |
| renewal_plan | str | 否 | 续保计划：""=未设置, Single=一次性, Annual=年缴, HalfYearly=半年缴, Quarterly=季缴 |
| sum_assured | float | 否 | 保额，≥0。默认0 |
| beneficiary_distribution_mode | int | 否 | 受益人分配模式：1=按比例, 2=按顺位。默认1 |
| beneficiaries | list | 否 | 受益人列表（见下方受益人字段） |
| remark | str | 否 | 备注 |

#### 受益人字段（beneficiaries列表中每项）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | 否 | 受益人中文姓名 |
| english_name | str | 否 | 受益人拼音或英文名 |
| id_number | str | 否 | 受益人证件号 |
| relationship | str | 否 | 与受保人关系 |
| proportion | float | 否 | 分配比例0~1，按比例模式时必填 |
| client_id | str | 否 | 关联客户ID（如该受益人已存在于客户库） |

### update_policy — 更新保单

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| policy_id | str | **是** | 保单ID |
| insurant_id | str | **是** | 受保人客户ID |
| sales_id | str | **是** | 业务代表用户ID |
| 其余字段 | 同create_policy | 否 | 只需传入需要修改的字段，未传字段保持不变。currency为选填 |

---

## 预约相关

### create_appointment — 创建预约

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sales_id | str | **是** | 业务代表用户ID |
| policyholder_ids | list[str] | **是** | 投保人客户ID列表 |
| insured_ids | list[str] | **是** | 受保人客户ID列表（至少1个） |
| policy_ids | list[str] | **是** | 关联保单ID列表（至少1个） |
| time | str | **是** | 预约时间，格式 YYYY-MM-DD HH:mm（如 2026-05-08 14:30） |
| type | int | 否 | 预约类型：0=个人预约, 1=独立预约, 2=文件协助, 3=全程协助。默认3 |
| channel_id | str | 否 | 转介人用户ID |
| signing_clerk_id | str | 否 | 签单文员ID |
| signing_room_id | str | 否 | 签单房间ID |
| reject_reason | str | 否 | 拒绝原因 |
| remark | str | 否 | 备注 |

### update_appointment — 更新预约

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| appointment_id | str | **是** | 预约ID |
| 其余字段 | 同create_appointment | 否 | 只需传入需要修改的字段，未传字段保持不变 |
