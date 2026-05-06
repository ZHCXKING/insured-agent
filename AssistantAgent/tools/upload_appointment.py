# TODO 这是一个大概的框架，具体情况还得等中台完成
import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
# 1. 定义中台需要的完整数据结构
class AppointmentSchema(BaseModel):
    client_name: str = Field(..., description="顾问或客户的姓名")
    appointment_time: str = Field(..., description="预约的具体时间，例如：2024-11-01 14:00")
    topic: str = Field(..., description="咨询的具体主题或诉求")
    phone_number: str = Field(..., description="联系电话")
# 2. 创建提交工具
@tool(args_schema=AppointmentSchema)
def submit_appointment_to_backend(client_name: str, appointment_time: str, topic: str, phone_number: str) -> str:
    """
    【关键工具】当且仅当你（AI）已经通过对话收集齐了用户的：姓名、时间、主题、电话这4个信息后，
    调用此工具将预约信息正式提交到业务中台。缺少任何一个信息都不要调用此工具。
    """
    try:
        # 这里写你请求中台 API 的逻辑
        payload = {
            "name": client_name,
            "time": appointment_time,
            "topic": topic,
            "phone": phone_number
        }
        # response = requests.post("https://your-backend.com/api/appointments", json=payload)
        # response.raise_for_status()
        # 模拟提交成功
        return f"预约已成功提交到中台！(预约人:{client_name}, 时间:{appointment_time})"
    except Exception as e:
        return f"提交失败，中台返回错误: {str(e)}。请让用户稍后再试。"