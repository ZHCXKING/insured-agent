---
name: appointment
description: 当顾问询问预约所需信息、预约模版、签单流程，或要求开始收集签单预约信息时，请使用此技能。它包含了向顾问收集信息的标准话术模板和后续的数据录入指引。
---

# 收集预约信息技能

## 概述
本技能用于在正式进行预约前，指导顾问提供完整的签单信息。分为两个阶段：信息收集（使用话术模板引导顾问填写）和系统录入（委托子代理执行创建操作）。

## 阶段一：信息收集

当用户询问预约所需信息时，请**严格按照以下格式和内容**回复用户，引导其填写。

### 话术模板
请读取同目录下的 `appointment_templates.md` 文件，将三个模块的内容分成三条消息，使用 `send_message` 工具依次发送给用户：
1. 确认归属（必填）
2. 预约信息简易版本
3. 预约签单完整信息（含证件要求）

先发简易版本让顾问快速预约保司，再发完整版本补充详细信息。

### 身份证类型辨别规则
解析顾问提供的身份证号时，必须严格区分大陆身份证和香港身份证，并填入系统对应字段：

| 特征 | 大陆身份证（id_number） | 香港身份证（hk_id_number） |
|---|---|---|
| 格式 | 18位数字，末位可能为X | 1位英文字母 + 6位数字 + (1位校验码) |
| 示例 | 110101199001011234 | A123456(7) |
| 系统字段 | `id_number` | `hk_id_number` |

辨别要点：
- 含英文字母开头且带括号校验码的 → 香港身份证 → `hk_id_number`
- 纯18位数字（末位可能X）的 → 大陆身份证 → `id_number`
- 若顾问未标明类型，根据格式自动判断；格式模糊时主动询问顾问
- 同一客户可能同时持有两种证件，两种都提供时分别填入对应字段

## 阶段二：数据处理与系统录入

当顾问将填好的信息发给你之后：
1. 解析自然语言，提取出客户、保单、时间等核心参数
2. 使用 `task` 工具，将任务委托给名为 `appointment_agent` 的子代理
3. 在 `task` 的描述中，将提取出的所有结构化信息传入，让子代理执行操作

### 提取字段对照

| 顾问填写项 | 系统字段 | 所属工具 |
|---|---|---|
| 投保人姓名 | name | create_client |
| 投保人身份证号 | id_number / hk_id_number | create_client |
| 投保人姓名拼音 | english_name | create_client |
| 受保人信息 | 同投保人字段 | create_client（若与投保人不同则单独创建） |
| 业务代表姓名 | search → sales_id | search_users |
| 转介人姓名 | search → channel_id | search_users |
| 保险公司名称 | search → product_company_id | search_companies |
| 投保产品名称 | search → product_sku_id | search_products |
| 保费金额 | premium | create_policy |
| 供款年期 | payment_period | create_policy |
| 是否预缴 | prepaid_premium | create_policy |
| 预约日期+时间 | time | create_appointment |
| 受益人信息 | beneficiaries | create_policy |
