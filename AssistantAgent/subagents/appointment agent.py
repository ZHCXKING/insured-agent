# %%
from pydantic import BaseModel, Field
from typing import List, Optional
# %%
class ReservationData(BaseModel):
    """预约签单的底层结构化数据"""
    client_name: Optional[str] = Field(None, description="投保人/客户姓名")
    product_name: Optional[str] = Field(None, description="投保的产品或保司名称")
    reservation_date: Optional[str] = Field(None, description="预约签单的日期，格式 YYYY.MM.DD")
    reservation_time: Optional[str] = Field(None, description="预约的具体时间")
    is_prepaid: bool = Field(False, description="是否已预缴")
    holding_person: Optional[str] = Field(None, description="业绩持牌人姓名")
    referral_person: Optional[str] = Field(None, description="转介人姓名，若无则为空")
    is_complete: bool = Field(False, description="资料是否已收集完整")
    missing_fields: List[str] = Field(default_factory=list, description="记录缺失的字段列表")
# %%
class SpecialistResponse(BaseModel):
    """预约专员的完整响应结构"""
    summary: str = Field(description="对当前沟通进展的简短总结")
    needs_question: bool = Field(description="是否需要向用户进一步提问以补全信息")
    question_content: Optional[str] = Field(None, description="如果需要提问，这里填写具体的提问话术；否则为空")
    current_data: ReservationData = Field(description="当前已提取并整理的预约结构化数据")

# 修改配置
reservation_specialist = {
    "name": "reservation_specialist",
    "description": "负责在签单群内引导用户填写信息并返回分段式的结构化分析。",
    "system_prompt": """你是一位严谨的预约审核员。
    请按以下逻辑处理：
    1. 总结：简述用户提供了哪些信息。
    2. 判断：检查关键字段（姓名、产品、日期、时间）是否齐全。
    3. 提问：如果信息不全，设置 needs_question 为 true，并在 question_content 中给出引导回复。
    4. 填充：将提取到的信息填入 current_data 模型。""",
    # 👇 这里的响应格式改为顶层容器模型
    "response_format": SpecialistResponse,
    "skills": ["/skills/reservation/"]
}

ALL_SUBAGENTS = [reservation_specialist]