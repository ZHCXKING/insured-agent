# %%
from datetime import datetime, timezone, timedelta
from langchain.tools import tool
# %%
@tool()
def get_current_time() -> str:
    """获取当前的日期和时间，返回格式为 YYYY-MM-DD HH:mm（星期X）。当需要知道当前时间来判断日期时使用。"""
    now = datetime.now(timezone(timedelta(hours=8)))
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    weekday = weekdays[now.weekday()]
    return now.strftime(f"%Y-%m-%d %H:%M（星期{weekday}）")
